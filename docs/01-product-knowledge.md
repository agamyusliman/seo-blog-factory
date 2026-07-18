# Product Knowledge — Kekasir (untuk Blog SEO)

Sumber utama: `kekasir-docs/`, marketing `kekasir-selforder`, Content Hub blog di `sas-pos-platform`.

## Positioning

| Item | Value |
|------|--------|
| Brand | **Kekasir.id** |
| Produk | Aplikasi kasir / POS cloud untuk UMKM |
| Domain marketing | `https://kekasir.id` |
| POS app | `https://pos.kekasir.id` |
| Owner dashboard | `https://dashboard.kekasir.id` |
| Blog target | `blog.kekasir.id` (API public sudah ada) |
| Trial CTA | **Coba gratis 14 hari** (Pro full, tanpa CC) → `dashboard.kekasir.id/register` |
| Harga publik (WAJIB) | Basic **Rp60.000**/bln · **Rp575.000**/th; Pro **Rp120.000**/bln · **Rp1.150.000**/th — unit **per outlet** |
| QRIS MDR | ~**0,7%**; settlement ~T+2; copy provider-neutral |
| CS WA | `https://wa.me/6283193533330` |
| RAG corpus | `kekasir-blog/rag/corpus/*` (source of truth generator) |

> Angka internal lama 50k/100k di beberapa docs engineering = **STALE**. Artikel massal ikut live `/harga` + `rag/corpus/01-brand-pricing.md`.

## Jenis usaha (persona) — **F&B ONLY untuk konten blog**

> Produk SaaS publik saat ini diposisikan **hanya F&B**. Retail & Services **jangan** jadi vertical artikel SEO.

1. **F&B tanpa meja** — gerobak, bazar, kontainer, booth, PKL, takeaway  
2. **F&B rumahan / katering** — pre-order, nasi kotak, dapur rumah  
3. **F&B duduk** — cafe, restoran, coffee shop (meja, KDS, self-order → Pro)  
4. **Cloud kitchen / food court stall**  
5. **Bakery / dessert / seblak / camilan**  
6. **Multi-cabang / franchise F&B** (+ enterprise custom bila perlu)

## Fitur inventory (CTA-safe)

### Core POS (semua)

| Fitur | Deskripsi singkat | Contoh CTA blog |
|-------|-------------------|-----------------|
| Transaksi cepat | Katalog, keranjang, qty, catatan | “Catat penjualan harian tanpa ribet di Kekasir POS” |
| Multi pembayaran | Tunai, QRIS, transfer, kartu, e-wallet, **split payment** | “Terima QRIS + tunai dalam satu transaksi” |
| Struk thermal | Print Bluetooth/USB, reprint | “Cetak struk rapi untuk pelanggan” |
| Offline PWA | Cache + sync | “Kasir tetap jalan meski sinyal putus-putus” |
| Hold / parkir order | Simpan order lanjut nanti | “Parkir pesanan saat antrian padat” |
| Void / refund | Batalkan & refund (permission) | “Kelola retur dengan jejak jelas” |
| Shift kasir | Buka/tutup shift, rekap kas, variance | “Tutup shift rapi, kas tidak bocor” |
| Pengeluaran | Catat expense harian | “Pisahkan omzet dan pengeluaran harian” |
| Laporan | Penjualan, produk, staff, keuangan, inventori | “Pantau omzet multi-outlet dari dashboard” |
| Multi-outlet | Owner kelola banyak cabang | “Satu akun owner, banyak outlet” |

### F&B (banyak Pro)

| Fitur | CTA blog |
|-------|----------|
| Manajemen meja | “Visual meja: kosong / terisi / reservasi” |
| Pindah & gabung meja | “Gabung meja rombongan tanpa double order” |
| Split bill | “Pisah tagihan per tamu” |
| KDS dapur | “Order masuk dapur real-time, kurangi salah masak” |
| Customer display | “Tampilkan total & QRIS di layar kedua” |
| Reservasi meja | “Ambil booking meja tanpa kertas” |
| Dine-in / takeaway / delivery | “Catat sumber order delivery (label platform)” |
| Combo / paket menu | “Paket hemat otomatis di kasir” |
| Bahan baku + HPP / resep | “Hitung HPP seblak dari resep bahan baku” |
| Pre-order | “Terima pre-order / catering terjadwal” |

