#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from ai_client import chat, last_chat_model
from common import (
    count_words,
    load_catalog,
    load_config,
    now_iso,
    save_catalog,
    unique_slug,
)
from paths import CONTENT, CORPUS, ensure_dirs
from retrieve import format_context, retrieve
from validate_article import meta_from_body, validate_article

sys.path.insert(0, str(Path(__file__).resolve().parent))

SYSTEM = """Kamu penulis artikel blog Kekasir.id untuk pemilik usaha kuliner di Indonesia.

BAHASA (paling penting):
- Tulis Bahasa Indonesia yang natural, hidup, mudah dipahami warung/cafe — BUKAN terjemahan Inggris.
- JANGAN AI-slop: "Yuk mulai dari dasar", "Mari kita bedah", "Tanpa basa-basi", "di dunia F&B", "di era digital", "rahasia sukses".
- JANGAN istilah asing yang tidak lazim di lapangan: food cost, food costing, waste, buffer, markup (sebagai kata utama), bill of material, COGS, menu engineering, menu bintang, menu kuda pacu, menu teka-teki, menu beban, overhead (pakai "biaya operasional"), FIFO tanpa penjelasan.
- GANTI: food cost→biaya bahan/HPP; waste→sisa dapur/bahan terbuang/susut; buffer→cadangan/antisipasi susut; markup→pengali harga/naikkan dari HPP; menu engineering→evaluasi/analisa menu laris; menu bintang→menu andalan laris untung; kuda pacu→laris tapi untung tipis; teka-teki→untung tapi sepi; beban→sepi dan merugikan.
- Boleh & perbanyak alami: HPP, QRIS, omzet, margin, stok, shift, resep, porsi, promo, **aplikasi kasir**, **point of sales**, **POS**, sistem kasir.
- "F&B" jarang saja; utamakan "usaha kuliner/warung/cafe/restoran".
- Nada seperti orang lokal menjelaskan ke sesama pengusaha, bukan dosen atau brosur luar negeri.

LOKASI (anti-hoax):
- Keyword kota BOLEH: **Batam**, **Tanjungpinang** (opsional Kepri). Artinya: ada SaaS POS di kota itu — BUKAN klaim merchant spesifik.
- JANGAN sebut kelurahan/area dalam kota sebagai studi kasus: Nagoya, Batu Aji, Sekupang, Batam Centre, Harbour Bay, Lagoi, Tanjung Uban, Senggarang, dll.
- JANGAN klaim "usaha di [daerah] sudah pakai Kekasir". Boleh skenario hipotetis: "misalnya warung di Batam…", "contoh alur…".
- Ide usaha generik OK tanpa alamat fiktif.

SUDUT MASALAH → SOLUSI:
- Utamakan artikel yang menjawab masalah/tantangan operasional (nota berantakan, antrian, selisih kas, internet putus, HPP kacau, order dapur salah, dll.) lalu tawarkan solusi dengan aplikasi kasir / point of sales Kekasir.
- Pakai fakta FAQ: trial 14 hari Pro, Basic vs Pro, offline, self-order, KDS, shift, QRIS T+2, dll. tanpa mengarang.

ISI:
- ORIGINAL, jangan plagiat. Hanya usaha kuliner (bukan retail/jasa salon-laundry).
- 500–2000 kata (target 900–1400). Intro + min 4 H2 + bullet/list + CTA penutup.
- Gambar inline: tepat {n_images} buah, format ![alt deskriptif](images/fig-01.webp) … fig-0N.
- PENEMPATAN GAMBAR (wajib):
  - fig-01 setelah intro (sebelum H2 pertama).
  - fig-02… setelah H2 yang relevan (bukan diacak di akhir).
  - Alt text wajib deskriptif sesuai konteks section:
    * DEFAULT = ilustrasi scene editorial (orang di warung/dapur/kafe + makanan + props) yang mendukung cerita section.
    * HANYA jika section benar-benar menjelaskan alur sistem / workflow (mis. alur order kasir→dapur) → alt boleh sebut "diagram alur" / "alur".
    * Topik HPP / margin / harga / tips / checklist → TETAP scene (bukan diagram rumus), contoh: pemilik warung hitung bahan di dapur.
  - Contoh alt scene: "Ilustrasi pemilik warung menghitung bahan di dapur", "Suasana pelanggan scan QR meja di kafe".
  - Contoh alt diagram (opsional, hanya alur sistem): "Alur pesanan dari kasir ke dapur di restoran".
  - Jangan memaksa semua image jadi diagram — mayoritas scene, diagram hanya bila dibutuhkan.
  - Jangan menaruh semua gambar berurutan; sisipkan di tengah redaksi section terkait.
- Patuhi FAKTA PRODUK & LEGAL: Basic Rp60.000 / Pro Rp120.000 (tahunan Rp576.000 / Rp1.152.000), trial 14 hari Pro sekali per WA, QRIS ~0,7% tanpa markup Kekasir, settlement ~T+2 hari kerja.
- Self-order QR meja / KDS / reservasi = Pro (atau trial Pro).
- Jangan sebut brand payment gateway. Jangan klaim API GoFood/Grab otomatis.
- Jangan janji refund langganan bebas, refund QRIS otomatis, MDR dikembalikan, atau surcharge QRIS ke pelanggan.
- Jika sebut harga/QRIS/refund, boleh taut ke /syarat-ketentuan, /kebijakan-privasi, /kebijakan-refund.
- Internal link hanya [[link:slug|anchor]] ke RELATED_SLUGS.

PANDUAN BACKLINK (WAJIB):
- Setiap outlet punya katalog online otomatis (mirip Linktree F&B) di `kekasir.id/{slug-outlet}`: profil outlet + menu online + QR self-order + pickup order + bayar QRIS auto-confirm.
- Boleh sisipkan 1–2 backlink ke panduan Kekasir bila topik artikel berkaitan langsung. Format natural: "Pelajari [topik] di panduan Kekasir: https://kekasir.id/panduan/..." atau "Tonton video tutorial [topik]: https://www.youtube.com/watch?v=...".
- Jangan spam backlink. Hanya taut yang relevan dengan section.
- Panduan populer: setup QRIS (/panduan/owner/qris), kelola meja + QR self-order (/panduan/outlet/kelola-meja), konfigurasi bisnis outlet (/panduan/outlet/konfigurasi-bisnis), kelola produk (/panduan/outlet/kelola-produk), upgrade paket (/panduan/owner/upgrade-paket), inventori & HPP (/panduan/outlet/inventori-hpp), shift kasir (/panduan/outlet/shift-kasir), katalog & self-order (/panduan/outlet/pengaturan/katalog-self-order), staff & perangkat (/panduan/outlet/staff-perangkat), kupon & diskon (/panduan/outlet/kupon-diskon).
- Video YouTube: daftar owner (tLrLXU1Tklk), tambah outlet (kFDrN-VRrD0), upgrade paket (DcwUSF3yNIA), konfigurasi bisnis (gABYci3oQhg), kelola produk (IuBeR6ola0g), kelola meja (MMWQbmEIECw).

KATALOG ONLINE + SELF-ORDER EMPHASIS:
- Artikel yang bahas usaha rumahan / katering / bakery / pre-order / cloud kitchen → sebut katalog online sebagai "etalase digital" (slug custom, profil outlet, menu online, share ke IG/WA/TikTok).
- Artikel yang bahas cafe / resto duduk / antrian / peak hour → sebut self-order QR meja (Pro) + KDS dapur.
- Artikel yang bahas pembayaran / QRIS → sebut QRIS auto-confirm di self-order: pelanggan bayar dari HP, kasir langsung tercatat tanpa konfirmasi manual.
- Jangan bilang katalog online "gratis terpisah" — katalog online bawaan ekosistem Kekasir per outlet.
- Custom tema Linktree-style (banner, warna brand, sosmed) = Pro. Tema dasar bawaan semua paket.

- Primary keyword alami di title, intro, 1 H2 — jangan dipaksa tiap kalimat.
- Output HANYA markdown (boleh # title). Tanpa JSON, tanpa catatan meta.
"""


