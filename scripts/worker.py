#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

from common import (
    heartbeat,
    load_config,
    load_queue,
    load_state,
    now_iso,
    save_queue,
    save_state,
)
from generate_article import generate_one
from generate_images import generate_for_article
from paths import CONTENT, ensure_dirs

sys.path.insert(0, str(Path(__file__).resolve().parent))


def daily_cap_ok(cfg: dict[str, Any]) -> bool:
    st = load_state()
    cap = int(cfg.get("daily_cap") or os.environ.get("BLOG_DAILY_CAP") or 30)
    st["daily_cap"] = cap
    save_state(st)
    return st.get("counters", {}).get("done_today", 0) < cap


def pick_job(queue: list[dict[str, Any]]) -> dict[str, Any] | None:
    for j in queue:
        if j.get("status") == "pending" and int(j.get("attempts") or 0) < 3:
            return j
    return None


def mark(queue: list[dict[str, Any]], job_id: str, **fields: Any) -> None:
    for j in queue:
        if j.get("id") == job_id:
            j.update(fields)
            j["updated_at"] = now_iso()
            break


def process_job(job: dict[str, Any], with_images: bool) -> bool:
    heartbeat(job.get("id"))
    folder = CONTENT / job["category"] / job["slug"]
    article = folder / "article.md"
    text_ok = article.exists()
    if not text_ok:
        print(f"[text] {job['slug']}", flush=True)
        res = generate_one(job)
        print(res, flush=True)
        text_ok = bool(res.get("path") or article.exists())
        if not text_ok:
            return False
    if with_images:
        print(f"[images] {job['slug']} (text+image pipeline)", flush=True)
        img = generate_for_article(
            job["category"],
            job["slug"],
            force=True,
            use_ai=True,
        )
        print(img, flush=True)
        return bool(img.get("ok") and article.exists())
    return article.exists()


def run_once(count: int, with_images: bool) -> int:
    ensure_dirs()
    cfg = load_config()
    done = 0
    queue = load_queue()
    while done < count:
        if not daily_cap_ok(cfg):
            print("daily_cap reached", flush=True)
            break
        job = pick_job(queue)
        if not job:
            print("no pending jobs", flush=True)
            break
        job["attempts"] = int(job.get("attempts") or 0) + 1
        job["status"] = "generating"
        save_queue(queue)
        try:
            ok = process_job(job, with_images=with_images)
            if ok:
                mark(queue, job["id"], status="done")
                st = load_state()
                st["counters"]["done_today"] = st.get("counters", {}).get("done_today", 0) + 1
                save_state(st)
                done += 1
            else:
                mark(queue, job["id"], status="failed" if job["attempts"] >= 3 else "pending")
                st = load_state()
                st["counters"]["failed_today"] = st.get("counters", {}).get("failed_today", 0) + 1
                save_state(st)
        except Exception as e:
            print(f"error {job.get('slug')}: {e}", flush=True)
            mark(
                queue,
                job["id"],
                status="failed" if job["attempts"] >= 3 else "pending",
                last_error=str(e)[:500],
            )
            st = load_state()
            st["counters"]["failed_today"] = st.get("counters", {}).get("failed_today", 0) + 1
            save_state(st)
        save_queue(queue)
        heartbeat(job.get("id"))
    return done


def recover_stuck(minutes: int = 30) -> int:
    from datetime import datetime, timedelta

    queue = load_queue()
    n = 0
    cutoff = datetime.now().astimezone() - timedelta(minutes=minutes)
    for j in queue:
        if j.get("status") != "generating":
            continue
        updated = j.get("updated_at") or j.get("created_at")
        if not updated:
            j["status"] = "pending"
            n += 1
            continue
        try:
            ts = datetime.fromisoformat(updated)
            if ts < cutoff:
                j["status"] = "pending"
                n += 1
        except Exception:
            j["status"] = "pending"
            n += 1
    save_queue(queue)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--max-per-hour", type=int, default=20)
    ap.add_argument("--sleep", type=int, default=30)
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--recover-stuck", action="store_true")
    ap.add_argument("--text-only", action="store_true")
    args = ap.parse_args()

    ensure_dirs()
    st = load_state()
    st["worker_pid"] = os.getpid()
    save_state(st)

    if args.recover_stuck:
        n = recover_stuck()
        print(f"recovered={n}")
        return 0

    with_images = not (args.no_images or args.text_only)
    if args.loop:
        hour_count = 0
        hour_start = time.time()
        while True:
            heartbeat()
            if time.time() - hour_start > 3600:
                hour_count = 0
                hour_start = time.time()
            if hour_count >= args.max_per_hour:
                time.sleep(args.sleep)
                continue
            n = run_once(1, with_images=with_images)
            hour_count += n
            if n == 0:
                time.sleep(args.sleep)
            else:
                time.sleep(2)
    else:
        n = run_once(args.count, with_images=with_images)
        print(f"processed={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
