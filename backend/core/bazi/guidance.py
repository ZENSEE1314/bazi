"""Prevention & Enhancement guidance keyed off Day Master + Useful God.

All output strings are available in English, Simplified Chinese, and Bahasa
Melayu. Pass ``lang="en"|"zh"|"ms"`` to the builders.
"""

from __future__ import annotations

Lang = str

# Element names translated.
ELEMENT_NAME: dict[str, dict[str, str]] = {
    "en": {"wood": "wood", "fire": "fire", "earth": "earth", "metal": "metal", "water": "water"},
    "zh": {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"},
    "ms": {"wood": "kayu", "fire": "api", "earth": "tanah", "metal": "logam", "water": "air"},
}


def _en(key: str) -> str:
    return key


# Per-element data, each field keyed by language.
ELEMENT_DATA: dict[str, dict[str, dict[str, list[str] | str]]] = {
    "wood": {
        "colors": {
            "en": ["green", "teal", "emerald", "forest", "mint"],
            "zh": ["绿色", "青色", "翠绿", "森林绿", "薄荷绿"],
            "ms": ["hijau", "biru kehijauan", "zamrud", "hijau hutan", "hijau pudina"],
        },
        "foods_favor": {
            "en": ["green vegetables", "sprouts", "citrus", "sour flavors", "sprouted grains"],
            "zh": ["绿叶蔬菜", "豆芽", "柑橘类", "酸味食物", "发芽谷物"],
            "ms": ["sayur hijau", "taugeh", "buah sitrus", "perisa masam", "bijirin bercambah"],
        },
        "foods_avoid": {
            "en": ["excessive sugar", "processed white flour", "deep-fried"],
            "zh": ["过量糖分", "精制白面粉", "油炸食品"],
            "ms": ["gula berlebihan", "tepung putih diproses", "makanan goreng"],
        },
        "activities_favor": {
            "en": ["gardening", "forest walks", "morning yoga", "learning a new language", "starting a project"],
            "zh": ["园艺", "森林散步", "晨瑜伽", "学习新语言", "启动新项目"],
            "ms": ["berkebun", "berjalan di hutan", "yoga pagi", "belajar bahasa baru", "memulakan projek"],
        },
        "activities_avoid": {
            "en": ["prolonged stillness", "over-controlling outcomes", "isolating from growth opportunities"],
            "zh": ["长期静止不动", "过度掌控结果", "脱离成长机会"],
            "ms": ["kekal pegun terlalu lama", "mengawal keputusan secara berlebihan", "menjauhi peluang berkembang"],
        },
        "gemstones": {
            "en": ["emerald", "jade", "green aventurine"],
            "zh": ["祖母绿", "翡翠", "绿东陵"],
            "ms": ["zamrud", "jed", "aventurin hijau"],
        },
        "careers": {
            "en": ["education", "publishing", "wellness", "botany", "non-profit", "coaching"],
            "zh": ["教育", "出版", "养生", "植物学", "非营利", "教练咨询"],
            "ms": ["pendidikan", "penerbitan", "kesihatan", "botani", "organisasi bukan untung", "bimbingan"],
        },
        "direction": {"en": "East", "zh": "东方", "ms": "Timur"},
        "numbers": [3, 4],
    },
    "fire": {
        "colors": {
            "en": ["red", "pink", "orange", "purple", "magenta"],
            "zh": ["红色", "粉色", "橙色", "紫色", "品红"],
            "ms": ["merah", "merah jambu", "jingga", "ungu", "magenta"],
        },
        "foods_favor": {
            "en": ["bitter greens", "coffee (moderate)", "red foods", "warming spices", "lamb"],
            "zh": ["苦味蔬菜", "适量咖啡", "红色食材", "温暖香料", "羊肉"],
            "ms": ["sayur pahit", "kopi (sederhana)", "makanan merah", "rempah panas", "daging kambing"],
        },
        "foods_avoid": {
            "en": ["excess raw cold foods", "ice water with meals", "chronic under-eating"],
            "zh": ["过多生冷食物", "用餐配冰水", "长期节食"],
            "ms": ["makanan mentah sejuk berlebihan", "air ais semasa makan", "kurang makan kronik"],
        },
        "activities_favor": {
            "en": ["cardio", "public speaking", "social gatherings", "dance", "sunlight"],
            "zh": ["有氧运动", "公开演讲", "社交聚会", "舞蹈", "晒太阳"],
            "ms": ["kardio", "bercakap di khalayak", "perhimpunan sosial", "menari", "cahaya matahari"],
        },
        "activities_avoid": {
            "en": ["isolation", "long indoor winters", "chronic under-stimulation"],
            "zh": ["孤立封闭", "长时间室内过冬", "长期缺乏刺激"],
            "ms": ["pengasingan", "musim sejuk panjang di dalam rumah", "kekurangan rangsangan yang berlarutan"],
        },
        "gemstones": {
            "en": ["ruby", "garnet", "carnelian", "red jasper"],
            "zh": ["红宝石", "石榴石", "红玉髓", "红碧玉"],
            "ms": ["batu delima", "garnet", "karnelian", "jasper merah"],
        },
        "careers": {
            "en": ["marketing", "performance", "hospitality", "beauty", "restaurants", "media"],
            "zh": ["市场营销", "表演艺术", "酒店业", "美容", "餐饮", "媒体"],
            "ms": ["pemasaran", "persembahan", "perhotelan", "kecantikan", "restoran", "media"],
        },
        "direction": {"en": "South", "zh": "南方", "ms": "Selatan"},
        "numbers": [9],
    },
    "earth": {
        "colors": {
            "en": ["yellow", "beige", "brown", "ochre", "camel", "terracotta"],
            "zh": ["黄色", "米色", "棕色", "土黄", "驼色", "赤陶色"],
            "ms": ["kuning", "krim", "coklat", "oker", "unta", "terakota"],
        },
        "foods_favor": {
            "en": ["root vegetables", "whole grains", "slow-cooked stews", "naturally sweet foods"],
            "zh": ["根茎类蔬菜", "全谷物", "慢炖汤羹", "天然甜味食物"],
            "ms": ["sayur ubi", "bijirin penuh", "stu masak perlahan", "makanan manis semula jadi"],
        },
        "foods_avoid": {
            "en": ["excess spicy", "irregular meals", "over-indulgence in sweets"],
            "zh": ["过度辛辣", "三餐不规律", "过食甜品"],
            "ms": ["pedas berlebihan", "waktu makan tidak tetap", "manisan berlebihan"],
        },
        "activities_favor": {
            "en": ["pottery", "cooking", "real-estate", "ceremonies", "long-term committments"],
            "zh": ["陶艺", "烹饪", "房地产", "仪式典礼", "长期承诺"],
            "ms": ["seni tembikar", "memasak", "hartanah", "upacara", "komitmen jangka panjang"],
        },
        "activities_avoid": {
            "en": ["hyper-mobility without rest", "impulsive decisions"],
            "zh": ["高频奔波无休息", "冲动决定"],
            "ms": ["bergerak berlebihan tanpa rehat", "keputusan terburu-buru"],
        },
        "gemstones": {
            "en": ["citrine", "tiger's eye", "amber", "yellow topaz"],
            "zh": ["黄水晶", "虎眼石", "琥珀", "黄托帕石"],
            "ms": ["sitrin", "mata harimau", "ambar", "topaz kuning"],
        },
        "careers": {
            "en": ["real estate", "construction", "agriculture", "HR / operations", "insurance"],
            "zh": ["房地产", "建筑", "农业", "人力资源 / 运营", "保险"],
            "ms": ["hartanah", "pembinaan", "pertanian", "HR / operasi", "insurans"],
        },
        "direction": {"en": "Southwest / Northeast", "zh": "西南 / 东北", "ms": "Barat Daya / Timur Laut"},
        "numbers": [2, 5, 8],
    },
    "metal": {
        "colors": {
            "en": ["white", "silver", "gold", "champagne", "gray"],
            "zh": ["白色", "银色", "金色", "香槟色", "灰色"],
            "ms": ["putih", "perak", "emas", "champagne", "kelabu"],
        },
        "foods_favor": {
            "en": ["pungent foods (onion, garlic, ginger)", "crisp textures", "white foods (rice, cauliflower)", "lung-supporting foods"],
            "zh": ["辛香食物（葱、姜、蒜）", "脆口食物", "白色食物（米饭、花椰菜）", "润肺食物"],
            "ms": ["makanan pedas (bawang, halia, bawang putih)", "tekstur rangup", "makanan putih (nasi, kubis bunga)", "makanan menyokong paru-paru"],
        },
        "foods_avoid": {
            "en": ["overly processed", "cold-and-damp foods", "excess dairy"],
            "zh": ["过度加工食品", "寒湿食物", "过量乳制品"],
            "ms": ["terlalu diproses", "makanan sejuk dan lembap", "tenusu berlebihan"],
        },
        "activities_favor": {
            "en": ["strength training", "precision crafts", "decluttering", "martial arts", "meditation"],
            "zh": ["力量训练", "精密手工艺", "整理断舍离", "武术", "静坐冥想"],
            "ms": ["latihan kekuatan", "kraf tepat", "mengemas barang", "seni mempertahankan diri", "meditasi"],
        },
        "activities_avoid": {
            "en": ["excessive talking", "late nights", "clutter accumulation"],
            "zh": ["话说太多", "熬夜", "杂物堆积"],
            "ms": ["bercakap berlebihan", "tidur lewat", "pengumpulan barang"],
        },
        "gemstones": {
            "en": ["clear quartz", "hematite", "pyrite", "moonstone"],
            "zh": ["白水晶", "赤铁矿", "黄铁矿", "月光石"],
            "ms": ["kuarza jernih", "hematit", "pirit", "batu bulan"],
        },
        "careers": {
            "en": ["finance", "law", "engineering", "surgery", "military / police", "precision tech"],
            "zh": ["金融", "法律", "工程", "外科", "军警", "精密科技"],
            "ms": ["kewangan", "undang-undang", "kejuruteraan", "pembedahan", "tentera / polis", "teknologi tepat"],
        },
        "direction": {"en": "West / Northwest", "zh": "西方 / 西北", "ms": "Barat / Barat Laut"},
        "numbers": [6, 7],
    },
    "water": {
        "colors": {
            "en": ["black", "navy", "midnight blue", "deep purple"],
            "zh": ["黑色", "藏青色", "午夜蓝", "深紫色"],
            "ms": ["hitam", "biru laut", "biru tengah malam", "ungu gelap"],
        },
        "foods_favor": {
            "en": ["seafood", "seaweed", "black beans", "salty (moderate)", "pork"],
            "zh": ["海鲜", "海藻", "黑豆", "适量咸味", "猪肉"],
            "ms": ["makanan laut", "rumpai laut", "kacang hitam", "masin (sederhana)", "daging babi"],
        },
        "foods_avoid": {
            "en": ["excessive dairy", "processed sugars", "overcooked foods"],
            "zh": ["过量乳制品", "加工糖", "过度烹调食物"],
            "ms": ["tenusu berlebihan", "gula diproses", "makanan terlebih masak"],
        },
        "activities_favor": {
            "en": ["swimming", "meditation", "writing", "strategic planning", "deep research"],
            "zh": ["游泳", "冥想", "写作", "战略规划", "深度研究"],
            "ms": ["berenang", "meditasi", "penulisan", "perancangan strategik", "penyelidikan mendalam"],
        },
        "activities_avoid": {
            "en": ["overthinking without action", "chronic emotional isolation"],
            "zh": ["想太多却不行动", "长期情感封闭"],
            "ms": ["terlalu memikir tanpa tindakan", "pengasingan emosi berlarutan"],
        },
        "gemstones": {
            "en": ["black tourmaline", "sapphire", "lapis lazuli", "obsidian"],
            "zh": ["黑碧玺", "蓝宝石", "青金石", "黑曜石"],
            "ms": ["tourmaline hitam", "safir", "lapis lazuli", "obsidian"],
        },
        "careers": {
            "en": ["transport / logistics", "maritime", "consulting", "research", "writing", "trading"],
            "zh": ["运输 / 物流", "航海", "咨询", "研究", "写作", "贸易"],
            "ms": ["pengangkutan / logistik", "maritim", "perundingan", "penyelidikan", "penulisan", "perdagangan"],
        },
        "direction": {"en": "North", "zh": "北方", "ms": "Utara"},
        "numbers": [1, 0],
    },
}


def element_guidance(elem: str, lang: str = "en") -> dict:
    data = ELEMENT_DATA.get(elem, {})
    out: dict = {}
    for key, payload in data.items():
        if isinstance(payload, dict):
            out[key] = payload.get(lang, payload.get("en"))
        else:
            out[key] = payload
    return out


# Strength guidance is narrative — use pre-translated full sentences.
STRENGTH_GUIDANCE: dict[str, dict[str, dict[str, list[str]]]] = {
    "strong": {
        "prevent": {
            "en": [
                "Overworking your own element — it's already abundant. Forcing more creates stagnation.",
                "Saying yes to everything out of capability; your bandwidth is finite.",
                "Rigid routines that refuse to bend; excess strength turns into inflexibility.",
            ],
            "zh": [
                "过度发挥本命元素——已经旺盛，再强会变成停滞。",
                "逞能来者不拒；您的精力有限。",
                "僵化、不愿变通的作息；强过头就成了固执。",
            ],
            "ms": [
                "Terlalu menggunakan unsur sendiri — sudah kuat; menambah lagi menyebabkan tergendala.",
                "Setuju kepada semua kerana mampu; kapasiti anda terhad.",
                "Rutin kaku tidak fleksibel; kekuatan berlebihan bertukar menjadi kekakuan.",
            ],
        },
        "enhance": {
            "en": [
                "Channel the excess through your Useful God — output, wealth pursuits, or disciplined leadership.",
                "Delegate generously; you have enough to give without emptying.",
                "Seek environments that challenge you gently (not your weak element).",
            ],
            "zh": [
                "把多余的能量导向用神——输出、求财或带有纪律的领导。",
                "慷慨授权；您付出而不会透支。",
                "寻找会温和挑战您的环境（而非您的弱行）。",
            ],
            "ms": [
                "Salurkan lebihan melalui Dewa Berguna anda — output, usaha kekayaan, atau kepimpinan berdisiplin.",
                "Wakilkan tugas dengan bermurah hati; anda cukup untuk memberi tanpa kehabisan.",
                "Cari persekitaran yang mencabar secara lembut (bukan unsur lemah anda).",
            ],
        },
    },
    "balanced": {
        "prevent": {
            "en": [
                "Complacency — a balanced chart can coast, missing peak opportunities.",
                "Overcorrecting toward any one element; you thrive in gentle variety.",
            ],
            "zh": [
                "安于现状——平衡的命盘容易顺其自然，错过高峰机会。",
                "过度向某一行倾斜；您在温和的多元中最自在。",
            ],
            "ms": [
                "Berpuas hati — carta seimbang mudah meluncur dan terlepas peluang kemuncak.",
                "Membetulkan secara berlebihan ke satu unsur; anda berkembang dalam variasi yang lembut.",
            ],
        },
        "enhance": {
            "en": [
                "Diversify: multiple skills, multiple income streams, multiple friend circles.",
                "Pick Useful God activities weekly for gentle stimulation without imbalance.",
            ],
            "zh": [
                "多元化：多技能、多收入来源、多朋友圈。",
                "每周做一些用神活动，温和刺激且不失衡。",
            ],
            "ms": [
                "Pelbagaikan: pelbagai kemahiran, sumber pendapatan, dan kalangan rakan.",
                "Pilih aktiviti Dewa Berguna setiap minggu untuk rangsangan lembut tanpa ketidakseimbangan.",
            ],
        },
    },
    "weak": {
        "prevent": {
            "en": [
                "Over-giving — your own element is scarce. Guard your energy like currency.",
                "Draining environments (toxic colleagues, loud spaces, chaotic schedules).",
                "Activities governed by the Avoid God element; they deplete faster than you refill.",
                "Chronic multi-tasking; single-focus conserves strength.",
            ],
            "zh": [
                "过度付出——本命元素本就稀缺，像珍惜金钱一样守住能量。",
                "消耗性环境（有毒同事、嘈杂空间、混乱日程）。",
                "忌神所管辖的活动；耗损比补充还快。",
                "长期多任务切换；单一专注可保精力。",
            ],
            "ms": [
                "Memberi secara berlebihan — unsur sendiri sudah lemah. Jaga tenaga seperti wang.",
                "Persekitaran mengisap tenaga (rakan sekerja toksik, ruang bising, jadual kelam-kabut).",
                "Aktiviti di bawah Dewa Elakkan; ia menyusutkan lebih cepat daripada anda mengisi semula.",
                "Terus multi-tasking; fokus tunggal menjimatkan tenaga.",
            ],
        },
        "enhance": {
            "en": [
                "Bring in Useful God + same-element support systematically.",
                "Choose partners whose Day Master nourishes yours (see Love Outlook).",
                "Rest as strategy, not reward — your chart reloads via downtime.",
                "Protect sleep, diet, and boundaries more strictly than peers.",
            ],
            "zh": [
                "系统性地引入用神与同类元素的支持。",
                "选择日主能滋养您的伴侣（详见“姻缘概观”）。",
                "把休息当策略，而非奖励——您靠停顿充电。",
                "比他人更严格地守护睡眠、饮食与边界。",
            ],
            "ms": [
                "Bawa masuk sokongan Dewa Berguna + unsur yang sama secara sistematik.",
                "Pilih pasangan yang Day Master-nya menyuburkan anda (lihat Pandangan Cinta).",
                "Rehat sebagai strategi, bukan ganjaran — carta anda isi semula semasa berehat.",
                "Lindungi tidur, pemakanan, dan sempadan peribadi lebih ketat daripada orang lain.",
            ],
        },
    },
}


def _join(items: list[str], lang: str) -> str:
    sep = "; " if lang != "zh" else "；"
    return sep.join(items)


def _comma(lang: str) -> str:
    return "，" if lang == "zh" else ", "


def _get_strength_bits(level: str, lang: str) -> dict[str, list[str]]:
    bits = STRENGTH_GUIDANCE.get(level, STRENGTH_GUIDANCE["balanced"])
    return {k: v.get(lang, v["en"]) for k, v in bits.items()}


_TEMPLATES = {
    "en": {
        "min_colors":     "Minimize concentration of {avoid} colors ({colors}) in bedroom and workspace.",
        "watch_habits":   "Watch out for {avoid}-amplifying habits: {items}.",
        "reduce_diet":    "Reduce {avoid}-heavy diet patterns: {items}.",
        "fill_colors":    "Fill wardrobe and environment with {useful} colors ({colors}).",
        "add_practices":  "Add {useful} practices weekly: {items}.",
        "favor_foods":    "Favor {useful}-nourishing foods: {items}.",
        "wear_gems":      "Wear {useful} gemstones: {items}.",
        "sleep_work":     "Sleep / work facing {direction} when possible.",
        "supplement":     "Consciously supplement your weakest element ({weakest}): {items}.",
    },
    "zh": {
        "min_colors":     "减少卧室和工作空间中过多的{avoid}色系（{colors}）。",
        "watch_habits":   "警惕会放大{avoid}的习惯：{items}。",
        "reduce_diet":    "减少偏{avoid}的饮食模式：{items}。",
        "fill_colors":    "在衣柜与环境中多用{useful}色系（{colors}）。",
        "add_practices":  "每周加入{useful}相关的练习：{items}。",
        "favor_foods":    "多食养{useful}的食物：{items}。",
        "wear_gems":      "佩戴{useful}宝石：{items}。",
        "sleep_work":     "睡眠 / 工作尽量朝向{direction}。",
        "supplement":     "有意识地补足您最弱的行（{weakest}）：{items}。",
    },
    "ms": {
        "min_colors":     "Kurangkan warna {avoid} ({colors}) di bilik tidur dan ruang kerja.",
        "watch_habits":   "Berhati-hati dengan tabiat yang menguatkan {avoid}: {items}.",
        "reduce_diet":    "Kurangkan corak diet yang berat {avoid}: {items}.",
        "fill_colors":    "Isi almari dan persekitaran dengan warna {useful} ({colors}).",
        "add_practices":  "Tambahkan amalan {useful} setiap minggu: {items}.",
        "favor_foods":    "Utamakan makanan yang menyuburkan {useful}: {items}.",
        "wear_gems":      "Pakai batu permata {useful}: {items}.",
        "sleep_work":     "Tidur / bekerja menghadap {direction} jika boleh.",
        "supplement":     "Lengkapkan secara sedar unsur paling lemah anda ({weakest}): {items}.",
    },
}


def build_prevention_enhancement(
    day_master: str,
    useful_god: str,
    avoid_god: str,
    strength_level: str,
    weakest_element: str,
    lang: str = "en",
) -> dict:
    """Produce prevention & enhancement lists for a chart in the requested language."""
    tpl = _TEMPLATES.get(lang, _TEMPLATES["en"])
    ug = element_guidance(useful_god, lang)
    ag = element_guidance(avoid_god, lang)
    we = element_guidance(weakest_element, lang)

    element_name = ELEMENT_NAME.get(lang, ELEMENT_NAME["en"])
    ug_name = element_name.get(useful_god, useful_god)
    ag_name = element_name.get(avoid_god, avoid_god)
    we_name = element_name.get(weakest_element, weakest_element)

    strength_bits = _get_strength_bits(strength_level, lang)

    prevention: list[str] = list(strength_bits["prevent"])
    enhancement: list[str] = list(strength_bits["enhance"])
    comma = _comma(lang)

    if ag:
        colors = comma.join(ag["colors"][:3])
        prevention.append(tpl["min_colors"].format(avoid=ag_name, colors=colors))
        if ag.get("activities_avoid"):
            prevention.append(
                tpl["watch_habits"].format(avoid=ag_name, items=_join(ag["activities_avoid"][:2], lang))
            )
        if ag.get("foods_avoid"):
            prevention.append(
                tpl["reduce_diet"].format(avoid=ag_name, items=comma.join(ag["foods_avoid"][:2]))
            )

    if ug:
        colors = comma.join(ug["colors"][:3])
        enhancement.append(tpl["fill_colors"].format(useful=ug_name, colors=colors))
        if ug.get("activities_favor"):
            enhancement.append(
                tpl["add_practices"].format(useful=ug_name, items=comma.join(ug["activities_favor"][:3]))
            )
        if ug.get("foods_favor"):
            enhancement.append(
                tpl["favor_foods"].format(useful=ug_name, items=comma.join(ug["foods_favor"][:3]))
            )
        if ug.get("gemstones"):
            enhancement.append(
                tpl["wear_gems"].format(useful=ug_name, items=comma.join(ug["gemstones"][:3]))
            )
        if ug.get("direction"):
            enhancement.append(tpl["sleep_work"].format(direction=ug["direction"]))

    if we and weakest_element != avoid_god:
        enhancement.append(
            tpl["supplement"].format(weakest=we_name, items=comma.join(we["activities_favor"][:2]))
        )

    return {
        "prevention": prevention,
        "enhancement": enhancement,
        "color_palette_favor": ug.get("colors", []),
        "color_palette_avoid": ag.get("colors", []),
        "foods_favor": ug.get("foods_favor", []),
        "foods_avoid": ag.get("foods_avoid", []),
        "gemstones": ug.get("gemstones", []),
        "lucky_numbers": ug.get("numbers", []),
        "best_direction": ug.get("direction", ""),
        "best_careers": ug.get("careers", []),
    }


# Back-compat shim: existing callers expect ELEMENT_GUIDANCE (English).
ELEMENT_GUIDANCE: dict[str, dict] = {
    elem: element_guidance(elem, "en") for elem in ELEMENT_DATA
}
