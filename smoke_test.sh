#!/usr/bin/env bash
# Local Mac smoke test — 1 article (text + images) with latest pipeline.
# Usage:
#   ./smoke_test.sh                       # first seed after queue rebuild
#   ./smoke_test.sh "Cara Hitung HPP"     # filter by title substring
#   ./smoke_test.sh --keep-content "QR"   # do not wipe existing content/*
set -euo pipefail

cd "$(dirname "$0")"
export PATH="/Users/agamyusliman/Library/PhpWebStudy/env/node/bin:${PATH:-}"
export PYTHONPATH=scripts

KEEP_CONTENT=0
TITLE_FILTER=""
for arg in "$@"; do
  case "$arg" in
    --keep-content) KEEP_CONTENT=1 ;;
    *) TITLE_FILTER="$arg" ;;
  esac
done

PYTHON=".venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi

echo "=== ENV ==="
grep -E "AI_CHAT_MODELS|AI_CHAT_MODEL|AI_IMAGE_MODEL|BLOG_DAILY_CAP" .env 2>/dev/null || true
echo "  keep_content=$KEEP_CONTENT title_filter=${TITLE_FILTER:-<first seed>}"
echo ""

echo "=== VERIFY AI CLIENT (round-robin + UTF-8) ==="
$PYTHON - <<'PY'
import sys
sys.path.insert(0, "scripts")
from ai_client import chat, last_chat_model, _chat_models, fix_mojibake
print("  Configured:", _chat_models())
for i in range(2):
    out = chat([{"role": "user", "content": "Reply with exactly: OK"}], temperature=0.1)
    print(f"  Call {i+1}: model={last_chat_model()!r} out={out[:40]!r}")
sample = "daftar bahan â total"
fixed = fix_mojibake(sample)
print(f"  mojibake repair: {sample!r} -> {fixed!r}")
assert "â" not in fixed or "→" in fixed or "->" in fixed or fixed != sample
print("  OK")
PY
echo ""

echo "=== RESET QUEUE ==="
$PYTHON scripts/plan_topics.py --from-seeds --reset-queue 2>&1 | tail -3

echo ""
echo "=== RESET CATALOG ==="
$PYTHON - <<'PY'
import json
from pathlib import Path
c = {
    "posts": [],
    "slugs": [],
    "categories": [
        {"slug": "tips-bisnis", "name": "tips-bisnis", "count": 0},
        {"slug": "ide-usaha", "name": "ide-usaha", "count": 0},
        {"slug": "operasional", "name": "operasional", "count": 0},
        {"slug": "info-produk", "name": "info-produk", "count": 0},
        {"slug": "inspirasi", "name": "inspirasi", "count": 0},
    ],
}
Path("data/catalog.json").write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  catalog reset")
PY

if [ "$KEEP_CONTENT" -eq 0 ]; then
  echo ""
  echo "=== CLEAN content/ (keep from-dc12*) ==="
  $PYTHON - <<'PY'
from pathlib import Path
import shutil
root = Path("content")
root.mkdir(exist_ok=True)
removed = []
for p in list(root.iterdir()):
    if p.name.startswith("from-dc12"):
        continue
    if p.name.startswith("."):
        continue
    if p.is_dir():
        shutil.rmtree(p)
        removed.append(p.name)
    elif p.is_file() and p.suffix in {".md", ".json"}:
        p.unlink()
        removed.append(p.name)
print("  removed:", ", ".join(removed) if removed else "(nothing)")
PY
else
  echo ""
  echo "=== KEEP existing content/ (--keep-content) ==="
fi

