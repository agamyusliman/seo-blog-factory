#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

BRAND = {
    "navy": "#1E3A8A",
    "orange": "#EA580C",
    "sky": "#BAE6FD",
    "blue": "#0EA5E9",
    "warm_bg": "#FFFBF5",
    "slate": "#1E293B",
    "slate_body": "#334155",
    "wa": "#25D366",
}

IMAGE_SPECS: dict[str, dict[str, Any]] = {
    "thumbnail": {
        "role": "thumbnail",
        "width": 1200,
        "height": 630,
        "aspect": "1.91:1",
        "aspect_label": "Open Graph / featured image",
        "filename": "thumbnail.webp",
        "webp_quality": 82,
        "prompt_size_line": "exact framing for 1200x630 px (1.91:1 landscape Open Graph)",
        "usage": "og:image, listing card, article hero",
    },
    "supporting": {
        "role": "supporting",
        "width": 1200,
        "height": 800,
        "aspect": "3:2",
        "aspect_label": "In-article illustration (3:2)",
        "filename_pattern": "fig-{nn:02d}.webp",
        "webp_quality": 80,
        "prompt_size_line": "exact framing for 1200x800 px (3:2 landscape in-article)",
        "usage": "body markdown images",
    },
}

ILLUSTRATION_RULES = f"""
ILLUSTRATION STYLE (MANDATORY — NOT photorealistic photos):
- Flat / modern editorial ILLUSTRATION — scene-style by default, diagram-style only when the section is explicitly a process/flow
- Soft shadows, rounded shapes, generous whitespace, SaaS marketing aesthetic
- Color system (Kekasir brand — use these hex values):
  - Navy primary: {BRAND["navy"]} (headings, main shapes, icons)
  - Orange accent: {BRAND["orange"]} (CTA, highlights, active steps)
  - Sky: {BRAND["sky"]} (soft backgrounds, cards)
  - Blue: {BRAND["blue"]} (secondary icons, arrows, links)
  - Warm cream bg: {BRAND["warm_bg"]} or clean white / light slate
  - Body text dark: {BRAND["slate"]}
- Human figures: stylized flat illustrations only (no realistic faces), simple shapes, diverse Indonesian F&B operators (kasir, koki, pemilik warung, pelanggan)
- Scene objects: warung/kafe/dapur/meja/QR meja/tablet kasir/gerobak — simplified flat icons + shapes, not photorealistic
- Typography in-image (only if diagram mode): short Indonesian labels (2–6 words per label), clean sans-serif
- For scene illustrations: minimal or no text in image — let the scene speak
- FORBIDDEN: photorealistic humans, stock photo faces, batik, third-party logos, app store badges
- FORBIDDEN: screenshot UI dashboard palsu dengan brand lain, foto kamera realistis
- FORBIDDEN: white picture frame / polaroid border around the art; full-bleed illustration to edges
- FORBIDDEN: forcing every image to be a flowchart/diagram — scene illustrations are equally valid
- Do NOT draw kekasir watermark text in the scene (watermark applied in post-process)
- No cluttered meme style; keep professional F&B POS / UMKM SaaS look
""".strip()

CATEGORY_SCENE = {
    "tips-bisnis": "pemilik warung/kafe sedang menganalisa laporan di meja kasir tablet",
    "ide-usaha": "konsep usaha F&B baru — gerobak/booth/kafe dengan menu dan pelanggan",
    "operasional": "suasana dapur dan kasir warung yang tertata rapi",
    "info-produk": "tablet kasir POS Kekasir menampilkan menu dan transaksi",
    "inspirasi": "transisi warung manual menjadi warung digital modern",
}

DIAGRAM_KEYWORDS = (
    "alur",
    "flow",
    "workflow",
    "cara kerja",
    "tahap",
    "step by step",
    "langkah-langkah",
    "proses ",
    "order masuk",
    "dari order",
    "urutan proses",
)

COMPARISON_KEYWORDS = (
    "banding",
    " vs ",
    "basic vs pro",
    "paket basic",
    "paket pro",
    "perbandingan paket",
    "manual vs digital",
    "manual vs aplikasi",
)

