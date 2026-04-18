"""Five Factors (五行十神) — element balance recast as Ten-God categories.

Standard Ten-God groupings from the Day Master's perspective:
    Companion (比劫 同我)  → same element as DM
    Resource  (印   生我)  → element that produces DM
    Output    (食伤 我生)  → element produced by DM
    Influence (官杀 克我)  → element that controls DM
    Wealth    (财   我克)  → element that DM controls
"""

from __future__ import annotations

from dataclasses import dataclass

from .calculator import FourPillars
from .elements import element_balance
from .ten_gods import CONTROLS, PRODUCES


def _inverse_of(mapping: dict[str, str], target: str) -> str:
    for k, v in mapping.items():
        if v == target:
            return k
    raise KeyError(target)


@dataclass(frozen=True)
class FactorRow:
    key: str            # companion | resource | output | influence | wealth
    label: str
    element: str
    amount: float
    percent: float


def five_factors(pillars: FourPillars) -> list[FactorRow]:
    dm_elem = pillars.day.stem_element
    bal = element_balance(pillars).as_dict
    total = sum(bal.values()) or 1.0

    mapping = {
        "companion": ("Companion", dm_elem),
        "resource":  ("Resource",  _inverse_of(PRODUCES, dm_elem)),
        "output":    ("Output",    PRODUCES[dm_elem]),
        "influence": ("Influence", _inverse_of(CONTROLS, dm_elem)),
        "wealth":    ("Wealth",    CONTROLS[dm_elem]),
    }

    rows = [
        FactorRow(
            key=key,
            label=label,
            element=element,
            amount=round(bal[element], 2),
            percent=round(bal[element] / total * 100.0, 1),
        )
        for key, (label, element) in mapping.items()
    ]
    # Sort by descending percent (like the chinesemetasoft display).
    return sorted(rows, key=lambda r: r.percent, reverse=True)
