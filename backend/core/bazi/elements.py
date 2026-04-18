"""Five-Elements balance from Four Pillars, including hidden stems."""

from __future__ import annotations

from dataclasses import dataclass

from .calculator import FourPillars, Pillar
from .constants import ELEMENTS, HIDDEN_STEMS, STEM_ELEMENT

STEM_WEIGHT = 1.0
BRANCH_HIDDEN_TOTAL_WEIGHT = 1.0


@dataclass(frozen=True)
class ElementBalance:
    wood: float
    fire: float
    earth: float
    metal: float
    water: float

    @property
    def as_dict(self) -> dict[str, float]:
        return {
            "wood": self.wood,
            "fire": self.fire,
            "earth": self.earth,
            "metal": self.metal,
            "water": self.water,
        }

    @property
    def total(self) -> float:
        return self.wood + self.fire + self.earth + self.metal + self.water

    def dominant(self) -> str:
        return max(self.as_dict.items(), key=lambda kv: kv[1])[0]

    def weakest(self) -> str:
        return min(self.as_dict.items(), key=lambda kv: kv[1])[0]


def element_balance(pillars: FourPillars, include_hidden: bool = True) -> ElementBalance:
    """Compute the Five-Elements balance across all four pillars.

    Contributions:
      - Each stem contributes ``STEM_WEIGHT`` to its element.
      - When ``include_hidden`` is True, each branch contributes its hidden
        stems (weights summing to ``BRANCH_HIDDEN_TOTAL_WEIGHT`` per branch).
      - When False, each branch contributes ``BRANCH_HIDDEN_TOTAL_WEIGHT`` to
        its main element only.
    """
    totals: dict[str, float] = {e: 0.0 for e in ELEMENTS}
    for pillar in (pillars.year, pillars.month, pillars.day, pillars.hour):
        _add_pillar_contributions(pillar, totals, include_hidden)
    return ElementBalance(
        wood=totals["wood"],
        fire=totals["fire"],
        earth=totals["earth"],
        metal=totals["metal"],
        water=totals["water"],
    )


def _add_pillar_contributions(
    pillar: Pillar, totals: dict[str, float], include_hidden: bool
) -> None:
    totals[pillar.stem_element] += STEM_WEIGHT
    if include_hidden:
        for stem_idx, weight in HIDDEN_STEMS[pillar.branch_index]:
            totals[STEM_ELEMENT[stem_idx]] += weight
    else:
        totals[pillar.branch_element] += BRANCH_HIDDEN_TOTAL_WEIGHT
