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

COLOR_WORDS = (
    "deep navy blue, warm orange accent, soft sky blue, cream and soft peach ambient light, "
    "wood brown counters, teal or mint kitchen tiles, golden warm lamp light, clean white plates"
)

STYLE_LOCK = f"""
VISUAL STYLE TARGET (editorial F&B marketing illustration):
- Warm flat 2D vector illustration, soft painted fills, gentle shadows, friendly Indonesian UMKM mood
- DEFAULT = ONE coherent LIVED-IN SCENE: place + 1 main human + food/props + rich background atmosphere
- Character: stylized flat Indonesian F&B person (pemilik warung, koki, kasir, pelanggan) — simple face, no photorealism
- Foreground: main character + key action (writing, cooking, scanning, serving, checking tablet)
- Midground: food, ingredients, tools, counter, tablet/phone as story props
- Background MUST feel alive (never empty cream void): shelves with jars, hanging pans, menu board, steam, plants,
  window light, string lanterns, customers silhouette, street glimpse, tiled wall, fridge, spice rack, crates
- Depth layers: foreground / midground / background with soft atmospheric perspective
- Soft environmental lighting: warm lamp glow, window daylight, kitchen steam haze, evening warung lamps
- Palette by color names only (never write hex codes): {COLOR_WORDS}
- Full-bleed edge-to-edge art, no polaroid frame, no white border
- Optional subtle floating UI card or phone mock as a prop INSIDE the scene (small, secondary)

BACKGROUND / ATMOSPHERE (CRITICAL):
- Fill at least 40-60% of the canvas with environmental storytelling, not empty negative space
- Add 5–10 small background details that fit the place
- Soft gradients of wall color + furniture + props so the scene feels like a real dapur/warung/kafe
- Keep the main subject readable, but background must look inhabited and warm

ABSOLUTELY FORBIDDEN:
- Empty plain cream/beige background with only a person and a table floating in space
- Making EVERY image a flowchart / process diagram / numbered step cards / chevron arrows
- Icon grid or icon circle around a center object as the default composition
- ANY hex color codes or design-token strings visible as text on the image
- Writing color codes, design tokens, or hex labels on cards or arrows
- Photorealistic photos, stock faces, third-party logos, app-store badges
- Drawing kekasir watermark text (watermark applied later in post-process)
- Same generic icon-set recycled for every figure
""".strip()

SCENE_EXAMPLES = """
REFERENCE SCENE PATTERNS (DEFAULT style — like polished F&B blog illustrations):
1) Young owner at glowing wooden counter with nasi goreng + sate plates; open kitchen shelves and hanging utensils behind; soft floating UI bubbles secondary only
2) Woman in warm dapur writing recipe book while holding calculator phone; stove steam, pots, spice jars, chalkboard menu, stacked plates behind
3) Chef in busy dapur thinking with ingredients priced on table; hanging fish, rice sacks, pans on wall, simmering pot, window light
4) Cashier at evening warung with blue lanterns; food display shelves full of snacks/drinks; phone in hand; soft street night light outside

Each figure = different STORY moment + different room details. Background must feel occupied.
""".strip()


def _is_true_flow_section(section_heading: str, section_excerpt: str, alt: str) -> bool:
    """Only true system workflows may use diagram mode — not every HPP/tips section."""
    blob = f"{section_heading} {section_excerpt} {alt}".lower()
    flow_markers = (
        "alur kerja",
        "alur order",
        "alur pesanan",
        "alur sistem",
        "workflow",
        "cara kerja sistem",
        "urutan proses",
        "langkah-langkah sistem",
        "flow order",
        "order masuk ke dapur",
        "diagram alur",
        "alur dari kasir ke dapur",
    )
    false_friends = (
        "cara hitung",
        "cara naikkan",
        "cara tentukan",
        "tips",
        "checklist buka",
        "kesalahan umum",
        "kenapa",
        "manfaat",
    )
    if any(k in blob for k in false_friends) and not any(k in blob for k in flow_markers):
        return False
    return any(k in blob for k in flow_markers)


def _scene_for_topic(title: str, heading: str, alt: str, category: str) -> str:
    blob = f"{title} {heading} {alt}".lower()
    if any(k in blob for k in ("hpp", "margin", "harga jual", "biaya bahan", "resep", "hitung")):
        return (
            "warm Indonesian kitchen: owner/chef at prep table with ingredients, scale, notebook or calculator tablet; "
            "background shelves with spice jars, rice bowl, hanging utensils, stove steam, chalkboard menu, stacked plates"
        )
    if any(k in blob for k in ("qris", "bayar", "pembayaran", "scan qr", "self-order", "self order")):
        return (
            "cozy cafe or warung dining area: customer scanning QR at table, soft pendant lights, menu board, "
            "other tables with food, plants, window daylight, cashier counter visible in depth"
        )
    if any(k in blob for k in ("laporan", "omzet", "penjualan", "analisa", "grafik")):
        return (
            "owner behind a lively warung counter reviewing sales on phone/tablet; behind: food display shelves, "
            "lanterns or warm lamps, receipts, drink glasses, evening street glow outside"
        )
    if any(k in blob for k in ("dapur", "kds", "order dapur", "koki")):
        return (
            "busy kitchen depth: chef with tablet/order screen, steam, pans on wall, ingredients crates, "
            "pass window to dining area, warm stove light"
        )
    if any(k in blob for k in ("gerobak", "booth", "food truck", "bazar", "pop-up")):
        return (
            "street food cart or bazar booth at golden hour: seller, customers, umbrellas, hanging lights, "
            "smoke from grill, city street blur behind"
        )
    if any(k in blob for k in ("multi cabang", "multi-cabang", "franchise", "cabang")):
        return (
            "owner outdoors between two small storefronts or inside office with two outlet photos on wall, "
            "city/neighborhood atmosphere, plants, warm afternoon light"
        )
    if any(k in blob for k in ("stok", "inventori", "gudang", "bahan baku")):
        return (
            "stock room or kitchen storage: staff checking crates and shelves of ingredients with tablet, "
            "rice sacks, chili baskets, jars, fluorescent soft light"
        )
    if category == "ide-usaha":
        return (
            "aspirational F&B startup scene: new booth or small cafe opening, menu board, plants, "
            "street life and passersby, warm hopeful lighting"
        )
    if category == "info-produk":
        return (
            "modern warung counter with POS tablet while serving customer; shelves of drinks/snacks behind, "
            "soft ambient light, friendly bustle"
        )
    return (
        "Indonesian warung or cafe daily life with rich interior details matching the section topic: "
        "furniture, food displays, lighting, background activity"
    )


