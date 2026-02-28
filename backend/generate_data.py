from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Article
from .processing import (
    build_trends,
    canonicalize_url,
    cluster_articles,
    dedupe_articles,
    get_summarizer,
    is_probably_article_url,
)

MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "300"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "public"))


def sample_articles() -> list[Article]:
    raw = [
        {
            "id": "a1",
            "title": "OpenAI announces lightweight reasoning model",
            "source_name": "OpenAI",
            "source_url": "https://openai.com/blog/reasoning",
            "published_at": "2026-02-24T10:00:00Z",
            "topic": "AI",
            "url": "https://openai.com/blog/reasoning?utm_source=x",
            "content": "OpenAI released a lighter reasoning model for edge inference. The model improves latency and cost.",
        },
        {
            "id": "a2",
            "title": "New battery chemistry improves charging speed",
            "source_name": "ScienceDaily",
            "source_url": "https://www.sciencedaily.com/releases/2026/02/260224123.htm",
            "published_at": "2026-02-24T11:00:00Z",
            "topic": "ScienceTech",
            "url": "https://www.sciencedaily.com/releases/2026/02/260224123.htm",
            "content": "Researchers developed new electrolyte that can charge fast with better thermal stability.",
        },
        {
            "id": "a3",
            "title": "OpenAI announces lightweight reasoning model for devices",
            "source_name": "TechCrunch",
            "source_url": "https://techcrunch.com/2026/02/24/openai-reasoning-model/",
            "published_at": "2026-02-24T10:30:00Z",
            "topic": "AI",
            "url": "https://techcrunch.com/2026/02/24/openai-reasoning-model/",
            "content": "The company announced a lightweight model for on-device reasoning with lower cost.",
        },
    ]
    summarizer = get_summarizer(os.getenv("SUMMARIZER_STRATEGY", "rule"))
    items: list[Article] = []
    for item in raw[:MAX_ARTICLES]:
        summary, points, keywords = summarizer.summarize(item["content"])
        canonical = canonicalize_url(item["url"])
        items.append(
            Article(
                id=item["id"],
                title=item["title"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                published_at=item["published_at"],
                topic=item["topic"],
                canonical_url=canonical,
                original_url=item["url"],
                is_valid_source_url=is_probably_article_url(canonical),
                source_url_status_code=200,
                summary_ko=summary,
                key_points=points[:4],
                keywords=keywords,
                content_text=item["content"][:400],
            )
        )
    return items


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    articles = dedupe_articles(sample_articles())
    articles, clusters = cluster_articles(articles)
    trends = build_trends(articles)

    feed = {
        "mode": "static",
        "items": [a.to_dict() for a in articles],
        "clusters": [c.to_dict() for c in clusters],
        "generated_at": "2026-02-25T00:00:00Z",
    }
    write_json(OUTPUT_DIR / "feed.json", feed)
    write_json(OUTPUT_DIR / "clusters.json", [c.to_dict() for c in clusters])
    write_json(OUTPUT_DIR / "trends.json", trends)
    for article in articles:
        write_json(OUTPUT_DIR / "articles" / f"{article.id}.json", article.to_dict())


if __name__ == "__main__":
    main()
