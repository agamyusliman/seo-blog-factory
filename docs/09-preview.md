# Preview Artikel (HTML + JS)

## Goal

Satu file (atau minimal) untuk **preview lokal** hasil generate: list kategori, detail artikel, gambar, related links.

## Approach

```
preview/
  index.html      # UI + JS
  app.js          # optional split
  styles.css      # optional
```

Serve static dari root `kekasir-blog`:

```bash
python -m http.server 8765
# buka http://localhost:8765/preview/
```

> `file://` sering block fetch JSON — wajib http.server.

## Fitur preview v1

1. Load `../data/catalog.json`  
2. Sidebar: 5 kategori + count  
3. List cards: title, excerpt, thumbnail, word count  
4. Detail: fetch `../content/{cat}/{slug}/article.md`  
5. Render markdown (CDN `marked` + `DOMPurify`)  
6. Resolve image relative path ke folder artikel  
7. Tampilkan CTA + internal links dari meta.json  
8. Search title client-side  

## Wireframe

```
┌──────────┬────────────────────────────┐
│ Kategori │  [Search]                  │
│ • All    │  ┌────┐ ┌────┐ ┌────┐     │
│ • Tips   │  │card│ │card│ │card│     │
│ • Ide    │  └────┘ └────┘ └────┘     │
│ ...      │                            │
│          │  ── detail view ──         │
│          │  H1 title                  │
│          │  body html                 │
│          │  images                    │
└──────────┴────────────────────────────┘
```

## Tidak termasuk v1

- SEO meta editor  
- Publish ke CMS  
- Auth  

## Phase 2

Embed di admin atau Storybook-like review before publish.
