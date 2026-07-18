# Scraper Plan — Referensi Kompetitor

## Tujuan scrape

**Bukan** menyalin artikel. Hanya metadata:

| Field | Wajib | Digunakan untuk |
|-------|-------|-----------------|
| `title` | ✅ | Seed topic / gap analysis |
| `url` | ✅ | Attribution internal (opsional, tidak dipublish) |
| `category` | ✅ jika ada | Mapping ke 5 kategori kita |
| `excerpt` | optional | Nada / angle |
| `published_at` | optional | Tren topik |
| `site` | ✅ | Source tag |

**Jangan** simpan full HTML body untuk di-paraphrase. Flag baris: `inspiration_only=true`.

## Target sites

| Site | List URL | Prioritas | Catatan |
|------|----------|-----------|---------|
| Kledo | sitemap + `/blog/page/N/` | P0 | WP + Yoast; volume besar — **sitemap first** |
| Qasir | `https://blog.qasir.id/?page=N` | P0 | SSR mudah; path kategori `/tips`, `/inspirasi`, `/studi-kasus` |
| Moka | `/blog` + `/blog/category/*` | P1 | Next.js; Load More → escalate browser |
| Olsera | `/id/blog?page=N` (+ en) | P2 | Nuxt; cek locale ID vs EN |
| ESB | `/id/inspirasi` | P3 | Page berat — browser-first |

## Stack tiered (keputusan 2026-07-19)

```text
Layer 0  httpx + BeautifulSoup     ← DEFAULT (sitemaps, SSR list)
Layer 1  CloakBrowser (Playwright) ← flag per-site jika 403 / HTML kosong / CF
Layer 2  stealth-browser-mcp       ← debug agent/manual SAJA, bukan worker
Layer 3  CloakBrowser-Manager      ← opsional nanti (multi-profile GUI)
```

### Kenapa tier ini?

| Tool | Role | Alasan |
|------|------|--------|
| **httpx + BS4** | Primary | Ringan, sopan, cukup untuk Kledo/Qasir SSR + sitemap |
| **[CloakBrowser](https://github.com/CloakHQ/CloakBrowser)** | Primary stealth untuk factory | `pip install cloakbrowser`, API Playwright, cocok batch Python worker |
| **[stealth-browser-mcp](https://github.com/vibheksoni/stealth-browser-mcp)** | Agent debug only | ~97 MCP tools + nodriver; bagus untuk investigasi 1 halaman, **bukan** cron unattended |
| **CloakBrowser-Manager** | Later | Multi-profile Docker GUI — overkill untuk 5 blog publik |

### Install CloakBrowser

```bash
pip install cloakbrowser
python -m cloakbrowser install   # ~200MB patched Chromium
```

### CLI usulan

```bash
python scripts/scrape_refs.py --engine auto --sites all --max-pages 15 --delay 3
python scripts/scrape_refs.py --engine cloak --sites moka,esb --max-pages 5
python scripts/scrape_refs.py --engine httpx --sites qasir,kledo --max-pages 20
```

`auto` = httpx dulu; jika status 403/429/body terlalu pendek → retry 1× dengan CloakBrowser.

### Pola kode CloakBrowser (worker)

```python
from cloakbrowser import launch

UA = "KekasirBlogResearchBot/1.0 (+https://kekasir.id; research)"

browser = launch(headless=True)
page = browser.new_page()
page.set_extra_http_headers({"User-Agent": UA})
page.goto(url, wait_until="domcontentloaded", timeout=60_000)
html = page.content()
browser.close()
# parse title/url/category dengan BS4 — jangan archive full body
```

Jika challenge: `headless=False`, opsional `humanize=True` + proxy residential. **Jangan** pasang captcha solver berbayar untuk list blog publik kecuali terpaksa.

### stealth-browser-mcp (debug saja)

```bash
git clone https://github.com/vibheksoni/stealth-browser-mcp.git
# pip install -r requirements.txt; butuh Chrome host
# daftarkan sebagai MCP server di agent — bukan di scrape_refs.py
```

Pakai untuk: “buka Moka blog, list title+href, screenshot selector”. Hasil manual masuk seed queue.

## Flag per site (start)

| Site | Start engine | Escalate if |
|------|--------------|-------------|
| Kledo | httpx (+ sitemap) | 403 / empty |
| Qasir | httpx | SPA shell only |
| Moka | httpx → cloak | Load More / empty cards |
| Olsera | httpx | client-only cards |
| ESB | cloak | page >5MB / empty SSR |

## Etika & legal (non-negotiable)

1. Baca `robots.txt`; hormati Disallow / crawl-delay.  
2. UA: `KekasirBlogResearchBot/1.0 (+https://kekasir.id; research)`.  
3. Delay **2–4 detik** + jitter per host; max concurrent 1/host.  
4. Cap pages (default 20 list / site); Kledo → prefer sitemap, jangan crawl 322 pages buta.  
5. Metadata only; generator original + RAG product facts.  
6. Jangan hotlink gambar kompetitor.  
7. Stealth tool **tidak** melegitimasi crawl agresif.

## Output

`data/refs/{site}/{yyyy-mm-dd}.jsonl`:

```json
{"site":"qasir","title":"...","url":"https://...","category_raw":"Tips","excerpt":null,"scraped_at":"...","inspiration_only":true,"engine":"httpx"}
```

## Dedup & scoring

1. Fingerprint title (normalize).  
2. Jaccard cluster similar titles.  
3. Score: match fitur Kekasir (+2), F&B/UMKM (+1), pure accounting deep Kledo (−1 jika di luar positioning).  
4. Top seeds → `plan_topics.py` → `queue.jsonl`.

## Mapping kategori kompetitor → kita

| Mereka | Kita |
|--------|------|
| Tips / Tips Bisnis | `tips-bisnis` |
| Ide bisnis / inspirasi | `ide-usaha` atau `inspirasi` |
| Cerita sukses / studi kasus | `inspirasi` |
| Info produk / fitur | `info-produk` |
| Operasional / stok / kas | `operasional` |
| Akuntansi murni | filter ketat |

## Dependencies

```text
httpx
beautifulsoup4
lxml
cloakbrowser   # optional extra: [geoip]
# playwright not required separately if using cloakbrowser wrapper
```
