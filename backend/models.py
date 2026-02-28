from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Article:
    id: str
    title: str
    source_name: str
    source_url: str
    published_at: str
    topic: str
    canonical_url: str
    original_url: str
    is_valid_source_url: bool
    source_url_status_code: int | None
    summary_ko: str
    key_points: list[str]
    keywords: list[str]
    content_text: str | None = None
    cluster_id: str | None = None
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Cluster:
    cluster_id: str
    cluster_title: str
    cluster_summary_ko: str
    keywords: list[str]
    article_ids: list[str]
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
