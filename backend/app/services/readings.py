"""Wraps the pure calculation engines as API-shaped responses."""

from __future__ import annotations

from datetime import datetime

from ...core.bazi.calculator import FourPillars, Pillar, four_pillars
from ...core.bazi.constants import BRANCH_PINYIN, STEM_PINYIN
from ...core.bazi.elements import element_balance
from ..schemas import (
    BaZiReading,
    CompatibilityReading,
    DailyLuck,
    NumerologyReading,
    Pillar as PillarSchema,
)
from ...core.numerology.scorer import score_number

# 五行生克: productive (生) and destructive (克) cycles.
PRODUCES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}
DESTROYS = {
    "wood": "earth",
    "fire": "metal",
    "earth": "water",
    "metal": "wood",
    "water": "fire",
}


def _pillar_schema(p: Pillar) -> PillarSchema:
    return PillarSchema(
        stem=p.stem,
        branch=p.branch,
        stem_element=p.stem_element,
        branch_element=p.branch_element,
        pinyin=f"{STEM_PINYIN[p.stem_index]} {BRANCH_PINYIN[p.branch_index]}",
    )


def build_bazi_reading(birth: datetime) -> BaZiReading:
    fp = four_pillars(birth)
    bal = element_balance(fp)
    return BaZiReading(
        year=_pillar_schema(fp.year),
        month=_pillar_schema(fp.month),
        day=_pillar_schema(fp.day),
        hour=_pillar_schema(fp.hour),
        day_master=fp.day_master,
        day_master_element=fp.day_master_element,
        zodiac=fp.zodiac,
        elements=bal.as_dict,
        dominant_element=bal.dominant(),
        weakest_element=bal.weakest(),
    )


def build_numerology_reading(number: str) -> NumerologyReading:
    s = score_number(number)
    return NumerologyReading(
        wealth=s.wealth,
        safety=s.safety,
        health=s.health,
        overall=s.overall,
        dominant_element=s.dominant_element,
        element_counts=s.element_counts,
    )


def build_daily_luck(birth: datetime, today: datetime) -> DailyLuck:
    """Luck for *today* relative to the person's birth Day Master."""
    user_fp = four_pillars(birth)
    user_element = user_fp.day_master_element

    day_fp = four_pillars(today)
    day_stem_element = day_fp.day.stem_element
    day_branch_element = day_fp.day.branch_element

    score = 50
    supportive: list[str] = []
    clashing: list[str] = []

    for label, day_elem in (("stem", day_stem_element), ("branch", day_branch_element)):
        if day_elem == user_element:
            score += 15
            supportive.append(f"Day {label} shares your element ({day_elem}).")
        elif PRODUCES[day_elem] == user_element:
            score += 18
            supportive.append(f"Day {label} {day_elem} nourishes your {user_element}.")
        elif PRODUCES[user_element] == day_elem:
            score += 6
            supportive.append(f"You give to today's {day_elem} — expect outflow.")
        elif DESTROYS[day_elem] == user_element:
            score -= 18
            clashing.append(f"Day {label} {day_elem} controls your {user_element}.")
        elif DESTROYS[user_element] == day_elem:
            score -= 4
            clashing.append(f"You push against today's {day_elem}.")

    score = max(0, min(100, score))

    if score >= 75:
        summary = "Strong supportive day. Push on what matters."
    elif score >= 60:
        summary = "Favorable flow. Good for decisions and meetings."
    elif score >= 45:
        summary = "Neutral day. Steady progress, no heroics."
    elif score >= 30:
        summary = "Friction. Move carefully; avoid confrontations."
    else:
        summary = "Heavy day. Rest, reflect, postpone big moves."

    return DailyLuck(
        date=today.date().isoformat(),
        day_pillar=_pillar_schema(day_fp.day),
        score=score,
        summary=summary,
        supportive_elements=supportive,
        clashing_elements=clashing,
    )


def build_compatibility(birth_a: datetime, birth_b: datetime) -> CompatibilityReading:
    fp_a = four_pillars(birth_a)
    fp_b = four_pillars(birth_b)

    bal_a = element_balance(fp_a).as_dict
    bal_b = element_balance(fp_b).as_dict

    # Element blend: weaker side gets lifted by partner's dominant.
    blend = {e: round(bal_a[e] + bal_b[e], 2) for e in bal_a}

    dm_a = fp_a.day_master_element
    dm_b = fp_b.day_master_element

    score = 55
    harmony: list[str] = []
    tension: list[str] = []

    if dm_a == dm_b:
        score += 10
        harmony.append(f"Shared Day Master element ({dm_a}): natural affinity, similar instincts.")
    elif PRODUCES[dm_a] == dm_b or PRODUCES[dm_b] == dm_a:
        score += 20
        feeder = dm_a if PRODUCES[dm_a] == dm_b else dm_b
        fed = dm_b if PRODUCES[dm_a] == dm_b else dm_a
        harmony.append(f"{feeder.title()} nourishes {fed}: one partner energizes the other.")
    elif DESTROYS[dm_a] == dm_b or DESTROYS[dm_b] == dm_a:
        score -= 18
        aggressor = dm_a if DESTROYS[dm_a] == dm_b else dm_b
        target = dm_b if DESTROYS[dm_a] == dm_b else dm_a
        tension.append(f"{aggressor.title()} controls {target}: friction around leadership and pace.")

    # Fill-the-gap bonus: if A's weakest is B's dominant, or vice versa.
    weak_a = min(bal_a, key=bal_a.get)
    weak_b = min(bal_b, key=bal_b.get)
    dom_a = max(bal_a, key=bal_a.get)
    dom_b = max(bal_b, key=bal_b.get)
    if dom_b == weak_a:
        score += 8
        harmony.append(f"Partner's {dom_b} fills your gap in {weak_a}.")
    if dom_a == weak_b:
        score += 8
        harmony.append(f"Your {dom_a} fills partner's gap in {weak_b}.")

    shared_dominant = dom_a if dom_a == dom_b else None
    if shared_dominant:
        harmony.append(f"Both lean heavily on {shared_dominant}: aligned strengths, shared blind spots.")

    score = max(0, min(100, score))

    if score >= 80:
        summary = "Highly compatible — complementary energies."
    elif score >= 65:
        summary = "Strong match with room to grow."
    elif score >= 50:
        summary = "Workable — requires conscious effort on friction points."
    elif score >= 35:
        summary = "Challenging — significant elemental tension."
    else:
        summary = "Difficult pairing — needs deep compromise."

    return CompatibilityReading(
        score=score,
        summary=summary,
        harmony=harmony,
        tension=tension,
        shared_dominant=shared_dominant,
        element_blend=blend,
    )
