from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from paths import CATALOG, CONFIG, QUEUE, STATE, ensure_dirs


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_config() -> dict[str, Any]:
    ensure_dirs()
    if CONFIG.exists() and yaml is not None:
        return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    if CONFIG.exists():
        return _minimal_yaml(CONFIG.read_text(encoding="utf-8"))
    return {}


def _minimal_yaml(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#") or line.startswith(" "):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip().strip('"').strip("'")
            if v.isdigit():
                out[k.strip()] = int(v)
            elif re.match(r"^\d+\.\d+$", v):
                out[k.strip()] = float(v)
            elif v in ("true", "false"):
                out[k.strip()] = v == "true"
            else:
                out[k.strip()] = v
    return out


def load_catalog() -> dict[str, Any]:
    ensure_dirs()
    if not CATALOG.exists():
        cat = {
            "version": 1,
            "updated_at": None,
            "categories": [],
            "posts": [],
            "slugs": [],
        }
        save_catalog(cat)
        return cat
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def save_catalog(cat: dict[str, Any]) -> None:
    ensure_dirs()
    cat["updated_at"] = now_iso()
    CATALOG.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_state() -> dict[str, Any]:
    ensure_dirs()
    if not STATE.exists():
        st = {
            "worker_pid": None,
            "last_heartbeat": None,
            "last_job_id": None,
            "counters": {"done_today": 0, "failed_today": 0, "images_today": 0},
            "daily_cap": 0,
            "date": datetime.now().date().isoformat(),
        }
        save_state(st)
        return st
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(st: dict[str, Any]) -> None:
    ensure_dirs()
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def heartbeat(job_id: str | None = None) -> None:
    st = load_state()
    today = datetime.now().date().isoformat()
    if st.get("date") != today:
        st["date"] = today
        st["counters"] = {"done_today": 0, "failed_today": 0, "images_today": 0}
    st["last_heartbeat"] = now_iso()
    if job_id:
        st["last_job_id"] = job_id
    save_state(st)


def slugify(title: str, max_len: int = 80) -> str:
    text = unicodedata.normalize("NFKD", title)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len].strip("-")


def unique_slug(base: str, existing: set[str]) -> str:
    slug = slugify(base)
    if slug not in existing:
        return slug
    for i in range(2, 100):
        cand = f"{slug[:70]}-{i}" if len(slug) > 70 else f"{slug}-{i}"
        if cand not in existing:
            return cand
    return f"{slug}-{int(datetime.now().timestamp())}"


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def rewrite_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def count_words(text: str) -> int:
    body = re.sub(r"```.*?```", " ", text, flags=re.S)
    body = re.sub(r"[#>*`\[\]\(\)!|_-]", " ", body)
    return len(re.findall(r"\w+", body, flags=re.UNICODE))


def load_queue() -> list[dict[str, Any]]:
    return read_jsonl(QUEUE)


def save_queue(rows: list[dict[str, Any]]) -> None:
    rewrite_jsonl(QUEUE, rows)
