# Data Format — Rekomendasi

## Jawaban: MD + images + JSON (hybrid)

| Opsi | Kelebihan | Kekurangan | Verdict |
|------|-----------|------------|---------|
| **Hanya MD** | Mudah baca/edit | Sulit query kategori, backlink, status batch | Kurang |
| **Hanya JSON** | Mudah program | Body panjang jelek di git, susah review copy | Kurang |
| **MD + JSON catalog** | Body human-friendly + index machine-friendly | 2 file per artikel | **Pilih ini** |

### Per artikel

```
content/tips-bisnis/cara-hitung-hpp-menu-warung/
├── article.md          # body + frontmatter ringan
├── meta.json           # structured metadata (source of truth machine)
└── images/
    ├── thumbnail.webp  # cover / OG
    ├── fig-01-hpp-simple.webp
    ├── fig-02-resep-bahan.webp
    └── fig-03-dashboard-laporan.webp
```

### Frontmatter `article.md` (opsional, mirror meta)

```md
---
title: "Cara Hitung HPP Menu Warung agar Margin Aman"
slug: "cara-hitung-hpp-menu-warung"
category: "tips-bisnis"
status: draft
word_count: 1120
---

# Cara Hitung HPP Menu Warung agar Margin Aman

Paragraf pembuka...

## Apa itu HPP?

...

![Contoh breakdown HPP seblak](images/fig-01-hpp-simple.webp)

## Langkah praktis

1. ...
2. ...

## Solusi dengan aplikasi kasir

CTA dinamis...

## Artikel terkait

- [Link internal](/blog/slug-lain)
```

### `meta.json` (per artikel)

```json
{
  "id": "uuid-or-ulid",
  "title": "Cara Hitung HPP Menu Warung agar Margin Aman",
  "slug": "cara-hitung-hpp-menu-warung",
  "category": "tips-bisnis",
  "tags": ["hpp", "fnb", "margin", "warung"],
  "excerpt": "Pelajari cara menghitung HPP menu warung...",
  "meta_title": "Cara Hitung HPP Menu Warung | Kekasir",
  "meta_description": "Panduan hitung HPP makanan untuk UMKM...",
  "word_count": 1120,
  "read_minutes": 6,
  "status": "done",
  "cta": {
    "feature_keys": ["hpp_recipe", "inventory_fnb", "reports"],
    "primary_text": "Hitung HPP otomatis dari resep di Kekasir",
    "primary_url": "https://kekasir.id/harga",
    "secondary_text": "Coba gratis 14 hari",
    "secondary_url": "https://dashboard.kekasir.id/register"
  },
  "images": {
    "thumbnail": "images/thumbnail.webp",
    "inline": [
      {"file": "images/fig-01-hpp-simple.webp", "alt": "Breakdown HPP seblak", "prompt": "..."},
      {"file": "images/fig-02-resep-bahan.webp", "alt": "Resep bahan baku", "prompt": "..."}
    ]
  },
  "internal_links": [
    {"slug": "tips-naikkan-margin-restoran", "anchor": "cara naikkan margin restoran"},
    {"slug": "panduan-stok-bahan-baku-fnb", "anchor": "kelola stok bahan baku"}
  ],
  "source_inspiration": [
    {"site": "kledo", "title": "Kalkulator HPP...", "url": "https://..."}
  ],
  "created_at": "2026-07-19T10:00:00+07:00",
  "updated_at": "2026-07-19T10:15:00+07:00",
  "model": "grok-4.5"
}
```

### `data/catalog.json` (global index)

```json
{
  "version": 1,
  "updated_at": "2026-07-19T12:00:00+07:00",
  "categories": [
    {"slug": "tips-bisnis", "name": "Tips Bisnis", "count": 0},
    {"slug": "ide-usaha", "name": "Ide Usaha & F&B", "count": 0},
    {"slug": "info-produk", "name": "Info Produk Kekasir", "count": 0},
    {"slug": "inspirasi", "name": "Inspirasi & Studi Kasus", "count": 0},
    {"slug": "operasional", "name": "Operasional Kasir & Outlet", "count": 0}
  ],
  "posts": [
    {
      "title": "...",
      "slug": "...",
      "category": "tips-bisnis",
      "path": "content/tips-bisnis/cara-hitung-hpp-menu-warung/",
      "status": "done",
      "thumbnail": "content/tips-bisnis/cara-hitung-hpp-menu-warung/images/thumbnail.webp",
      "word_count": 1120,
      "internal_links": ["tips-naikkan-margin-restoran"]
    }
  ],
  "slugs": ["cara-hitung-hpp-menu-warung"]
}
```

> `slugs[]` array/set untuk O(1) uniqueness check.

### `data/queue.jsonl`

Satu job per baris:

```json
{"id":"job_001","title":"...","slug":"...","category":"tips-bisnis","outline":["..."],"feature_keys":["hpp_recipe"],"status":"pending","attempts":0}
```

## Naming gambar

```
{slug-context}-{role}-{nn}.webp
```

Contoh:

- `cara-hitung-hpp-menu-warung-thumbnail.webp` (atau `thumbnail.webp` di folder artikel)  
- `fig-01-breakdown-hpp.webp`  
- `fig-02-tampilan-kasir.webp`  

Slug folder = slug artikel → path stabil untuk publish.

## Konversi publish

| Lokal | Content Hub |
|-------|-------------|
| `article.md` body | `body_html` (markdown → HTML) |
| `meta.excerpt` | `excerpt` |
| `images/thumbnail` | `coverFileId` (upload) |
| `category` | category slug CMS |
| `tags` | `tags[]` |
| `meta_title/desc` | SEO fields |

## Preview

`preview/index.html` + JS fetch `../data/catalog.json` + render markdown (marked.js CDN) + local image paths via simple static server.
