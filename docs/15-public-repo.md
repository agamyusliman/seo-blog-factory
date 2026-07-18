# Saran nama repo & deskripsi (public)

## Rekomendasi utama

| | |
|--|--|
| **Nama repo** | `kekasir-blog-factory` |
| **Deskripsi (GitHub short)** | SEO blog content factory for Kekasir.id (F&B POS) — RAG articles, photorealistic images, local preview |
| **Topics** | `seo`, `blog`, `content-factory`, `indonesia`, `fnb`, `pos`, `rag`, `python` |

### Kenapa nama ini
- Jelas: blog + factory (bukan website publish CMS)
- Brand `kekasir` di depan untuk discoverability
- Netral teknis, cocok open/public tooling

## Alternatif nama

| Nama | Nuansa |
|------|--------|
| `kekasir-seo-engine` | Lebih “engine”, sedikit marketing |
| `kekasir-content-pipeline` | Teknis/pipeline CI-friendly |
| `fnb-blog-factory` | Generic (hilang brand) — kurang disarankan jika official |
| `kekasir-blog-ai` | Pendek, tapi terlalu generik “AI” |

## Deskripsi panjang (About / README blurb)

**EN**  
Automated content factory that drafts Indonesian F&B SEO articles for Kekasir POS, injects product/legal RAG, generates photorealistic section-matched images with brand watermark, and previews results locally.

**ID**  
Pabrik konten SEO untuk blog Kekasir.id: artikel Bahasa Indonesia (F&B), RAG produk/legal, gambar fotorealistik per section + watermark logo, preview HTML lokal. Bukan CMS publish — fokus generate offline.

## Checklist sebelum `git push --public`

1. [ ] Tidak ada `.env` di tree (`git status` bersih dari secrets)  
2. [ ] `git check-ignore -v .env` → ignored  
3. [ ] Tidak commit `content/` atau `assets/panduan/`  
4. [ ] Rotate API key jika pernah ter-expose di chat/history  
5. [ ] Pilih license + cantumkan trademark Kekasir  
6. [ ] README pakai placeholder gateway (sudah di `.env.example`)  

## Init git (opsional)

```bash
cd kekasir-blog
git init
git add .
git status   # pastikan .env TIDAK muncul
git commit -m "Initial public release: Kekasir blog SEO factory"
# gh repo create softventure-id/kekasir-blog-factory --public --source=. --remote=origin --push
```