### Self-Order (Pro)

| Fitur | CTA blog |
|-------|----------|
| QR meja | “Pelanggan scan QR → pesan dari HP” |
| Menu digital publik | “Katalog online SEO-friendly per outlet” |
| Bayar di kasir vs QRIS online | “Self-order + bayar QRIS tanpa antri” |
| Deeplink e-wallet | “Bayar lewat GoPay/OVO/Dana/ShopeePay” |
| Theme Linktree-style | “Halaman outlet branded: warna, banner, sosmed” |
| Custom slug | `kekasir.id/nama-gerai` |
| Pickup order | “Order ambil sendiri tanpa meja” |

### Stok F&B (bukan retail)

| Fitur | CTA blog |
|-------|----------|
| Bahan baku + HPP / resep | “Hitung food cost dari resep” |
| Stok bahan dapur | “Pantau bahan baku agar tidak kehabisan” |

### Pembayaran & QRIS

| Fitur | CTA blog | Catatan |
|-------|----------|---------|
| QRIS dinamis | “Terima QRIS dinamis per transaksi” | Fee marketing ~**0,7%** (provider-neutral wording) |
| Pencairan / settlement | “Pantau settlement & pencairan ke rekening” | Jangan sebut brand PG spesifik di blog massal kecuali disetujui |
| Owner QRIS onboarding | “Daftar QRIS dari dashboard owner” | |

### Lainnya

| Fitur | CTA blog |
|-------|----------|
| Diskon & kupon (Pro) | “Promo otomatis + kode kupon” |
| Staff & role | “Kasir / dapur / admin dengan permission” |
| Marketplace hardware | “Printer & scanner kompatibel di toko Kekasir” |
| AI Vision menu import | “Foto menu → draft produk (F&B)” |
| WA magic link login | Opsional, jarang untuk SEO top-of-funnel |

## USP vs kompetitor (sudut konten)

1. **F&B-first** tapi tetap retail & service  
2. **Self-order + theme branding** (Linktree-like) di domain `kekasir.id/{slug}`  
3. **KDS + meja + customer display** dalam satu ekosistem  
4. **Offline-capable POS (PWA)**  
5. **Multi-outlet owner dashboard** + laporan konsolidasi  
6. **HPP / resep bahan baku** untuk margin F&B  
7. Harga entry UMKM + trial 14 hari  

## Jangan klaim di artikel (guardrail)

- **Retail / services sebagai target produk** (minimarket, barbershop, laundry, salon)  
- Integrasi API otomatis GoFood/GrabFood (saat ini **label/pencatatan**, bukan auto-ingest full)  
- Loyalty points “sudah live”  
- Nama payment gateway spesifik di copy massal (pakai **Mitra Penyelenggara Pembayaran / QRIS**)  
- Fitur enterprise yang belum di marketing pages  
- Angka harga/fee tanpa verifikasi ulang di `/harga` & legal  

## Mapping keyword → fitur (untuk generator)

| Keyword cluster | Fitur Kekasir |
|-----------------|---------------|
| aplikasi kasir restoran | POS F&B, meja, KDS |
| aplikasi kasir cafe / coffee shop | POS + self-order + shift |
| self order QR meja | Self-order Pro |
| QRIS usaha / kasir QRIS | Multi payment + QRIS dinamis |
| HPP makanan / resep menu | Bahan baku + HPP |
| stok opname toko | Inventori retail |
| shift kasir tutup kas | Shift management |
| multi cabang outlet | Owner multi-outlet |
| printer struk bluetooth | Print system |
| reservasi meja restoran | Reservation |
| food cost / food costing | HPP resep F&B |

## Referensi file docs

- `kekasir-docs/README.md`  
- `kekasir-docs/category.md` (taxonomy panduan — beda dari kategori **blog**)  
- `kekasir-docs/kekasir-webapps/02-features.md`  
- `kekasir-docs/kekasir-selforder/README.md` + `features/*`  
- `kekasir-docs/kekasir-selforder/landingpage/marketing-pages.md`  
- `kekasir-docs/sas-pos-platform/modules/content/*` (blog CMS + public API)  
