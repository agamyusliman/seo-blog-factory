#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ai_client import generate_image_b64, save_image_b64
from common import heartbeat, load_config, load_state, now_iso, save_state
from image_style import IMAGE_SPECS, supporting_prompt, thumbnail_prompt
from local_brand_image import render_supporting, render_thumbnail
from paths import CONTENT, ensure_dirs
from watermark import apply_watermark

sys.path.insert(0, str(Path(__file__).resolve().parent))


def article_folder(category: str, slug: str) -> Path:
    return CONTENT / category / slug


def load_meta(folder: Path) -> dict[str, Any]:
    return json.loads((folder / "meta.json").read_text(encoding="utf-8"))


def save_meta(folder: Path, meta: dict[str, Any]) -> None:
    meta["updated_at"] = now_iso()
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bump_image_counter(n: int = 1) -> None:
    st = load_state()
    st.setdefault("counters", {})
    st["counters"]["images_today"] = st["counters"].get("images_today", 0) + n
    save_state(st)


def clear_article_images(img_dir: Path) -> None:
    if not img_dir.exists():
        return
    for p in img_dir.iterdir():
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            p.unlink()


def normalize_fig_matches(body: str, n: int) -> list[tuple[str, str, str]]:
    found = re.findall(r"!\[([^\]]*)\]\((images/([^)]+))\)", body)
    if found:
        return [(a, b, c) for a, b, c in found]
    return [
        (f"Ilustrasi pendukung {i}", f"images/fig-{i:02d}.webp", f"fig-{i:02d}.webp")
        for i in range(1, n + 1)
    ]


def extract_figure_contexts(body: str) -> list[dict[str, Any]]:
    if not body:
        return []
    text = re.sub(r"^---[\s\S]*?---\s*", "", body.strip())
    pattern = re.compile(r"!\[([^\]]*)\]\((images/[^)]+)\)")
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    contexts: list[dict[str, Any]] = []
    for i, m in enumerate(matches):
        start, end = m.start(), m.end()
        before = text[:start]
        after = text[end:]
        heads = list(re.finditer(r"^(#{2,3})\s+(.+)$", before, flags=re.M))
        if heads:
            h = heads[-1]
            section_heading = h.group(2).strip()
            section_body = before[h.end() :].strip()
            placement = f"inside/after section «{section_heading}»"
        else:
            section_heading = "Pembuka / intro artikel"
            section_body = before.strip()
            placement = "after intro, before first H2"

        after_para = ""
        next_heading = ""
        for line in after.splitlines():
            s = line.strip()
            if not s:
                if after_para:
                    break
                continue
            if s.startswith("#"):
                if s.startswith("##"):
                    next_heading = re.sub(r"^#+\s*", "", s).strip()
                break
            if s.startswith("!["):
                break
            after_para += (" " if after_para else "") + s
            if len(after_para) > 220:
                break

        if next_heading and len(section_body) < 80:
            section_heading = next_heading
            placement = f"just before section «{section_heading}»"

        paras = [p.strip() for p in re.split(r"\n\s*\n", section_body) if p.strip()]
        excerpt = " ".join(paras[-2:] if paras else [])
        excerpt = re.sub(r"\s+", " ", excerpt).strip()
        if after_para:
            excerpt = (excerpt + " " + after_para).strip() if excerpt else after_para
        if len(excerpt) > 480:
            excerpt = excerpt[:480].rsplit(" ", 1)[0] + "…"

        contexts.append(
            {
                "index": i + 1,
                "alt": m.group(1).strip(),
                "rel": m.group(2),
                "file": Path(m.group(2)).name,
                "section_heading": section_heading,
                "section_excerpt": excerpt,
                "placement": placement,
            }
        )
    return contexts


def _save_ai_or_local(
    *,
    role: str,
    prompt: str,
    out_path: Path,
    title: str,
    category: str,
    index: int = 1,
    alt: str = "",
) -> tuple[Path, str]:
    spec = IMAGE_SPECS["thumbnail" if role == "thumbnail" else "supporting"]
    w, h = int(spec["width"]), int(spec["height"])
    q = int(spec["webp_quality"])
    try:
        b64 = generate_image_b64(prompt)
        if b64:
            path = save_image_b64(b64, out_path, width=w, height=h, webp_quality=q)
            apply_watermark(
                path,
                position="top-right",
                max_width_ratio=0.17,
                opacity=0.92,
            )
            return path, "ai"
    except Exception as e:
        print(f"[images] grok failed ({role}): {e}", flush=True)

    if role == "thumbnail":
        path = render_thumbnail(out_path, title, category)
    else:
        path = render_supporting(out_path, title, index, alt)
    apply_watermark(
        path,
        position="top-right",
        max_width_ratio=0.17,
        opacity=0.92,
    )
    return path, "local_brand"


