"""Score a digit sequence (phone, bank, account number) on three axes:
Wealth, Safety, Health -- each on a 0..100 scale.

Scoring model (transparent, rule-based):

  1. Element balance:
       Each digit contributes 1 unit to its element (see DIGIT_ELEMENT).
       Balance score = 100 - (stdev(counts) * k), clamped to [0, 100].
       An even distribution scores near 100; skewed distributions score lower.

  2. Auspicious digit bonus:
       Digits in WEALTH_DIGITS boost the Wealth axis.
       Digits in SAFETY_DIGITS boost the Safety axis.
       Digits in HEALTH_DIGITS boost the Health axis.

  3. Inauspicious penalty:
       Digits in INAUSPICIOUS_DIGITS apply a penalty to all axes.

  4. Last-4 weighting:
       The final four digits are weighted 2x, reflecting the numerology
       convention that the "ending" of a number most strongly influences fate.

Final values are clamped to [0, 100] and rounded to integers.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .constants import (
    DIGIT_ELEMENT,
    ELEMENTS_GENERATIVE,
    HEALTH_DIGITS,
    INAUSPICIOUS_DIGITS,
    SAFETY_DIGITS,
    WEALTH_DIGITS,
)

BALANCE_STDEV_SCALE = 25.0
AUSPICIOUS_BONUS_PER_DIGIT = 8.0
INAUSPICIOUS_PENALTY_PER_DIGIT = 10.0
LAST_N_WEIGHT = 2.0
LAST_N = 4
BASELINE = 50.0
HEALTH_BALANCE_MIX = 0.4  # share of balance in the final health score


@dataclass(frozen=True)
class NumerologyScore:
    wealth: int
    safety: int
    health: int
    dominant_element: str
    element_counts: dict[str, float]

    @property
    def overall(self) -> int:
        return round((self.wealth + self.safety + self.health) / 3)


def score_number(number: str) -> NumerologyScore:
    """Score a digit sequence on Wealth, Safety, and Health axes.

    Non-digit characters are stripped (spaces, dashes, plus signs, etc.).
    Raises ValueError if the input contains no digits.
    """
    digits = _parse_digits(number)
    weights = _weighted_counts(digits)
    counts = _element_counts(digits, weights)

    balance = _balance_score(counts)
    wealth = _axis_score(digits, weights, WEALTH_DIGITS)
    safety = _axis_score(digits, weights, SAFETY_DIGITS)
    health_raw = _axis_score(digits, weights, HEALTH_DIGITS)
    health = (1.0 - HEALTH_BALANCE_MIX) * health_raw + HEALTH_BALANCE_MIX * balance

    dominant = max(counts.items(), key=lambda kv: kv[1])[0]
    return NumerologyScore(
        wealth=round(wealth),
        safety=round(safety),
        health=round(health),
        dominant_element=dominant,
        element_counts=counts,
    )


def _parse_digits(number: str) -> list[int]:
    digits = [int(c) for c in number if c.isdigit()]
    if not digits:
        raise ValueError("Number must contain at least one digit")
    return digits


def _weighted_counts(digits: list[int]) -> list[float]:
    n = len(digits)
    return [LAST_N_WEIGHT if i >= n - LAST_N else 1.0 for i in range(n)]


def _element_counts(digits: list[int], weights: list[float]) -> dict[str, float]:
    counts = {e: 0.0 for e in ELEMENTS_GENERATIVE}
    for d, w in zip(digits, weights):
        counts[DIGIT_ELEMENT[d]] += w
    return counts


def _balance_score(element_counts: dict[str, float]) -> float:
    values = list(element_counts.values())
    if sum(values) == 0:
        return 0.0
    stdev = statistics.pstdev(values)
    return max(0.0, min(100.0, 100.0 - stdev * BALANCE_STDEV_SCALE))


def _axis_score(
    digits: list[int],
    weights: list[float],
    favored: frozenset[int],
) -> float:
    score = BASELINE
    for d, w in zip(digits, weights):
        if d in favored:
            score += AUSPICIOUS_BONUS_PER_DIGIT * w
        if d in INAUSPICIOUS_DIGITS:
            score -= INAUSPICIOUS_PENALTY_PER_DIGIT * w
    return max(0.0, min(100.0, score))
