# Scheduler / Cron / Watchdog

## Masalah

Bot generate “tanpa henti” bisa:

- mati (OOM, network, API error)  
- stuck di job `generating`  
- kehabisan queue  

Butuh **worker loop** + **cron eksternal** yang memastikan hidup.

## Model proses

### A. Worker long-running (utama)

```bash
# systemd / screen / tmux / launchd
python scripts/worker.py --loop --max-per-hour 20
```

Loop:

```
while True:
  heartbeat state.json
  job = dequeue()
  if no job:
    maybe plan_topics refill
    sleep 30
    continue
  process(job)
  sleep throttle
```

### B. Cron watchdog (wajib)

Contoh crontab (setiap 10 menit):

```cron
*/10 * * * * cd /path/kekasir-blog && ./scripts/watchdog.sh >> logs/watchdog.log 2>&1
```

`watchdog.sh` logic:

1. Baca `data/state.json` → `last_heartbeat`  
2. Jika > 15 menit tanpa heartbeat **dan** queue masih ada pending → restart worker  
3. Jika job `generating` > 30 menit → mark `failed`, requeue  
4. Optional: daily `scrape_refs` jam 03:00  
5. Optional: `link_graph` jam 04:00  

### C. macOS launchd (opsional)

`~/Library/LaunchAgents/id.kekasir.blog-worker.plist` — KeepAlive true.

### D. GitHub Actions (tidak ideal untuk loop panjang)

Bisa untuk scrape harian / batch kecil, bukan 500 artikel nonstop (timeout runner).

## `state.json`

```json
{
  "worker_pid": 12345,
  "last_heartbeat": "2026-07-19T12:00:00+07:00",
  "last_job_id": "job_042",
  "counters": {
    "done_today": 12,
    "failed_today": 1,
    "images_today": 36
  },
  "daily_cap": 30,
  "date": "2026-07-19"
}
```

## Refill queue otomatis

Jika `pending < 5`:

```
plan_topics.py --from-refs --count 50 --ensure-unique
```

## Notifikasi (opsional)

- Telegram bot: worker down, daily summary  
- File `logs/alerts.log`  

## Safety caps

| Cap | Default |
|-----|---------|
| Max artikel / hari | 30 |
| Max retry / job | 3 |
| Max concurrent image | 1 |
| Max runtime / job | 15 menit |

## Perintah operasional

```bash
# start
python scripts/worker.py --loop

# one-shot 5 artikel
python scripts/worker.py --count 5

# status
python scripts/status.py

# recover stuck
python scripts/worker.py --recover-stuck
```
