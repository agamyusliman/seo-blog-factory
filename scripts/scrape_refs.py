#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from common import append_jsonl, load_config, now_iso
from paths import REFS, ensure_dirs

sys.path.insert(0, str(Path(__file__).resolve().parent))


def fetch_httpx(url: str, ua: str, timeout: float = 30.0) -> tuple[int, str]:
    headers = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"}
    with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as client:
        r = client.get(url)
        return r.status_code, r.text


def fetch_cloak(url: str, ua: str, timeout: float = 60.0) -> tuple[int, str]:
    try:
        from cloakbrowser import launch
    except ImportError as e:
        raise RuntimeError("cloakbrowser not installed; pip install cloakbrowser") from e
    browser = launch(headless=True)
    try:
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": ua})
        page.goto(url, wait_until="domcontentloaded", timeout=int(timeout * 1000))
        html = page.content()
        return 200, html
    finally:
        browser.close()


def should_escalate(status: int, html: str) -> bool:
    if status in (403, 429, 503):
        return True
    if status >= 400:
        return True
    text = BeautifulSoup(html or "", "lxml").get_text(" ", strip=True)
    return len(text) < 400


def expand_urls(templates: list[str], max_pages: int) -> list[str]:
    urls: list[str] = []
    for t in templates:
        if "{page}" in t:
            for p in range(1, max_pages + 1):
                urls.append(t.replace("{page}", str(p)))
        else:
            urls.append(t)
    seen: set[str] = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def extract_cards(site: str, base_url: str, html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: list[dict[str, Any]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        full = urljoin(base_url, href)
        path = urlparse(full).path.rstrip("/")
        title = a.get_text(" ", strip=True)
        if not title or len(title) < 12:
            continue
        if not _looks_like_article(site, full, path):
            continue
        if any(x in path.lower() for x in ("/category/", "/author/", "/tag/", "/page/")):
            continue
        items.append(
            {
                "site": site,
                "title": title[:200],
                "url": full.split("?")[0],
                "category_raw": _guess_category(path, a),
                "excerpt": None,
                "scraped_at": now_iso(),
                "inspiration_only": True,
            }
        )
    return _dedupe(items)


def _looks_like_article(site: str, full: str, path: str) -> bool:
    host = urlparse(full).netloc.lower()
    if site == "qasir":
        return "blog.qasir.id" in host and path.count("/") >= 2
    if site == "kledo":
        return "kledo.com" in host and "/blog/" in path and path != "/blog"
    if site == "moka":
        return "mokapos.com" in host and "/blog/" in path and "/category/" not in path
    if site == "olsera":
        return "olsera.com" in host and "/blog/" in path
    if site == "esb":
        return "esb.id" in host and ("inspirasi" in path or "/blog" in path or len(path) > 12)
    return "/blog" in path


def _guess_category(path: str, a_tag) -> str | None:
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2 and parts[0] in ("tips", "inspirasi", "studi-kasus", "event", "promo-qasir"):
        return parts[0]
    parent = a_tag.find_parent(["article", "div", "li"])
    if parent:
        badge = parent.find(class_=re.compile(r"cat|badge|label|tag", re.I))
        if badge:
            t = badge.get_text(" ", strip=True)
            if t and len(t) < 40:
                return t
    return None


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out = []
    for it in items:
        key = it["url"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def scrape_site(
    site: str,
    conf: dict[str, Any],
    engine: str,
    delay: float,
    ua: str,
) -> list[dict[str, Any]]:
    max_pages = int(conf.get("max_pages", 5))
    site_engine = conf.get("engine") or engine
    urls = expand_urls(conf.get("list_urls") or [], max_pages)
    all_items: list[dict[str, Any]] = []
    for url in urls:
        use = site_engine if site_engine != "auto" else "httpx"
        status, html = 0, ""
        try:
            if use == "cloak":
                status, html = fetch_cloak(url, ua)
            else:
                status, html = fetch_httpx(url, ua)
                if engine == "auto" and should_escalate(status, html):
                    print(f"  escalate cloak: {url} status={status}", file=sys.stderr)
                    status, html = fetch_cloak(url, ua)
                    use = "cloak"
        except Exception as e:
            print(f"  fail {url}: {e}", file=sys.stderr)
            time.sleep(delay + random.uniform(0, 1))
            continue
        items = extract_cards(site, url, html)
        for it in items:
            it["engine"] = use
            it["list_url"] = url
            it["http_status"] = status
        all_items.extend(items)
        print(f"  {url} -> {len(items)} cards ({use})", file=sys.stderr)
        time.sleep(delay + random.uniform(0, 1.2))
    return _dedupe(all_items)


def main() -> int:
    ensure_dirs()
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="all", help="comma list or all")
    ap.add_argument("--engine", default=None, help="auto|httpx|cloak")
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--delay", type=float, default=None)
    args = ap.parse_args()

    cfg = load_config()
    engine = args.engine or cfg.get("engine") or "auto"
    delay = float(args.delay if args.delay is not None else cfg.get("delay_seconds", 3))
    ua = cfg.get("user_agent") or "KekasirBlogResearchBot/1.0 (+https://kekasir.id; research)"
    sites_cfg: dict[str, Any] = cfg.get("sites") or {}

    if args.sites == "all":
        names = [k for k, v in sites_cfg.items() if v.get("enabled", True)]
    else:
        names = [s.strip() for s in args.sites.split(",") if s.strip()]

    day = datetime.now().strftime("%Y-%m-%d")
    total = 0
    for name in names:
        conf = dict(sites_cfg.get(name) or {})
        if not conf:
            print(f"skip unknown site {name}", file=sys.stderr)
            continue
        if args.max_pages:
            conf["max_pages"] = args.max_pages
        print(f"== {name} ==", file=sys.stderr)
        items = scrape_site(name, conf, engine, delay, ua)
        out = REFS / name / f"{day}.jsonl"
        for it in items:
            append_jsonl(out, it)
        print(f"wrote {len(items)} -> {out}", file=sys.stderr)
        total += len(items)
    print(f"done total={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