def thumbnail_prompt(title: str, category: str, persona: str = "") -> str:
    spec = IMAGE_SPECS["thumbnail"]
    persona_bit = f" Persona cue: {persona}." if persona else ""
    scene = _scene_for_topic(title, "", title, category)
    return f"""
ROLE: Blog featured illustration (editorial lived-in SCENE by default — not a diagram, not a photo).
FRAME: {spec['prompt_size_line']} — target {spec['width']}x{spec['height']} px.

Article topic: "{title}"
Category: {category}.{persona_bit}

DRAW THIS (SCENE DEFAULT):
- One strong human-centered SCENE: {scene}
- Rich environmental background (shelves, lights, food displays, steam, room depth) — not empty cream void
- Composition readable as a small card thumbnail
- Warm ambient lighting, deep navy + warm orange accents, soft sky blue secondary
- Optional tiny UI prop (phone/tablet chart) secondary only
- No title text required; if any label appears, max 3 short Indonesian words, never hex codes
- Do NOT make the thumbnail a flowchart unless the title explicitly says alur/workflow sistem

{SCENE_EXAMPLES}

{STYLE_LOCK}

Output: one full-bleed editorial scene illustration with lively atmosphere matching the article topic.
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
    focus = (alt or "").strip() or f"supporting scene about {title}"
    heading = (section_heading or "").strip() or "intro section"
    excerpt = (section_excerpt or "").strip()
    if len(excerpt) > 360:
        excerpt = excerpt[:360].rsplit(" ", 1)[0] + "…"
    place = (placement or "").strip() or "inline after related section"
    scene = _scene_for_topic(title, heading, focus, category)
    true_flow = _is_true_flow_section(heading, excerpt, focus)

    if true_flow:
        mode_block = (
            "MODE = OPTIONAL WORKFLOW VISUAL (allowed because this section is a true system alur). "
            "Prefer a gentle left-to-right STORYBOARD of 3 mini-scenes of people doing steps inside real rooms "
            "(dapur/warung), OR a simple clean flow with short Indonesian labels. "
            "Still avoid hex color codes, icon-only grids, and empty backgrounds. "
            "If a full flowchart would look sterile, fall back to one strong lived-in scene instead."
        )
        mode_name = "workflow_optional"
    else:
        mode_block = (
            "MODE = EDITORIAL SCENE (DEFAULT for almost all sections). "
            "Draw a human story scene with food + kitchen/warung environment. "
            "Do NOT draw flowchart, icon grid, numbered step cards, formula boxes, or comparison cards. "
            "Even if the topic is HPP / margin / harga / tips / checklist — still a SCENE "
            "(calculator/tablet/phone only as props in the room). "
            "Background must be detailed and atmospheric, never plain empty color."
        )
        mode_name = "editorial_scene"

    return f"""
ROLE: In-article supporting illustration for one article section.
FRAME: {spec['prompt_size_line']} — target {spec['width']}x{spec['height']} px.

Article: "{title}" ({category})
Figure {index} of {total}
Placement: {place}
Section heading: {heading}
Section context: {excerpt or focus}
Alt intent: {focus}
Feature context: {", ".join(feature_keys or []) or "F&B POS"}
Selected mode: {mode_name}

POLICY:
- Most figures = editorial scene illustrations (Indonesian F&B people in dapur/warung/kafe with food + devices + storytelling)
- Flow diagram is OPTIONAL and only when the section truly describes a system workflow/alur
- Never force every image to be a diagram

DRAW THIS:
- Primary scene idea: {scene}
- Make figure {index} unique vs other figures (different angle / character / room moment)
- Human + place + food/props first; tech device second
- Fill the room: shelves, utensils, lights, food displays, window/street depth, steam/atmosphere
- Soft cream walls OK only if covered by furniture/props/light — never empty void background
- Minimal text in image; short Indonesian words only if needed
- NEVER render hex color codes, design tokens, or #RRGGBB text

{mode_block}

{SCENE_EXAMPLES}

{STYLE_LOCK}

Output: one full-bleed illustration — usually a lived-in editorial scene; diagram only if mode allows and it truly helps.
""".strip()


def spec_for(role: str) -> dict[str, Any]:
    if role == "thumbnail":
        return IMAGE_SPECS["thumbnail"]
    return IMAGE_SPECS["supporting"]
