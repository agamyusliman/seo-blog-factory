# RAG Consistency Layer — Blog Factory

> **Tujuan**: Artikel ratusan tetap **konsisten** soal harga, fitur, CTA, guardrail, tone — tidak “halusinasi” beda tiap generate.

## Masalah tanpa RAG

| Gejala | Dampak |
|--------|--------|
| Model hafal harga 50k/100k (stale docs) | SEO + trust rusak |
| Klaim fitur Basic yang sebenarnya Pro | Komplain trial |
| CTA random / hard-sell berulang | Konversi jelek |
| Internal link ke slug fiktif | Broken link |
| Nama PG / klaim integrasi GoFood API | Legal/marketing risk |

## Arsitektur RAG (lokal dulu)

```
┌─────────────────────────────────────────────────────────┐
│  rag/corpus/   (source of truth markdown chunks)        │
│   01-brand-pricing.md                                   │
│   02-features-cta.md                                    │
│   03-anti-claims.md                                     │
│   04-personas.md                                        │
│   05-tone-seo.md                                        │
│   06-urls-cta.md                                        │
│   07-keywords-supporting.md  (LSI / long-tail per cluster)│
│   08-local-kepri.md  (Batam, Tanjungpinang, Bintan, Kepri)│
│   09-bahasa-lokal.md (anti AI-slop, kamus ganti istilah) │
│   10-legal-compliance.md (S&K, privasi, refund)         │
│   11-faq-product-truth.md (FAQ resmi kekasir.id/faq)    │
│   published/*.md  (artikel done — for style + backlink) │
└───────────────────────┬─────────────────────────────────┘
                        │ build_index.py
                        ▼
┌─────────────────────────────────────────────────────────┐
│  rag/index/                                             │
│   chunks.jsonl   (id, text, metadata, embedding?)       │
│   faiss.idx  OR  simple bm25.json  (fase 1 = BM25)      │
└───────────────────────┬─────────────────────────────────┘
                        │ retrieve(query, k=8)
                        ▼
┌─────────────────────────────────────────────────────────┐
│  generate_article.py                                    │
│   system = base_rules + RAG_CONTEXT                     │
│   user   = title/outline/feature_keys                   │
└─────────────────────────────────────────────────────────┘
```

## Fase implementasi

### Fase 1 — Keyword / BM25 (MVP, tanpa embedding API)

1. Chunk corpus per section (`##` heading = 1 chunk, max ~400 token).  
2. Index inverted: token → chunk_ids.  
3. Query = `title + category + feature_keys + tags`.  
4. Top-k (default 8) → inject ke prompt sebagai:

```
### FAKTA PRODUK (wajib patuhi; jangan bertentangan)
{chunk_1}
...
### LARANGAN
{anti_claims}
### CTA YANG DIIZINKAN UNTUK JOB INI
{resolved_ctas}
```

**Kelebihan**: zero cost embedding, deterministik, mudah debug.  
**Cukup** untuk konsistensi harga/fitur.

### Fase 2 — Embedding (opsional)

Jika gateway support embeddings, atau pakai model lokal (`sentence-transformers`):

- Embed chunks + query  
- Cosine top-k  
- Hybrid: `0.6 * dense + 0.4 * bm25`

### Fase 3 — Memory artikel publish

Setiap artikel `status=done` → chunk title+excerpt+H2+feature_keys ke `published/`  
Retrieve untuk:

- gaya penulisan  
- kandidat internal link (slug nyata)  
- hindari topik duplikat (similarity > threshold → retitle)

## Retrieval policy per job type

| Job category | Wajib retrieve |
|--------------|----------------|
| `info-produk` | brand-pricing + features-cta + urls |
| `operasional` | features-cta (ops) + anti-claims |
| `tips-bisnis` | personas + tone + soft CTA trial |
| `ide-usaha` | personas + soft CTA |
| `inspirasi` | personas + case-study rules (no fake metrics) |

## Prompt contract (generator)

```
1. Jika FAKTA PRODUK menyebutkan harga/fitur, salin angka itu — jangan ganti.
2. Jangan sebut fitur di luar feature_keys job + retrieved facts.
3. Internal link HANYA ke slug yang ada di daftar RELATED_SLUGS.
4. CTA pakai template dari CTA_ALLOWED; boleh parafrase ringan, jangan ubah URL.
5. Jika ragu fitur Pro vs Basic → tulis "tersedia di paket Pro / cek di halaman Harga".
```

## Validasi post-RAG (gate)

Script `validate_article.py`:

| Check | Fail if |
|-------|---------|
| Harga | Muncul `50000` / `50.000` / `100.000` paket (stale) tanpa konteks lain |
| Basic claim | Regex fitur Pro (`self-order QR meja`, `KDS`, `reservasi`) + kata "Basic" same section |
| Forbidden | `GoFood API`, brand PG terlarang, `loyalty points sudah ada` |
| Link | `[[link:slug]]` slug not in catalog |
| Word count | <500 or >2000 |

Fail → auto rewrite once dengan error list di user prompt.

## File layout

```
kekasir-blog/
  rag/
    corpus/           # human-edited truth
    index/            # generated (gitignore optional)
    build_index.py
    retrieve.py
  docs/12-rag-consistency.md  # this file
```

## Sync dari product docs

Jangan auto-scrape seluruh monorepo tiap generate (noisy).  
**Manual / semi-auto**:

```bash
# update corpus from marketing truth sources
python scripts/sync_rag_corpus.py
# sources:
#   kekasir-selforder marketing /harga /faq /qris-dinamis (preferred)
#   kekasir-blog/docs/01-product-knowledge.md
#   kekasir-blog/rag/corpus/*.md overrides
```

Priority truth:

1. Live marketing pages (`/harga`, `/faq`, `/qris-dinamis`)  
2. `rag/corpus/*` (curated)  
3. `docs/01-product-knowledge.md`  
4. `kekasir-docs/*` (engineering — boleh stale price)

## Metrics konsistensi

| Metric | Target |
|--------|--------|
| % artikel pass validate | ≥95% |
| Harga mismatch | 0 |
| Broken internal link | 0 |
| Duplicate title/slug | 0 |
| Same CTA boilerplate 5x berturut | <10% (rotate templates) |
