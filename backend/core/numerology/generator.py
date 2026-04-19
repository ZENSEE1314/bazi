"""Generate candidate numbers optimised for a user's Useful God element.

Strategy:
1. Pick a digit pool biased toward the Useful God's digits + neutral (5, 0).
2. Build candidate sequences where each adjacent digit pair is auspicious
   (Sheng Qi / Yan Nian / Tian Yi / Fu Wei), falling back to neutral
   (5/0) when no auspicious option is reachable.
3. Score every candidate via the existing scorer, plus pair-counts.
4. Return the top-N ranked.

Purposes (phone / bank / car / id / credit) tune default length and the
prefix strategy (e.g. we don't generate a country code for phone numbers
— callers can glue one on manually if needed).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..bazi.guidance import ELEMENT_GUIDANCE
from .pairs import AUSPICIOUS_TARGETS, pair_category
from .scorer import score_number

PURPOSE_DEFAULT_LENGTH = {
    "phone":  10,
    "bank":   10,
    "car":    4,
    "id":     12,
    "credit": 16,
    "custom": 10,
}

# Digits always in the pool (neutral, don't break chains)
_NEUTRAL = (5, 0)


@dataclass
class GeneratedNumber:
    number: str
    overall: int
    wealth: int
    safety: int
    health: int
    auspicious_pair_count: int
    inauspicious_pair_count: int
    dominant_element: str
    favored_digit_count: int
    avoid_digit_count: int


def _preferred_pool(useful_god: str, avoid_god: str | None) -> tuple[list[int], set[int]]:
    guide_u = ELEMENT_GUIDANCE.get(useful_god, {}).get("numbers") or []
    guide_a = ELEMENT_GUIDANCE.get(avoid_god or "", {}).get("numbers") or []
    favored = list(guide_u)
    # Add neutrals; dedupe while preserving order
    for n in _NEUTRAL:
        if n not in favored and n not in guide_a:
            favored.append(n)
    avoid = set(guide_a)
    # Ensure at least 3 digits in the pool (some elements like fire only map to [9])
    if len(favored) < 3:
        # Fill with digits that aren't in the avoid set
        for n in range(10):
            if n not in avoid and n not in favored and len(favored) < 6:
                favored.append(n)
    return favored, avoid


def _next_digit(
    prev: int,
    pool: list[int],
    avoid: set[int],
    rng: random.Random,
) -> int:
    """Pick next digit so (prev, next) forms an auspicious pair; prefer pool."""
    candidates: list[int] = []
    for d in pool:
        if d in avoid:
            continue
        reading = pair_category(prev, d)
        if reading and reading.category_key in AUSPICIOUS_TARGETS:
            candidates.append(d)
    if candidates:
        return rng.choice(candidates)
    # Fallback: try any non-avoid digit that forms an auspicious pair.
    fallback: list[int] = []
    for d in range(10):
        if d in avoid or d == prev:
            continue
        reading = pair_category(prev, d)
        if reading and reading.category_key in AUSPICIOUS_TARGETS:
            fallback.append(d)
    if fallback:
        return rng.choice(fallback)
    # Last resort: pick a neutral
    for n in _NEUTRAL:
        if n not in avoid:
            return n
    return rng.choice(pool)


def _gen_one(length: int, pool: list[int], avoid: set[int], rng: random.Random) -> list[int]:
    seq = [rng.choice(pool)]
    while len(seq) < length:
        seq.append(_next_digit(seq[-1], pool, avoid, rng))
    return seq


def generate_numbers(
    useful_god: str,
    avoid_god: str | None = None,
    purpose: str = "phone",
    length: int | None = None,
    count: int = 10,
    prefix: str = "",
    attempts: int = 400,
) -> list[GeneratedNumber]:
    """Return up to ``count`` candidate numbers, highest overall-score first."""
    if length is None:
        length = PURPOSE_DEFAULT_LENGTH.get(purpose, 10)
    length = max(4, min(length, 20))

    pool, avoid = _preferred_pool(useful_god, avoid_god)
    favored_set = set(pool) - set(_NEUTRAL)

    # Dedicated RNG seeded from OS entropy — independent per call, so every
    # request produces a genuinely fresh batch.
    rng = random.Random()
    seen: set[str] = set()
    results: list[GeneratedNumber] = []

    for _ in range(attempts):
        seq = _gen_one(length, pool, avoid, rng)
        s = "".join(str(d) for d in seq)
        if s in seen:
            continue
        seen.add(s)

        full = (prefix + s) if prefix else s
        scored = score_number(full)

        from .pairs import analyse_pairs
        pairs = analyse_pairs(full)
        ausp = sum(1 for p in pairs if p.auspicious)

        digits = [int(c) for c in full if c.isdigit()]
        fav = sum(1 for d in digits if d in favored_set)
        avd = sum(1 for d in digits if d in avoid)

        results.append(
            GeneratedNumber(
                number=full,
                overall=scored.overall,
                wealth=scored.wealth,
                safety=scored.safety,
                health=scored.health,
                auspicious_pair_count=ausp,
                inauspicious_pair_count=len(pairs) - ausp,
                dominant_element=scored.dominant_element,
                favored_digit_count=fav,
                avoid_digit_count=avd,
            )
        )

    # Sort: overall score desc, auspicious-pair-count desc, avoid-digits asc.
    results.sort(
        key=lambda r: (r.overall, r.auspicious_pair_count, -r.avoid_digit_count),
        reverse=True,
    )
    # Build a strong pool (top 4× count, min 40), shuffle, then take `count`.
    # This keeps quality high but guarantees a different mix on every call.
    pool_size = max(count * 4, 40)
    strong = results[:pool_size]
    rng.shuffle(strong)
    # Re-rank the shuffled subset slightly so the best still drift toward the top.
    strong.sort(
        key=lambda r: (r.overall + rng.uniform(-5, 5), r.auspicious_pair_count),
        reverse=True,
    )
    unique: list[GeneratedNumber] = []
    seen2: set[str] = set()
    for r in strong:
        if r.number in seen2:
            continue
        seen2.add(r.number)
        unique.append(r)
        if len(unique) >= count:
            break
    return unique
