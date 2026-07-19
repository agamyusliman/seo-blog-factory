from __future__ import annotations

import base64
import io
import itertools
import json
import os
import re
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from paths import ROOT

load_dotenv(ROOT / ".env")


# Multi-model chat: AI_CHAT_MODELS (comma-separated, round-robin) or AI_CHAT_MODEL (single).
# Image stays single AI_IMAGE_MODEL (grok-4.5).
_CHAT_MODELS: list[str] | None = None
_CHAT_CYCLE: itertools.cycle | None = None
_LAST_CHAT_MODEL: str = ""


def last_chat_model() -> str:
    return _LAST_CHAT_MODEL


def _chat_models() -> list[str]:
    global _CHAT_MODELS, _CHAT_CYCLE
    if _CHAT_MODELS is not None:
        return _CHAT_MODELS
    raw = os.environ.get("AI_CHAT_MODELS") or os.environ.get("KEKASIR_AI_CHAT_MODELS") or ""
    models = [m.strip() for m in raw.split(",") if m.strip()]
    if not models:
        single = os.environ.get("AI_CHAT_MODEL", os.environ.get("KEKASIR_AI_CHAT_MODEL", "grok-4.5"))
        models = [single]
    _CHAT_MODELS = models
    _CHAT_CYCLE = itertools.cycle(models)
    return models


def _next_chat_model() -> str:
    _chat_models()
    assert _CHAT_CYCLE is not None
    return next(_CHAT_CYCLE)


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


def fix_mojibake(text: str) -> str:
    """Repair UTF-8 text that was mis-decoded as latin-1 (e.g. → becomes â\x86\x92)."""
    if not text:
        return text
    if any(m in text for m in ("â", "Ã", "Â", "ð")):
        try:
            repaired = text.encode("latin-1").decode("utf-8")
            if sum(repaired.count(c) for c in ("â", "Ã", "Â")) < sum(text.count(c) for c in ("â", "Ã", "Â")):
                text = repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    # Hard replacements for common leftovers
    replacements = {
        "â": "→",
        "â": "—",
        "â": "–",
        "â¦": "…",
        "â": "“",
        "â": "”",
        "â": "‘",
        "â": "’",
        "Ã·": "÷",
        "Ã": "×",
        "Â°": "°",
        "Â·": "·",
        "â¢": "•",
        "â": "≈",
        "â¤": "≤",
        "â¥": "≥",
        "Â ": " ",
    }
    for bad, good in replacements.items():
        if bad in text:
            text = text.replace(bad, good)
    return text


def _parse_sse_stream(resp: requests.Response) -> dict[str, Any]:
    content_parts: list[str] = []
    model_name = ""
    usage: dict[str, Any] | None = None
    finish_reason = ""
    # Gateway returns text/event-stream without charset; force UTF-8 so → — ÷ stay intact.
    resp.encoding = "utf-8"
    for raw in resp.iter_lines(decode_unicode=False):
        if not raw:
            continue
        try:
            line = raw.decode("utf-8")
        except UnicodeDecodeError:
            line = raw.decode("utf-8", errors="replace")
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if not model_name and chunk.get("model"):
            model_name = chunk["model"]
        if chunk.get("usage"):
            usage = chunk["usage"]
        choices = chunk.get("choices") or []
        if choices:
            delta = choices[0].get("delta") or {}
            if delta.get("content"):
                content_parts.append(delta["content"])
            if choices[0].get("finish_reason"):
                finish_reason = choices[0]["finish_reason"]
    content = fix_mojibake("".join(content_parts))
    return {
        "content": content,
        "model": model_name,
        "usage": usage,
        "finish_reason": finish_reason,
    }


def chat(
    messages: list[dict[str, Any]],
    model: str | None = None,
    temperature: float = 0.7,
    timeout: int = 180,
) -> str:
    global _LAST_CHAT_MODEL
    models = [model] if model else _chat_models()
    if not model and _CHAT_CYCLE is not None:
        start = next(_CHAT_CYCLE)
        models = [start] + [m for m in models if m != start]

    last_err: Exception | None = None
    for m in models:
        payload = {
            "model": m,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
        }
        try:
            r = requests.post(
                f"{_base()}/chat/completions",
                headers=_headers(),
                json=payload,
                timeout=timeout,
                stream=True,
            )
            r.raise_for_status()
            parsed = _parse_sse_stream(r)
            content = parsed["content"]
            if not content:
                raise ValueError(f"empty content from {parsed.get('model', m)}")
            _LAST_CHAT_MODEL = parsed.get("model") or m
            return fix_mojibake(content)
        except (requests.HTTPError, requests.RequestException, KeyError, ValueError) as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("no chat models configured")


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
