from backend.models import Article
from backend.processing import canonicalize_url, dedupe_articles


def mk_article(idx: str, title: str, url: str, content: str):
    return Article(
        id=idx,
        title=title,
        source_name="src",
        source_url=url,
        published_at="2026-02-24T10:00:00Z",
        topic="AI",
        canonical_url=url,
        original_url=url,
        is_valid_source_url=True,
        source_url_status_code=200,
        summary_ko="s",
        key_points=["k"],
        keywords=["ai"],
        content_text=content,
    )


def test_canonicalize_url_removes_utm_and_slash():
    got = canonicalize_url("https://Example.com/blog/post/?utm_source=x&a=1")
    assert got == "https://example.com/blog/post?a=1"


def test_dedupe_by_url_and_hash_and_title_similarity():
    a1 = mk_article("1", "OpenAI model released", "https://a.com/p?utm=1", "same content")
    a2 = mk_article("2", "OpenAI model released", "https://a.com/p", "same content")
    a3 = mk_article("3", "OpenAI model released today", "https://b.com/q", "different")
    out = dedupe_articles([a1, a2, a3], title_threshold=0.95)
    assert len(out) == 2
    assert sorted(a.id for a in out) == ["1", "3"]
