# SEO Blog Factory

Automated SEO content factory for product blogs — **case study: [Kekasir.id](https://kekasir.id)** (Indonesian F&B POS / cashier SaaS).

**Pipeline:** topic seeds → multi-model RAG articles (Bahasa Indonesia) → section-bound **editorial scene illustrations** + brand watermark → local HTML preview.

> **Product scope (this case study):** culinary / F&B UMKM only (warung, cafe, restaurant, food cart, catering, cloud kitchen). Not retail, salon, or laundry marketing content.

Public repo name is intentionally **brand-neutral** (`seo-blog-factory`). Brand details live in README + `rag/corpus/` as a study case you can replace.

---

## Case study: Kekasir

**Problem.** Growing a POS product in Indonesia needs a steady stream of SEO articles that sound local, stay factually aligned with pricing / FAQ / legal pages, and ship with on-brand images—without a full-time content team rewriting every draft.

**What this repo solves.** A small Python factory that:

1. Plans F&B topics from seeds (and optional competitor **title** research).
2. Generates long-form articles with a **RAG corpus** (product truth, anti-claims, legal, local tone).
3. Places supporting images next to relevant sections; prompts use that section context.
4. Defaults to **editorial scene illustrations** (people + warung/dapur + food); flow diagrams only when a section is a true system workflow.
5. Applies a **post-process watermark** from the real brand logo asset (not a redrawn fake logo).
6. Previews drafts locally (or via SSH tunnel to a remote worker host) before any CMS publish step.

**Outcome for the brand.** Repeatable production of 500–2,000 word Indonesian posts with consistent product claims (e.g. Basic / Pro pricing, 14-day Pro trial rules, QRIS fee messaging) and illustration-style imagery suitable for blog + Open Graph.

---

## Who this is for

If you need a **sample / starter content factory** for supporting blog articles—topic queue, multi-model chat, RAG-safe generation, image pipeline, and a review UI—this repository is a concrete reference implementation you can clone, re-brand, and adapt.

Typical use cases:

- End-to-end AI content ops for a product blog (not just a single chat prompt)
- Internal tooling for an F&B SaaS or local marketplace blog
- Reference implementation: OpenAI-compatible multi-model chat + image tools, BM25 RAG, watermark compositing

---

## Features

| Area | What you get |
|------|----------------|
| **Articles** | OpenAI-compatible chat + product/legal RAG |
| **Multi-model chat** | `AI_CHAT_MODELS` round-robin + fallback (e.g. large-context model + backup) |
| **Streaming UTF-8** | SSE chat parsing with forced UTF-8 (avoids `→` / `—` mojibake) |
| **SEO** | Unique title/slug catalog, supporting keywords, OG-ready thumbs |
| **Images** | Thumbnail **1200×630**, supporting **1200×800**, WebP |
| **Image style** | Editorial **scene** default; optional workflow diagram only for true alur/sistem sections |
| **Section binding** | Image prompts use nearest H2 + surrounding paragraphs |
| **Brand** | Watermark from `assets/brand/logo-horizontal.png` (top-right, no white plate) |
| **Backlinks** | Contextual product CTA + optional panduan / video links (max 1–2) |
| **Preview** | Static `preview/index.html` (list + detail + keyword chips) |
| **Batch** | Queue + `worker.py` / `run_factory.sh` (text and/or images) |
| **Ops** | Optional daily cap (`0` = unlimited), status script, recover-stuck |

---

## Requirements

### Runtime

| Requirement | Notes |
|-------------|--------|
| **Python** | 3.11+ recommended (3.10+ should work) |
| **OS** | macOS / Linux / WSL; Windows via venv |
| **Disk** | ~100 MB code + RAG; generated `content/` grows with articles/images |
| **Network** | Outbound HTTPS to your AI gateway |

### Python packages

See [`requirements.txt`](./requirements.txt):

- `openai`, `httpx`, `requests` — API clients
- `python-dotenv`, `PyYAML` — config
- `Pillow` — image resize + watermark composite
- `beautifulsoup4`, `lxml` — optional scrape helpers
- `markdown` — preview / processing helpers

```bash
pip install -r requirements.txt
```

### External services

| Service | Purpose |
|---------|---------|
| **OpenAI-compatible chat API** | Article body (`POST /v1/chat/completions`, often **SSE stream**) |
| **Image-capable gateway** | Images via `POST /v1/responses` + tool `image_generation` |

Configure via `.env` (never commit real keys):

```env
AI_BASE_URL=https://your-gateway.example/v1
AI_API_KEY=replace-with-your-api-key
# Chat: multi-model round-robin + fallback
AI_CHAT_MODELS=glm-5.2,grok-4.5
# Legacy single model (used only if AI_CHAT_MODELS is empty)
AI_CHAT_MODEL=grok-4.5
# Image: single model that supports image_generation
AI_IMAGE_MODEL=grok-4.5
# BLOG_DAILY_CAP=0   # 0 or unset = no daily limit
```

Copy from [`.env.example`](./.env.example).

Some gateways (especially multi-provider proxies) return **SSE** for chat even when you request non-stream JSON. This factory uses `stream=true` + a UTF-8 SSE parser (`scripts/ai_client.py`).

---

## Quick start

```bash
# 1) Environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Secrets
cp .env.example .env
# edit .env — set AI_BASE_URL + AI_API_KEY (+ AI_CHAT_MODELS)

# 3) RAG index
PYTHONPATH=scripts python scripts/retrieve.py --rebuild --query "hpp warung" --k 3

# 4) Queue sample topics
PYTHONPATH=scripts python scripts/plan_topics.py --from-seeds --count 5 --reset-queue

# 5) Generate one article + images
PYTHONPATH=scripts python scripts/worker.py --count 1
# or
./run_factory.sh

# Text only
PYTHONPATH=scripts python scripts/worker.py --count 1 --text-only

# Continuous batch (example)
./run_factory.sh --loop --max-per-hour 20 --sleep 30

# Status
./status_factory.sh

# Images only for an existing article
PYTHONPATH=scripts python scripts/generate_images.py \
  --category tips-bisnis \
  --slug your-article-slug \
  --force
```

### Local smoke test (optional)

```bash
./smoke_test.sh
# or filter by title substring
./smoke_test.sh "Cara Hitung HPP"
```

### Local preview

From the **repo root** (so `data/` and `content/` paths resolve):

```bash
python3 -m http.server 8765 --bind 127.0.0.1
# open http://127.0.0.1:8765/preview/
```

Remote worker host: SSH tunnel to that host’s `8765`, then open the same URL on your laptop. See [`docs/09-preview.md`](./docs/09-preview.md).

---

## Repository layout

```text
seo-blog-factory/          # public clone name may differ
├── assets/brand/          # public brand logo (watermark source)
├── config.yaml            # caps, image sizes, watermark rules
├── data/
│   └── seed_titles.jsonl  # sample F&B topic seeds (safe to publish)
├── docs/                  # architecture, RAG, image system notes
├── preview/               # static HTML + JS preview
├── rag/corpus/            # product truth, legal, FAQ, language rules
├── scripts/               # Python pipeline
├── run_factory.sh         # batch runner + recover-stuck
├── status_factory.sh      # queue / process health
├── smoke_test.sh          # local one-article smoke test
├── content/               # generated output (gitignored)
├── requirements.txt
└── .env.example
```

---

## Image API (gateway)

Providers that support OpenAI-style responses + image tool:

```http
POST {BASE}/responses
Authorization: Bearer {API_KEY}

{
  "model": "grok-4.5",
  "stream": false,
  "store": false,
  "tools": [{"type": "image_generation"}],
  "input": [{
    "role": "user",
    "content": [
      {"type": "input_text", "text": "Generate an image: ...\n\nUse the image_generation tool."}
    ]
  }]
}
```

Response: base64 in `output[]` → decode → WebP + watermark.

Articles use `{BASE}/chat/completions` (SSE stream, UTF-8).

Image style rules: [`docs/14-image-design-system.md`](./docs/14-image-design-system.md), [`docs/16-content-image-rules.md`](./docs/16-content-image-rules.md).

---

## Content rules (high level)

- Natural Bahasa Indonesia (anti AI-slop / forced English jargon)
- Emphasize product language naturally: **aplikasi kasir**, **point of sales**, **POS**
- Align with public product pages: pricing, FAQ, terms, privacy, refund
- Competitor research = metadata only (no full-text copy)
- Do not reuse in-app “panduan” UI screenshots as blog art
- City keywords (this case study): Batam / Tanjungpinang only — no sub-area “fake case studies”
- Images: **editorial scene first**; diagram only for true system workflows (not every HPP/tips section)

Full rules: `docs/` and `rag/corpus/`.

---

## Security (public repo)

| Never commit | Why |
|--------------|-----|
| `.env` | API keys |
| `content/` | Generated articles & images |
| `data/queue.jsonl`, `data/state.json`, `data/refs/` | Runtime / scrape cache |
| `rag/corpus/published/` | Generated excerpts (optional) |
| `assets/panduan/` | Demo UI screenshots |
| `.venv/` | Local Python env |

Rotate any key that was ever pasted into chat or a public log.

---

## Tech highlights

- **Orchestration:** seed → plan → generate → validate → images → catalog
- **RAG:** lightweight BM25 over curated Markdown corpus (pricing, legal, tone, panduan map)
- **Chat:** multi-model list + fallback; SSE UTF-8 decode + mojibake repair
- **Vision pipeline:** section-aware prompts, editorial scene default, Pillow watermark
- **Ops-minded:** optional daily cap, queue state, local/remote preview before publish

---

## Docs index

See [`docs/README.md`](./docs/README.md) for the full plan set (architecture, RAG, API, images, preview, public checklist).

---

## License

Choose a license when publishing (e.g. MIT for code).

**Kekasir** name, logo, and product copy remain trademarks / property of **PT. Mitra Kekasir Indonesia**. Do not use brand assets to imply official affiliation without permission.

---

## Author

**Agam Yusliman** — built for [Kekasir.id](https://kekasir.id).

If this factory helps you design your own blog support pipeline, adapt the `scripts/` layout and replace `rag/corpus/` with your product truth.
