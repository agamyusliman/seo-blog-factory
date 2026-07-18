# Kekasir Blog SEO Factory — Plan Index

> **Status**: 📋 Planning (2026-07-19)  
> **Goal**: Pipeline otomatis scrape referensi → generate ratusan artikel SEO → gambar → backlink internal → preview  
> **Target publish**: `blog.kekasir.id` (Content Hub di `sas-pos-platform` sudah siap: `/api/public/content/blog/*`)

## Dokumen

| # | File | Isi |
|---|------|-----|
| 01 | [01-product-knowledge.md](./01-product-knowledge.md) | Fitur Kekasir, persona, USP, peta CTA |
| 02 | [02-architecture.md](./02-architecture.md) | Arsitektur pipeline scrape + AI + image + cron |
| 03 | [03-data-format.md](./03-data-format.md) | **Rekomendasi format**: MD + images + `catalog.json` |
| 04 | [04-categories-topics.md](./04-categories-topics.md) | Max 5 kategori + cluster topik 100+ ide |
| 05 | [05-scraper-plan.md](./05-scraper-plan.md) | Scrape kompetitor (inspirasi, bukan copy) |
| 06 | [06-generator-plan.md](./06-generator-plan.md) | Prompt Grok, slug, word count, multi-image |
| 07 | [07-cta-backlink.md](./07-cta-backlink.md) | CTA dinamis + internal linking graph |
| 08 | [08-scheduler-cron.md](./08-scheduler-cron.md) | Cron / watchdog jika bot berhenti |
| 09 | [09-preview.md](./09-preview.md) | Preview HTML+JS lokal |
| 10 | [10-implementation-roadmap.md](./10-implementation-roadmap.md) | Fase implementasi script Python |
| 11 | [11-api-config.md](./11-api-config.md) | AI gateway config (chat + image) |
| 12 | [12-rag-consistency.md](./12-rag-consistency.md) | **RAG** BM25 + corpus harga/fitur/anti-claim |
| 13 | [13-panduan-assets.md](./13-panduan-assets.md) | Screenshot panduan (opsional) |
| 14 | [14-image-design-system.md](./14-image-design-system.md) | **Grok images** + brand navy/orange thumbnail system |

## Keputusan cepat

| Pertanyaan | Jawaban plan |
|------------|-------------|
| Format artikel? | **Markdown body** + **gambar file** + **JSON catalog** (hybrid) |
| Berapa kategori? | **5** (lihat 04) |
| Panjang artikel? | **500–2000 kata** (target ideal 900–1400) |
| Gambar per artikel? | **1 thumbnail** + **1–5 inline** (dinamis per outline) |
| Model teks? | `grok-4.5` via `AI_BASE_URL` |
| Model image? | `grok-4.5` + tool `image_generation` via `POST /v1/responses` |
| Konsistensi? | **RAG** `rag/corpus/*` + `scripts/retrieve.py` (BM25) inject ke prompt |
| Scrape engine? | **httpx default** → **CloakBrowser** escalate; MCP stealth = debug only |
| Loop tanpa henti? | Queue + worker + cron watchdog (08) |
| Publish ke CMS? | Phase 2: push ke Content Hub (`sys/content/blog`) |

## Struktur folder (target)

```
kekasir-blog/
├── docs/                 # rencana (file ini)
├── rag/
│   ├── corpus/           # source of truth (harga, fitur, anti-claim)
│   └── index/            # generated BM25 chunks (gitignore)
├── scripts/
│   ├── retrieve.py       # RAG retrieve (ada)
│   ├── scrape_refs.py
│   ├── plan_topics.py
│   ├── generate_article.py
│   ├── generate_images.py
│   ├── link_graph.py
│   ├── worker.py
│   └── preview_server.py
├── data/
│   ├── catalog.json
│   ├── queue.jsonl
│   ├── refs/
│   └── state.json
├── content/{category}/{slug}/
│   ├── article.md
│   ├── meta.json
│   └── images/
├── preview/
└── logs/
```

## Prinsip konten (wajib)

1. **Inspirasi ≠ copy** — scrape hanya title/topic/structure; body 100% original Kekasir.
2. **CTA jujur** — hanya fitur yang benar-benar ada di produk (lihat 01 + RAG corpus).
3. **Title & slug unik** — cek `catalog.json` sebelum generate.
4. **Internal link** — tiap artikel link ke 2–5 artikel lain + 1 CTA produk.
5. **Bahasa** — Indonesia, natural, SEO tanpa keyword stuffing.
6. **RAG wajib** — setiap generate inject top-k corpus (harga Basic 60k / Pro 120k, anti-claim).
