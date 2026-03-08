from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from math import sqrt
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .models import Article, Cluster

HOME_PATHS = {"", "/", "/home", "/news", "/category", "/categories", "/topics", "/ai", "/science", "/tech"}


class BaseSummarizer:
    def summarize(self, article_text: str) -> tuple[str, list[str], list[str]]:
        raise NotImplementedError


class RuleBasedSummarizer(BaseSummarizer):
    def summarize(self, article_text: str) -> tuple[str, list[str], list[str]]:
        cleaned = re.sub(r"\s+", " ", article_text).strip()
        sentences = [s.strip() for s in re.split(r"[.!?]", cleaned) if s.strip()]
        summary = (" ".join(sentences[:2]) or "요약 생성 실패")[:240]
        key_points = [s[:90] for s in sentences[:4]]
        words = [w.lower() for w in re.findall(r"[A-Za-z가-힣]{3,}", cleaned)]
        keywords = [w for w, _ in Counter(words).most_common(6)]
        return summary, key_points or ["핵심 문장 추출 실패"], keywords


def get_summarizer(strategy: str | None = None) -> BaseSummarizer:
    # LLM summarizer can be injected later; keep default as rule-based.
    return RuleBasedSummarizer()


def canonicalize_url(url: str) -> str:
    parsed = urlparse((url or "").strip())
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False) if not k.startswith("utm_")]
    path = re.sub(r"/+", "/", parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    netloc = parsed.netloc.lower()
    return urlunparse((parsed.scheme.lower(), netloc, path, "", urlencode(query), ""))


def is_probably_article_url(url: str) -> bool:
    parsed = urlparse(url)
    path = (parsed.path or "").rstrip("/").lower()
    return path not in HOME_PATHS and len(path.split("/")) > 1


def content_hash(content: str | None) -> str | None:
    if not content:
        return None
    normalized = re.sub(r"\s+", " ", content).strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def pick_representative(existing: Article, incoming: Article) -> Article:
    if len(incoming.content_text or "") > len(existing.content_text or ""):
        return incoming
    if incoming.published_at > existing.published_at:
        return incoming
    return existing


def dedupe_articles(articles: list[Article], title_threshold: float = 0.92) -> list[Article]:
    by_url: dict[str, Article] = {}
    by_hash: dict[str, Article] = {}
    deduped: list[Article] = []
    for article in articles:
        article = replace(article, canonical_url=canonicalize_url(article.canonical_url))
        article = replace(article, content_hash=content_hash(article.content_text))
        existing = by_url.get(article.canonical_url)
        if existing:
            by_url[article.canonical_url] = pick_representative(existing, article)
            continue
        if article.content_hash and article.content_hash in by_hash:
            rep = pick_representative(by_hash[article.content_hash], article)
            by_hash[article.content_hash] = rep
            by_url[rep.canonical_url] = rep
            continue
        matched = None
        for prev in deduped:
            if title_similarity(prev.title, article.title) >= title_threshold:
                matched = prev
                break
        if matched:
            rep = pick_representative(matched, article)
            deduped = [rep if x.id == matched.id else x for x in deduped]
            by_url[rep.canonical_url] = rep
            if rep.content_hash:
                by_hash[rep.content_hash] = rep
            continue
        deduped.append(article)
        by_url[article.canonical_url] = article
        if article.content_hash:
            by_hash[article.content_hash] = article
    return deduped


def _vectorize(text: str) -> Counter[str]:
    terms = re.findall(r"[A-Za-z가-힣]{3,}", text.lower())
    return Counter(terms)


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[k] * b.get(k, 0) for k in a)
    norm_a = sqrt(sum(v * v for v in a.values()))
    norm_b = sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def cluster_articles(articles: list[Article], threshold: float = 0.28) -> tuple[list[Article], list[Cluster]]:
    vectors = {a.id: _vectorize(f"{a.title} {a.summary_ko}") for a in articles}
    parent = {a.id: a.id for a in articles}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(articles):
        for b in articles[i + 1 :]:
            if _cosine(vectors[a.id], vectors[b.id]) >= threshold:
                union(a.id, b.id)

    groups: dict[str, list[Article]] = defaultdict(list)
    for article in articles:
        groups[find(article.id)].append(article)

    clusters: list[Cluster] = []
    updated_articles: list[Article] = []
    for idx, group in enumerate(groups.values(), start=1):
        cid = f"cluster-{idx:03d}" if len(group) > 1 else None
        if cid:
            top_keywords = Counter(k for a in group for k in a.keywords).most_common(5)
            title = sorted(group, key=lambda x: x.published_at, reverse=True)[0].title
            clusters.append(
                Cluster(
                    cluster_id=cid,
                    cluster_title=title,
                    cluster_summary_ko=" / ".join(a.summary_ko for a in group[:2]),
                    keywords=[k for k, _ in top_keywords],
                    article_ids=[a.id for a in sorted(group, key=lambda x: x.published_at, reverse=True)],
                )
            )
        for a in group:
            updated_articles.append(replace(a, cluster_id=cid))
    return updated_articles, clusters


def stable_sort_articles(articles: list[Article], order: str = "latest") -> list[Article]:
    reverse = order == "latest"
    return sorted(
        articles,
        key=lambda a: (a.published_at, a.source_name.lower(), a.title.lower(), a.id),
        reverse=reverse,
    )


def filter_with_auto_relax(
    articles: list[Article], topic: str = "All", period: str = "24h", keyword: str = ""
) -> tuple[list[Article], str | None]:
    now = datetime.now(timezone.utc)
    windows = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "all": None,
    }
    sequence = [period] + [p for p in ["24h", "7d", "30d", "all"] if p != period]
    keyword = keyword.strip().lower()
    for idx, p in enumerate(sequence):
        cutoff = windows[p]
        filtered = []
        for a in articles:
            if topic != "All" and a.topic != topic:
                continue
            if cutoff:
                dt = datetime.fromisoformat(a.published_at.replace("Z", "+00:00"))
                if now - dt > cutoff:
                    continue
            if keyword and keyword not in (a.title + " " + a.summary_ko).lower():
                continue
            filtered.append(a)
        if filtered:
            badge = None if idx == 0 else f"기간을 자동 확장했습니다: {period} → {p}"
            return stable_sort_articles(filtered), badge
    return [], "조건에 맞는 기사가 없어 all 기간까지 확장했습니다."


def build_trends(articles: list[Article], days: int = 7, top_n: int = 10) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = [
        a
        for a in articles
        if datetime.fromisoformat(a.published_at.replace("Z", "+00:00")) >= cutoff
    ]
    kw = Counter(k for a in recent for k in a.keywords).most_common(top_n)
    src = Counter(a.source_name for a in recent)
    topic = Counter(a.topic for a in recent)
    return {
        "recent_days": days,
        "keywords_top": [{"keyword": k, "count": c} for k, c in kw],
        "source_distribution": [{"source": k, "count": v} for k, v in src.items()],
        "topic_ratio": {"AI": topic.get("AI", 0), "ScienceTech": topic.get("ScienceTech", 0), "Other": topic.get("Other", 0)},
    }
