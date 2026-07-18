# Kategori (max 5) & Cluster Topik

## 5 Kategori Blog (final proposal)

| # | Slug | Nama | Fokus SEO | % target volume |
|---|------|------|-----------|-----------------|
| 1 | `tips-bisnis` | Tips Bisnis | How-to, checklist, strategi UMKM | 30% |
| 2 | `ide-usaha` | Ide Usaha F&B | Ide jualan kuliner, menu, model bisnis F&B | 25% |
| 3 | `operasional` | Operasional Kasir & Outlet | Kasir, shift, stok, dapur, laporan | 20% |
| 4 | `info-produk` | Info Produk Kekasir | Fitur, tutorial soft-sell, update | 15% |
| 5 | `inspirasi` | Inspirasi & Studi Kasus | Cerita, skenario outlet, digitalisasi | 10% |

Alasan 5: mirror kompetitor (Moka/Qasir) tapi **disederhanakan** + slot khusus operasional POS (kekuatan Kekasir).

---

## Cluster topik (sample seeds → ratusan artikel)

Planner akan **variasi** title (angka, persona, lokasi, jenis usaha) agar slug unik.

### A. Tips Bisnis (`tips-bisnis`)

- Cara hitung HPP menu warung / cafe / seblak  
- Cara tentukan harga jual makanan  
- 7 cara naikkan omzet warung tanpa iklan berbayar  
- Checklist buka usaha F&B pertama kali  
- Cara kelola cashflow harian UMKM  
- Tips promo musiman tetap profit  
- Cara baca laporan penjualan mingguan  
- Strategi bundling paket hemat  
- Cara hitung break-even restoran kecil  
- Tips rekrut & latih kasir baru  
- Cara hadapi sepi pengunjung di hari kerja  
- Digitalisasi warung: mulai dari mana  
- Cara hitung biaya listrik & overhead outlet  
- Tips upselling di kasir  
- Cara kelola multi-cabang dengan budget terbatas  

### B. Ide Usaha & F&B (`ide-usaha`)

- Ide usaha modal kecil di rumah (F&B)  
- Ide menu kopi kekinian untuk cafe kecil  
- Ide usaha seblak / camilan viral  
- Ide bakery mini / dessert box  
- Ide food truck vs kios permanen  

- Ide menu ramadan / natal / lebaran  
- Ide franchise vs independent outlet  
- Ide combo menu anak + keluarga  
- Ide usaha cloud kitchen  
- Ide menu sehat / diet untuk gen Z  
- Ide usaha minuman boba / thai tea  

### C. Operasional (`operasional`)

- Cara buka & tutup shift kasir yang rapi  
- Cara pantau stok bahan baku dapur  
- Cara atur meja restoran saat peak hour  
- Cara kerja dapur dengan KDS  
- Cara terima QRIS di usaha kecil  
- Cara pisah bill rombongan  
- Cara catat order delivery (GoFood/Grab label)  
- Cara kurangi selisih kas di akhir shift  
- Cara kelola stok bahan baku F&B  
- Cara setup printer struk bluetooth  
- Cara handle void & refund  

- Cara buat reservasi meja  
- Cara self-order QR meja untuk cafe  
- Cara multi-payment (tunai + QRIS)  
- Cara laporan produk terlaris  
- Cara hitung variance kas  

### D. Info Produk (`info-produk`)

- Apa itu aplikasi kasir online?  
- Perbedaan Basic vs Pro Kekasir (fitur)  
- Mengenal self-order QR Kekasir  
- Cara daftar & coba gratis 14 hari  
- Fitur multi-outlet untuk owner  
- Fitur customer display di POS  
- Fitur HPP & resep di Kekasir  
- Fitur diskon & kupon  
- Offline mode: kasir tetap jalan  
- QRIS dinamis untuk outlet  
- Import menu dari foto (AI Vision) — soft  
- Hardware printer yang cocok  
- Keamanan data multi-tenant (high-level)  

### E. Inspirasi & Studi Kasus (`inspirasi`)

- Studi kasus: warung seblak naik omzet dengan digitalisasi kasir  
- Studi kasus: cafe 2 lantai pakai self-order  
- Cerita outlet multi-cabang kelola stok  

- Dari nota kertas ke struk digital  
- Kasus: antrian panjang → self-order QR  
- Kasus: selisih stok → opname rutin  
- Inspirasi layout meja restoran kecil  
- Inspirasi evaluasi menu laris dari data penjualan  

---

## Pola title generator (unik)

Template:

```
{angka?} {kata_kerja} {objek} {untuk|bagi} {persona} {modifier?}
```

Contoh variasi slug-safe:

- `cara-hitung-hpp-menu-warung`  
- `cara-hitung-hpp-menu-cafe-kopi`  
- `7-cara-naikkan-omzet-warung-tanpa-iklan`  
- `checklist-buka-usaha-fnb-pertama-kali`  

Rules:

1. Lowercase, kebab-case, strip aksen  
2. Max 80 char (selaras Content Hub slug)  
3. Cek `catalog.slugs` — jika bentrok: ubah modifier (`-2026`, `-umkm`, `-pemula`, jenis usaha)  
4. Title case ID natural (bukan Title Case Inggris kaku)  

## Tag taxonomy (bebas, multi)

`fnb`, `kuliner`, `qris`, `self-order`, `hpp`, `food-cost`, `bahan-baku`, `shift`, `multi-outlet`, `promo`, `umkm`, `cafe`, `restoran`, `warung`, `katering`, `gerobak`, `cloud-kitchen`, `bakery`
