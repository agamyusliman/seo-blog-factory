# Article & Image Generator Plan

## API

| Use | Endpoint | Model |
|-----|----------|--------|
| Teks artikel | `POST /v1/chat/completions` | `grok-4.5` |
| Gambar | `POST /v1/responses` + `tools: [{type: image_generation}]` | `grok-4.5` |
| Base | `AI_BASE_URL` (OpenAI-compatible gateway) | |
| Auth | `Authorization: Bearer $AI_API_KEY` | |

SDK: `openai` Python client dengan `base_url` custom **atau** `requests` murni (image lewat responses).

## Pipeline satu artikel

```
1. Ambil job (title, slug, category, outline, feature_keys)
2. RAG retrieve: scripts/retrieve.py (title + feature_keys + category) → top-k chunks
3. Build system prompt = rules + RAG_CONTEXT (wajib)
4. Generate outline detail (jika belum) → H2 list + image slots
5. Generate body markdown (500–2000 kata)
6. Validate: word count, harga, anti-claim, slug, CTA (lihat 12-rag)
7. Generate image prompts (thumbnail + fig 1..N)
8. Generate images → save webp/png
9. Pick internal links from catalog (slug nyata saja)
10. Write article.md + meta.json + update catalog + mark job done
11. (opsional) salin excerpt ke rag/corpus/published/{slug}.md
```

## System prompt (intisari)

```
Kamu copywriter SEO Indonesia untuk blog Kekasir.id (aplikasi kasir/POS UMKM).
- Artikel ORIGINAL, jangan plagiat.
- Bahasa natural, jelas, untuk pemilik usaha.
- Panjang 500–2000 kata (target 900–1400).
- Struktur: intro, H2/H3, bullet/numbered list, tabel opsional, penutup CTA.
- Sisipkan 1–5 placeholder gambar: ![alt](images/fig-0N-....webp)
- Sebut fitur Kekasir HANYA jika relevan: {feature_keys} + FAKTA RAG.
- CTA dinamis dari template yang diizinkan; tidak hard-sell tiap paragraf.
- Internal link HANYA ke slug di RELATED_SLUGS: [[link:slug|anchor text]]
- Jangan sebut brand PG; gunakan QRIS / mitra pembayaran.
- JANGAN bertentangan dengan blok FAKTA PRODUK (harga, plan, anti-claim).
```

## User prompt template

```
Judul: {title}
Slug: {slug}
Kategori: {category}
Persona: {persona}
Outline wajib: {outline}
Fitur CTA: {feature_keys}
Artikel terkait kandidat: {related_slugs}
Keyword fokus: {primary_kw}
Jumlah gambar inline: {n_images} (1–5)

{RAG_CONTEXT}   ← output format_context(retrieve(...))
```

## Validasi post-generate

| Check | Action |
|-------|--------|
| word_count < 500 | regenerate expand |
| word_count > 2000 | rewrite compress |
| title/slug sudah di catalog | abort / retitle |
| 0 heading | reject |
| 0 list/bullet (flat) | rewrite once “tambah list” |
| competitor brand copy-paste | strip / rewrite |
| image placeholders ≠ n_images | align |

## Image generation

### Thumbnail

Prompt style:

```
Editorial blog thumbnail, Indonesian MSME {scene}, clean modern flat-illustration,
no text watermark, 16:9, brand-friendly teal/navy accents, high quality
Context: {title}
```

### Inline figures

Sesuai section: diagram sederhana, mock kasir, meja restoran, stok, dll.  
**Hindari** logo palsu bank/e-wallet.

Extract base64 dari `output[]` (`result` / `b64_json`) → decode → optional convert WebP (Pillow).

## Concurrency

- Worker single-threaded dulu (stabil).  
- Optional: pool 2 chat, 1 image.  

## Retry

- HTTP 429/5xx → exponential backoff  
- Image empty b64 → retry 2x → continue article without that fig (log warning)  

## Estimasi throughput

| Step | ~waktu |
|------|--------|
| Chat body | 30–90s |
| Images ×3 | 60–180s |
| Total / artikel | ~2–5 menit |

→ ~12–30 artikel / jam (teoritis, tergantung quota).  
Daily cap disarankan untuk kontrol kualitas.
