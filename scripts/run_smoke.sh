#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"

echo "== deps =="
python3 -c "import httpx,bs4,requests,dotenv,yaml; print('ok imports')"

echo "== rag =="
python3 scripts/retrieve.py --rebuild --query "hpp warung F&B" --k 3 >/dev/null
echo "rag ok"

echo "== plan seeds =="
python3 scripts/plan_topics.py --from-seeds --count 5 --reset-queue
python3 scripts/status.py

echo "== generate 1 article text =="
python3 scripts/worker.py --count 1 --text-only

echo "== status =="
python3 scripts/status.py
echo "smoke done"
