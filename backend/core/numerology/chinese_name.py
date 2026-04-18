"""Chinese name analysis using stroke-count (五格 5-Grids) system.

Traditional 81-stroke-number interpretation reduces every grid number to the
1..81 table. We approximate stroke counts via a common-character table; rare
characters fall back to a pragmatic estimate.

Grids:
    天格 Heaven (Tian Ge)  = surname strokes + 1
    人格 Person (Ren Ge)   = last surname char + first given-name char
    地格 Earth (Di Ge)     = given-name strokes (+1 if single given name)
    总格 Total (Zong Ge)   = all strokes
    外格 Outer (Wai Ge)    = Total - Person + 1
"""

from __future__ import annotations

from dataclasses import dataclass

from .pairs import life_path  # reused digit-sum reduction

# --- Common-character stroke table --------------------------------------
# Covers the ~200 most common surname & given-name characters. Not exhaustive;
# callers should accept that rare chars fall back to a heuristic.
# Sources cross-checked against standard stroke-count tables.
_STROKES: dict[str, int] = {
    # surnames (百家姓 top)
    "王": 4, "李": 7, "张": 7, "刘": 6, "陈": 7, "杨": 7, "黄": 11, "赵": 9,
    "吴": 7, "周": 8, "徐": 10, "孙": 6, "马": 3, "朱": 6, "胡": 9, "郭": 11,
    "何": 7, "高": 10, "林": 8, "罗": 8, "郑": 8, "梁": 11, "谢": 12, "宋": 7,
    "唐": 10, "许": 6, "邓": 5, "冯": 5, "韩": 12, "曹": 11, "曾": 12, "彭": 12,
    "萧": 12, "蔡": 14, "潘": 15, "田": 5, "董": 12, "袁": 10, "于": 3, "余": 7,
    "叶": 5, "蒋": 13, "杜": 7, "苏": 7, "魏": 17, "程": 12, "吕": 6, "丁": 2,
    "沈": 7, "任": 6, "姚": 9, "卢": 5, "傅": 12, "钟": 9, "姜": 9, "崔": 11,
    "谭": 14, "廖": 14, "范": 8, "汪": 7, "陆": 7, "金": 8, "石": 5, "戴": 17,
    "贾": 10, "韦": 4, "夏": 10, "邱": 7, "方": 4, "侯": 9, "邹": 7, "熊": 14,
    "孟": 8, "秦": 10, "白": 5, "江": 6, "阎": 11, "薛": 16, "尹": 4, "段": 9,
    "雷": 13, "黎": 15, "史": 5, "龙": 5, "陶": 10, "贺": 9, "顾": 10, "毛": 4,
    "郝": 9, "龚": 11, "邵": 7, "万": 3, "钱": 10, "严": 7, "覃": 12, "武": 8,
    # common given-name chars
    "一": 1, "乙": 1, "二": 2, "人": 2, "三": 3, "大": 3, "小": 3, "子": 3,
    "上": 3, "下": 3, "千": 3, "山": 3, "川": 3, "之": 4, "天": 4, "心": 4,
    "中": 4, "水": 4, "元": 4, "文": 4, "月": 4, "木": 4, "父": 4, "风": 4,
    "仁": 4, "仆": 4, "化": 4, "反": 4, "介": 4, "云": 4, "玉": 5, "平": 5,
    "永": 5, "世": 5, "以": 5, "正": 5, "出": 5, "北": 5, "古": 5, "可": 5,
    "右": 5, "生": 5, "圣": 5, "本": 5, "民": 5, "甘": 5, "史": 5, "立": 5,
    "光": 6, "地": 6, "同": 6, "好": 6, "如": 6, "宇": 6, "守": 6, "安": 6,
    "年": 6, "早": 6, "有": 6, "行": 6, "西": 6, "先": 6, "向": 6, "成": 6,
    "冰": 6, "竹": 6, "米": 6, "全": 6, "名": 6, "合": 6, "吉": 6, "地": 6,
    "我": 7, "言": 7, "秀": 7, "男": 7, "里": 7, "步": 7, "伸": 7, "伯": 7,
    "伶": 7, "似": 7, "伴": 7, "佑": 7, "佛": 7, "位": 7, "志": 7, "花": 8,
    "芳": 7, "苏": 7, "英": 8, "明": 8, "昕": 8, "昊": 8, "昆": 8, "昇": 8,
    "佳": 8, "依": 8, "使": 8, "来": 7, "征": 8, "承": 8, "青": 8, "奇": 8,
    "松": 8, "林": 8, "易": 8, "昌": 8, "尚": 8, "宙": 8, "定": 8, "宜": 8,
    "宝": 8, "忠": 8, "欣": 8, "泉": 9, "洪": 9, "泰": 9, "宣": 9, "宪": 9,
    "帅": 9, "幽": 9, "建": 9, "弈": 9, "思": 9, "恒": 9, "星": 9, "春": 9,
    "秋": 9, "美": 9, "南": 9, "相": 9, "柯": 9, "柔": 9, "柏": 9, "架": 9,
    "信": 9, "修": 10, "倩": 10, "凌": 10, "峰": 10, "宸": 10, "家": 10, "容": 10,
    "展": 10, "峻": 10, "师": 10, "海": 10, "涛": 10, "浪": 10, "珊": 10, "珍": 10,
    "珂": 10, "真": 10, "祖": 10, "祝": 10, "笑": 10, "纯": 9, "紫": 12, "素": 10,
    "耕": 10, "致": 10, "航": 10, "莉": 11, "健": 11, "凯": 12, "博": 12, "梦": 11,
    "敏": 11, "琴": 12, "琪": 12, "琦": 12, "翔": 12, "晶": 12, "惠": 12, "棒": 12,
    "森": 12, "童": 12, "翔": 12, "雅": 12, "智": 12, "祥": 10, "菁": 13, "嘉": 14,
    "诚": 13, "福": 13, "榕": 14, "睿": 14, "豪": 14, "梓": 11, "瑾": 15, "瑶": 14,
    "璇": 15, "慧": 15, "霖": 16, "颖": 16, "静": 14, "燕": 16, "蓉": 14, "艳": 10,
    "鑫": 24, "馨": 20, "怡": 8, "诗": 13, "欣": 8, "悦": 10, "妍": 7, "瑞": 13,
    "涵": 11, "晨": 11, "昱": 9, "铭": 11, "梓": 11, "雨": 8, "雪": 11, "云": 4,
    "龙": 5, "航": 10, "泽": 8, "子": 3, "轩": 7, "浩": 10, "宇": 6, "睿": 14,
    "彦": 9, "逸": 11, "锦": 13, "鸿": 11, "雯": 12, "婷": 12, "洁": 9, "薇": 16,
    "琬": 12, "佩": 8, "嫣": 14, "娜": 9, "娟": 10,
    # English letter fallback: map to consonant-stroke approximations
}

