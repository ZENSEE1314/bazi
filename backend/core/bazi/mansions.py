"""Eight Mansions (八宅) direction tables for each Life Kua.

Four auspicious directions:
    生气 Sheng Qi   — Wealth / Vitality (strongest positive)
    天医 Tian Yi    — Health / Helpful people
    延年 Yan Nian   — Longevity / Relationships
    伏位 Fu Wei     — Stability / Career groundedness

Four inauspicious directions:
    绝命 Jue Ming   — Total Loss (strongest negative)
    五鬼 Wu Gui     — Setbacks / Illness / Disputes
    六煞 Liu Sha    — Quarrels / Relationship loss
    祸害 Huo Hai    — Mishaps / Obstacles
"""

from __future__ import annotations

DIRECTION_NAMES = {
    "N": "North", "NE": "Northeast", "E": "East", "SE": "Southeast",
    "S": "South", "SW": "Southwest", "W": "West", "NW": "Northwest",
}

LUCKY_CATEGORIES = {
    "sheng_qi": {"cn": "生气", "en": "Sheng Qi",  "meaning": "Wealth & vitality"},
    "tian_yi":  {"cn": "天医", "en": "Tian Yi",   "meaning": "Health & helpful people"},
    "yan_nian": {"cn": "延年", "en": "Yan Nian",  "meaning": "Longevity & relationships / romance"},
    "fu_wei":   {"cn": "伏位", "en": "Fu Wei",    "meaning": "Stability & career"},
}

UNLUCKY_CATEGORIES = {
    "jue_ming": {"cn": "绝命", "en": "Jue Ming",  "meaning": "Total loss / health disaster"},
    "wu_gui":   {"cn": "五鬼", "en": "Wu Gui",    "meaning": "Setbacks, disputes, illness"},
    "liu_sha":  {"cn": "六煞", "en": "Liu Sha",   "meaning": "Quarrels, relationship loss"},
    "huo_hai":  {"cn": "祸害", "en": "Huo Hai",   "meaning": "Mishaps, obstacles"},
}

# For each Kua number, map each of the eight categories to a compass direction.
_TABLE: dict[int, dict[str, str]] = {
    # East group: Kuas 1, 3, 4, 9
    1: {  # 坎 Kan (N)
        "sheng_qi": "SE", "yan_nian": "S",  "tian_yi": "E",  "fu_wei": "N",
        "jue_ming": "SW", "huo_hai": "W",   "wu_gui":  "NE", "liu_sha": "NW",
    },
    3: {  # 震 Zhen (E)
        "sheng_qi": "S",  "yan_nian": "SE", "tian_yi": "N",  "fu_wei": "E",
        "jue_ming": "W",  "huo_hai": "SW",  "wu_gui":  "NE", "liu_sha": "NW",
    },
    4: {  # 巽 Xun (SE)
        "sheng_qi": "N",  "yan_nian": "E",  "tian_yi": "S",  "fu_wei": "SE",
        "jue_ming": "NE", "huo_hai": "NW",  "wu_gui":  "SW", "liu_sha": "W",
    },
    9: {  # 离 Li (S)
        "sheng_qi": "E",  "yan_nian": "N",  "tian_yi": "SE", "fu_wei": "S",
        "jue_ming": "NW", "huo_hai": "NE",  "wu_gui":  "W",  "liu_sha": "SW",
    },
    # West group: Kuas 2, 6, 7, 8
    2: {  # 坤 Kun (SW)
        "sheng_qi": "NE", "yan_nian": "NW", "tian_yi": "W",  "fu_wei": "SW",
        "jue_ming": "N",  "huo_hai": "S",   "wu_gui":  "SE", "liu_sha": "E",
    },
    6: {  # 乾 Qian (NW)
        "sheng_qi": "W",  "yan_nian": "SW", "tian_yi": "NE", "fu_wei": "NW",
        "jue_ming": "S",  "huo_hai": "N",   "wu_gui":  "SE", "liu_sha": "E",
    },
    7: {  # 兑 Dui (W)
        "sheng_qi": "NW", "yan_nian": "NE", "tian_yi": "SW", "fu_wei": "W",
        "jue_ming": "E",  "huo_hai": "SE",  "wu_gui":  "N",  "liu_sha": "S",
    },
    8: {  # 艮 Gen (NE)
        "sheng_qi": "SW", "yan_nian": "W",  "tian_yi": "NW", "fu_wei": "NE",
        "jue_ming": "SE", "huo_hai": "E",   "wu_gui":  "S",  "liu_sha": "N",
    },
}


def mansions_for(kua: int) -> dict[str, dict]:
    """Return lucky/unlucky direction maps for a Kua.

    Result shape:
        {
          "lucky":   {"S": {"cat": "sheng_qi", "cn": ..., "meaning": ...}, ...},
          "unlucky": {"W": {"cat": "jue_ming", ...}, ...},
        }
    """
    if kua not in _TABLE:
        raise ValueError(f"Invalid Kua {kua}")
    mapping = _TABLE[kua]
    lucky: dict[str, dict] = {}
    unlucky: dict[str, dict] = {}
    for cat, direction in mapping.items():
        if cat in LUCKY_CATEGORIES:
            info = LUCKY_CATEGORIES[cat]
            lucky[direction] = {
                "category_key": cat, "cn": info["cn"], "en": info["en"],
                "meaning": info["meaning"], "direction_name": DIRECTION_NAMES[direction],
            }
        else:
            info = UNLUCKY_CATEGORIES[cat]
            unlucky[direction] = {
                "category_key": cat, "cn": info["cn"], "en": info["en"],
                "meaning": info["meaning"], "direction_name": DIRECTION_NAMES[direction],
            }
    return {"lucky": lucky, "unlucky": unlucky}
