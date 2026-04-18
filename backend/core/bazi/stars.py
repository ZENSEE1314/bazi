"""Auxiliary 'stars' (神煞): nobleman, peach blossom, academic star."""

from __future__ import annotations

from .calculator import FourPillars

# --- 天乙贵人 (Nobleman) ---------------------------------------------------
# Keyed by day stem: which earthly branches are noblemen for that stem.
_NOBLEMAN_BY_DAY_STEM: dict[int, frozenset[int]] = {
    0: frozenset({1, 7}),    # 甲 → 丑未
    4: frozenset({1, 7}),    # 戊 → 丑未
    6: frozenset({1, 7}),    # 庚 → 丑未
    1: frozenset({0, 8}),    # 乙 → 子申
    5: frozenset({0, 8}),    # 己 → 子申
    2: frozenset({9, 11}),   # 丙 → 酉亥
    3: frozenset({9, 11}),   # 丁 → 酉亥
    7: frozenset({2, 6}),    # 辛 → 寅午
    8: frozenset({3, 5}),    # 壬 → 卯巳
    9: frozenset({3, 5}),    # 癸 → 卯巳
}

# --- 桃花 (Peach Blossom) — romance/popularity --------------------------
# Keyed by day branch (or year branch in some schools); value: the peach-blossom branch.
_PEACH_BY_DAY_BRANCH: dict[int, int] = {
    # 申子辰 → 酉
    8: 9, 0: 9, 4: 9,
    # 巳酉丑 → 午
    5: 6, 9: 6, 1: 6,
    # 寅午戌 → 卯
    2: 3, 6: 3, 10: 3,
    # 亥卯未 → 子
    11: 0, 3: 0, 7: 0,
}

# --- 文昌 (Academic Star) -----------------------------------------------
_ACADEMIC_BY_DAY_STEM: dict[int, int] = {
    0: 5,   # 甲 → 巳
    1: 6,   # 乙 → 午
    2: 8,   # 丙 → 申
    4: 8,   # 戊 → 申
    3: 9,   # 丁 → 酉
    5: 9,   # 己 → 酉
    6: 11,  # 庚 → 亥
    7: 0,   # 辛 → 子
    8: 2,   # 壬 → 寅
    9: 3,   # 癸 → 卯
}


# --- 驿马 (Sky Horse) — travel, relocation, sudden change -----------------
# Classic formula: opposite branch of the 三合 triad the day branch belongs to.
#   申子辰 (water triad) → 寅
#   亥卯未 (wood triad)  → 巳
#   寅午戌 (fire triad)  → 申
#   巳酉丑 (metal triad) → 亥
_SKY_HORSE_BY_DAY_BRANCH: dict[int, int] = {}
for triad, horse in (
    (frozenset({8, 0, 4}),  2),   # 申子辰 → 寅
    (frozenset({11, 3, 7}), 5),   # 亥卯未 → 巳
    (frozenset({2, 6, 10}), 8),   # 寅午戌 → 申
    (frozenset({5, 9, 1}),  11),  # 巳酉丑 → 亥
):
    for b in triad:
        _SKY_HORSE_BY_DAY_BRANCH[b] = horse


def find_stars(pillars: FourPillars) -> dict[str, list[str]]:
    """Return {star_name: [pillar_labels_where_it_appears]}."""
    dm = pillars.day.stem_index
    day_branch = pillars.day.branch_index

    labelled = [
        ("Year", pillars.year),
        ("Month", pillars.month),
        ("Day", pillars.day),
        ("Hour", pillars.hour),
    ]
    result: dict[str, list[str]] = {
        "nobleman": [],
        "peach_blossom": [],
        "academic": [],
        "sky_horse": [],
    }
    nobleman_branches = _NOBLEMAN_BY_DAY_STEM.get(dm, frozenset())
    peach_branch = _PEACH_BY_DAY_BRANCH.get(day_branch)
    academic_branch = _ACADEMIC_BY_DAY_STEM.get(dm)
    sky_horse_branch = _SKY_HORSE_BY_DAY_BRANCH.get(day_branch)

    for label, p in labelled:
        if p.branch_index in nobleman_branches:
            result["nobleman"].append(label)
        if peach_branch is not None and p.branch_index == peach_branch:
            result["peach_blossom"].append(label)
        if academic_branch is not None and p.branch_index == academic_branch:
            result["academic"].append(label)
        if sky_horse_branch is not None and p.branch_index == sky_horse_branch:
            result["sky_horse"].append(label)

    return result


def star_branches(pillars: FourPillars) -> dict[str, str | None]:
    """Return the 'triggering branch' name for each star, as Chinese character.

    Lets the frontend show `Nobleman: 子, 申` style labels regardless of whether
    the star appears in the chart.
    """
    from .constants import EARTHLY_BRANCHES

    dm = pillars.day.stem_index
    day_branch = pillars.day.branch_index

    nob = sorted(_NOBLEMAN_BY_DAY_STEM.get(dm, frozenset()))
    peach = _PEACH_BY_DAY_BRANCH.get(day_branch)
    academic = _ACADEMIC_BY_DAY_STEM.get(dm)
    sky_horse = _SKY_HORSE_BY_DAY_BRANCH.get(day_branch)

    return {
        "nobleman":      " ".join(EARTHLY_BRANCHES[b] for b in nob) if nob else None,
        "peach_blossom": EARTHLY_BRANCHES[peach] if peach is not None else None,
        "academic":      EARTHLY_BRANCHES[academic] if academic is not None else None,
        "sky_horse":     EARTHLY_BRANCHES[sky_horse] if sky_horse is not None else None,
    }


STAR_HINT = {
    "nobleman": "Nobleman (天乙贵人) — mentors and helpers appear when needed.",
    "peach_blossom": "Peach Blossom (桃花) — magnetism, romantic opportunity, artistic charm.",
    "academic": "Intelligence / Academic (文昌) — learning, literary talent, exam/credential luck.",
    "sky_horse": "Sky Horse (驿马) — travel, relocation, sudden change, international opportunity.",
}
