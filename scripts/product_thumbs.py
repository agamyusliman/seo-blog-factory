#!/usr/bin/env python3
"""Generate square 1:1 product thumbnails for the Kekasir demo outlets.

For each product it asks a text-to-image model for a single dish/drink on a
plain studio background, then resizes to a small WebP thumbnail. The prompt is
built per outlet so the two demo tenants look different (each has its own
background colour), and per category so a coffee does not get a rice-plate
prompt.

The generated file is written to <out-dir>/<sku>.webp. Uploading and attaching
to products is a separate step (see --upload), so a generation run can be
inspected before anything touches the demo data.

Usage:
    python scripts/product_thumbs.py --out /tmp/thumbs
    python scripts/product_thumbs.py --out /tmp/thumbs --only DB-AYM-001
    python scripts/product_thumbs.py --out /tmp/thumbs --upload --base-url ...
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

API_BASE = os.environ.get("IMG_API_BASE", "https://inferenesia.cloud/v1")
API_KEY = os.environ.get("IMG_API_KEY", "")
MODEL = os.environ.get("IMG_MODEL", "hunyuan-image-v3.0-art")

# Square, small: these render at 64–96 CSS px in the cashier grid.
THUMB_SIZE = 256
WEBP_QUALITY = 82

# Per-outlet studio backdrop. The demo brief asks for the same framing with a
# different theme per outlet, so this is the only thing that changes visually.
OUTLET_STYLE = {
    "tenant_dmpro1": {
        "bg": "warm cream (#F6EFE3) seamless studio backdrop",
        "note": "warm restaurant lighting, subtle amber tone",
    },
    "tenant_dmbas1": {
        "bg": "cool light grey (#EEF1F4) seamless studio backdrop",
        "note": "bright dimsum-house lighting, clean neutral tone",
    },
}

# Category-specific subject hints keep the prompt honest: the product name
# alone would make "Kopi O" and "Es Kopi Pandan" render the same cup.
CATEGORY_HINT = {
    "Kopi": "a single glass of coffee, garnish matching the name",
    "Minuman": "a single glass of the drink, condensation on the glass",
    "Ayam & Nasi": "a plated chicken rice dish, one portion",
    "Rice Bowl": "a rice bowl with toppings, one portion",
    "Lauk & Camilan": "a small plate of the side dish, one portion",
    "Dimsum Kukus": "a bamboo steamer basket of steamed dimsum",
    "Dimsum Goreng": "a plate of fried dimsum, one portion",
    "Camilan": "a small plate of the snack, one portion",
    "Saus Tambahan": "a small sauce bowl, one portion",
    "Paket Hemat": "a set meal with the items plated together",
    "Paket": "a set meal with the items plated together",
}


def prompt_for(product: dict, style: dict) -> str:
    hint = CATEGORY_HINT.get(product["category"], "the dish, one portion")
    return (
        f"Professional food photography of {product['name']}: {hint}. "
        f"Centered composition, {style['bg']}, {style['note']}, "
        "soft even shadow, no text, no logo, no hands, no people, "
        "square 1:1 framing, appetizing, high detail"
    )


def request_image(prompt: str, size: int = THUMB_SIZE) -> bytes:
    payload = json.dumps(
        {"model": MODEL, "prompt": prompt, "n": 1, "size": f"{size}x{size}"}
    ).encode()
    req = urllib.request.Request(
        f"{API_BASE}/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read())
    # Accept either a URL or inline base64; providers differ.
    item = (body.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=120) as img:
            return img.read()
    raise RuntimeError(f"no image in response: {str(body)[:200]}")


def to_thumb(raw: bytes) -> bytes:
    """Centre-crop to a square and encode a small WebP."""
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    side = min(im.size)
    left = (im.width - side) // 2
    top = (im.height - side) // 2
    im = im.crop((left, top, left + side, top + side))
    im = im.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
    return out.getvalue()


def load_products(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", default="scripts/products.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    if not API_KEY:
        print("IMG_API_KEY is not set", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    products = load_products(args.products)
    if args.only:
        wanted = set(args.only)
        products = [p for p in products if p["sku"] in wanted]

    done, failed = 0, []
    for p in products:
        style = OUTLET_STYLE.get(p["tenant"], next(iter(OUTLET_STYLE.values())))
        target = os.path.join(args.out, f"{p['sku']}.webp")
        if os.path.exists(target) and os.path.getsize(target) > 0:
            print(f"skip  {p['sku']:14} {p['name']} (exists)")
            done += 1
            continue
        prompt = prompt_for(p, style)
        for attempt in range(1, args.retries + 1):
            try:
                raw = request_image(prompt)
                data = to_thumb(raw)
                with open(target, "wb") as fh:
                    fh.write(data)
                print(f"ok    {p['sku']:14} {p['name']}  {len(data)//1024}kB")
                done += 1
                break
            except Exception as exc:  # noqa: BLE001 - report and retry
                last = str(exc)[:160]
                print(f"retry {p['sku']:14} attempt {attempt}: {last}", file=sys.stderr)
                time.sleep(2 * attempt)
        else:
            failed.append((p["sku"], p["name"], last))

    print(f"\n{done}/{len(products)} generated")
    if failed:
        print("failed:")
        for sku, name, err in failed:
            print(f"  {sku} {name}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
