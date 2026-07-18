#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import shutil
from pathlib import Path
from typing import Any

from paths import DATA, ROOT

MANIFEST = DATA / "panduan_assets_manifest.json"


def load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {"items": [], "by_feature": {}, "by_topic": {}}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def pick_assets(
    feature_keys: list[str] | None = None,
    topics: list[str] | None = None,
    limit: int = 3,
    exclude_paths: set[str] | None = None,
) -> list[dict[str, Any]]:
    man = load_manifest()
    items = man.get("items") or []
    exclude_paths = exclude_paths or set()
    scored: list[tuple[int, dict[str, Any]]] = []
    feats = set(feature_keys or [])
    tops = set(topics or [])
    for it in items:
        if it.get("path") in exclude_paths:
            continue
        score = 0
        it_feats = set(it.get("features") or [])
        it_tops = set(it.get("topics") or [])
        score += 3 * len(feats & it_feats)
        score += 2 * len(tops & it_tops)
        if score <= 0:
            continue
        scored.append((score, it))
    scored.sort(key=lambda x: (-x[0], x[1].get("path") or ""))
    # diversify: max 1 per stem basename preference
    picked: list[dict[str, Any]] = []
    seen_files: set[str] = set()
    for score, it in scored:
        fn = it.get("file") or ""
        if fn in seen_files:
            continue
        seen_files.add(fn)
        picked.append(it)
        if len(picked) >= limit:
            break
    if len(picked) < limit:
        # fill with high-value general F&B UI shots
        pool = [it for it in items if it.get("path") not in exclude_paths and it not in picked]
        random.shuffle(pool)
        for it in pool:
            if (it.get("file") or "") in seen_files:
                continue
            if any(t in (it.get("topics") or []) for t in ("produk-menu", "pos-shift", "hpp-stok", "meja-qr", "qris")):
                picked.append(it)
                seen_files.add(it.get("file") or "")
            if len(picked) >= limit:
                break
    return picked[:limit]


def copy_to_article(
    asset: dict[str, Any],
    dest_dir: Path,
    dest_name: str,
) -> Path | None:
    src = ROOT / asset["path"]
    if not src.exists():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / dest_name
    if dest.suffix.lower() != src.suffix.lower():
        dest = dest.with_suffix(src.suffix.lower())
    shutil.copy2(src, dest)
    return dest


def pick_and_copy(
    dest_dir: Path,
    feature_keys: list[str] | None = None,
    limit: int = 3,
    name_prefix: str = "fig",
) -> list[dict[str, Any]]:
    picks = pick_assets(feature_keys=feature_keys, limit=limit)
    out = []
    for i, asset in enumerate(picks, 1):
        name = f"{name_prefix}-{i:02d}{Path(asset['path']).suffix.lower()}"
        dest = copy_to_article(asset, dest_dir, name)
        if not dest:
            continue
        out.append(
            {
                "file": f"images/{dest.name}",
                "alt": asset.get("alt") or dest.stem,
                "source": "panduan",
                "source_path": asset.get("path"),
            }
        )
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="hpp_recipe,pos_core")
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()
    feats = [x.strip() for x in args.features.split(",") if x.strip()]
    for a in pick_assets(feature_keys=feats, limit=args.limit):
        print(f"{a['topics']} {a['features']} -> {a['path']}")
