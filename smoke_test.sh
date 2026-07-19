#!/usr/bin/env bash
# Local Mac smoke test — regenerate 1 article with latest code (GLM-5.2 streaming + scene image prompts).
# Usage:
#   ./smoke_test.sh                       # first seed (default)
#   ./smoke_test.sh "Cara Hitung HPP"     # filter by title substring
set -e

cd "$(dirname "$0")"
export PATH="/Users/agamyusliman/Library/PhpWebStudy/env/node/bin:$PATH"

TITLE_FILTER="${1:-}"

echo "=== ENV ==="
grep -E "AI_CHAT_MODELS|AI_IMAGE_MODEL|BLOG_DAILY_CAP" .env || true
echo ""

echo "=== VERIFY AI CLIENT (GLM-5.2 round-robin) ==="
.venv/bin/python -c "
import sys; sys.path.insert(0, 'scripts')
from ai_client import chat, last_chat_model, _chat_models
print('  Configured:', _chat_models())
for i in range(2):
    out = chat([{'role':'user','content':'Reply: OK'}], temperature=0.1)
    print(f'  Call {i+1}: model={last_chat_model()!r} out={out[:30]!r}')
"
echo ""

echo "=== RESET QUEUE + CATALOG + CONTENT ==="
.venv/bin/python scripts/plan_topics.py --from-seeds --reset-queue 2>&1 | tail -3
.venv/bin/python -c "
import json, shutil, os
c = {'posts':[], 'slugs':[], 'categories':[
    {'slug':'tips-bisnis','name':'tips-bisnis','count':0},
    {'slug':'ide-usaha','name':'ide-usaha','count':0},
    {'slug':'operasional','name':'operasional','count':0},
    {'slug':'info-produk','name':'info-produk','count':0},
    {'slug':'inspirasi','name':'inspirasi','count':0},
]}
json.dump(c, open('data/catalog.json','w'), ensure_ascii=False, indent=2)
p = 'content/tips-bisnis'
if os.path.exists(p):
    shutil.rmtree(p)
    print(f'  removed {p}')
print('  catalog reset')
"

if [ -n "$TITLE_FILTER" ]; then
    echo ""
    echo "=== FILTER QUEUE BY TITLE: '$TITLE_FILTER' ==="
    .venv/bin/python << EOF
import json
lines = open('data/queue.jsonl').readlines()
filt = "$TITLE_FILTER".lower()
kept = [l for l in lines if filt in json.loads(l)['title'].lower()]
if not kept:
    print('  NO MATCH - keeping first job only')
    kept = lines[:1]
else:
    print(f'  Found {len(kept)} match(es), keeping first')
open('data/queue.jsonl','w').write(kept[0])
j = json.loads(kept[0])
print(f'  Job: {j["slug"]} | {j["title"]}')
EOF
fi

echo ""
echo "=== QUEUE (1 job) ==="
.venv/bin/python -c "
import json
lines = [l for l in open('data/queue.jsonl') if l.strip()]
j = json.loads(lines[0])
print(f'  slug: {j[\"slug\"]}')
print(f'  title: {j[\"title\"]}')
print(f'  category: {j[\"category\"]}')
print(f'  status: {j[\"status\"]}')
"

echo ""
echo "=== GENERATE ARTICLE (text + 3 images + thumbnail) ==="
echo "START: $(date +%H:%M:%S)"
.venv/bin/python scripts/worker.py --count 1
echo "END:   $(date +%H:%M:%S)"

echo ""
echo "=== RESULT ==="
ARTICLE_DIR=$(find content -type d -name "tips-bisnis" -prune -exec find {} -maxdepth 1 -mindepth 1 -type d \; | head -1)
if [ -z "$ARTICLE_DIR" ]; then
    echo "  NO ARTICLE GENERATED — check errors above"
    exit 1
fi

echo "--- meta ---"
.venv/bin/python -c "
import json
m = json.load(open('$ARTICLE_DIR/meta.json'))
print(f'  slug: {m.get(\"slug\")}')
print(f'  model: {m.get(\"model\")}')
print(f'  word_count: {m.get(\"word_count\")}')
print(f'  n_images: {m.get(\"n_images\")}')
imgs = m.get('images', {})
print(f'  thumbnail: {imgs.get(\"thumbnail\",\"?\")}')
print(f'  inline: {[i[\"file\"] for i in imgs.get(\"inline\",[])]}')
"

echo ""
echo "--- image alt text (scene vs diagram) ---"
grep -E "!\[" "$ARTICLE_DIR/article.md" | while read -r line; do
    echo "  $line"
done

echo ""
echo "--- image files ---"
ls -lh "$ARTICLE_DIR/images/" 2>/dev/null

echo ""
echo "--- forbidden sub-area check ---"
.venv/bin/python -c "
forbidden = ['nagoya','batu aji','sekupang','batam centre','harbour bay','lagoi','tanjung uban','senggarang']
text = open('$ARTICLE_DIR/article.md').read().lower()
found = [x for x in forbidden if x in text]
print('  ' + ('CLEAN' if not found else f'FOUND: {found}'))
"

echo ""
echo "--- panduan backlinks count ---"
echo "  $(grep -c 'kekasir.id/panduan\|youtube.com/watch' "$ARTICLE_DIR/article.md" 2>/dev/null || echo 0) backlink(s)"

echo ""
echo "--- preview article ---"
echo "  path: $ARTICLE_DIR/article.md"
echo "  images: $ARTICLE_DIR/images/"

echo ""
echo "=== DONE ==="