# Unicode range for CJK Unified Ideographs: used as a fallback heuristic
def _is_cjk(c: str) -> bool:
    cp = ord(c)
    return 0x4E00 <= cp <= 0x9FFF

def _estimate_strokes(c: str) -> int:
    """Fallback stroke estimate for a character not in the table.

    Uses character-position as a crude hash to avoid pathological extremes.
    Typical Chinese characters fall in 4-20 strokes; we aim for a
    reasonable-ish value rather than precise.
    """
    if c in _STROKES:
        return _STROKES[c]
    if _is_cjk(c):
        # Rough: use a deterministic-but-reasonable value based on code point
        return 6 + (ord(c) % 12)  # range 6-17, biased moderate
    # Latin letter: each counts as 1 "phoneme" (different system, kept minimal)
    return 1


# --- 81-number meanings (abridged) --------------------------------------
# Each number maps to a traditional "auspicious" quality.
# For a production app you'd use the full classical text.
_EIGHTY_ONE: dict[int, dict[str, str | bool]] = {
    1:  {"en": "Cosmic Beginning", "quality": "auspicious", "theme": "Leadership, founding, auspicious origin."},
    2:  {"en": "Split Fortune", "quality": "inauspicious", "theme": "Instability, indecision; effort without reward."},
    3:  {"en": "Three Talents Harmony", "quality": "auspicious", "theme": "Charm, wit, creative success."},
    4:  {"en": "Four Directions Broken", "quality": "inauspicious", "theme": "Hardship, setbacks; perseverance required."},
    5:  {"en": "Five Blessings", "quality": "auspicious", "theme": "Wealth, longevity, harmony."},
    6:  {"en": "Heaven's Virtue", "quality": "auspicious", "theme": "Protection, integrity, slow-built fortune."},
    7:  {"en": "Iron Will", "quality": "auspicious", "theme": "Determination turns obstacles into stepping stones."},
    8:  {"en": "Unyielding Mountain", "quality": "auspicious", "theme": "Steady wealth through perseverance."},
    9:  {"en": "Grand Venture Failure", "quality": "inauspicious", "theme": "Reaching too far; pull back to consolidate."},
    10: {"en": "Empty Void", "quality": "inauspicious", "theme": "Effort without result; risk of loss."},
    11: {"en": "Renewal by Rain", "quality": "auspicious", "theme": "Fresh starts, abundance after struggle."},
    12: {"en": "Lonely Branch", "quality": "inauspicious", "theme": "Isolation, weak support network."},
    13: {"en": "Brilliant Talent", "quality": "auspicious", "theme": "Intelligence, artistic genius, leadership."},
    14: {"en": "Shattered Family", "quality": "inauspicious", "theme": "Family discord, misfortune."},
    15: {"en": "Lucky Harmony", "quality": "auspicious", "theme": "Balanced good fortune; beloved by many."},
    16: {"en": "Abundant Virtue", "quality": "auspicious", "theme": "Leadership respected and supported."},
    17: {"en": "Strong Will", "quality": "auspicious", "theme": "Direct action succeeds; watch out for stubbornness."},
    18: {"en": "Steel Determination", "quality": "auspicious", "theme": "Business success through grit."},
    19: {"en": "Wealth in Adversity", "quality": "inauspicious", "theme": "Gains followed by reversals."},
    20: {"en": "Withered Branch", "quality": "inauspicious", "theme": "Exhaustion; rest required."},
    21: {"en": "Moonlit Beauty", "quality": "auspicious", "theme": "Late-blooming success."},
    22: {"en": "Fall Grass Fortune", "quality": "inauspicious", "theme": "Sudden setbacks; guard health."},
    23: {"en": "Rising Sun", "quality": "auspicious", "theme": "Strong growth, recognition, authority."},
    24: {"en": "Golden Wealth", "quality": "auspicious", "theme": "Material success, enjoying abundance."},
    25: {"en": "Resourceful Success", "quality": "auspicious", "theme": "Intelligence + opportunity meet."},
    26: {"en": "Variable Fortune Hero", "quality": "mixed", "theme": "Great highs and lows; strong character needed."},
    27: {"en": "Middle-Life Pause", "quality": "inauspicious", "theme": "Midlife crisis; tempered ambition."},
    28: {"en": "Broken Family Wheel", "quality": "inauspicious", "theme": "Relationship friction; separations."},
    29: {"en": "Wisdom and Courage", "quality": "auspicious", "theme": "Intelligence + willpower; leadership."},
    30: {"en": "Fortune Fluctuation", "quality": "mixed", "theme": "Gambling energy; up-and-down."},
    31: {"en": "Intelligence and Fortune", "quality": "auspicious", "theme": "Wisdom-based success; mentor figure."},
    32: {"en": "Good Luck Sun Rising", "quality": "auspicious", "theme": "Helpers appear; unexpected support."},
    33: {"en": "Dragon Transforms", "quality": "auspicious", "theme": "Heroic rise; reputation."},
    34: {"en": "Broken Sword", "quality": "inauspicious", "theme": "Sudden downfall from ambition."},
    35: {"en": "Calm Peace", "quality": "auspicious", "theme": "Peaceful, stable, respected life."},
    36: {"en": "Heroic Yet Lonely", "quality": "mixed", "theme": "Great deeds, some isolation."},
    37: {"en": "Steady Growth", "quality": "auspicious", "theme": "Consistent progress, recognized leadership."},
    38: {"en": "Artistic Star", "quality": "auspicious", "theme": "Creative excellence, refined taste."},
    39: {"en": "Authority and Wealth", "quality": "auspicious", "theme": "Position and prosperity combined."},
    40: {"en": "Rising from Ruin", "quality": "mixed", "theme": "Strength tested by reversals."},
    41: {"en": "Noble Virtue", "quality": "auspicious", "theme": "Charisma, integrity; loyal following."},
    42: {"en": "Difficult Progress", "quality": "inauspicious", "theme": "Effort with limited reward; patience."},
    43: {"en": "Scattered Wealth", "quality": "inauspicious", "theme": "Earnings slip away; discipline required."},
    44: {"en": "Broken Family", "quality": "inauspicious", "theme": "Health and family challenges."},
    45: {"en": "Smooth Success", "quality": "auspicious", "theme": "Graceful attainment of goals."},
    46: {"en": "Hidden Obstacles", "quality": "inauspicious", "theme": "Surface calm, underlying issues."},
    47: {"en": "Fortune's Flower", "quality": "auspicious", "theme": "Prosperity, reputation, charm."},
    48: {"en": "Wisdom Worth Consulting", "quality": "auspicious", "theme": "Advisory roles; respected elder energy."},
    49: {"en": "Changing Winds", "quality": "mixed", "theme": "Adapt or stagnate."},
    50: {"en": "Half Fortune", "quality": "mixed", "theme": "Gains and losses in equal measure."},
    51: {"en": "Fluctuating Wave", "quality": "mixed", "theme": "Fortune rises and falls with effort."},
    52: {"en": "Far-sighted Success", "quality": "auspicious", "theme": "Strategic thinking pays off long-term."},
    53: {"en": "Outward Fortune Inner Struggle", "quality": "mixed", "theme": "Looks good outside, private challenges."},
    54: {"en": "Hardship Overflow", "quality": "inauspicious", "theme": "Relentless trouble; reset required."},
    55: {"en": "Mountain and Sea", "quality": "mixed", "theme": "Grand ambition, heavy burden."},
    56: {"en": "Missed Opportunity", "quality": "inauspicious", "theme": "Timing off; missed chances."},
    57: {"en": "Strong Determination", "quality": "auspicious", "theme": "Iron will achieves vision."},
    58: {"en": "Fortune After Struggle", "quality": "mixed", "theme": "Late-life fortune after early hardship."},
    59: {"en": "Broken Peace", "quality": "inauspicious", "theme": "Unstable; avoid risky ventures."},
    60: {"en": "Empty Wealth", "quality": "inauspicious", "theme": "Wealth without satisfaction."},
    61: {"en": "Wealth and Respect", "quality": "auspicious", "theme": "Material + reputational success."},
    62: {"en": "Declining Fortune", "quality": "inauspicious", "theme": "Slow erosion; protect foundations."},
    63: {"en": "Wisdom and Fortune", "quality": "auspicious", "theme": "Intelligent prosperity."},
    64: {"en": "Broken Joy", "quality": "inauspicious", "theme": "Happiness short-lived."},
    65: {"en": "Everlasting Prosperity", "quality": "auspicious", "theme": "Long-term stable wealth."},
    66: {"en": "Sudden Loss", "quality": "inauspicious", "theme": "Unexpected setbacks."},
    67: {"en": "Heaven's Blessing", "quality": "auspicious", "theme": "Favorable timing, helpers arrive."},
    68: {"en": "Wisdom of Elders", "quality": "auspicious", "theme": "Advisory authority; enduring respect."},
    69: {"en": "Prolonged Suffering", "quality": "inauspicious", "theme": "Persistent difficulty; escape required."},
    70: {"en": "Lone Struggle", "quality": "inauspicious", "theme": "Isolation, hard climb."},
    71: {"en": "Outer Success Inner Weakness", "quality": "mixed", "theme": "Strong facade, fragile core."},
    72: {"en": "Hidden Difficulties", "quality": "inauspicious", "theme": "Surface ease, covert issues."},
    73: {"en": "Inactive Fortune", "quality": "mixed", "theme": "Fortune without pursuit; passive ease."},
    74: {"en": "Lonely Wanderer", "quality": "inauspicious", "theme": "Unstable; rootless."},
    75: {"en": "Peaceful Retirement", "quality": "auspicious", "theme": "Contentment, steady life."},
    76: {"en": "Struggle then Rise", "quality": "mixed", "theme": "Hardship followed by fortune."},
    77: {"en": "Early Prosperity Late Decline", "quality": "mixed", "theme": "Strong youth, guard later years."},
    78: {"en": "Gradual Decline", "quality": "mixed", "theme": "Slow shift; adapt gracefully."},
    79: {"en": "Scattered Fortune", "quality": "inauspicious", "theme": "Energy leaks; focus required."},
    80: {"en": "Adversity Overcome", "quality": "mixed", "theme": "Victory through perseverance."},
    81: {"en": "Great Fortune Returns", "quality": "auspicious", "theme": "Cycle completes in abundance; rebirth."},
}


