#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STATE="$ROOT/data/state.json"
LOG="$ROOT/logs/watchdog.log"
mkdir -p "$ROOT/logs"

ts() { date '+%Y-%m-%d %H:%M:%S%z'; }

if [[ ! -f "$STATE" ]]; then
  echo "$(ts) no state; starting worker" | tee -a "$LOG"
  nohup python3 scripts/worker.py --loop --text-only --max-per-hour 12 >> logs/worker.log 2>&1 &
  echo $! > logs/worker.pid
  exit 0
fi

python3 - <<'PY' >>"$LOG" 2>&1
import json, os, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path

root = Path(".").resolve()
state_path = root / "data" / "state.json"
queue_path = root / "data" / "queue.jsonl"
log = print

st = json.loads(state_path.read_text())
hb = st.get("last_heartbeat")
pending = 0
if queue_path.exists():
    for line in queue_path.read_text().splitlines():
        if not line.strip():
            continue
        j = json.loads(line)
        if j.get("status") == "pending":
            pending += 1

stale = True
if hb:
    try:
        ts = datetime.fromisoformat(hb)
        stale = datetime.now().astimezone() - ts > timedelta(minutes=15)
    except Exception:
        stale = True

pid_file = root / "logs" / "worker.pid"
alive = False
if pid_file.exists():
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)
        alive = True
    except Exception:
        alive = False

if pending == 0:
    log(f"{datetime.now().isoformat()} queue empty; skip")
    sys.exit(0)

if alive and not stale:
    log(f"{datetime.now().isoformat()} worker ok pid alive pending={pending}")
    sys.exit(0)

# recover stuck jobs
subprocess.run([sys.executable, "scripts/worker.py", "--recover-stuck"], check=False)
# restart
if alive and pid_file.exists():
    try:
        os.kill(int(pid_file.read_text().strip()), 15)
    except Exception:
        pass
log(f"{datetime.now().isoformat()} restart worker pending={pending} stale={stale}")
proc = subprocess.Popen(
    [sys.executable, "scripts/worker.py", "--loop", "--text-only", "--max-per-hour", "12"],
    stdout=open(root / "logs" / "worker.log", "a"),
    stderr=subprocess.STDOUT,
    cwd=str(root),
)
pid_file.write_text(str(proc.pid))
PY
