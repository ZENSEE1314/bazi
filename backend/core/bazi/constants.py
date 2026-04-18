"""Ba Zi (Four Pillars) constants: Heavenly Stems, Earthly Branches, Five Elements."""

from __future__ import annotations

WOOD = "wood"
FIRE = "fire"
EARTH = "earth"
METAL = "metal"
WATER = "water"

ELEMENTS = (WOOD, FIRE, EARTH, METAL, WATER)

HEAVENLY_STEMS = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
STEM_PINYIN = ("Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui")
STEM_ELEMENT = (WOOD, WOOD, FIRE, FIRE, EARTH, EARTH, METAL, METAL, WATER, WATER)
STEM_YANG = (True, False, True, False, True, False, True, False, True, False)

EARTHLY_BRANCHES = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
BRANCH_PINYIN = ("Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai")
BRANCH_ELEMENT = (
    WATER,  # 子 Zi
    EARTH,  # 丑 Chou
    WOOD,   # 寅 Yin
    WOOD,   # 卯 Mao
    EARTH,  # 辰 Chen
    FIRE,   # 巳 Si
    FIRE,   # 午 Wu
    EARTH,  # 未 Wei
    METAL,  # 申 Shen
    METAL,  # 酉 You
    EARTH,  # 戌 Xu
    WATER,  # 亥 Hai
)

# Hidden stems (藏干) inside each branch with standard weights.
# Maps branch index -> tuple of (stem_index, weight). Weights per branch sum to 1.0.
HIDDEN_STEMS: dict[int, tuple[tuple[int, float], ...]] = {
    0: ((9, 1.0),),                              # 子: 癸
    1: ((5, 0.6), (9, 0.3), (7, 0.1)),           # 丑: 己, 癸, 辛
    2: ((0, 0.6), (2, 0.3), (4, 0.1)),           # 寅: 甲, 丙, 戊
    3: ((1, 1.0),),                              # 卯: 乙
    4: ((4, 0.6), (1, 0.3), (9, 0.1)),           # 辰: 戊, 乙, 癸
    5: ((2, 0.6), (4, 0.3), (6, 0.1)),           # 巳: 丙, 戊, 庚
    6: ((3, 0.7), (5, 0.3)),                     # 午: 丁, 己
    7: ((5, 0.6), (3, 0.3), (1, 0.1)),           # 未: 己, 丁, 乙
    8: ((6, 0.6), (8, 0.3), (4, 0.1)),           # 申: 庚, 壬, 戊
    9: ((7, 1.0),),                              # 酉: 辛
    10: ((4, 0.6), (7, 0.3), (3, 0.1)),          # 戌: 戊, 辛, 丁
    11: ((8, 0.7), (0, 0.3)),                    # 亥: 壬, 甲
}

ZODIAC_ANIMALS = (
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
)
