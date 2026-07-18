#!/usr/bin/env python3
"""RAG BM25 retrieve for Kekasir blog generator. CLI: --query --feature-keys --category --k --rebuild --json"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "rag" / "corpus"
INDEX_DIR = ROOT / "rag" / "index"
CHUNKS_PATH = INDEX_DIR / "chunks.jsonl"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.I)
PRICING_BOOST = 1.25
ANTI_CLAIM_BOOST = 1.2
FEATURE_BOOST = 1.15
ALWAYS_BIAS = " harga basic pro 60000 120000 qris 0,7 trial 14 hari anti claim"


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "") if len(t) > 1]


def split_chunks(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n(?=## )", text)
    chunks = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if i == 0 and part.startswith("# ") and "\n" not in part.strip():
            continue
        heading = part.split("\n", 1)[0][:120]
        chunks.append(
            {
                "id": f"{path.stem}::{i}",
                "source": str(path.relative_to(ROOT)),
                "heading": heading,
                "text": part,
                "tokens": tokenize(part),
            }
        )
    return chunks


def build_index() -> list[dict]:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks: list[dict] = []
    for md in sorted(CORPUS.glob("*.md")):
        all_chunks.extend(split_chunks(md))
    pub = CORPUS / "published"
    if pub.is_dir():
        for md in sorted(pub.glob("*.md")):
            all_chunks.extend(split_chunks(md))

    with CHUNKS_PATH.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            row = {k: v for k, v in c.items() if k != "tokens"}
            row["token_count"] = len(c["tokens"])
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return all_chunks


def load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        return build_index()
    chunks = []
    for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["tokens"] = tokenize(row["text"])
        chunks.append(row)
    return chunks


def source_boost(src: str) -> float:
    if "01-brand-pricing" in src:
        return PRICING_BOOST
    if "03-anti-claims" in src:
        return ANTI_CLAIM_BOOST
    if "10-legal-compliance" in src or "11-faq-product-truth" in src:
        return 1.22
    if "09-bahasa-lokal" in src:
        return 1.18
    if "02-features-cta" in src:
        return FEATURE_BOOST
    return 1.0


def bm25_scores(
    query_tokens: list[str], chunks: list[dict], k1: float = 1.5, b: float = 0.75
) -> list[tuple[float, dict]]:
    if not chunks:
        return []
    df: Counter[str] = Counter()
    for c in chunks:
        df.update(set(c["tokens"]))
    n = len(chunks)
    avgdl = sum(len(c["tokens"]) for c in chunks) / max(n, 1)
    scores: list[tuple[float, dict]] = []
    qtf = Counter(query_tokens)
    for c in chunks:
        dl = len(c["tokens"]) or 1
        tf = Counter(c["tokens"])
        score = 0.0
        for term, qn in qtf.items():
            if term not in tf:
                continue
            n_q = df.get(term, 0) or 1
            idf = math.log(1 + (n - n_q + 0.5) / (n_q + 0.5))
            freq = tf[term]
            denom = freq + k1 * (1 - b + b * dl / avgdl)
            score += idf * (freq * (k1 + 1) / denom) * qn
        score *= source_boost(c.get("source", ""))
        scores.append((score, c))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores


def retrieve(
    query: str,
    k: int = 8,
    feature_keys: list[str] | None = None,
    category: str | None = None,
) -> list[dict]:
    chunks = load_chunks()
    q = query
    if feature_keys:
        q += " " + " ".join(feature_keys)
    if category:
        q += " " + category
    q += ALWAYS_BIAS
    ranked = bm25_scores(tokenize(q), chunks)
    out = []
    for score, c in ranked[:k]:
        if score <= 0:
            continue
        out.append(
            {
                "id": c["id"],
                "source": c["source"],
                "heading": c.get("heading"),
                "score": round(score, 4),
                "text": c["text"][:2000],
            }
        )
    return out


def format_context(hits: list[dict]) -> str:
    blocks = ["### FAKTA PRODUK & ATURAN (wajib patuhi; jangan bertentangan)\n"]
    for i, h in enumerate(hits, 1):
        blocks.append(f"#### [{i}] {h['source']} — {h.get('heading', '')}\n{h['text']}\n")
    return "\n".join(blocks)


def main() -> int:
    ap = argparse.ArgumentParser(description="Retrieve RAG chunks for blog generation")
    ap.add_argument("--query", default="")
    ap.add_argument("--feature-keys", default="")
    ap.add_argument("--category", default="")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.rebuild or not CHUNKS_PATH.exists():
        build_index()
        print(f"index built → {CHUNKS_PATH}", file=sys.stderr)

    keys = [x.strip() for x in args.feature_keys.split(",") if x.strip()]
    hits = retrieve(args.query, k=args.k, feature_keys=keys, category=args.category or None)
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        print(format_context(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
