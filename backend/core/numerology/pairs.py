"""Ba Zhai / He Luo-style pair interpretations and Life Path number."""

from __future__ import annotations

from dataclasses import dataclass

# Eight-Mansions pair categories. Each two-digit combination (unordered) maps
# to one of eight categories, four auspicious and four inauspicious.
#
#   Auspicious:
#     生气 Sheng Qi  — Life Force / Wealth
#     延年 Yan Nian  — Longevity / Stability
#     天医 Tian Yi   — Heavenly Doctor / Health
#     伏位 Fu Wei    — Stability / Self-seat
#
#   Inauspicious:
#     绝命 Jue Ming  — Disaster / Loss
#     五鬼 Wu Gui    — Five Ghosts / Loss of wealth
#     六煞 Liu Sha   — Six Killings / Relationship strain
#     祸害 Huo Hai   — Mishap / Small troubles
#
# Digits map to the Eight Trigrams by Lo-Shu positions:
#   1=坎 Water  2=坤 Earth  3=震 Wood   4=巽 Wood
#   6=乾 Metal  7=兑 Metal  8=艮 Earth  9=离 Fire
#   5 and 0 are treated as neutral "earth-core" in this simplified model.

AUSPICIOUS_CATEGORIES = {"sheng_qi", "yan_nian", "tian_yi", "fu_wei"}
INAUSPICIOUS_CATEGORIES = {"jue_ming", "wu_gui", "liu_sha", "huo_hai"}

_PAIR_CATEGORY: dict[frozenset[int], str] = {
    # 生气 Sheng Qi
    frozenset({1, 4}): "sheng_qi",
    frozenset({9, 7}): "sheng_qi",
    frozenset({2, 8}): "sheng_qi",
    frozenset({3, 6}): "sheng_qi",
    # 延年 Yan Nian
    frozenset({1, 9}): "yan_nian",
    frozenset({8, 7}): "yan_nian",
    frozenset({2, 3}): "yan_nian",
    frozenset({4, 6}): "yan_nian",
    # 天医 Tian Yi
    frozenset({1, 6}): "tian_yi",
    frozenset({9, 8}): "tian_yi",
    frozenset({2, 7}): "tian_yi",
    frozenset({3, 4}): "tian_yi",
    # 伏位 Fu Wei (same trigram — same digits)
    # handled dynamically below
    # 绝命 Jue Ming
    frozenset({1, 2}): "jue_ming",
    frozenset({9, 6}): "jue_ming",
    frozenset({3, 7}): "jue_ming",
    frozenset({4, 8}): "jue_ming",
    # 五鬼 Wu Gui
    frozenset({1, 3}): "wu_gui",
    frozenset({9, 2}): "wu_gui",
    frozenset({4, 7}): "wu_gui",
    frozenset({6, 8}): "wu_gui",
    # 六煞 Liu Sha
    frozenset({1, 7}): "liu_sha",
    frozenset({9, 4}): "liu_sha",
    frozenset({2, 6}): "liu_sha",
    frozenset({3, 8}): "liu_sha",
    # 祸害 Huo Hai
    frozenset({1, 8}): "huo_hai",
    frozenset({9, 3}): "huo_hai",
    frozenset({2, 4}): "huo_hai",
    frozenset({6, 7}): "huo_hai",
}

CATEGORY_INFO: dict[str, dict[str, str]] = {
    "sheng_qi":  {"cn": "生气", "en": "Sheng Qi — Life Force",  "theme": "opportunity, wealth, vitality"},
    "yan_nian":  {"cn": "延年", "en": "Yan Nian — Longevity",   "theme": "stability, commitment, long-term gain"},
    "tian_yi":   {"cn": "天医", "en": "Tian Yi — Health",       "theme": "healing, protection, support networks"},
    "fu_wei":    {"cn": "伏位", "en": "Fu Wei — Self-Seat",     "theme": "calm, steady, small but stable"},
    "jue_ming":  {"cn": "绝命", "en": "Jue Ming — Disaster",    "theme": "crisis, loss, major setbacks"},
    "wu_gui":    {"cn": "五鬼", "en": "Wu Gui — Five Ghosts",   "theme": "financial leaks, gossip, disputes"},
    "liu_sha":   {"cn": "六煞", "en": "Liu Sha — Six Killings", "theme": "relationship strain, arguments"},
    "huo_hai":   {"cn": "祸害", "en": "Huo Hai — Mishap",       "theme": "small troubles, delays, irritations"},
}


