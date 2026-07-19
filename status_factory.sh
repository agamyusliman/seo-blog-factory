#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

PYTHON=".venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
fi

echo "=== FACTORY STATUS $(date +%Y-%m-%dT%H:%M:%S%z) ==="

echo ""
echo "=== Processes ==="
pgrep -af "worker.py|run_factory" 2>/dev/null | grep -v grep || echo "  no factory running"

echo ""
echo "=== Queue ==="
if [ -f data/queue.jsonl ]; then
    $PYTHON -c "
import json
q = [json.loads(l) for l in open('data/queue.jsonl') if l.strip()]
status_count = {}
for j in q:
    s = j.get('status','?')
    status_count[s] = status_count.get(s, 0) + 1
total = len(q)
done = status_count.get('done', 0)
pending = status_count.get('pending', 0)
generating = status_count.get('generating', 0)
failed = status_count.get('failed', 0)
print(f'  total: {total}')
print(f'  done: {done}')
print(f'  pending: {pending}')
print(f'  generating: {generating}')
print(f'  failed: {failed}')
if total > 0:
    print(f'  progress: {done}/{total} ({done*100//total}%)')
"
else
    echo "  no queue file"
fi

echo ""
echo "=== State ==="
if [ -f data/state.json ]; then
    cat data/state.json | $PYTHON -c "
import json, sys
s = json.load(sys.stdin)
print(f\"  worker_pid: {s.get('worker_pid')}\")
print(f\"  last_heartbeat: {s.get('last_heartbeat')}\")
print(f\"  last_job_id: {s.get('last_job_id')}\")
c = s.get('counters', {})
print(f\"  done_today: {c.get('done_today', 0)}\")
print(f\"  failed_today: {c.get('failed_today', 0)}\")
print(f\"  images_today: {c.get('images_today', 0)}\")
print(f\"  daily_cap: {s.get('daily_cap', '?')} (0 = unlimited)\")
"
else
    echo "  no state file"
fi

echo ""
echo "=== Catalog ==="
if [ -f data/catalog.json ]; then
    $PYTHON -c "
import json
c = json.load(open('data/catalog.json'))
posts = c.get('posts', [])
print(f'  posts: {len(posts)}')
done = sum(1 for p in posts if p.get('status') == 'done')
print(f'  done: {done}')
"
else
    echo "  no catalog file"
fi

echo ""
echo "=== Content ==="
CONTENT_COUNT=$(find content/ -name article.md 2>/dev/null | wc -l | tr -d ' ')
echo "  article.md files: $CONTENT_COUNT"

echo ""
echo "=== Latest log ==="
LATEST_LOG=$(ls -t logs/factory-*.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "  $LATEST_LOG"
    tail -5 "$LATEST_LOG" 2>/dev/null | sed 's/^/    /'
else
    echo "  no log file"
fi

echo ""
echo "=== DONE ==="