def _reduce_to_81(n: int) -> int:
    if n <= 0:
        return 1
    if n > 81:
        n = ((n - 1) % 81) + 1
    return n


def _meaning(n: int) -> dict:
    k = _reduce_to_81(n)
    m = dict(_EIGHTY_ONE[k])
    m["number"] = k
    return m


@dataclass
class ChineseNameGrids:
    heaven: dict
    person: dict
    earth: dict
    total: dict
    outer: dict


@dataclass
class ChineseNameReading:
    name: str
    surname: str
    given: str
    character_strokes: list[dict]   # [{char, strokes}]
    grids: ChineseNameGrids
    element_profile: dict[str, int] # per-element counts from name strokes via digit -> element
    dominant_element: str
    auspicious_grids: int
    inauspicious_grids: int
    mixed_grids: int
    summary: str


# Digit-to-element (same mapping as numerology scorer)
_DIGIT_ELEMENT = {
    0: "water", 1: "water", 2: "earth", 3: "wood", 4: "wood",
    5: "earth", 6: "metal", 7: "metal", 8: "earth", 9: "fire",
}


def analyse_chinese_name(full_name: str, surname_length: int | None = None) -> ChineseNameReading:
    """Analyse a Chinese name using the 5-Grids / 81-Numbers system.

    ``surname_length``: how many leading characters are the surname. Defaults to
    1 for 1-3 char names, 2 for 4-char names (double-surname assumed).
    """
    name = full_name.strip()
    if not name:
        raise ValueError("Name is required.")

    if surname_length is None:
        surname_length = 2 if len(name) >= 4 else 1
    surname_length = max(1, min(surname_length, len(name) - 1))

    surname = name[:surname_length]
    given = name[surname_length:]

    per_char = []
    for c in name:
        per_char.append({"char": c, "strokes": _estimate_strokes(c)})

    surname_strokes = sum(x["strokes"] for x in per_char[:surname_length])
    given_strokes = sum(x["strokes"] for x in per_char[surname_length:])
    total_strokes = surname_strokes + given_strokes

    heaven_num = surname_strokes + 1  # 天格
    # 人格 = last char of surname + first char of given
    person_num = per_char[surname_length - 1]["strokes"] + per_char[surname_length]["strokes"]
    # 地格 = all given-name strokes; if single given char, +1
    earth_num = given_strokes + (1 if len(given) == 1 else 0)
    total_num = total_strokes                           # 总格
    outer_num = total_num - person_num + 1              # 外格

    grids = ChineseNameGrids(
        heaven=_meaning(heaven_num),
        person=_meaning(person_num),
        earth=_meaning(earth_num),
        total=_meaning(total_num),
        outer=_meaning(outer_num),
    )

    # Element profile from per-char last digit
    profile = {"wood": 0, "fire": 0, "earth": 0, "metal": 0, "water": 0}
    for ch in per_char:
        d = ch["strokes"] % 10
        profile[_DIGIT_ELEMENT[d]] += 1
    dominant = max(profile, key=profile.get)

    # Tally grid qualities
    all_grids = [grids.heaven, grids.person, grids.earth, grids.total, grids.outer]
    ausp = sum(1 for g in all_grids if g["quality"] == "auspicious")
    inausp = sum(1 for g in all_grids if g["quality"] == "inauspicious")
    mixed = sum(1 for g in all_grids if g["quality"] == "mixed")

    if ausp >= 4:
        summary = "Highly auspicious name — multiple grids reinforce good fortune."
    elif ausp >= 3 and inausp <= 1:
        summary = "Good name overall; carries more helping than hindering forces."
    elif ausp == inausp:
        summary = "Mixed name: strengths and challenges in balance; destiny carries more weight than name."
    elif inausp >= 3:
        summary = "Challenging name: consider complementing with favorable Day-Master elements in practice."
    else:
        summary = "Name leans slightly favorable; the Person grid (self) matters most."

    return ChineseNameReading(
        name=name,
        surname=surname,
        given=given,
        character_strokes=per_char,
        grids=grids,
        element_profile=profile,
        dominant_element=dominant,
        auspicious_grids=ausp,
        inauspicious_grids=inausp,
        mixed_grids=mixed,
        summary=summary,
    )