def related_slugs(catalog: dict[str, Any], category: str, limit: int = 5) -> list[str]:
    posts = catalog.get("posts") or []
    same = [p["slug"] for p in posts if p.get("category") == category and p.get("status") == "done"]
    other = [p["slug"] for p in posts if p.get("status") == "done" and p["slug"] not in same]
    return (same + other)[:limit]


def build_user_prompt(job: dict[str, Any], rag: str, related: list[str], n_images: int, target_words: int) -> str:
    outline = job.get("outline") or []
    outline_txt = "\n".join(f"- {x}" for x in outline) if outline else "(buat outline sendiri, min 4 H2)"
    return f"""Judul: {job['title']}
Slug: {job['slug']}
Kategori: {job['category']}
Persona: {job.get('persona') or 'umkm'}
Primary keyword: {job.get('primary_kw') or job['title']}
Feature keys CTA: {', '.join(job.get('feature_keys') or [])}
Jumlah gambar inline: {n_images}
Target kata: {target_words}
RELATED_SLUGS: {', '.join(related) if related else '(belum ada — skip internal link atau 0 link)'}
Outline:
{outline_txt}

{rag}

Tulis artikel lengkap sekarang.
Sisipkan tepat {n_images} gambar di section yang relevan:
![alt cocok section](images/fig-01.webp) … sampai fig-{n_images:02d}.webp
Alt = deskripsi ilustrasi pendukung sesuai konteks section:
- DEFAULT: scene editorial (orang di warung/dapur/kafe + makanan + props) yang mendukung cerita section
- DIAGRAM alur HANYA jika section benar-benar menjelaskan workflow sistem (alur order/kasir-dapur); topik HPP/margin/tips tetap scene
- Mayoritas scene, diagram opsional hanya bila dibutuhkan
- Bukan foto realistis, bukan "ilustrasi generik"
"""