def generate_for_article(
    category: str,
    slug: str,
    *,
    force: bool = False,
    use_ai: bool = True,
) -> dict[str, Any]:
    ensure_dirs()
    cfg = load_config()
    folder = article_folder(category, slug)
    meta_path = folder / "meta.json"
    if not meta_path.exists():
        return {"ok": False, "error": "meta_missing", "path": str(folder)}

    meta = load_meta(folder)
    title = meta.get("title") or slug
    persona = meta.get("persona") or ""
    feature_keys = list((meta.get("cta") or {}).get("feature_keys") or meta.get("tags") or [])
    n = int(meta.get("n_images") or cfg.get("default_inline_images") or 3)

    img_dir = folder / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    if force:
        clear_article_images(img_dir)

    body_path = folder / "article.md"
    body = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
    fig_matches = normalize_fig_matches(body, n)
    fig_contexts = extract_figure_contexts(body)
    ctx_by_idx: dict[int, dict[str, Any]] = {}
    for ctx in fig_contexts:
        m = re.search(r"fig-(\d+)", ctx.get("file") or "")
        if m:
            ctx_by_idx[int(m.group(1))] = ctx
        else:
            ctx_by_idx[ctx["index"]] = ctx

    results: dict[str, Any] = {
        "thumbnail": None,
        "inline": [],
        "errors": [],
        "sources": {"ai": 0, "local_brand": 0},
        "sizes": {
            "thumbnail": f"{IMAGE_SPECS['thumbnail']['width']}x{IMAGE_SPECS['thumbnail']['height']}",
            "supporting": f"{IMAGE_SPECS['supporting']['width']}x{IMAGE_SPECS['supporting']['height']}",
        },
        "section_binding": True,
    }
    inline_meta: list[dict[str, Any]] = []

    for i, fig in enumerate(fig_matches, 1):
        alt, rel = fig[0], fig[1]
        ctx = ctx_by_idx.get(i) or {}
        if not alt and ctx.get("alt"):
            alt = ctx["alt"]
        out_base = img_dir / f"fig-{i:02d}.webp"
        if not force and any(img_dir.glob(f"fig-{i:02d}.*")):
            existing = next(img_dir.glob(f"fig-{i:02d}.*"))
            inline_meta.append(
                {
                    "file": f"images/{existing.name}",
                    "alt": alt,
                    "source": "existing",
                    "role": "supporting",
                    "size": results["sizes"]["supporting"],
                    "section_heading": ctx.get("section_heading"),
                    "placement": ctx.get("placement"),
                }
            )
            results["inline"].append(f"{existing.name} (exists)")
            continue

        prompt = supporting_prompt(
            title,
            category,
            i,
            len(fig_matches),
            alt,
            feature_keys,
            section_heading=ctx.get("section_heading") or "",
            section_excerpt=ctx.get("section_excerpt") or "",
            placement=ctx.get("placement") or "",
        )
        print(
            f"[images] fig-{i:02d} section={ctx.get('section_heading')!r} place={ctx.get('placement')!r}",
            flush=True,
        )
        if use_ai:
            path, src = _save_ai_or_local(
                role="supporting",
                prompt=prompt,
                out_path=out_base,
                title=title,
                category=category,
                index=i,
                alt=alt,
            )
        else:
            path = render_supporting(out_base, title, i, alt)
            src = "local_brand"

        final_rel = f"images/{path.name}"
        inline_meta.append(
            {
                "file": final_rel,
                "alt": alt,
                "source": src,
                "role": "supporting",
                "size": results["sizes"]["supporting"],
                "model": "grok-4.5" if src == "ai" else "local_brand_v1",
                "style": "kekasir-photo-section-bound",
                "section_heading": ctx.get("section_heading"),
                "section_excerpt": (ctx.get("section_excerpt") or "")[:280],
                "placement": ctx.get("placement"),
            }
        )
        results["inline"].append(path.name)
        results["sources"][src] = results["sources"].get(src, 0) + 1
        bump_image_counter()
        heartbeat()
        if body_path.exists() and rel != final_rel:
            body = body.replace(rel, final_rel)

    thumb_existing = list(img_dir.glob("thumbnail.*"))
    if force or not thumb_existing:
        tprompt = thumbnail_prompt(title, category, persona)
        out_thumb = img_dir / "thumbnail.webp"
        if use_ai:
            path, src = _save_ai_or_local(
                role="thumbnail",
                prompt=tprompt,
                out_path=out_thumb,
                title=title,
                category=category,
            )
        else:
            path = render_thumbnail(out_thumb, title, category)
            src = "local_brand"
        results["thumbnail"] = path.name
        results["sources"][src] = results["sources"].get(src, 0) + 1
        bump_image_counter()
    else:
        results["thumbnail"] = thumb_existing[0].name

    if body_path.exists() and body:
        body_path.write_text(body, encoding="utf-8")

    thumb_name = results.get("thumbnail") or "thumbnail.webp"
    meta["images"] = {
        "thumbnail": f"images/{thumb_name}",
        "thumbnail_size": results["sizes"]["thumbnail"],
        "supporting_size": results["sizes"]["supporting"],
        "inline": inline_meta,
    }
    meta["image_sources"] = results["sources"]
    meta["image_style"] = "kekasir-photo-realistic-v2"
    meta["watermark"] = {
        "enabled": True,
        "asset": "assets/brand/logo-horizontal.png",
        "position": "top-right",
        "max_width_ratio": 0.17,
        "opacity": 0.92,
        "no_background": True,
        "method": "post_process_composite",
    }
    meta["status"] = "done" if not results["errors"] else "images_partial"
    save_meta(folder, meta)

    try:
        from common import load_catalog, save_catalog

        cat = load_catalog()
        for p in cat.get("posts") or []:
            if p.get("slug") == slug:
                p["status"] = meta["status"]
                p["thumbnail"] = f"content/{category}/{slug}/images/{thumb_name}"
        save_catalog(cat)
    except Exception:
        pass

    return {"ok": True, "slug": slug, **results}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-ai", action="store_true")
    args = ap.parse_args()
    res = generate_for_article(
        args.category,
        args.slug,
        force=args.force,
        use_ai=not args.no_ai,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
