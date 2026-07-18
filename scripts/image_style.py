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
        "aspect_label": "In-article photo (3:2)",
        "filename_pattern": "fig-{nn:02d}.webp",
        "webp_quality": 80,
        "prompt_size_line": "exact framing for 1200x800 px (3:2 landscape in-article)",
        "usage": "body markdown images",
    },
}

PHOTO_RULES = """
PHOTO REALISM RULES (MANDATORY):
- Photorealistic editorial photography ONLY (not cartoon, not flat illustration, not 3D render, not anime, not vector)
- Real human subjects with Indonesian faces (Southeast Asian / Nusantara features), natural skin tones
- Clothing ALWAYS varies per image: plain solid colors, polo, plain kemeja, kaos, apron dapur — NEVER batik, NEVER traditional batik motif
- Different outfit each generation so the series does not look copy-paste
- Indonesian F&B UMKM setting matching context: warung, cafe, resto kecil, dapur, gerobak, bazar, kontainer
- NO readable third-party logos, brand names, soft-drink logos, payment logos, fashion logos, app store badges
- NO cartoon mascot, clipart, plastic CGI look
- Keep faces and main subject inside SAFE ZONE (not cut by edges)
- Do NOT draw any kekasir watermark in the scene (watermark is applied later in post-process)
- FORBIDDEN: software UI screenshots, dashboard mockups, fake app screens, admin panel photos, product tutorial screenshots
- Prefer real physical scenes (people, food, kitchen, notes, cash) over digital screens

FULL-BLEED / NO FRAME (CRITICAL — never violate):
- Image MUST be full-bleed edge-to-edge: scene fills 100% of the canvas
- FORBIDDEN: white/gray/black border, picture frame, mat, polaroid edge, postcard margin, drop shadow around the photo, vignette that looks like a card on a background
- FORBIDDEN: photo floating on a blank canvas, mockup frame, laptop/phone frame unless the article is specifically about a device UI (even then fill the whole canvas)
- Background of the real scene must touch all four edges of the image
""".strip()

CATEGORY_SCENE = {
    "tips-bisnis": "Indonesian warung owner at counter reviewing notes and phone, warm afternoon light",
    "ide-usaha": "young Indonesian entrepreneur plating food in small kitchen startup space",
    "operasional": "busy Indonesian cafe counter, staff with POS tablet, natural indoor light",
    "info-produk": "Indonesian owner using tablet POS at clean modern warung/cafe counter (device screen blurred, no brand UI)",
    "inspirasi": "confident Indonesian F&B owner in small restaurant, soft natural documentary portrait",
}

CLOTHING_VARIANTS = [
    "plain navy polo shirt",
    "simple white crew-neck t-shirt under light gray apron",
    "solid charcoal short-sleeve work shirt",
    "plain olive green henley",
    "solid black polo with sleeves rolled",
    "light blue plain button shirt (no pattern)",
    "maroon plain t-shirt and beige half-apron",
    "solid cream shirt, no motifs",
]


def _clothing_line(index: int = 1) -> str:
    outfit = CLOTHING_VARIANTS[(max(1, index) - 1) % len(CLOTHING_VARIANTS)]
    return (
        f"Subject clothing this frame: {outfit}. "
        "Must differ from other images in the series. Absolutely no batik fabric or batik print."
    )


def thumbnail_prompt(title: str, category: str, persona: str = "") -> str:
    spec = IMAGE_SPECS["thumbnail"]
    scene = CATEGORY_SCENE.get(category, CATEGORY_SCENE["tips-bisnis"])
    persona_bit = f" Persona: {persona}." if persona else ""
    return f"""
ROLE: BLOG THUMBNAIL / FEATURED PHOTO (not an in-article figure).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Topic: "{title}"
Category: {category}.{persona_bit}
Hero scene: {scene}, clearly related to the article topic.

THUMBNAIL composition:
- Single strong focal subject readable at small card size
- Subject left/center; soft environmental depth on the right
- Natural bokeh background, not cluttered
- Important subject not glued to extreme edges (camera framing), but PHOTO IS FULL-BLEED (no empty frame border)
- ONE clear story moment — no collage

{_clothing_line(1)}

{PHOTO_RULES}

Output: one photorealistic FULL-BLEED landscape photo filling the entire frame edge-to-edge, no border, no mat, no caption text, no third-party brands.
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
    focus = (alt or "").strip() or f"supporting photo {index} about {title}"
    feats = ", ".join(feature_keys or []) or "F&B outlet operations"
    heading = (section_heading or "").strip() or "(intro / opening section)"
    excerpt = (section_excerpt or "").strip()
    if len(excerpt) > 420:
        excerpt = excerpt[:420].rsplit(" ", 1)[0] + "…"
    place = (placement or "").strip() or "inline after related section"
    return f"""
ROLE: IN-ARTICLE SUPPORTING PHOTO placed inside a specific article section (not the main og:image thumbnail).
SIZE / SEO FRAME: {spec['prompt_size_line']}
Target export: {spec['width']}x{spec['height']} px, aspect {spec['aspect']}.

Article title: "{title}" (category: {category})
Figure index: {index} of {total}
Placement in article: {place}
Nearest section heading (H2/H3): {heading}
Section excerpt / paragraph context the photo must match:
\"\"\"{excerpt or focus}\"\"\"

Photo purpose / alt intent (must match this section's redaction): {focus}
Feature context: {feats}

SECTION-MATCH RULES (CRITICAL):
- The photo MUST visually illustrate THIS section's topic and nearby paragraphs — not a random F&B stock scene
- If section is about counting HPP/costs: show writing notes, ingredients, calculator, comparing prices
- If section is about waste/susut/cadangan: show kitchen ingredients, leftover handling, careful portioning
- If section is about pricing/margin: show menu board / price thinking / comparing costs (no software UI)
- If section is about checklist/closing: show calm end-of-day review with notes
- Prefer physical real-world props over digital screens; NO app dashboard screenshots

SUPPORTING PHOTO rules:
- Documentary / explanatory, ONE clear idea
- Feels like content photography, not ad banner
- FULL-BLEED: scene touches all four edges — never a framed photo on a blank background

{_clothing_line(index)}

{PHOTO_RULES}

Output: one photorealistic FULL-BLEED landscape photo filling the entire canvas edge-to-edge, no border, no mat, no frame, no caption text, no third-party brands.
""".strip()


def spec_for(role: str) -> dict[str, Any]:
    if role == "thumbnail":
        return IMAGE_SPECS["thumbnail"]
    return IMAGE_SPECS["supporting"]