def extract_image_placeholders(body: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", body)


def ensure_image_placeholders(body: str, n: int) -> str:
    existing = extract_image_placeholders(body)
    if len(existing) >= n:
        return body
    extra = []
    for i in range(len(existing) + 1, n + 1):
        extra.append(f"\n\n![Ilustrasi pendukung {i}](images/fig-{i:02d}.webp)\n")
    m = re.search(r"^## .+$", body, flags=re.M)
    if m:
        pos = m.end()
        return body[:pos] + "".join(extra) + body[pos:]
    return body + "".join(extra)


def resolve_internal_links(body: str) -> str:
    def repl(m: re.Match) -> str:
        slug, anchor = m.group(1), m.group(2)
        return f"[{anchor}](/blog/{slug})"

    return re.sub(r"\[\[link:([a-z0-9-]+)\|([^\]]+)\]\]", repl, body)


FEATURE_KW_LABELS = {
    "hpp_recipe": "HPP & resep",
    "inventory": "stok bahan",
    "reports": "laporan penjualan",
    "pos_core": "aplikasi kasir",
    "qris": "QRIS",
    "qris_self": "bayar QRIS",
    "self_order_qr": "self-order QR meja",
    "catalog_online": "menu digital",
    "theme": "tema katalog",
    "pickup": "order pickup",
    "kds": "KDS dapur",
    "table_mgmt": "manajemen meja",
    "split_bill": "pisah tagihan",
    "split_pay": "multi metode bayar",
    "multi_pay": "pembayaran multi metode",
    "shift": "shift kasir",
    "print": "struk thermal",
    "offline": "kasir offline",
    "multi_outlet": "multi cabang",
    "tax": "pajak PB1",
    "expense": "pengeluaran",
    "combo": "paket combo",
    "pre_order": "pre-order",
    "reservation": "reservasi meja",
    "customer_display": "layar pelanggan",
    "hardware_toko": "perangkat kasir",
    "enterprise": "enterprise",
    "trial": "coba gratis 14 hari",
    "pricing": "harga paket",
    "ai_menu": "import menu foto",
    "hold_order": "parkir order",
    "refund": "refund",
}

CATEGORY_KW = {
    "tips-bisnis": ["tips bisnis UMKM", "usaha kuliner"],
    "ide-usaha": ["ide usaha kuliner", "modal kecil"],
    "operasional": ["operasional kasir", "outlet F&B"],
    "info-produk": ["aplikasi kasir Kekasir", "fitur kasir"],
    "inspirasi": ["inspirasi usaha", "studi kasus kuliner"],
}


def build_keywords(job: dict[str, Any]) -> dict[str, Any]:
    primary = (job.get("primary_kw") or job.get("title") or "").strip()
    supporting: list[str] = []
    seen: set[str] = set()

    def add(label: str) -> None:
        lab = (label or "").strip()
        if not lab:
            return
        key = lab.lower()
        if key in seen:
            return
        if primary and key == primary.lower():
            return
        seen.add(key)
        supporting.append(lab)

    for fk in job.get("feature_keys") or []:
        add(FEATURE_KW_LABELS.get(fk, fk.replace("_", " ")))
    for lab in CATEGORY_KW.get(job.get("category") or "", []):
        add(lab)
    persona = (job.get("persona") or "").strip()
    if persona:
        add(persona)
    for lab in ("margin menu", "biaya bahan", "omzet warung"):
        add(lab)

    return {
        "primary": primary,
        "supporting": supporting[:12],
        "all": ([primary] if primary else []) + supporting[:12],
    }


def write_article(job: dict[str, Any], body: str, cfg: dict[str, Any]) -> Path:
    cat = job["category"]
    slug = job["slug"]
    folder = CONTENT / cat / slug
    img_dir = folder / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    body = resolve_internal_links(body)
    mm = meta_from_body(job["title"], body)
    n_images = int(job.get("n_images") or cfg.get("default_inline_images") or 3)
    figs = extract_image_placeholders(body)
    keywords = build_keywords(job)
    meta = {
        "id": job.get("id"),
        "title": job["title"],
        "slug": slug,
        "category": cat,
        "tags": job.get("feature_keys") or [],
        "keywords": keywords,
        "excerpt": mm["excerpt"],
        "meta_title": f"{job['title']} | Kekasir",
        "meta_description": mm["excerpt"][:160],
        "word_count": mm["word_count"],
        "read_minutes": mm["read_minutes"],
        "status": "text_done",
        "cta": {
            "feature_keys": job.get("feature_keys") or [],
            "primary_url": (cfg.get("cta_urls") or {}).get("register"),
            "secondary_url": (cfg.get("cta_urls") or {}).get("pricing"),
        },
        "images": {
            "thumbnail": "images/thumbnail.webp",
            "inline": [{"file": f, "alt": ""} for f in figs],
        },
        "internal_links": re.findall(r"\(/blog/([a-z0-9-]+)\)", body),
        "primary_kw": job.get("primary_kw"),
        "persona": job.get("persona"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "model": last_chat_model() or os.environ.get("AI_CHAT_MODEL", "grok-4.5"),
        "n_images": n_images,
    }
    front = (
        f"---\ntitle: {json.dumps(job['title'], ensure_ascii=False)}\n"
        f"slug: {slug}\ncategory: {cat}\nstatus: text_done\n"
        f"word_count: {mm['word_count']}\n---\n\n"
    )
    if not body.lstrip().startswith("#"):
        body = f"# {job['title']}\n\n{body}"
    (folder / "article.md").write_text(front + body, encoding="utf-8")
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return folder


def update_catalog_entry(job: dict[str, Any], folder: Path, word_count: int, status: str = "text_done") -> None:
    cat = load_catalog()
    slug = job["slug"]
    posts = [p for p in (cat.get("posts") or []) if p.get("slug") != slug]
    posts.append(
        {
            "title": job["title"],
            "slug": slug,
            "category": job["category"],
            "path": f"content/{job['category']}/{slug}/",
            "status": status,
            "thumbnail": f"content/{job['category']}/{slug}/images/thumbnail.webp",
            "word_count": word_count,
            "internal_links": [],
        }
    )
    cat["posts"] = posts
    slugs = set(cat.get("slugs") or [])
    slugs.add(slug)
    cat["slugs"] = sorted(slugs)
    counts: dict[str, int] = {}
    for p in posts:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    for c in cat.get("categories") or []:
        c["count"] = counts.get(c["slug"], 0)
    if not cat.get("categories"):
        cfg = load_config()
        cat["categories"] = [
            {"slug": c["slug"], "name": c["name"], "count": counts.get(c["slug"], 0)}
            for c in (cfg.get("categories") or [])
        ]
    save_catalog(cat)


def generate_one(job: dict[str, Any], skip_validate: bool = False) -> dict[str, Any]:
    ensure_dirs()
    cfg = load_config()
    min_w = int(cfg.get("min_words") or 500)
    max_w = int(cfg.get("max_words") or 2000)
    target = int(cfg.get("target_words") or 1100)
    n_images = int(job.get("n_images") or cfg.get("default_inline_images") or 3)
    catalog = load_catalog()
    existing = set(catalog.get("slugs") or [])
    if job["slug"] in existing and (CONTENT / job["category"] / job["slug"] / "article.md").exists():
        return {"ok": False, "error": "slug_exists", "slug": job["slug"]}

    hits = retrieve(
        f"{job['title']} {job.get('primary_kw') or ''} bahasa lokal HPP biaya bahan sisa dapur "
        f"syarat ketentuan refund qris 0,7 settlement faq trial grace 14 hari",
        k=10,
        feature_keys=job.get("feature_keys") or [],
        category=job.get("category"),
    )
    rag = format_context(hits)
    related = related_slugs(catalog, job["category"])
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": build_user_prompt(job, rag, related, n_images, target)},
    ]
    body = chat(messages, temperature=0.65)
    body = body.strip()
    if body.startswith("```"):
        body = re.sub(r"^```(?:markdown|md)?\n?", "", body)
        body = re.sub(r"\n?```$", "", body)
    body = ensure_image_placeholders(body, n_images)

    errors = [] if skip_validate else validate_article(
        body, min_words=min_w, max_words=max_w, catalog_slugs=set(related) | existing
    )
    # allow unknown link warnings only as soft — strip hard fail for unknown if no related
    errors = [e for e in errors if not e.startswith("unknown_internal_slug")]

    if errors and not skip_validate:
        fix = (
            "Perbaiki artikel berikut agar memenuhi:\n- "
            + "\n- ".join(errors)
            + "\n\n---\n"
            + body
        )
        body = chat(
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": build_user_prompt(job, rag, related, n_images, target)},
                {"role": "assistant", "content": body},
                {"role": "user", "content": fix},
            ],
            temperature=0.4,
        ).strip()
        body = ensure_image_placeholders(body, n_images)
        errors = validate_article(body, min_words=min_w, max_words=max_w)
        errors = [e for e in errors if not e.startswith("unknown_internal_slug")]

    folder = write_article(job, body, cfg)
    wc = count_words(body)
    update_catalog_entry(job, folder, wc, status="text_done" if not errors else "needs_review")
    pub = CORPUS / "published" / f"{job['slug']}.md"
    pub.parent.mkdir(parents=True, exist_ok=True)
    pub.write_text(
        f"# {job['title']}\n\ncategory: {job['category']}\nfeatures: {', '.join(job.get('feature_keys') or [])}\n\n{body[:1500]}\n",
        encoding="utf-8",
    )
    return {
        "ok": len(errors) == 0,
        "slug": job["slug"],
        "path": str(folder),
        "word_count": wc,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--category", default="tips-bisnis")
    ap.add_argument("--feature-keys", default="pos_core,trial")
    ap.add_argument("--primary-kw", default="")
    ap.add_argument("--persona", default="umkm")
    ap.add_argument("--job-json", default="")
    ap.add_argument("--skip-validate", action="store_true")
    args = ap.parse_args()

    if args.job_json:
        job = json.loads(Path(args.job_json).read_text(encoding="utf-8"))
    else:
        if not args.title:
            print("need --title or --job-json", file=sys.stderr)
            return 2
        catalog = load_catalog()
        existing = set(catalog.get("slugs") or [])
        slug = args.slug or unique_slug(args.title, existing)
        job = {
            "id": "manual",
            "title": args.title,
            "slug": slug,
            "category": args.category,
            "feature_keys": [x.strip() for x in args.feature_keys.split(",") if x.strip()],
            "primary_kw": args.primary_kw or args.title.lower(),
            "persona": args.persona,
            "outline": [],
        }
    result = generate_one(job, skip_validate=args.skip_validate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
