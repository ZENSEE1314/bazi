"""Ten Gods (十神) — the relationship of every stem to the Day Master.

Rules: comparing any stem X to the Day Master (DM):

    Element relation    | Same polarity       | Opposite polarity
    --------------------+---------------------+----------------------
    Same as DM          | 比肩 Friend         | 劫财 Rob Wealth
    DM produces X       | 食神 Eating God     | 伤官 Hurting Officer
    DM controls X       | 偏财 Indirect Wealth| 正财 Direct Wealth
    X controls DM       | 七杀 Seven Killings | 正官 Direct Officer
    X produces DM       | 偏印 Indirect Res.  | 正印 Direct Resource
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import HEAVENLY_STEMS, HIDDEN_STEMS, STEM_ELEMENT, STEM_YANG

PRODUCES = {"wood": "fire", "fire": "earth", "earth": "metal", "metal": "water", "water": "wood"}
CONTROLS = {"wood": "earth", "fire": "metal", "earth": "water", "metal": "wood", "water": "fire"}

# English names; Chinese names kept for display.
TEN_GODS: dict[str, dict[str, str]] = {
    "friend":            {"cn": "比肩", "en": "Friend"},
    "rob_wealth":        {"cn": "劫财", "en": "Rob Wealth"},
    "eating_god":        {"cn": "食神", "en": "Eating God"},
    "hurting_officer":   {"cn": "伤官", "en": "Hurting Officer"},
    "indirect_wealth":   {"cn": "偏财", "en": "Indirect Wealth"},
    "direct_wealth":     {"cn": "正财", "en": "Direct Wealth"},
    "seven_killings":    {"cn": "七杀", "en": "Seven Killings"},
    "direct_officer":    {"cn": "正官", "en": "Direct Officer"},
    "indirect_resource": {"cn": "偏印", "en": "Indirect Resource"},
    "direct_resource":   {"cn": "正印", "en": "Direct Resource"},
}


def ten_god_for(day_master_stem_index: int, other_stem_index: int) -> str:
    """Return the Ten-God key for ``other_stem`` relative to ``day_master``."""
    dm_elem = STEM_ELEMENT[day_master_stem_index]
    x_elem = STEM_ELEMENT[other_stem_index]
    same_polarity = STEM_YANG[day_master_stem_index] == STEM_YANG[other_stem_index]

    if x_elem == dm_elem:
        return "friend" if same_polarity else "rob_wealth"
    if PRODUCES[dm_elem] == x_elem:
        return "eating_god" if same_polarity else "hurting_officer"
    if CONTROLS[dm_elem] == x_elem:
        return "indirect_wealth" if same_polarity else "direct_wealth"
    if CONTROLS[x_elem] == dm_elem:
        return "seven_killings" if same_polarity else "direct_officer"
    # Remaining: x produces dm
    return "indirect_resource" if same_polarity else "direct_resource"


@dataclass(frozen=True)
class HiddenStemReading:
    stem: str
    stem_pinyin_pos: int  # index in HEAVENLY_STEMS
    element: str
    weight: float
    ten_god_key: str
    ten_god_cn: str
    ten_god_en: str


def branch_hidden_readings(
    branch_index: int, day_master_stem_index: int
) -> list[HiddenStemReading]:
    readings: list[HiddenStemReading] = []
    for stem_idx, weight in HIDDEN_STEMS[branch_index]:
        tg = ten_god_for(day_master_stem_index, stem_idx)
        readings.append(
            HiddenStemReading(
                stem=HEAVENLY_STEMS[stem_idx],
                stem_pinyin_pos=stem_idx,
                element=STEM_ELEMENT[stem_idx],
                weight=weight,
                ten_god_key=tg,
                ten_god_cn=TEN_GODS[tg]["cn"],
                ten_god_en=TEN_GODS[tg]["en"],
            )
        )
    return readings


# Life-area mapping — which Ten Gods govern which life area (traditional view).
AREA_RULERS = {
    "career":       ["direct_officer", "seven_killings"],
    "wealth":       ["direct_wealth", "indirect_wealth"],
    "creativity":   ["eating_god", "hurting_officer"],
    "learning":     ["direct_resource", "indirect_resource"],
    "peers":        ["friend", "rob_wealth"],
}

TEN_GOD_HINT: dict[str, str] = {
    "friend":            "Peers, siblings, partners of equal footing; competition and cooperation both.",
    "rob_wealth":        "Rivals who can help or compete; watch out for shared losses and forceful allies.",
    "eating_god":        "Creativity, output, children, enjoyment; gentle expression of talent.",
    "hurting_officer":   "Bold self-expression, rebellion, original work; clashes with authority if unchecked.",
    "indirect_wealth":   "Unfixed income, speculation, side ventures; windfalls and fast money.",
    "direct_wealth":     "Stable income, spouse (for male), steady accumulation, responsibility.",
    "seven_killings":    "Authority, discipline, pressure, competitive drive; leadership under stress.",
    "direct_officer":    "Official position, reputation, law & order, spouse (for female).",
    "indirect_resource": "Stepmother figures, alternative learning, intuition, occult study.",
    "direct_resource":   "Mother, formal education, support, documents, status via credentials.",
}
