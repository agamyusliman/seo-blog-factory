#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from common import load_catalog, load_queue, load_state
from paths import CONTENT, ensure_dirs

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    ensure_dirs()
    st = load_state()
    q = load_queue()
    cat = load_catalog()
    by = Counter(j.get("status") for j in q)
    articles = list(CONTENT.glob("*/*/article.md"))
    print(json.dumps(
        {
            "state": st,
            "queue": dict(by),
            "queue_total": len(q),
            "catalog_posts": len(cat.get("posts") or []),
            "catalog_slugs": len(cat.get("slugs") or []),
            "article_files": len(articles),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