@dataclass(frozen=True)
class PairReading:
    a: int
    b: int
    category_key: str
    category_cn: str
    category_en: str
    theme: str
    auspicious: bool


def pair_category(a: int, b: int) -> PairReading | None:
    if a == b:
        info = CATEGORY_INFO["fu_wei"]
        return PairReading(a, b, "fu_wei", info["cn"], info["en"], info["theme"], True)
    key = _PAIR_CATEGORY.get(frozenset({a, b}))
    if key is None:
        # 5 and 0 are neutral — treat as 伏位-like in this simplified model.
        if 5 in (a, b) or 0 in (a, b):
            info = CATEGORY_INFO["fu_wei"]
            return PairReading(a, b, "fu_wei", info["cn"], info["en"], info["theme"], True)
        return None
    info = CATEGORY_INFO[key]
    return PairReading(
        a, b, key, info["cn"], info["en"], info["theme"],
        auspicious=key in AUSPICIOUS_CATEGORIES,
    )


def analyse_pairs(number: str) -> list[PairReading]:
    """Walk consecutive digit pairs left→right and return their readings."""
    digits = [int(c) for c in number if c.isdigit()]
    out: list[PairReading] = []
    for i in range(len(digits) - 1):
        r = pair_category(digits[i], digits[i + 1])
        if r is not None:
            out.append(r)
    return out


def life_path(number: str) -> int:
    """Reduce the digit sum to a single digit (with no master-number shortcut)."""
    digits = [int(c) for c in number if c.isdigit()]
    if not digits:
        raise ValueError("Number must contain at least one digit")
    n = sum(digits)
    while n >= 10:
        n = sum(int(c) for c in str(n))
    return n


# Trigrams per digit (1-9). 5/0 are neutral earth-core in this simplified model.
DIGIT_TRIGRAM: dict[int, dict[str, str]] = {
    1: {"cn": "坎", "en": "Kan",  "element": "water"},
    2: {"cn": "坤", "en": "Kun",  "element": "earth"},
    3: {"cn": "震", "en": "Zhen", "element": "wood"},
    4: {"cn": "巽", "en": "Xun",  "element": "wood"},
    6: {"cn": "乾", "en": "Qian", "element": "metal"},
    7: {"cn": "兑", "en": "Dui",  "element": "metal"},
    8: {"cn": "艮", "en": "Gen",  "element": "earth"},
    9: {"cn": "离", "en": "Li",   "element": "fire"},
}


def explain_pair(a: int, b: int) -> str:
    """Narrative explanation of WHY a digit pair is auspicious or inauspicious."""
    reading = pair_category(a, b)
    if reading is None:
        return f"{a}-{b}: neutral (5/0 act as earth-core flow)."
    if a == b:
        return (
            f"{a}-{b} repeats the same energy — 伏位 (Self-Seat): calm stability. "
            "Predictable but not growth-oriented."
        )
    ta = DIGIT_TRIGRAM.get(a)
    tb = DIGIT_TRIGRAM.get(b)
    if not ta or not tb:
        return f"{a}-{b}: neutral — one digit is 5 or 0 (earth-core amplifier)."

    base = f"{a} ({ta['cn']} {ta['en']}, {ta['element']}) + {b} ({tb['cn']} {tb['en']}, {tb['element']}): "
    key = reading.category_key

    why = {
        "sheng_qi": "生气 — {ea}+{eb} form the Sheng Qi life-force axis across the 8-trigrams, the most potent wealth/opportunity combination. Promotes expansion, income growth, fertility of ideas.",
        "yan_nian": "延年 — {ea}+{eb} form Yan Nian stability axis. Slow, committed, long-term energy. Good for marriage, mortgages, enduring partnerships.",
        "tian_yi": "天医 — {ea}+{eb} form Tian Yi healing axis. Promotes health, recovery, timely helpers appearing in crises.",
        "fu_wei": "伏位 — same/similar positions form Fu Wei self-seat. Calm, stable, low-growth — good for rest, bad for ambition.",
        "jue_ming": "绝命 — {ea} and {eb} sit in direct elemental opposition (the Jue Ming disaster axis). Multiplies risk of loss and health shock. Strongest inauspicious pairing.",
        "wu_gui": "五鬼 — {ea}+{eb} forms the Five Ghosts axis. Money leaks, gossip, petty disputes. Small drains that compound.",
        "liu_sha": "六煞 — {ea}+{eb} forms the Six Killings axis. Relationship strain, arguments, heated emotional spillover.",
        "huo_hai": "祸害 — {ea}+{eb} forms the Huo Hai mishap axis. Small irritations, delays, minor accidents — rarely catastrophic but wearying over time.",
    }
    template = why.get(key, "")
    return base + template.format(ea=ta["element"], eb=tb["element"])