CHECKLIST_KEYWORDS = (
    "checklist",
    "daftar siapkan",
    "persiapan awal",
    "tips singkat",
    "yang harus disiapkan",
)

FORMULA_KEYWORDS = (
    "rumus hpp",
    "rumus margin",
    "hitung hpp",
    "formula hpp",
    "perhitungan hpp",
    "cara hitung hpp",
    "rumus harga jual",
)

PAYMENT_FLOW_KEYWORDS = (
    "alur qris",
    "flow qris",
    "qris auto confirm",
    "settlement qris",
    "pencairan qris",
    "alur pembayaran qris",
)

SHIFT_FLOW_KEYWORDS = (
    "alur shift",
    "buka shift",
    "tutup kas",
    "tutup shift",
    "rekap shift",
    "selisih kas",
)


def _detect_visual_mode(section_heading: str, section_excerpt: str, alt: str) -> str:
    blob = f"{section_heading} {section_excerpt} {alt}".lower()
    if any(k in blob for k in DIAGRAM_KEYWORDS):
        return "process_flow"
    if any(k in blob for k in PAYMENT_FLOW_KEYWORDS):
        return "payment_flow"
    if any(k in blob for k in SHIFT_FLOW_KEYWORDS):
        return "shift_diagram"
    if any(k in blob for k in FORMULA_KEYWORDS):
        return "formula_diagram"
    if any(k in blob for k in COMPARISON_KEYWORDS):
        return "comparison"
    if any(k in blob for k in CHECKLIST_KEYWORDS):
        return "checklist"
    return "scene_illustration"


def _mode_instructions(mode: str, section_heading: str, section_excerpt: str, title: str) -> str:
    modes = {
        "process_flow": (
            "Draw a LEFT-TO-RIGHT or TOP-TO-BOTTOM process FLOW DIAGRAM with 3–6 numbered steps, "
            "rounded rectangles, navy→orange accent arrows, short Indonesian step labels. "
            "Looks like a product explainer, not a photo. Only use this when the section explicitly describes a process/workflow."
        ),
        "comparison": (
            "Two-column or side-by-side comparison cards (e.g. Basic vs Pro, manual vs digital) "
            "with checkmarks, navy headers, orange highlights. Only use this when the section explicitly compares two options."
        ),
        "checklist": (
            "Vertical checklist illustration with rounded cards, orange check icons, clear Indonesian items. "
            "Only use this when the section is explicitly a preparation/checklist list."
        ),
        "formula_diagram": (
            "Clean formula / HPP–margin diagram: boxes for bahan, porsi, harga jual, margin %; "
            "simple math visual, no messy handwriting photo. Only use this when the section explicitly shows a formula/calculation."
        ),
        "payment_flow": (
            "Payment flow: customer → QRIS scan → konfirmasi → laporan; icons only, brand colors. "
            "Only use this when the section explicitly describes QRIS/payment flow."
        ),
        "shift_diagram": (
            "Shift lifecycle diagram: buka shift → transaksi → tutup kas → selisih; numbered steps. "
            "Only use this when the section explicitly describes shift opening/closing flow."
        ),
        "scene_illustration": (
            f"Draw a SUPPORTING SCENE ILLUSTRATION that matches the topic/activity of this section. "
            f"The scene should visually represent the situation or context described — NOT a diagram. "
            f"Examples of scene types: warung/kafe interior with kasir + pelanggan, koki di dapur memasak, "
            f"pemilik warung menganalisa laporan di tablet, bahan baku dapur tertata, pelanggan scan QR meja, "
            f"staf mencatat stok gudang, gerobak kuliner di lokasi, booth bazar ramai. "
            f"Pick a scene that naturally fits this section's topic: \"{section_heading or title}\". "
            f"Use flat stylized human figures (no realistic faces), simple shapes, brand colors. "
            f"Minimal or no text in image. NO flowchart, NO boxes-and-arrows, NO checklist cards — "
            f"this is a NARRATIVE scene illustration that supports the section's story."
        ),
    }
    return modes.get(mode, modes["scene_illustration"])


