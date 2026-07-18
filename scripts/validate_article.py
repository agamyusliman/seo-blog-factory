from __future__ import annotations

import re
from typing import Any

from common import count_words


STALE_PRICES = [
    r"rp\s*50[\.\s]?000",
    r"rp\s*100[\.\s]?000",
    r"50\.000\s*/\s*bulan",
    r"100\.000\s*/\s*bulan",
]

FORBIDDEN = [
    r"gofood\s+api",
    r"grabfood\s+api",
    r"shopeefood\s+api",
    r"integrasi\s+otomatis\s+gofood",
    r"\bxendit\b",
    r"\bduitku\b",
    r"\bdurianpay\b",
    r"loyalty\s+points?\s+(sudah|telah)\s+(ada|live|aktif)",
    r"qris\s+gratis",
    r"tanpa\s+biaya\s+mdr",
    r"\bbarbershop\b",
    r"\bsalon\b",
    r"\blaundry\b",
    r"\bminimarket\b",
    r"toko\s+kelontong",
    r"aplikasi\s+kasir\s+retail",
    r"untuk\s+retail\s+dan\s+jasa",
    r"janji\s+temu\s+(salon|barber|klinik)",
    r"refund\s+otomatis\s+(qris|ke\s+pelanggan)",
    r"mdr\s+(dikembalikan|di-?refund)",
    r"langganan\s+bisa\s+di-?refund",
    r"pro-?rata\s+refund",
    r"surcharge",
    r"biaya\s+tambahan\s+qris\s+ke\s+pelanggan",
    r"settlement\s+instan",
    r"cair\s+di\s+hari\s+yang\s+sama\s+selalu",
]

UNNATURAL_ID = [
    r"\bfood\s*cost(ing)?\b",
    r"\bwaste\b",
    r"\bbuffer\b",
    r"\bmarkup\b",
    r"\boverhead\b",
    r"bill\s+of\s+material",
    r"\bcogs\b",
    r"menu\s+engineering",
    r"menu\s+bintang",
    r"kuda\s+pacu",
    r"menu\s+teka-?teki",
    r"menu\s+beban",
    r"\bfifo\b",
    r"di\s+dunia\s+f&b",
    r"di\s+era\s+digital",
    r"yuk\s+mulai",
    r"mari\s+kita\s+bedah",
    r"tanpa\s+basa-?basi",
    r"rahasia\s+sukses",
    r"pendorong\s+omzet",
    r"dompet\s+lebih\s+tenang",
    r"feeling\s+laris",
    r"raw\s+food",
    r"target\s+food\s+cost",
]

PRO_FEATURES = [
    r"self[-\s]?order\s+qr",
    r"qr\s+meja",
    r"\bkds\b",
    r"kitchen\s+display",
    r"reservasi\s+meja",
]


def validate_article(
    body: str,
    *,
    min_words: int = 500,
    max_words: int = 2000,
    catalog_slugs: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    wc = count_words(body)
    if wc < min_words:
        errors.append(f"word_count {wc} < {min_words}")
    if wc > max_words:
        errors.append(f"word_count {wc} > {max_words}")

    low = body.lower()
    for pat in STALE_PRICES:
        if re.search(pat, low):
            errors.append(f"stale_price_pattern: {pat}")
            break

    for pat in FORBIDDEN:
        if re.search(pat, low):
            errors.append(f"forbidden: {pat}")

    for pat in UNNATURAL_ID:
        if re.search(pat, low):
            errors.append(f"unnatural_id: {pat}")

    if re.search(r"\bbasic\b", low):
        for sec in re.split(r"\n#{2,3}\s+", body):
            sec_l = sec.lower()
            if "basic" in sec_l and any(re.search(p, sec_l) for p in PRO_FEATURES):
                if not re.search(r"pro|upgrade|trial", sec_l):
                    errors.append("pro_feature_claimed_as_basic")
                    break

    h2 = len(re.findall(r"^##\s+", body, flags=re.M))
    if h2 < 3:
        errors.append(f"headings H2 count {h2} < 3")

    lists = len(re.findall(r"^(\s*[-*]|\s*\d+\.)\s+", body, flags=re.M))
    if lists < 2:
        errors.append("too_flat_need_lists")

    if catalog_slugs is not None:
        for m in re.finditer(r"\[\[link:([a-z0-9-]+)\|", body):
            if m.group(1) not in catalog_slugs:
                errors.append(f"unknown_internal_slug:{m.group(1)}")

    return errors


def meta_from_body(title: str, body: str) -> dict[str, Any]:
    plain = re.sub(r"[#>*`\[\]\(\)!|_-]", " ", body)
    plain = re.sub(r"\s+", " ", plain).strip()
    excerpt = plain[:180].rsplit(" ", 1)[0] + "…" if len(plain) > 180 else plain
    wc = count_words(body)
    return {
        "excerpt": excerpt,
        "word_count": wc,
        "read_minutes": max(1, round(wc / 200)),
    }
