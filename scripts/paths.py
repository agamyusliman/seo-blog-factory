from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("BLOG_ROOT", Path(__file__).resolve().parents[1])).resolve()
DATA = ROOT / "data"
CONTENT = ROOT / "content"
LOGS = ROOT / "logs"
RAG = ROOT / "rag"
CORPUS = RAG / "corpus"
CATALOG = DATA / "catalog.json"
QUEUE = DATA / "queue.jsonl"
STATE = DATA / "state.json"
CONFIG = ROOT / "config.yaml"
REFS = DATA / "refs"
SEED_TITLES = DATA / "seed_titles.jsonl"


def ensure_dirs() -> None:
    for p in (DATA, CONTENT, LOGS, REFS, CORPUS / "published"):
        p.mkdir(parents=True, exist_ok=True)
