# Screenshot Panduan — TIDAK dipakai di blog

## Keputusan (2026-07-19)

Screenshot dari folder panduan **tidak boleh** dipakai sebagai gambar artikel blog.

Alasan: konteks studi kasus / data demo di UI panduan **berbeda** dengan narasi artikel SEO. Memakai screenshot itu bisa menyesatkan (outlet, menu, angka, branding kasus panduan).

## Sumber gambar blog yang diizinkan

| Sumber | Status |
|--------|--------|
| Grok AI (`/v1/responses` + design system) | **Default** |
| Local brand renderer (navy/orange, ukuran SEO) | Fallback jika Grok gagal |
| Screenshot panduan | **Dilarang** |
| Foto merchant fiktif seolah nyata | **Dilarang** |

## Ukuran

- Thumbnail: **1200×630**  
- Supporting: **1200×800**  

Lihat [14-image-design-system.md](./14-image-design-system.md).

## Folder `assets/panduan/`

Boleh tetap ada di disk untuk keperluan **panduan produk** / arsip internal, tetapi **pipeline blog tidak mengimpor** file tersebut (`generate_images.py` tidak memanggil `asset_library`).
