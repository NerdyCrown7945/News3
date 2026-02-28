from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI

from .generate_data import main as generate_static

app = FastAPI(title="AI ScienceTech Briefing API")
DATA_DIR = Path("public")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@app.get("/api/feed")
def get_feed():
    return _read_json(DATA_DIR / "feed.json")


@app.get("/api/articles/{article_id}")
def get_article(article_id: str):
    return _read_json(DATA_DIR / "articles" / f"{article_id}.json")


@app.get("/api/clusters")
def get_clusters():
    return _read_json(DATA_DIR / "clusters.json")


@app.get("/api/trends")
def get_trends():
    return _read_json(DATA_DIR / "trends.json")


@app.post("/api/collect")
def run_collection():
    generate_static()
    return {"ok": True, "message": "수집 및 정적 데이터 재생성 완료"}
