#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from common import (
    load_catalog,
    load_config,
    load_queue,
    now_iso,
    read_jsonl,
    save_queue,
    slugify,
    unique_slug,
)
from paths import REFS, SEED_TITLES, ensure_dirs

sys.path.insert(0, str(Path(__file__).resolve().parent))

CAT_MAP = {
    "tips": "tips-bisnis",
    "tips bisnis": "tips-bisnis",
    "inspirasi": "inspirasi",
    "studi kasus": "inspirasi",
    "studi-kasus": "inspirasi",
    "cerita sukses": "inspirasi",
    "info produk": "info-produk",
    "ide bisnis": "ide-usaha",
    "ide-usaha": "ide-usaha",
}


def map_category(raw: str | None, default: str = "tips-bisnis") -> str:
    if not raw:
        return default
    key = raw.strip().lower()
    return CAT_MAP.get(key, default)


def feature_guess(title: str) -> list[str]:
    t = title.lower()
    keys = []
    pairs = [
        (["self order", "self-order", "qr meja", "menu digital"], "self_order_qr"),
        (["qris"], "qris"),
        (["hpp", "food cost", "margin"], "hpp_recipe"),
        (["stok", "opname", "inventori", "inventory"], "inventory"),
        (["shift", "rekap kas", "tutup kas"], "shift"),
        (["dapur", "kds", "kitchen"], "kds"),
        (["meja", "reservasi"], "table_mgmt"),
        (["offline"], "offline"),
        (["printer", "struk"], "print"),
        (["multi cabang", "multi outlet", "cabang"], "multi_outlet"),
        (["laporan", "omzet"], "reports"),
        (["barcode"], "barcode"),
        (["appointment", "janji temu", "booking"], "appointment"),
    ]
    for words, key in pairs:
        if any(w in t for w in words):
            keys.append(key)
    if not keys:
        keys = ["pos_core", "trial"]
    return keys[:4]


def load_refs() -> list[dict[str, Any]]:
    rows = []
    if not REFS.exists():
        return rows
    for path in REFS.rglob("*.jsonl"):
        rows.extend(read_jsonl(path))
    return rows


def build_jobs_from_seeds(limit: int | None, existing_slugs: set[str]) -> list[dict[str, Any]]:
    seeds = read_jsonl(SEED_TITLES)
    jobs = []
    for s in seeds:
        title = s["title"]
        base = slugify(title)
        slug = unique_slug(base, existing_slugs)
        existing_slugs.add(slug)
        jobs.append(
            {
                "id": f"job_{uuid.uuid4().hex[:10]}",
                "title": title,
                "slug": slug,
                "category": s.get("category") or "tips-bisnis",
                "feature_keys": s.get("feature_keys") or feature_guess(title),
                "persona": s.get("persona") or "umkm",
                "primary_kw": s.get("primary_kw") or title.lower(),
                "outline": s.get("outline") or [],
                "status": "pending",
                "attempts": 0,
                "source": "seed",
                "created_at": now_iso(),
            }
        )
        if limit and len(jobs) >= limit:
            break
    return jobs


def build_jobs_from_refs(limit: int, existing_slugs: set[str], existing_titles: set[str]) -> list[dict[str, Any]]:
    refs = load_refs()
    jobs = []
    for r in refs:
        title = (r.get("title") or "").strip()
        if len(title) < 15:
            continue
        norm = title.lower()
        if norm in existing_titles:
            continue
        if any(b in norm for b in ("qasir", "moka", "olsera", "kledo", "esb ")):
            title = re_brand_neutral(title)
        base = slugify(title)
        if not base:
            continue
        slug = unique_slug(base, existing_slugs)
        existing_slugs.add(slug)
        existing_titles.add(norm)
        jobs.append(
            {
                "id": f"job_{uuid.uuid4().hex[:10]}",
                "title": title,
                "slug": slug,
                "category": map_category(r.get("category_raw")),
                "feature_keys": feature_guess(title),
                "persona": "umkm",
                "primary_kw": title.lower()[:80],
                "outline": [],
                "status": "pending",
                "attempts": 0,
                "source": f"ref:{r.get('site')}",
                "source_url": r.get("url"),
                "created_at": now_iso(),
            }
        )
        if len(jobs) >= limit:
            break
    return jobs


def re_brand_neutral(title: str) -> str:
    import re

    t = re.sub(r"\b(Qasir|Moka|Olsera|Kledo|ESB)\b", "", title, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" -–|:")
    return t or title


def main() -> int:
    ensure_dirs()
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-seeds", action="store_true")
    ap.add_argument("--from-refs", action="store_true")
    ap.add_argument("--count", type=int, default=50)
    ap.add_argument("--reset-queue", action="store_true")
    args = ap.parse_args()

    if not args.from_seeds and not args.from_refs:
        args.from_seeds = True

    cat = load_catalog()
    existing_slugs = set(cat.get("slugs") or [])
    for j in load_queue():
        if j.get("slug"):
            existing_slugs.add(j["slug"])
    existing_titles = { (j.get("title") or "").lower() for j in load_queue() }

    jobs: list[dict[str, Any]] = []
    if args.from_seeds:
        jobs.extend(build_jobs_from_seeds(args.count if not args.from_refs else None, existing_slugs))
    if args.from_refs:
        need = max(0, args.count - len(jobs)) if args.from_seeds else args.count
        jobs.extend(build_jobs_from_refs(need or args.count, existing_slugs, existing_titles))

    jobs = jobs[: args.count]
    if args.reset_queue:
        queue = jobs
    else:
        queue = load_queue()
        pending_slugs = {j["slug"] for j in queue if j.get("status") == "pending"}
        for j in jobs:
            if j["slug"] not in pending_slugs and j["slug"] not in set(cat.get("slugs") or []):
                queue.append(j)
    save_queue(queue)
    pending = sum(1 for j in queue if j.get("status") == "pending")
    print(f"queue_size={len(queue)} pending={pending} added≈{len(jobs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
