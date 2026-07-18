# Fitur → CTA (RAG)

## Core POS (Basic + Pro)

| key | Fitur | Frasa CTA aman |
|-----|-------|----------------|
| pos_core | Kasir multi-device (HP/tablet/desktop) | Catat penjualan rapi di aplikasi kasir Kekasir |
| multi_pay | Tunai, QRIS, transfer, kartu, e-wallet | Terima banyak metode bayar dalam satu kasir |
| split_pay | Split payment | Satu nota bisa bayar campur tunai + QRIS |
| offline | Offline PWA (transaksi antre, sync) | Tetap jualan saat internet putus-putus |
| shift | Buka/tutup shift, selisih kas | Tutup shift rapi, pantau selisih kas |
| print | Struk thermal Bluetooth/USB 58/80mm | Cetak struk thermal dari HP/tablet |
| hold_order | Parkir / hold order | Parkir pesanan saat antrian padat |
| refund | Void & refund | Kelola retur dengan jejak jelas |
| reports | Laporan penjualan & export | Pantau omzet dan unduh laporan |
| multi_outlet | Multi cabang, plan per outlet | Kelola banyak cabang dari dashboard owner |
| tax | PB1/PPN/service charge | Atur pajak restoran di pengaturan outlet |
| expense | Catat pengeluaran | Pisahkan omzet dan pengeluaran harian |

## F&B Pro

| key | Fitur | Frasa CTA aman |
|-----|-------|----------------|
| table_mgmt | Manajemen meja, pindah/gabung | Kelola meja restoran dari POS |
| split_bill | Split bill | Pisah tagihan per tamu |
| kds | Kitchen Display System | Order masuk dapur real-time |
| reservation | Reservasi meja | Catat reservasi meja tanpa kertas |
| customer_display | Layar pelanggan | Tampilkan pesanan di layar kedua |
| combo | Paket combo menu | Jual paket hemat di kasir |
| hpp_recipe | HPP manual / resep bahan baku | Hitung HPP & margin per menu |
| pre_order | Pre-order terjadwal | Terima pre-order / katering terjadwal |
| ai_menu | Import menu dari foto (AI) | Input menu lebih cepat dari foto |

## Self-order

| key | Fitur | Plan | Frasa CTA aman |
|-----|-------|------|----------------|
| self_order_qr | QR meja self-order | **Pro** | Aktifkan self-order QR meja Kekasir |
| catalog_online | Menu digital `kekasir.id/{slug}` | Ada di ekosistem | Bagikan link menu online outlet |
| theme | Tema Linktree-style, banner, sosmed | Pro custom | Custom tampilan halaman outlet |
| pickup | Order pickup + bayar QRIS | Cek matrix | Terima order pickup bayar online |
| qris_self | QRIS di self-order + deeplink e-wallet | | Bayar QRIS langsung dari HP pelanggan |

## Stok & HPP F&B (bukan retail minimarket)

| key | Fitur | Frasa CTA aman |
|-----|-------|----------------|
| hpp_recipe | HPP manual / resep bahan baku | Hitung HPP & margin menu |
| inventory | Stok bahan baku F&B | Pantau bahan baku dapur |

Jangan framing “inventori minimarket / multi-barcode toko ritel”.

## Hardware & toko perangkat (untuk outlet F&B)

| key | Fitur | Frasa CTA aman |
|-----|-------|----------------|
| hardware_toko | Printer thermal, tablet, aksesori kasir | Lihat perangkat di toko & katalog Kekasir |
| print | Struk thermal BT/USB | Pasangkan printer thermal dengan kasir HP |

Landing: https://kekasir.id/toko · https://kekasir.id/toko/katalog  
Fokus perangkat **kasir F&B** (struk dapur/kasir), bukan scanner ritel minimarket sebagai tema utama.

## Enterprise & custom (F&B scale)

| key | Fitur | Frasa CTA aman |
|-----|-------|----------------|
| enterprise | Custom development F&B, white-label, SOP multi-outlet kuliner | Konsultasi Enterprise / custom POS F&B |

Landing: https://kekasir.id/enterprise  
Jangan samakan dengan paket Basic/Pro SaaS standar.

## Skala usaha F&B

| Skala | Ciri | Fokus fitur / CTA |
|-------|------|-------------------|
| Gerobak / PKL / bazar / kontainer / tanpa meja | Mobile, outdoor, sering offline | offline, qris, print, shift, Basic + trial |
| Usaha rumahan / katering / pre-order | Order chat, ambil sendiri | catalog_online, pre_order, qris, pos_core |
| Cafe / resto duduk | Meja, dapur, antrian | self_order_qr, kds, table_mgmt → Pro |
| Multi cabang / franchise F&B | Banyak outlet kuliner | multi_outlet, reports; enterprise jika custom |

## Scope

- **Hanya F&B.** Jangan feature_keys `appointment` / kasir jasa non-kuliner di artikel.
- Jangan artikel “aplikasi kasir barbershop / laundry / minimarket”.

## Aturan sebut plan

- Self-order QR meja, KDS, reservasi, meja advanced, kupon/diskon Pro → **sebut Pro** atau “tersedia di trial 14 hari (Pro)”.
- Usaha **tanpa meja / gerobak / bazar** → sudut **Basic** + QRIS + offline — jangan paksakan fitur meja.
- Hardware: `/toko` dan `/toko/katalog`, tanpa klaim stok/harga perangkat spesifik kecuali diverifikasi.
- Enterprise: custom / skala besar **F&B** — jangan hard-sell ke gerobak.
- Jangan bilang fitur Pro “sudah termasuk Basic”.
