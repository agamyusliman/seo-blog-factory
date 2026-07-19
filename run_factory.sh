#!/usr/bin/env bash
# SEO Blog Factory runner — process queue with optional loop.
# Usage:
#   ./run_factory.sh              # one-shot, 1 job (text + images)
#   ./run_factory.sh --loop       # continuous loop until queue empty
#   ./run_factory.sh --loop --max-per-hour 30 --sleep 30
#   ./run_factory.sh --text-only  # text only, no images
#   ./run_factory.sh --count 5    # process 5 jobs then exit
set -e

cd "$(dirname "$0")"

if [ -x "/Users/agamyusliman/Library/PhpWebStudy/env/node/bin/node" ]; then
    export PATH="/Users/agamyusliman/Library/PhpWebStudy/env/node/bin:$PATH"
fi

PYTHON=".venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
fi

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/factory-$(date +%Y%m%d).log"

echo "=== factory start $(date +%Y-%m-%dT%H:%M:%S%z) ===" | tee -a "$LOG_FILE"
echo "python: $PYTHON" | tee -a "$LOG_FILE"
echo "env: AI_CHAT_MODELS=${AI_CHAT_MODELS:-<from .env>}, AI_IMAGE_MODEL=${AI_IMAGE_MODEL:-<from .env>}" | tee -a "$LOG_FILE"

$PYTHON scripts/worker.py --recover-stuck 2>&1 | tee -a "$LOG_FILE"

ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
    ARGS=(--count 1)
fi

$PYTHON scripts/worker.py "${ARGS[@]}" 2>&1 | tee -a "$LOG_FILE"

echo "=== factory end $(date +%Y-%m-%dT%H:%M:%S%z) ===" | tee -a "$LOG_FILE"
