# Kekasir Blog Factory

Automated SEO content factory for [Kekasir.id](https://kekasir.id), an Indonesian F&B (food & beverage) POS / cashier SaaS.

**Pipeline:** topic seeds → RAG-grounded articles (Bahasa Indonesia) → photorealistic section-matched images + brand watermark → local HTML preview.

> **Product scope:** culinary / F&B UMKM only (warung, cafe, restaurant, food cart, catering). Not retail, salon, or laundry marketing content.

---

## Case study: Kekasir

**Problem.** Growing a POS product in Indonesia needs a steady stream of SEO articles that sound local, stay factually aligned with pricing / FAQ / legal pages, and ship with on-brand images—without a full-time content team rewriting every draft.

**What this repo solves.** A small Python factory that:

1. Plans F&B topics from seeds (and optional competitor title research).
2. Generates long-form articles with a **RAG corpus** (product truth, anti-claims, legal, local tone).
3. Places supporting images next to relevant sections and generates visuals whose prompts use that section context.
4. Applies a **post-process watermark** from the real Kekasir logo asset (not a redrawn fake logo).
5. Previews drafts locally before any CMS publish step.

**Outcome for the brand.** Repeatable production of 500–2,000 word Indonesian posts with consistent product claims (e.g. Basic / Pro pricing, 14-day Pro trial rules, QRIS fee messaging) and photorealistic imagery suitable for blog + Open Graph.

---

## Who this is for

If you need a **sample / starter content factory** for supporting blog articles—topic queue, RAG-safe generation, image pipeline, and a review UI—this repository is a concrete reference implementation you can clone, re-brand, and adapt.

Typical use cases:

- End-to-end AI content ops for a product blog (not just a single chat prompt)
- Internal tooling for an F&B SaaS or local marketplace blog
- Reference implementation: OpenAI-compatible chat + image tools, BM25 RAG, watermark compositing

---

## Features

| Area | What you get |
|------|----------------|
| **Articles** | OpenAI-compatible chat generation + product/legal RAG |
| **SEO** | Unique title/slug catalog, supporting keyword badges, OG-ready thumbs |
| **Images** | Thumbnail **1200×630**, supporting **1200×800**, WebP, photorealistic prompts |
| **Section binding** | Image prompts use nearest H2 + surrounding paragraphs |
| **Brand** | Watermark from `assets/brand/logo-horizontal.png` (top-right, no white plate) |
| **Preview** | Static `preview/index.html` (list + detail + keyword chips) |
| **Batch** | Queue + `worker.py` (text and/or images) |
| **Research** | Optional competitor **metadata** scrape (titles only—no full-text plagiarism) |

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
| **OpenAI-compatible chat API** | Article body generation (`/v1/chat/completions`) |
| **Image-capable gateway** | Photorealistic images via `/v1/responses` + tool `image_generation` |

Configure via `.env` (never commit real keys):

```env
AI_BASE_URL=https://your-gateway.example/v1
AI_API_KEY=replace-with-your-api-key
AI_CHAT_MODEL=grok-4.5
AI_IMAGE_MODEL=grok-4.5
```

Copy from [`.env.example`](./.env.example).

### Optional

- Stealth browser tooling for harder scrape targets (not required for seed-based generation)
- Local HTTP server for preview (`python3 -m http.server`)

---

## Quick start

```bash
# 1) Environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Secrets
cp .env.example .env
# edit .env — set AI_BASE_URL + AI_API_KEY

# 3) RAG index
PYTHONPATH=scripts python scripts/retrieve.py --rebuild --query "hpp warung" --k 3

# 4) Queue sample topics
PYTHONPATH=scripts python scripts/plan_topics.py --from-seeds --count 5 --reset-queue

# 5) Generate one article + images
PYTHONPATH=scripts python scripts/worker.py --count 1

# Text only
PYTHONPATH=scripts python scripts/worker.py --count 1 --text-only

# Images only for an existing article
PYTHONPATH=scripts python scripts/generate_images.py \
  --category tips-bisnis \
  --slug your-article-slug \
  --force
```

### Local preview

From the **repo root** (so `data/` and `content/` paths resolve):

```bash
python3 -m http.server 8765
# open http://localhost:8765/preview/
```

---

## Repository layout

```text
kekasir-blog/
├── assets/brand/          # public brand logo (watermark source)
├── config.yaml            # caps, image sizes, watermark rules
├── data/
│   └── seed_titles.jsonl  # sample F&B topic seeds (safe to publish)
├── docs/                  # architecture, RAG, image system notes
├── preview/               # static HTML + JS preview
├── rag/corpus/            # product truth, legal, FAQ, language rules
├── scripts/               # Python pipeline
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

Articles use `{BASE}/chat/completions`.

---

## Content rules (high level)

- Natural Bahasa Indonesia (anti AI-slop / forced English jargon)
- Align with public product pages: pricing, FAQ, terms, privacy, refund
- Competitor research = metadata only (no full-text copy)
- Do not reuse in-app “panduan” UI screenshots as blog art (demo tenant context differs)

Full rules: `docs/` and `rag/corpus/`.

---

## Security (public repo)

| Never commit | Why |
|--------------|-----|
| `.env` | API keys |
| `content/` | Generated articles & images |
| `data/queue.jsonl`, `data/state.json`, `data/refs/` | Runtime / scrape cache |
| `assets/panduan/` | Demo UI screenshots |
| `.venv/` | Local Python env |

---

## Tech highlights

- **Orchestration:** seed → plan → generate → validate → images → catalog
- **RAG:** lightweight BM25 over curated Markdown corpus (pricing, legal, tone)
- **Vision pipeline:** section-aware prompts, full-bleed photorealism constraints, Pillow watermark
- **Ops-minded:** daily caps, queue state, local preview before publish

---

## License

Choose a license when publishing (e.g. MIT for code).

**Kekasir** name, logo, and product copy remain trademarks / property of **PT. Mitra Kekasir Indonesia**. Do not use brand assets to imply official affiliation without permission.

---

## Author

**Agam Yusliman** — built for [Kekasir.id](https://kekasir.id).

If this factory helps you design your own blog support pipeline, adapt the `scripts/` layout to your brand.