AUSPICIOUS_TARGETS = ("sheng_qi", "yan_nian", "tian_yi")


def suggest_replacement(existing_digit: int, target_categories: tuple[str, ...] = AUSPICIOUS_TARGETS) -> list[dict]:
    """Given an existing digit, return a list of better partner digits ranked by quality.

    Returns up to 4 suggestions, best first.
    """
    results: list[dict] = []
    for d in range(10):
        if d == existing_digit:
            continue
        reading = pair_category(existing_digit, d)
        if reading is None:
            continue
        if reading.category_key in target_categories:
            # Prioritise sheng_qi > yan_nian > tian_yi
            rank = target_categories.index(reading.category_key)
            results.append({
                "digit": d,
                "rank": rank,
                "category_cn": reading.category_cn,
                "category_en": reading.category_en,
                "theme": reading.theme,
            })
    results.sort(key=lambda r: r["rank"])
    return results[:4]


def suggest_better_number(number: str, useful_god_element: str | None = None) -> dict:
    """Given a number, suggest targeted replacements for its weakest digit pairs.

    Returns {"original": str, "issues": list, "suggestions": list[str]}.
    Each suggestion is a full candidate number where we've swapped the single
    worst digit for a better alternative. When useful_god_element is provided,
    prefer replacements that contain the element-favored digits.
    """
    digits = [int(c) for c in number if c.isdigit()]
    if not digits:
        raise ValueError("Number must contain at least one digit")

    # Identify the worst pair (inauspicious closest to the tail — tail is most impactful).
    worst_index: int | None = None
    worst_reading = None
    for i in range(len(digits) - 1):
        r = pair_category(digits[i], digits[i + 1])
        if r is None or r.auspicious:
            continue
        if worst_index is None or i > worst_index:
            worst_index = i
            worst_reading = r

    issues: list[str] = []
    suggestions: list[str] = []
    if worst_index is None:
        return {
            "original": number,
            "issues": ["All pairs already lean auspicious — no strong changes needed."],
            "suggestions": [],
        }

    a, b = digits[worst_index], digits[worst_index + 1]
    issues.append(
        f"Position {worst_index + 1}-{worst_index + 2}: digits {a}-{b} form "
        f"{worst_reading.category_cn} {worst_reading.category_en} — {worst_reading.theme}"
    )

    # Try replacing the SECOND digit of the worst pair (keeping earlier positions).
    alts = suggest_replacement(a)
    # If Useful-God preference exists, promote element-favored digits.
    from ..bazi.guidance import ELEMENT_GUIDANCE
    favored = set()
    if useful_god_element and useful_god_element in ELEMENT_GUIDANCE:
        favored = set(ELEMENT_GUIDANCE[useful_god_element].get("numbers", []))
    alts.sort(key=lambda r: (0 if r["digit"] in favored else 1, r["rank"]))

    for alt in alts[:3]:
        new_digits = list(digits)
        new_digits[worst_index + 1] = alt["digit"]
        suggestions.append(
            "".join(str(d) for d in new_digits) +
            f"   (swap {b}→{alt['digit']}: now {alt['category_cn']} {alt['category_en']})"
        )

    return {
        "original": number,
        "issues": issues,
        "suggestions": suggestions,
    }


LIFE_PATH_THEMES: dict[int, str] = {
    1: "Leadership, initiative, pioneering — built to start things.",
    2: "Partnership, diplomacy, sensitivity — built to harmonize and mediate.",
    3: "Expression, creativity, joy — built to communicate and inspire.",
    4: "Discipline, structure, foundation — built to build and stabilize.",
    5: "Freedom, change, adventure — built to adapt and explore.",
    6: "Responsibility, family, care — built to nurture and serve.",
    7: "Analysis, depth, inner work — built to investigate and know.",
    8: "Power, wealth, enterprise — built to organize value at scale.",
    9: "Humanitarian, closure, wisdom — built to complete cycles and give back.",
}