def thumbnail_prompt(title: str, category: str, persona: str = "") -> str:
    spec = IMAGE_SPECS["thumbnail"]
    scene = CATEGORY_SCENE.get(category, CATEGORY_SCENE["tips-bisnis"])
    persona_bit = f" Audience context: {persona}." if persona else ""
    return f"""
ROLE: BLOG THUMBNAIL / FEATURED ILLUSTRATION (not a photograph).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Topic: "{title}"
Category: {category}.{persona_bit}

THUMBNAIL composition — SCENE-style by default:
- Draw ONE supporting scene illustration that visually represents the article topic
- Scene example for this category: {scene}
- Adapt the scene to the specific article title above (e.g. if title is about HPP, show pemilik warung menghitung bahan di dapur; if about QRIS, show pelanggan scan QR meja; if about multi-cabang, show 2–3 outlet kecil)
- One strong central visual idea readable at small card size
- NO flowchart/diagram boxes-and-arrows — this is a scene illustration (unless the title explicitly says "alur" / "flow" / "cara kerja sistem")
- Optional short Indonesian label (max 4 words) if it strengthens the visual — otherwise no text
- Soft brand sky/warm background, navy + orange accents
- FULL-BLEED illustration edge-to-edge

{ILLUSTRATION_RULES}

Output: one polished brand scene illustration, full-bleed, no photo realism, no third-party brands.
""".strip()


def supporting_prompt(
    title: str,
    category: str,
    index: int,
    total: int,
    alt: str,
    feature_keys: list[str] | None = None,
    section_heading: str = "",
    section_excerpt: str = "",
    placement: str = "",
) -> str:
    spec = IMAGE_SPECS["supporting"]
    focus = (alt or "").strip() or f"supporting illustration {index} about {title}"
    feats = ", ".join(feature_keys or []) or "F&B POS operations"
    heading = (section_heading or "").strip() or "(intro / opening section)"
    excerpt = (section_excerpt or "").strip()
    if len(excerpt) > 420:
        excerpt = excerpt[:420].rsplit(" ", 1)[0] + "…"
    place = (placement or "").strip() or "inline after related section"
    mode = _detect_visual_mode(heading, excerpt, focus)
    mode_help = _mode_instructions(mode, heading, excerpt, title)

    return f"""
ROLE: IN-ARTICLE SUPPORTING ILLUSTRATION for a specific article section (not photorealistic photo).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Article title: "{title}" (category: {category})
Figure index: {index} of {total}
Placement: {place}
Nearest section heading (H2/H3): {heading}
Section excerpt the visual must relate to:
\"\"\"{excerpt or focus}\"\"\"

Alt / intent: {focus}
Feature context: {feats}
Detected visual mode: {mode}

SECTION-MATCH (CRITICAL):
- DEFAULT = scene illustration that matches the section's topic/activity (warung scene, dapur scene, kasir scene, etc.)
- ONLY use a diagram (flowchart / checklist / formula / comparison / payment-flow / shift-flow) when the section EXPLICITLY describes that process — keywords like "alur", "langkah-langkah", "rumus", "checklist", "vs", "perbandingan paket"
- If the section is informational/conceptual (e.g. "Kenapa HPP harus dihitung", "Kesalahan umum", "Tips singkat") → draw a SCENE illustration that supports the narrative, NOT a diagram
- Scene examples: pemilik warung bingung di kasir, koki menimbang bahan, pelanggan scan QR meja, staf cek stok gudang, gerobak kuliner ramai
- Short Indonesian labels ONLY when diagram mode; scene illustrations should have minimal/no text

MODE INSTRUCTIONS:
{mode_help}

{ILLUSTRATION_RULES}

Output: one full-bleed brand illustration matching the section's nature (scene OR diagram, never photorealism, never third-party brands).
""".strip()


def spec_for(role: str) -> dict[str, Any]:
    if role == "thumbnail":
        return IMAGE_SPECS["thumbnail"]
    return IMAGE_SPECS["supporting"]
