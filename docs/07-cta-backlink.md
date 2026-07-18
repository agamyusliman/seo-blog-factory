# CTA Dinamis & Internal Backlink

## Prinsip

1. **Tidak asal artikel** — tiap piece punya `feature_keys` + persona + intent.  
2. **CTA relevan** — self-order artikel → CTA QR meja; HPP → CTA resep/HPP.  
3. **Backlink internal** — graph antar artikel, bukan hanya homepage.  
4. Soft-sell: edukasi dulu, CTA di tengah (opsional) + penutup.

## Feature key registry (contoh)

| key | CTA text examples | Landing |
|-----|-------------------|---------|
| `pos_core` | “Catat penjualan rapi di aplikasi kasir Kekasir” | `https://kekasir.id` |
| `qris` | “Terima QRIS dinamis per transaksi” | `https://kekasir.id/qris-dinamis` (jika live) / harga |
| `self_order` | “Aktifkan self-order QR meja” | `https://kekasir.id` + panduan |
| `kds` | “Order dapur real-time dengan KDS” | harga / fitur Pro |
| `shift` | “Tutup shift dan rekap kas otomatis” | — |
| `hpp_recipe` | “Hitung HPP dari resep bahan baku” | — |
| `inventory` | “Stok & opname lebih terkontrol” | — |
| `multi_outlet` | “Kelola multi-cabang dari satu dashboard owner” | dashboard |
| `table_mgmt` | “Kelola meja, pindah & gabung meja” | — |
| `appointment` | “Jadwalkan janji temu layanan” | — |
| `offline` | “Kasir offline-ready saat sinyal jelek” | — |
| `trial` | “Coba gratis 14 hari” | register |
| `pricing` | “Lihat paket Basic & Pro” | `https://kekasir.id/harga` |

Generator pilih **1 primary + 0–1 secondary** dari keys job.

## Template CTA blocks (MD)

```md
> **Coba di Kekasir:** {primary_text}.  
> [Coba gratis 14 hari]({register}) · [Lihat harga]({harga})
```

Variasi tone: formal / santai / checklist — di-rotate biar tidak template-sama.

## Internal linking strategy

### Saat generate (fase 1)

- Jika catalog < 10 posts: sisipkan `[[link:pending|...]]` atau skip.  
- Jika ada kandidat: pilih 2–5 slug related by tag/category/feature.

### Pass `link_graph.py` (fase 2, batch)

Algoritma sederhana:

1. Embed / keyword TF-IDF antar title+tags (mulai: token overlap).  
2. Untuk tiap post, top-k similar (k=3–5), beda slug.  
3. Inject section **Artikel terkait** di akhir MD jika belum ada.  
4. Pastikan graph tidak star-only (hindari semua link ke 1 hub).  
5. Update `meta.internal_links` + `catalog`.

### Aturan SEO internal

- Anchor natural (bukan “klik di sini”).  
- Max 5 internal links di body + 3 di related.  
- Jangan link ke draft/failed.  
- Prefer deep link category silang (tips ↔ operasional).  

## Cross-link ke non-blog

| Target | Kapan |
|--------|--------|
| `kekasir.id` | CTA umum |
| `kekasir.id/harga` | perbandingan paket |
| `/panduan/...` | how-to produk detail (jika sudah live) |
| `dashboard.kekasir.id/register` | trial |

## Quality gate “tidak asal buat”

Job ditolak / di-rewrite jika:

- Tidak ada `feature_keys` dan kategori `info-produk`/`operasional`  
- Intent murni kompetitor-bashing  
- Keyword stuffing brand  
- Tidak ada outline minimal 4 H2  
