#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import load_catalog, save_catalog
from paths import CONTENT, ensure_dirs

sys.path.insert(0, str(Path(__file__).resolve().parent))


def tokenize_words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def post_tokens(p: dict) -> set[str]:
    folder = CONTENT / p["category"] / p["slug"]
    meta_path = folder / "meta.json"
    bits = [p.get("title") or "", p.get("slug") or "", p.get("category") or ""]
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        bits.append(meta.get("excerpt") or "")
        bits.extend(meta.get("tags") or [])
        bits.append(meta.get("primary_kw") or "")
    return tokenize_words(" ".join(bits))


def ensure_related_section(md: str, links: list[tuple[str, str]]) -> str:
    if not links:
        return md
    section = "\n\n## Artikel terkait\n\n" + "\n".join(f"- [{a}](/blog/{s})" for s, a in links) + "\n"
    if re.search(r"^##\s+Artikel terkait", md, flags=re.M | re.I):
        return re.sub(
            r"^##\s+Artikel terkait\n(?:.*\n)*?(?=^##\s|\Z)",
            section.lstrip() + "\n",
            md,
            count=1,
            flags=re.M | re.I,
        )
    return md.rstrip() + section


def main() -> int:
    ensure_dirs()
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3)
    args = ap.parse_args()

    cat = load_catalog()
    posts = [
        p
        for p in (cat.get("posts") or [])
        if p.get("status") in ("done", "text_done", "images_partial", "needs_review")
    ]
    if len(posts) < 2:
        print("need at least 2 posts")
        return 0

    vectors = [(p, post_tokens(p)) for p in posts]
    for p, tok in vectors:
        scored = []
        for q, qtok in vectors:
            if q["slug"] == p["slug"]:
                continue
            sc = jaccard(tok, qtok)
            if q.get("category") == p.get("category"):
                sc += 0.05
            scored.append((sc, q))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[: args.k]
        links = [(q["slug"], q["title"]) for sc, q in top if sc > 0]
        folder = CONTENT / p["category"] / p["slug"]
        md_path = folder / "article.md"
        meta_path = folder / "meta.json"
        if md_path.exists() and links:
            md = md_path.read_text(encoding="utf-8")
            md_path.write_text(ensure_related_section(md, links), encoding="utf-8")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["internal_links"] = [{"slug": s, "anchor": a} for s, a in links]
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        p["internal_links"] = [s for s, _ in links]
        print(f"{p['slug']} -> {[s for s, _ in links]}")

    save_catalog(cat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
