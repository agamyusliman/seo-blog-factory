#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

from image_style import IMAGE_SPECS

NAVY = (30, 58, 138)
ORANGE = (234, 88, 12)
SKY = (186, 230, 253)
BLUE = (14, 165, 233)
WARM = (255, 251, 245)
WHITE = (255, 255, 255)


def _seed(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient(size: tuple[int, int], c1: tuple[int, int, int], c2: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r, g, b = (_lerp(c1[i], c2[i], t) for i in range(3))
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render_thumbnail(out_path: Path, title: str, category: str) -> Path:
    spec = IMAGE_SPECS["thumbnail"]
    w, h = int(spec["width"]), int(spec["height"])
    img = gradient((w, h), WARM, SKY)
    d = ImageDraw.Draw(img)
    s = _seed(title + category)

    rounded_rect(d, (int(w * 0.04), int(h * 0.08), int(w * 0.42), int(h * 0.92)), 36, NAVY)
    d.ellipse((int(w * 0.30), int(h * 0.10), int(w * 0.52), int(h * 0.48)), fill=ORANGE)
    d.ellipse((int(w * 0.34), int(h * 0.16), int(w * 0.50), int(h * 0.44)), fill=NAVY)
    rounded_rect(d, (int(w * 0.48), int(h * 0.16), int(w * 0.94), int(h * 0.84)), 28, WHITE)
    rounded_rect(d, (int(w * 0.51), int(h * 0.22), int(w * 0.91), int(h * 0.78)), 20, (248, 250, 252))
    for i in range(5):
        y = int(h * 0.30) + i * int(h * 0.08)
        rounded_rect(d, (int(w * 0.54), y, int(w * 0.76), y + 18), 8, SKY if i % 2 == 0 else (226, 232, 240))
        rounded_rect(d, (int(w * 0.78), y, int(w * 0.88), y + 18), 8, ORANGE if i == 0 else BLUE)
    rounded_rect(d, (int(w * 0.54), int(h * 0.18), int(w * 0.66), int(h * 0.24)), 12, ORANGE)
    for i in range(8):
        x = int(w * 0.08) + (s + i * 47) % int(w * 0.22)
        y = int(h * 0.55) + (s // (i + 3) + i * 31) % int(h * 0.28)
        d.ellipse((x, y, x + 12, y + 12), fill=ORANGE if i % 2 == 0 else BLUE)

    out_path = out_path.with_suffix(".webp")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=int(spec["webp_quality"]), method=6)
    return out_path


def render_supporting(out_path: Path, title: str, index: int, alt: str) -> Path:
    spec = IMAGE_SPECS["supporting"]
    w, h = int(spec["width"]), int(spec["height"])
    variants = [(WARM, SKY), (SKY, WHITE), ((241, 245, 249), WARM)]
    c1, c2 = variants[(index - 1) % len(variants)]
    img = gradient((w, h), c1, c2)
    d = ImageDraw.Draw(img)
    s = _seed(f"{title}:{index}:{alt}")

    rounded_rect(d, (int(w * 0.06), int(h * 0.08), int(w * 0.94), int(h * 0.92)), 40, WHITE)
    rounded_rect(d, (int(w * 0.06), int(h * 0.08), int(w * 0.94), int(h * 0.20)), 40, NAVY)
    d.rectangle((int(w * 0.06), int(h * 0.18), int(w * 0.94), int(h * 0.21)), fill=ORANGE)

    mode = index % 5
    if mode == 1:
        for i in range(3):
            x0 = int(w * 0.12) + i * int(w * 0.26)
            rounded_rect(d, (x0, int(h * 0.28), x0 + int(w * 0.22), int(h * 0.78)), 24, (248, 250, 252))
            d.ellipse((x0 + 40, int(h * 0.34), x0 + 110, int(h * 0.46)), fill=NAVY if i != 1 else ORANGE)
            rounded_rect(d, (x0 + 20, int(h * 0.54), x0 + int(w * 0.18), int(h * 0.58)), 10, SKY)
    elif mode == 2:
        rounded_rect(d, (int(w * 0.12), int(h * 0.52), int(w * 0.88), int(h * 0.82)), 20, NAVY)
        for i in range(4):
            x = int(w * 0.16) + i * int(w * 0.17)
            rounded_rect(d, (x, int(h * 0.32), x + int(w * 0.12), int(h * 0.52)), 16, ORANGE if i % 2 == 0 else BLUE)
    elif mode == 3:
        for r in range(2):
            for c in range(3):
                x0 = int(w * 0.12) + c * int(w * 0.26)
                y0 = int(h * 0.28) + r * int(h * 0.28)
                rounded_rect(d, (x0, y0, x0 + int(w * 0.22), y0 + int(h * 0.22)), 20, (248, 250, 252))
                rounded_rect(d, (x0 + 16, y0 + 16, x0 + 90, y0 + 36), 8, ORANGE if (r + c) % 2 == 0 else BLUE)
    elif mode == 4:
        rounded_rect(d, (int(w * 0.36), int(h * 0.22), int(w * 0.64), int(h * 0.86)), 40, NAVY)
        rounded_rect(d, (int(w * 0.38), int(h * 0.26), int(w * 0.62), int(h * 0.82)), 28, WHITE)
        rounded_rect(d, (int(w * 0.41), int(h * 0.32), int(w * 0.59), int(h * 0.44)), 16, ORANGE)
        for i in range(4):
            y = int(h * 0.50) + i * int(h * 0.06)
            rounded_rect(d, (int(w * 0.42), y, int(w * 0.58), y + 20), 10, SKY if i % 2 == 0 else (226, 232, 240))
    else:
        rounded_rect(d, (int(w * 0.10), int(h * 0.30), int(w * 0.90), int(h * 0.80)), 24, (248, 250, 252))
        for i in range(5):
            x = int(w * 0.14) + i * int(w * 0.14)
            rounded_rect(d, (x, int(h * 0.38), x + int(w * 0.10), int(h * 0.68)), 14, NAVY if i % 2 == 0 else ORANGE)

    d.ellipse((w - 110, h - 110, w - 40, h - 40), fill=ORANGE)
    d.ellipse((w - 95, h - 95, w - 55, h - 55), fill=NAVY)

    out_path = out_path.with_suffix(".webp")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=int(spec["webp_quality"]), method=6)
    return out_path
