"""Branch relationships in a Ba Zi chart: clashes, combinations, punishments."""

from __future__ import annotations

from itertools import combinations

from .calculator import FourPillars
from .constants import EARTHLY_BRANCHES

# --- 六冲 (Six Clashes) — direct 180° oppositions ------------------------
SIX_CLASHES: frozenset[frozenset[int]] = frozenset({
    frozenset({0, 6}),    # 子 午
    frozenset({1, 7}),    # 丑 未
    frozenset({2, 8}),    # 寅 申
    frozenset({3, 9}),    # 卯 酉
    frozenset({4, 10}),   # 辰 戌
    frozenset({5, 11}),   # 巳 亥
})

# --- 六合 (Six Combinations) — harmonious pairs; value = resulting element
SIX_COMBINATIONS: dict[frozenset[int], str] = {
    frozenset({0, 1}):  "earth",   # 子 丑
    frozenset({2, 11}): "wood",    # 寅 亥
    frozenset({3, 10}): "fire",    # 卯 戌
    frozenset({4, 9}):  "metal",   # 辰 酉
    frozenset({5, 8}):  "water",   # 巳 申
    frozenset({6, 7}):  "earth",   # 午 未 (fire-earth, dominant earth)
}

# --- 三合 (Three Harmony) — transforming triads; value = resulting element
THREE_HARMONY: dict[frozenset[int], str] = {
    frozenset({8, 0, 4}):  "water",   # 申 子 辰
    frozenset({5, 9, 1}):  "metal",   # 巳 酉 丑
    frozenset({2, 6, 10}): "fire",    # 寅 午 戌
    frozenset({11, 3, 7}): "wood",    # 亥 卯 未
}

# --- 方合 (Directional combinations) — seasonal triads
DIRECTIONAL: dict[frozenset[int], str] = {
    frozenset({11, 0, 1}): "water",   # 亥子丑 winter
    frozenset({2, 3, 4}):  "wood",    # 寅卯辰 spring
    frozenset({5, 6, 7}):  "fire",    # 巳午未 summer
    frozenset({8, 9, 10}): "metal",   # 申酉戌 autumn
}

# --- 三刑 (Three Punishments)
THREE_PUNISHMENTS: list[frozenset[int]] = [
    frozenset({2, 5, 8}),   # 寅巳申 (no-gratitude punishment)
    frozenset({1, 10, 7}),  # 丑戌未 (relying-on-power punishment)
]
SELF_PUNISHMENT_PAIRS: frozenset[frozenset[int]] = frozenset({
    frozenset({0, 3}),   # 子卯 (rude punishment)
})
SELF_PUNISHMENT_SINGLES = {4, 6, 9, 11}  # 辰午酉亥 punish themselves when paired


def chart_relations(pillars: FourPillars) -> dict[str, list[dict]]:
    """Detect relationships among the four branch pillars of a chart.

    Returns a dict with keys: ``clashes``, ``combinations``, ``three_harmony``,
    ``directional``, ``punishments``. Each value is a list of dicts describing
    the relationship.
    """
    labelled = [
        ("Year", pillars.year.branch_index),
        ("Month", pillars.month.branch_index),
        ("Day", pillars.day.branch_index),
        ("Hour", pillars.hour.branch_index),
    ]
    branches = {label: b for label, b in labelled}
    all_branches = set(branches.values())

    clashes = []
    combos = []
    punishments = []
    for (la, ba), (lb, bb) in combinations(labelled, 2):
        pair = frozenset({ba, bb})
        if pair in SIX_CLASHES:
            clashes.append({
                "pillars": [la, lb],
                "branches": [EARTHLY_BRANCHES[ba], EARTHLY_BRANCHES[bb]],
                "note": "Direct clash (六冲): volatile polarity between these life areas.",
            })
        if pair in SIX_COMBINATIONS:
            combos.append({
                "kind": "six_combination",
                "pillars": [la, lb],
                "branches": [EARTHLY_BRANCHES[ba], EARTHLY_BRANCHES[bb]],
                "transforms_to": SIX_COMBINATIONS[pair],
                "note": f"Harmonious pair (六合) → {SIX_COMBINATIONS[pair]}.",
            })
        if pair in SELF_PUNISHMENT_PAIRS:
            punishments.append({
                "pillars": [la, lb],
                "branches": [EARTHLY_BRANCHES[ba], EARTHLY_BRANCHES[bb]],
                "kind": "rude",
                "note": "Rude punishment (无礼之刑): friction in etiquette / boundaries.",
            })

    # self punishments: same branch appears twice among the four pillars, and
    # that branch is in SELF_PUNISHMENT_SINGLES.
    seen: dict[int, list[str]] = {}
    for la, ba in labelled:
        seen.setdefault(ba, []).append(la)
    for b, labels in seen.items():
        if len(labels) >= 2 and b in SELF_PUNISHMENT_SINGLES:
            punishments.append({
                "pillars": labels,
                "branches": [EARTHLY_BRANCHES[b]] * len(labels),
                "kind": "self",
                "note": "Self punishment (自刑): internal conflict or self-sabotage.",
            })

    three_harmony = []
    for triad, element in THREE_HARMONY.items():
        if triad.issubset(all_branches):
            three_harmony.append({
                "branches": [EARTHLY_BRANCHES[b] for b in triad],
                "transforms_to": element,
                "note": f"Three Harmony (三合) → {element}: strong coherent force.",
            })

    directional = []
    for triad, element in DIRECTIONAL.items():
        if triad.issubset(all_branches):
            directional.append({
                "branches": [EARTHLY_BRANCHES[b] for b in triad],
                "transforms_to": element,
                "note": f"Directional (方合) → {element}: seasonal concentration.",
            })

    # Three-branch punishments
    for triad in THREE_PUNISHMENTS:
        if triad.issubset(all_branches):
            punishments.append({
                "pillars": [la for la, ba in labelled if ba in triad],
                "branches": [EARTHLY_BRANCHES[b] for b in triad],
                "kind": "three-way",
                "note": "Three Punishments (三刑): complex conflict, power struggle.",
            })

    return {
        "clashes": clashes,
        "combinations": combos,
        "three_harmony": three_harmony,
        "directional": directional,
        "punishments": punishments,
    }