echo ""
echo "=== KEEP ONLY 1 JOB IN QUEUE ==="
$PYTHON - <<PY
import json
from pathlib import Path
lines = [l for l in Path("data/queue.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
filt = """$TITLE_FILTER""".strip().lower()
if filt:
    kept = [l for l in lines if filt in json.loads(l)["title"].lower()]
    if not kept:
        print(f"  NO MATCH for {filt!r} — using first seed")
        kept = lines[:1]
    else:
        print(f"  Found {len(kept)} match(es), keeping first")
else:
    kept = lines[:1]
    print("  No filter — keeping first seed")
job = json.loads(kept[0])
# force pending single job
job["status"] = "pending"
job["attempts"] = 0
Path("data/queue.jsonl").write_text(json.dumps(job, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"  Job: {job['slug']}")
print(f"  Title: {job['title']}")
print(f"  Category: {job['category']}")
PY

echo ""
echo "=== GENERATE 1 ARTICLE (text + images) ==="
echo "START: $(date +%H:%M:%S)"
$PYTHON scripts/worker.py --count 1
echo "END:   $(date +%H:%M:%S)"

echo ""
echo "=== RESULT ==="
ARTICLE_DIR=$($PYTHON - <<'PY'
from pathlib import Path
cands = sorted(Path("content").rglob("article.md"), key=lambda p: p.stat().st_mtime, reverse=True)
# skip sample folders
cands = [p for p in cands if "from-dc12" not in p.parts]
if not cands:
    print("")
else:
    print(cands[0].parent)
PY
)

if [ -z "$ARTICLE_DIR" ]; then
  echo "  NO ARTICLE GENERATED — check errors above"
  exit 1
fi

echo "  dir: $ARTICLE_DIR"
echo ""
echo "--- meta ---"
$PYTHON - <<PY
import json
from pathlib import Path
m = json.loads(Path("$ARTICLE_DIR/meta.json").read_text(encoding="utf-8"))
print(f"  slug: {m.get('slug')}")
print(f"  model: {m.get('model')}")
print(f"  word_count: {m.get('word_count')}")
print(f"  n_images: {m.get('n_images')}")
imgs = m.get("images") or {}
print(f"  thumbnail: {imgs.get('thumbnail', '?')}")
print(f"  inline: {[i.get('file') for i in imgs.get('inline', [])]}")
PY

echo ""
echo "--- image alt text ---"
grep -E "!\[" "$ARTICLE_DIR/article.md" | sed 's/^/  /' || true

echo ""
echo "--- image files ---"
ls -lh "$ARTICLE_DIR/images/" 2>/dev/null || echo "  (no images dir)"

echo ""
echo "--- mojibake check ---"
$PYTHON - <<PY
from pathlib import Path
text = Path("$ARTICLE_DIR/article.md").read_text(encoding="utf-8")
bad = [x for x in ("â", "Ã", "Â") if x in text]
print("  " + ("CLEAN" if not bad else f"FOUND markers: {bad}"))
# show arrows if present
for needle in ("→", "—", "÷", "–"):
    if needle in text:
        print(f"  has unicode: {needle!r}")
        break
PY

echo ""
echo "--- forbidden sub-area check ---"
$PYTHON - <<PY
from pathlib import Path
forbidden = ["nagoya","batu aji","sekupang","batam centre","harbour bay","lagoi","tanjung uban","senggarang"]
text = Path("$ARTICLE_DIR/article.md").read_text(encoding="utf-8").lower()
found = [x for x in forbidden if x in text]
print("  " + ("CLEAN" if not found else f"FOUND: {found}"))
PY

echo ""
echo "--- panduan / youtube backlinks ---"
$PYTHON - <<PY
from pathlib import Path
import re
text = Path("$ARTICLE_DIR/article.md").read_text(encoding="utf-8")
n = len(re.findall(r"kekasir\.id/panduan|youtube\.com/watch", text))
print(f"  {n} backlink(s)")
PY

echo ""
echo "--- paths ---"
echo "  article: $ARTICLE_DIR/article.md"
echo "  images:  $ARTICLE_DIR/images/"
echo "  preview: python3 -m http.server 8765 --bind 127.0.0.1  →  http://127.0.0.1:8765/preview/"
echo ""
echo "=== DONE ==="
