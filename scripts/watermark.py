#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image

from paths import ROOT

BRAND_DIR = ROOT / "assets" / "brand"
LOGO_SOURCE = BRAND_DIR / "logo-horizontal.png"


def logo_path() -> Path:
    if not LOGO_SOURCE.exists():
        raise FileNotFoundError(f"Logo PNG not found: {LOGO_SOURCE}")
    return LOGO_SOURCE


def apply_watermark(
    image_path: Path,
    *,
    opacity: float = 0.90,
    margin_ratio: float = 0.02,
    max_width_ratio: float = 0.13,
    position: str = "top-right",
) -> Path:
    if not image_path.exists():
        return image_path

    base = Image.open(image_path).convert("RGBA")
    bw, bh = base.size
    logo = Image.open(logo_path()).convert("RGBA")

    target_w = max(80, int(bw * max_width_ratio))
    scale = target_w / logo.width
    target_h = max(1, int(logo.height * scale))
    logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    if opacity < 1.0:
        alpha = logo.split()[-1].point(lambda p: int(p * opacity))
        logo.putalpha(alpha)

    margin = max(8, int(min(bw, bh) * margin_ratio))
    if position == "bottom-left":
        x, y = margin, bh - target_h - margin
    elif position == "bottom-right":
        x, y = bw - target_w - margin, bh - target_h - margin
    elif position == "top-left":
        x, y = margin, margin
    else:
        x, y = bw - target_w - margin, margin

    base.alpha_composite(logo, (x, y))
    out = base.convert("RGB")
    suffix = image_path.suffix.lower()
    if suffix == ".webp":
        out.save(image_path, "WEBP", quality=82, method=6)
    elif suffix in {".jpg", ".jpeg"}:
        out.save(image_path, "JPEG", quality=88, optimize=True)
    else:
        out.save(image_path, "PNG", optimize=True)
    return image_path


def apply_watermark_to_dir(img_dir: Path) -> list[str]:
    done = []
    if not img_dir.exists():
        return done
    for p in sorted(img_dir.iterdir()):
        if p.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg"}:
            apply_watermark(p)
            done.append(p.name)
    return done
