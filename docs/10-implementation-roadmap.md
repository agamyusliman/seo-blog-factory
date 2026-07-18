# Implementation Roadmap

## Fase 0 — Scaffold (½ hari)

- [x] Folder `kekasir-blog/` + docs plan  
- [x] RAG corpus + `scripts/retrieve.py` (BM25)  
- [x] `.env.example`  
- [x] `data/catalog.json` skeleton  
- [ ] `requirements.txt` (`openai`, `httpx`, `beautifulsoup4`, `python-dotenv`, `pillow`, `markdown`, `cloakbrowser` optional)  
- [ ] `config.yaml` (sites, categories, caps, engine)  

## Fase 1 — Scrape + topic plan (1 hari)

- [ ] `scrape_refs.py` multi-site, rate limit, jsonl out  
- [ ] Engine `auto|httpx|cloak` (CloakBrowser escalate)  
- [ ] `plan_topics.py` unique title/slug + queue.jsonl  
- [ ] Seed manual 50 title high-intent (tanpa scrape)  

## Fase 2 — Generator teks + RAG (1–2 hari)

- [x] `retrieve.py`  
- [ ] `ai_client.py` chat completions wrapper  
- [ ] `generate_article.py` inject RAG + validators (harga/anti-claim/word count)  
- [ ] Write `article.md` + `meta.json`  

## Fase 3 — Image (1 hari)

- [ ] `generate_images.py` via `/v1/responses`  
- [ ] Thumbnail + inline alignment  
- [ ] Pillow convert webp  

## Fase 4 — Worker + cron (1 hari)

- [ ] `worker.py` loop + recover  
- [ ] `watchdog.sh` + sample crontab  
- [ ] Logging + daily caps  

## Fase 5 — Link graph + preview (1 hari)

- [ ] `link_graph.py`  
- [ ] `preview/index.html` + JS  
- [ ] Smoke test 5–10 artikel end-to-end  

## Fase 6 — Publish ke Content Hub (opsional, belakangan)

- [ ] MD → HTML  
- [ ] Upload images ke file storage platform  
- [ ] Create/update blog post via admin API / server action  
- [ ] Draft vs publish workflow  

## Definition of Done (MVP)

1. Scrape ≥1 page per site target (atau seed manual fallback)  
2. Generate ≥10 artikel unik (slug unik)  
3. Tiap artikel: MD 500–2000 kata, ≥1 thumbnail, ≥1 inline image  
4. catalog.json konsisten  
5. Preview HTML bisa baca list + detail  
6. Worker + watchdog documented & tested 1 jam  

## Out of scope MVP

- Full 500 artikel quality human edit  
- Multilingual EN  
- Auto social post  
- A/B title testing  
