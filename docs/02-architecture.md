# Architecture — Blog SEO Factory

## High-level

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ Competitor blogs│────▶│ scrape_refs.py   │────▶│ data/refs/*.json   │
│ httpx→cloak     │     │ (rate-limited)   │     │ metadata only      │
└─────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                           │
┌─────────────────┐     ┌──────────────────┐               ▼
│ Product + RAG   │───▶│ plan_topics.py   │────▶ data/queue.jsonl
│ rag/corpus/*    │     │ unique title/slug│      (jobs: pending)
└─────────────────┘     └──────────────────┘
                                                           │
                        ┌──────────────────┐               ▼
                        │ worker.py        │◀── cron/watchdog
                        │ (loop forever)   │
                        └────────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
     retrieve.py (RAG)    generate_images.py  link_graph.py
     → generate_article   (/v1/responses)     (internal links)
     (grok-4.5 + context)
              │                  │                  │
              ▼                  ▼                  ▼
     content/{cat}/{slug}/article.md + images/ + meta.json
              │
              ▼
     data/catalog.json  +  rag/corpus/published/ (style memory)
              │
              ▼
     preview/index.html  │  (phase2) Content Hub API publish
```

Lihat [12-rag-consistency.md](./12-rag-consistency.md) dan [05-scraper-plan.md](./05-scraper-plan.md) (CloakBrowser).

## Komponen

| Komponen | Tanggung jawab |
|----------|----------------|
| **Scraper** | Ambil daftar title, URL, kategori, excerpt dari kompetitor. **Tidak** menyimpan full body untuk diparafase mentah. |
| **Topic planner** | Expand seed → title unik + slug + kategori + outline + feature CTA tags + target word count. |
| **Article generator** | Grok chat: body MD 500–2000 kata, H2/H3, bullet, list, placeholder `![alt](images/fig-0N.webp)`. |
| **Image generator** | 1 thumbnail + N inline (1–5) via image_generation tool; nama file = slug context. |
| **Link graph** | Setelah ≥N artikel, inject backlink internal + related posts di meta. |
| **Worker** | Ambil job `pending` → generate → `done` / `failed`; heartbeat di `state.json`. |
| **Cron watchdog** | Jika worker mati / queue stuck, restart atau alert. |
| **Preview** | Baca catalog + md, render HTML lokal. |

## State machine job

```
pending → generating → images → linking → done
                ↘ failed (retry ≤3) → dead_letter
```

## Idempotensi

- Key unik: `slug`  
- Skip jika folder `content/.../article.md` sudah ada dan `meta.status=done`  
- Title collision → regenerate title (+suffix/variant) sebelum write  

## Rate & cost control

| Resource | Limit default (config) |
|----------|------------------------|
| Scrape | 1 req / 2–4s per host, respect robots |
| Chat generate | concurrent 1–2 |
| Image generate | concurrent 1 (timeout 180s) |
| Daily cap | e.g. max 30 artikel/hari (configurable) |
| Word count | reject <500 atau >2000 → rewrite once |

## Keamanan API key

- Simpan di `.env` (gitignored), **jangan** hardcode di repo  
- User sudah share key sesi: pakai env `AI_API_KEY` + `AI_BASE_URL`  
- Rotate key jika bocor ke git history  

## Integrasi publish (fase belakangan)

Content Hub sudah support:

- Admin: `sys/content/blog`  
- Public: `GET /api/public/content/blog/posts` + `/{slug}`  
- Fields: title, slug, excerpt, body_html, cover, category, tags, meta SEO  

Pipeline lokal menghasilkan **MD + meta**; converter `md → body_html` + upload image → API publish (script terpisah).
