# Blog Image Design System (Grok)

## Policy (updated)

| Layer | Source | Notes |
|-------|--------|--------|
| **Thumbnail** | **Grok AI always** | One family look across all posts |
| **Supporting fig 1–N** | **Grok AI default** | Original illustrations, not screenshots |
| **Screenshot panduan** | **Dilarang** | Konteks studi kasus UI beda dengan artikel |

Jangan tempel screenshot dari `assets/panduan` / panduan-content ke artikel blog.

## API (sama seperti playground TempAI)

Playground chat image mode:

```http
POST /admin/chat/sessions/:id/messages
{ "content": "<prompt>", "stream": false, "generate_image": true }
```

Proxy internal (yang dipakai script blog):

```http
POST {AI_BASE_URL}/responses
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "model": "grok-4.5",
  "stream": false,
  "store": false,
  "tools": [{"type": "image_generation"}],
  "reasoning": {"effort": "high", "summary": "concise"},
  "input": [{
    "role": "user",
    "content": [
      {"type": "input_text", "text": "Generate an image: ...\n\nUse the image_generation tool."}
    ]
  }]
}
```

Response: `output[]` tipe `image_generation_call` / `output_image` → field `result` atau `content[].b64_json` (base64).  
Script: `scripts/ai_client.py` → `generate_image_b64()` decode + simpan webp/png.

**Gateway note:** image gen needs a provider that supports OpenAI-style `/v1/responses` + tool `image_generation` (not only `/v1/chat/completions`).

## Brand tokens (from Kekasir landing design system)

| Token | Hex | Role in images |
|-------|-----|----------------|
| Navy | `#1E3A8A` | Main shapes, depth, trust |
| Orange | `#EA580C` | Accent, energy, CTA vibe |
| Sky | `#BAE6FD` | Soft bg / light panels |
| Blue | `#0EA5E9` | Secondary accents / gradient |
| Warm bg | `#FFFBF5` | Warm off-white canvas |

Prompt source of truth: `scripts/image_style.py`

## Ukuran SEO (wajib beda: thumbnail vs pendukung)

| Role | Pixel | Aspek | File | Pemakaian SEO |
|------|-------|-------|------|----------------|
| **Thumbnail** | **1200×630** | ~1.91:1 (OG) | `thumbnail.webp` | `og:image`, Twitter card, listing, hero |
| **Supporting** | **1200×800** | **3:2** | `fig-01.webp` … | Gambar dalam body artikel (mobile/desktop) |

Prompt terpisah di `scripts/image_style.py`:

- `thumbnail_prompt()` → ROLE thumbnail, safe zone 8%, fokus readable kecil, **bukan** in-article figure  
- `supporting_prompt()` → ROLE in-article, lebih deskriptif, **bukan** hero/OG  

Setelah generate, file di-resize cover ke pixel di atas (WebP).

## Gaya foto (bukan kartun)

| Wajib | Dilarang |
|-------|----------|
| Fotorealistik, orang asli | Kartun, flat vector, anime, CGI plastik |
| Wajah Indonesia / Nusantara | Wajah stok non-relevan dipaksakan |
| Pakaian polos/bervariasi tiap gambar | **Batik** / motif tradisional dipaksakan |
| Latar warung/cafe/dapur/bazar | Logo brand pihak ketiga di scene |

## Watermark logo Kekasir (konsisten)

**Metode yang benar: post-process composite**, bukan minta AI menggambar logo.

```
Grok generate photo
  → decode base64
  → resize SEO (1200x630 / 1200x800)
  → PIL paste watermark asset (fixed)
  → save webp
```

| Parameter | Nilai default |
|-----------|----------------|
| Asset | `assets/brand/kekasir-logo.svg` → di-render ke `kekasir-watermark.png` |
| Posisi | **top-right** |
| Asset | `assets/brand/logo-horizontal.png` (file asli, tidak digambar ulang) |
| Lebar logo | **~17% lebar gambar** |
| Background | **tidak ada** (transparan) |
| Opacity | ~0.92 |
| Margin | ~2% dari tepi |

## Full-bleed (wajib)

- Foto harus **penuh canvas** tepi-ke-tepi  
- **Dilarang:** border putih/abu, frame polaroid, mat, bayangan kartu, foto mengambang di background kosong  

## Binding gambar ↔ section redaksi (wajib)

Setiap `fig-NN` di `article.md` diikat ke konteks section terdekat:

1. **Penempatan di markdown** — `generate_article` menyisipkan `![alt](images/fig-0N.webp)` di intro / setelah H2 yang relevan (bukan numpuk di akhir).  
2. **Alt text** — mendeskripsikan adegan yang cocok dengan paragraf section.  
3. **Generate image** — `extract_figure_contexts()` baca H2 terdekat + excerpt paragraf → masuk ke `supporting_prompt(..., section_heading, section_excerpt, placement)`.  
4. **Meta** — `meta.json` menyimpan `section_heading` / `placement` per gambar untuk audit.

Jadi gambar bukan “stok F&B acak”, melainkan visual untuk section yang sama.


Kenapa post-process?

1. **Ukuran & bentuk sama** di semua artikel (AI sering distorsi logo).  
2. **Penempatan tetap** (bottom-right).  
3. Logo tidak “ikut rusak” saat model ganti outfit/latar.  
4. Bisa re-watermark tanpa re-generate foto.

Script: `scripts/watermark.py` → dipanggil otomatis di `generate_images.py`.

## Thumbnail template (series consistency)

- Frame **1200×630**  
- Subject left/center + abstract UI/food shapes right  
- Soft warm/sky gradient; navy block + orange accent  
- Optional blurred device (unreadable UI)  
- No text / watermark / foreign logos  

## Supporting images

- Frame **1200×800 (3:2)**  
- Same color language as thumbnail  
- Variants: diagram, wide scene, abstract dashboard, phone, kitchen pass  
- AI illustration (default) atau fallback brand lokal — **tanpa** screenshot panduan

## Pipeline teks + gambar bersamaan

```bash
# default worker: tulis artikel lalu generate image (1 job)
PYTHONPATH=scripts .venv/bin/python scripts/worker.py --count 1

# text only (tanpa image)
PYTHONPATH=scripts .venv/bin/python scripts/worker.py --count 1 --text-only
```

## CLI image saja

```bash
.venv/bin/python scripts/generate_images.py \
  --category tips-bisnis \
  --slug cara-hitung-hpp-menu-warung-agar-margin-aman \
  --force
```

Jika Grok `/v1/responses` belum tersedia di production, pipeline fallback ke **local brand renderer** (warna Kekasir, ukuran SEO sama) supaya artikel tetap lengkap.

## Worker default

`worker.py` with images → **AI only** (Grok + design system).  
Use `--with-panduan` manually when a post needs real UI proof.
