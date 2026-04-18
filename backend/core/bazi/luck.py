"""Ten-Year Luck Pillars (大运) and annual luck (流年) helpers.

Direction rule:
  * Male + Yang year stem, or Female + Yin year stem   → forward (next pillar).
  * Male + Yin year stem, or Female + Yang year stem   → backward (previous pillar).

Starting age is traditionally computed from days between birth and the nearest
solar term (three days = one year). This module uses a simplified estimate:
a fixed starting age of 8 for forward direction and 2 for backward direction,
adjustable via parameters. Callers can supply a more precise ``start_age`` when
a precise solar-term ephemeris is available.
"""

from __future__ import annotations

from dataclasses import dataclass

from .calculator import FourPillars, Pillar
from .constants import STEM_YANG


def luck_direction(gender: str, year_stem_index: int) -> int:
    """Return +1 (forward) or -1 (backward).

    ``gender`` is 'male' or 'female' (case-insensitive); anything else defaults
    to forward.
    """
    g = (gender or "").strip().lower()
    is_yang_year = STEM_YANG[year_stem_index]
    if (g == "male" and is_yang_year) or (g == "female" and not is_yang_year):
        return 1
    if (g == "male" and not is_yang_year) or (g == "female" and is_yang_year):
        return -1
    return 1


@dataclass(frozen=True)
class LuckPillar:
    index: int          # 0 = first luck pillar
    start_age: int      # age when this pillar begins
    end_age: int        # age when the next begins (exclusive)
    pillar: Pillar


def luck_pillars(
    pillars: FourPillars,
    gender: str,
    count: int = 8,
    first_start_age: int | None = None,
) -> list[LuckPillar]:
    """Compute the first ``count`` luck pillars (each 10 years).

    ``first_start_age`` defaults to 8 for forward luck, 2 for backward luck.
    """
    direction = luck_direction(gender, pillars.year.stem_index)
    start_age = first_start_age if first_start_age is not None else (8 if direction > 0 else 2)

    results: list[LuckPillar] = []
    stem = pillars.month.stem_index
    branch = pillars.month.branch_index
    age = start_age
    for i in range(count):
        stem = (stem + direction) % 10
        branch = (branch + direction) % 12
        results.append(
            LuckPillar(
                index=i,
                start_age=age,
                end_age=age + 10,
                pillar=Pillar(stem_index=stem, branch_index=branch),
            )
        )
        age += 10
    return results


def annual_pillar(year: int) -> Pillar:
    """Pillar for a given solar Ba Zi year.

    Uses the same epoch as ``calculator._year_pillar``.
    """
    idx = year - 4
    return Pillar(stem_index=idx % 10, branch_index=idx % 12)
