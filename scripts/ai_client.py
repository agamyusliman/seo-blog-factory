from __future__ import annotations

import base64
import io
import os
import re
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from paths import ROOT

load_dotenv(ROOT / ".env")


def _base() -> str:
    return os.environ.get(
        "AI_BASE_URL",
        os.environ.get("KEKASIR_AI_BASE_URL", "https://your-gateway.example/v1"),
    ).rstrip("/")


def _key() -> str:
    key = os.environ.get("AI_API_KEY") or os.environ.get("KEKASIR_AI_API_KEY") or ""
    if not key or key in ("replace-me", "replace-with-your-api-key"):
        raise RuntimeError("Set AI_API_KEY in .env")
    return key


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def chat(
    messages: list[dict[str, Any]],
    model: str | None = None,
    temperature: float = 0.7,
    timeout: int = 180,
) -> str:
    model = model or os.environ.get(
        "AI_CHAT_MODEL", os.environ.get("KEKASIR_AI_CHAT_MODEL", "grok-4.5")
    )
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
    }
    r = requests.post(
        f"{_base()}/chat/completions",
        headers=_headers(),
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _extract_b64_from_responses(data: dict[str, Any]) -> str | None:
    for item in data.get("output") or []:
        if not isinstance(item, dict):
            continue
        t = item.get("type") or ""
        if t in ("image_generation_call", "output_image") and item.get("result"):
            return item["result"]
        for c in item.get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("b64_json"):
                return c["b64_json"]
            if c.get("type") in ("output_image", "image") and (
                c.get("image_base64") or c.get("result")
            ):
                return c.get("image_base64") or c.get("result")
        if item.get("result") and len(str(item["result"])) > 200:
            return item["result"]
    return None


def _extract_b64_from_markdown(text: str) -> str | None:
    if not text:
        return None
    m = re.search(
        r"data:image/(png|jpeg|jpg|webp|gif);base64,([A-Za-z0-9+/=]+)",
        text,
        flags=re.I,
    )
    if m:
        return m.group(2)
    return None


def generate_image_b64(
    prompt: str,
    model: str | None = None,
    timeout: int = 180,
    ref_images: list[str] | None = None,
) -> str | None:
    model = model or os.environ.get(
        "AI_IMAGE_MODEL", os.environ.get("KEKASIR_AI_IMAGE_MODEL", "grok-4.5")
    )
    prompt_text = f"Generate an image: {prompt}\n\nUse the image_generation tool."
    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt_text}]
    for img in (ref_images or [])[:4]:
        img = (img or "").strip()
        if img.startswith("data:image/"):
            content.append({"type": "input_image", "image_url": img})

    payload = {
        "model": model,
        "stream": False,
        "store": False,
        "tools": [{"type": "image_generation"}],
        "reasoning": {"effort": "high", "summary": "concise"},
        "input": [{"role": "user", "content": content}],
    }
    r = requests.post(
        f"{_base()}/responses",
        headers=_headers(),
        json=payload,
        timeout=timeout,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"image gen HTTP {r.status_code}: {r.text[:800]}")
    data = r.json()

    b64 = _extract_b64_from_responses(data)
    if b64:
        return b64

    if isinstance(data, dict):
        for key in ("content", "message", "text"):
            val = data.get(key)
            if isinstance(val, str):
                b64 = _extract_b64_from_markdown(val)
                if b64:
                    return b64
        choices = data.get("choices") or []
        if choices:
            msg = (choices[0].get("message") or {}).get("content") or ""
            b64 = _extract_b64_from_markdown(msg)
            if b64:
                return b64
    return None


def save_image_b64(
    b64: str,
    out_path: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    webp_quality: int = 82,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(b64)
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if width and height:
            img = _fit_cover(img, width, height)
        webp = out_path.with_suffix(".webp")
        img.save(webp, "WEBP", quality=webp_quality, method=6)
        if out_path.suffix.lower() != ".webp" and out_path.exists():
            out_path.unlink(missing_ok=True)
        return webp
    except Exception:
        out_path.write_bytes(raw)
        return out_path


def _fit_cover(img: Any, width: int, height: int) -> Any:
    from PIL import Image

    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    return resized.crop((left, top, left + width, top + height))


def save_pil_image(
    img: Any,
    out_path: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    webp_quality: int = 82,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if width and height:
        img = _fit_cover(img.convert("RGB"), width, height)
    else:
        img = img.convert("RGB")
    webp = out_path.with_suffix(".webp")
    img.save(webp, "WEBP", quality=webp_quality, method=6)
    return webp
