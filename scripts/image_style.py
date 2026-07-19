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
- Flat / modern editorial ILLUSTRATION or clean vector-style infographic
- Informative first: explain a concept, process, comparison, or checklist visually
- Soft shadows, rounded shapes, generous whitespace, SaaS marketing aesthetic
- Color system (Kekasir brand — use these hex values):
  - Navy primary: {BRAND["navy"]} (headings, main shapes, icons)
  - Orange accent: {BRAND["orange"]} (CTA, highlights, active steps)
  - Sky: {BRAND["sky"]} (soft backgrounds, cards)
  - Blue: {BRAND["blue"]} (secondary icons, arrows, links)
  - Warm cream bg: {BRAND["warm_bg"]} or clean white / light slate
  - Body text dark: {BRAND["slate"]}
- Typography in-image: short Indonesian labels only (2–6 words per label), clean sans-serif
- FORBIDDEN: photorealistic humans, stock photo faces, batik, third-party logos, app store badges
- FORBIDDEN: screenshot UI dashboard palsu dengan brand lain, foto kamera realistis
- FORBIDDEN: white picture frame / polaroid border around the art; full-bleed illustration to edges
- Do NOT draw kekasir watermark text in the scene (watermark applied in post-process)
- No cluttered meme style; keep professional F&B POS / UMKM SaaS look
""".strip()

CATEGORY_ILLUSTRATION = {
    "tips-bisnis": "infographic cards and simple process arrows about business tips",
    "ide-usaha": "idea board / startup F&B concept illustration with icons",
    "operasional": "operations flowchart: order → kitchen → payment → report",
    "info-produk": "product feature diagram: POS, QRIS, reports as icon modules",
    "inspirasi": "before/after digitalization illustration (manual notes → modern POS)",
}


def _detect_visual_mode(section_heading: str, section_excerpt: str, alt: str) -> str:
    blob = f"{section_heading} {section_excerpt} {alt}".lower()
    if any(
        k in blob
        for k in (
            "alur",
            "flow",
            "proses",
            "langkah",
            "cara kerja",
            "tahap",
            "workflow",
            "order masuk",
            "dari order",
            "step",
        )
    ):
        return "process_flow"
    if any(k in blob for k in ("banding", "vs", "basic", "pro", "paket", "harga", "perbandingan")):
        return "comparison"
    if any(k in blob for k in ("checklist", "daftar", "siapkan", "persiapan", "tips singkat")):
        return "checklist"
    if any(k in blob for k in ("hpp", "margin", "biaya", "hitung", "rumus", "persentase")):
        return "formula_diagram"
    if any(k in blob for k in ("qris", "bayar", "pembayaran", "settlement", "pencairan")):
        return "payment_flow"
    if any(k in blob for k in ("shift", "tutup kas", "selisih", "rekap")):
        return "shift_diagram"
    if any(k in blob for k in ("masalah", "tantangan", "solusi", "kendala", "error", "gagal")):
        return "problem_solution"
    return "concept_icons"


def _mode_instructions(mode: str) -> str:
    modes = {
        "process_flow": (
            "Draw a LEFT-TO-RIGHT or TOP-TO-BOTTOM process FLOW DIAGRAM with 3–6 numbered steps, "
            "rounded rectangles, navy→orange accent arrows, short Indonesian step labels. "
            "Looks like a product explainer, not a photo."
        ),
        "comparison": (
            "Two-column or side-by-side comparison cards (e.g. Basic vs Pro, manual vs digital) "
            "with checkmarks, navy headers, orange highlights."
        ),
        "checklist": (
            "Vertical checklist illustration with rounded cards, orange check icons, clear Indonesian items."
        ),
        "formula_diagram": (
            "Clean formula / HPP–margin diagram: boxes for bahan, porsi, harga jual, margin %; "
            "simple math visual, no messy handwriting photo."
        ),
        "payment_flow": (
            "Payment flow: customer → QRIS scan → konfirmasi → laporan; icons only, brand colors."
        ),
        "shift_diagram": (
            "Shift lifecycle diagram: buka shift → transaksi → tutup kas → selisih; numbered steps."
        ),
        "problem_solution": (
            "Split layout: left muted problem icons, right bright solution (POS / apps) with orange accent."
        ),
        "concept_icons": (
            "Hero illustration with 3–5 feature icons around a central POS/tablet motif, sky soft background."
        ),
    }
    return modes.get(mode, modes["concept_icons"])


def thumbnail_prompt(title: str, category: str, persona: str = "") -> str:
    spec = IMAGE_SPECS["thumbnail"]
    scene = CATEGORY_ILLUSTRATION.get(category, CATEGORY_ILLUSTRATION["tips-bisnis"])
    persona_bit = f" Audience: {persona}." if persona else ""
    return f"""
ROLE: BLOG THUMBNAIL / FEATURED ILLUSTRATION (not a photograph).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Topic: "{title}"
Category: {category}.{persona_bit}
Visual concept: {scene}, clearly related to the article topic (F&B POS / aplikasi kasir / point of sales).

THUMBNAIL composition:
- One strong central visual idea readable at small card size
- Optional short title-like label (max 5 words) in Indonesian if helpful
- Soft brand sky/warm background, navy + orange accents
- FULL-BLEED illustration edge-to-edge

{ILLUSTRATION_RULES}

Output: one polished brand illustration, full-bleed, no photo realism, no third-party brands.
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
    mode_help = _mode_instructions(mode)

    return f"""
ROLE: IN-ARTICLE SUPPORTING ILLUSTRATION for a specific article section (not photorealistic photo).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Article title: "{title}" (category: {category})
Figure index: {index} of {total}
Placement: {place}
Nearest section heading (H2/H3): {heading}
Section excerpt the visual must explain:
\"\"\"{excerpt or focus}\"\"\"

Alt / intent: {focus}
Feature context: {feats}
Detected visual mode: {mode}

SECTION-MATCH (CRITICAL):
- Illustration MUST teach THIS section's idea (flow, formula, checklist, comparison, or concept)
- If section describes a business process → use a clear FLOW / ALUR diagram with steps
- If section is about costs/HPP → formula or cost-structure diagram
- If section is about payment/QRIS → payment flow diagram
- Prefer informative diagrams over decorative scenery
- Short Indonesian labels on nodes only; no long paragraphs inside the image

MODE INSTRUCTIONS:
{mode_help}

{ILLUSTRATION_RULES}

Output: one full-bleed informative brand illustration matching the section, no photorealism, no third-party brands.
""".strip()


def spec_for(role: str) -> dict[str, Any]:
    if role == "thumbnail":
        return IMAGE_SPECS["thumbnail"]
    return IMAGE_SPECS["supporting"]
