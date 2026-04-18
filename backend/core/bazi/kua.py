"""Life Kua / Ming Gua (命卦) — personal trigram number 1–9, used in 八宅 Feng Shui."""

from __future__ import annotations

from dataclasses import dataclass

# Trigram metadata keyed by Kua number 1–9 (5 is special).
_TRIGRAMS: dict[int, dict[str, str]] = {
    1: {"cn": "坎", "pinyin": "Kan",  "element": "water", "direction": "N",  "group": "East"},
    2: {"cn": "坤", "pinyin": "Kun",  "element": "earth", "direction": "SW", "group": "West"},
    3: {"cn": "震", "pinyin": "Zhen", "element": "wood",  "direction": "E",  "group": "East"},
    4: {"cn": "巽", "pinyin": "Xun",  "element": "wood",  "direction": "SE", "group": "East"},
    6: {"cn": "乾", "pinyin": "Qian", "element": "metal", "direction": "NW", "group": "West"},
    7: {"cn": "兑", "pinyin": "Dui",  "element": "metal", "direction": "W",  "group": "West"},
    8: {"cn": "艮", "pinyin": "Gen",  "element": "earth", "direction": "NE", "group": "West"},
    9: {"cn": "离", "pinyin": "Li",   "element": "fire",  "direction": "S",  "group": "East"},
}


@dataclass(frozen=True)
class LifeKua:
    number: int           # 1..9, excluding 5
    trigram_cn: str
    trigram_pinyin: str
    element: str
    seated_direction: str # the trigram's own direction
    group: str            # "East" or "West"


def _digit_sum_reduce(n: int) -> int:
    while n >= 10:
        n = sum(int(c) for c in str(n))
    return n


def compute_life_kua(solar_year: int, gender: str) -> LifeKua:
    """Life Kua from solar-year digit-sum reduction.

    Traditional formula:
      * Year < 2000 — Male: (11 - reduced_sum) mod 9; Female: (4 + reduced_sum) mod 9
      * Year >= 2000 — Male: (10 - reduced_sum) mod 9; Female: (5 + reduced_sum) mod 9
    Result of 0 → 9. Result of 5 → 2 (male) or 8 (female).
    """
    digits_sum = sum(int(c) for c in str(solar_year))
    reduced = _digit_sum_reduce(digits_sum)

    g = (gender or "").strip().lower()
    is_male = g in {"male", "m", "man"}

    if solar_year >= 2000:
        raw = (10 - reduced) if is_male else (5 + reduced)
    else:
        raw = (11 - reduced) if is_male else (4 + reduced)

    kua = raw % 9 or 9
    if kua == 5:
        kua = 2 if is_male else 8

    info = _TRIGRAMS[kua]
    return LifeKua(
        number=kua,
        trigram_cn=info["cn"],
        trigram_pinyin=info["pinyin"],
        element=info["element"],
        seated_direction=info["direction"],
        group=info["group"],
    )
