"""Day-Master strength assessment and the 'Useful God' (用神) recommendation."""

from __future__ import annotations

from dataclasses import dataclass

from .calculator import FourPillars
from .constants import ELEMENTS
from .elements import element_balance
from .ten_gods import CONTROLS, PRODUCES

# Month-branch element: the element of each branch considered as season.
# Re-exported from constants via BRANCH_ELEMENT; duplicated intentionally so
# seasonal influence can be tuned here independently.
from .constants import BRANCH_ELEMENT

# Seasonal weights: how strongly does the month element treat the Day Master?
# If month matches DM element: very strong. If month produces DM: strong.
# If DM produces month (drains DM): weakens. If month controls DM: weakens.
# If DM controls month: slight gain (we command the season).
SEASONAL_SUPPORT = 2.0
SEASONAL_PRODUCE = 1.2
SEASONAL_SAME_WEAK = 0.0      # baseline
SEASONAL_CONTROLLED = -1.5    # season controls DM
SEASONAL_DRAIN = -1.0         # DM produces season
SEASONAL_COMMANDING = 0.3     # DM controls season


@dataclass(frozen=True)
class DayMasterStrength:
    score: float                 # fraction in [0, 1]
    level: str                   # "strong" | "balanced" | "weak"
    supportive_elements: list[str]
    draining_elements: list[str]
    seasonal_influence: str      # plain-English description
    useful_god: str              # recommended favorable element
    avoid_god: str               # element to minimise
    explanation: str


def day_master_strength(pillars: FourPillars) -> DayMasterStrength:
    dm_elem = pillars.day.stem_element
    month_elem = BRANCH_ELEMENT[pillars.month.branch_index]

    # Seasonal influence score
    if month_elem == dm_elem:
        seasonal = SEASONAL_SUPPORT
        seasonal_txt = f"Born in {month_elem} season — Day Master is in its own season (very strong)."
    elif PRODUCES[month_elem] == dm_elem:
        seasonal = SEASONAL_PRODUCE
        seasonal_txt = f"Born in {month_elem} season which produces {dm_elem} — Day Master is nourished."
    elif CONTROLS[month_elem] == dm_elem:
        seasonal = SEASONAL_CONTROLLED
        seasonal_txt = f"Born in {month_elem} season which controls {dm_elem} — Day Master is pressured."
    elif CONTROLS[dm_elem] == month_elem:
        seasonal = SEASONAL_COMMANDING
        seasonal_txt = f"Born in {month_elem} season which the Day Master commands — modest boost."
    elif PRODUCES[dm_elem] == month_elem:
        seasonal = SEASONAL_DRAIN
        seasonal_txt = f"Born in {month_elem} season which drains {dm_elem} — output season, Day Master leaks."
    else:
        seasonal = SEASONAL_SAME_WEAK
        seasonal_txt = f"Born in {month_elem} season (neutral relative to Day Master)."

    bal = element_balance(pillars).as_dict

    supporting_elems = {dm_elem, _inverse_produces(dm_elem)}   # same element + its mother
    draining_elems   = {PRODUCES[dm_elem], CONTROLS[dm_elem]}  # child + what DM controls
    attacking_elems  = {_inverse_controls(dm_elem)}            # what controls DM

    support_total = sum(bal[e] for e in supporting_elems) + max(seasonal, 0.0)
    drain_total   = sum(bal[e] for e in draining_elems | attacking_elems) + max(-seasonal, 0.0)
    total = support_total + drain_total
    score = support_total / total if total > 0 else 0.5

    if score >= 0.55:
        level = "strong"
        useful = list(draining_elems)[0]  # prefer the element that regulates the excess
        avoid  = dm_elem
        explanation = (
            f"Day Master {dm_elem} is strong. Favorable direction: use {useful} to channel "
            f"the excess (produce output or let wealth/officer roles discipline). Avoid piling more {dm_elem}."
        )
    elif score < 0.40:
        level = "weak"
        useful = _inverse_produces(dm_elem)  # the mother element that feeds DM
        avoid  = list(attacking_elems)[0]
        explanation = (
            f"Day Master {dm_elem} is weak. Favorable direction: bring in {useful} (Resource) or "
            f"own-element {dm_elem} (Friends) for reinforcement. Minimise {avoid}."
        )
    else:
        level = "balanced"
        useful = PRODUCES[dm_elem]
        avoid = _inverse_controls(dm_elem)
        explanation = (
            f"Day Master {dm_elem} is balanced. A useful-god that expresses talent ({useful}) or any "
            f"element that is currently thin in the chart will keep the equilibrium."
        )

    return DayMasterStrength(
        score=round(score, 3),
        level=level,
        supportive_elements=sorted(supporting_elems),
        draining_elements=sorted(draining_elems | attacking_elems),
        seasonal_influence=seasonal_txt,
        useful_god=useful,
        avoid_god=avoid,
        explanation=explanation,
    )


def _inverse_produces(elem: str) -> str:
    """The element that produces ``elem`` (its 'mother')."""
    for e in ELEMENTS:
        if PRODUCES[e] == elem:
            return e
    raise ValueError(elem)


def _inverse_controls(elem: str) -> str:
    """The element that controls ``elem`` (its 'attacker')."""
    for e in ELEMENTS:
        if CONTROLS[e] == elem:
            return e
    raise ValueError(elem)
