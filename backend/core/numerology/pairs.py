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
