"""Wraps the pure calculation engines as API-shaped responses."""

from __future__ import annotations

from datetime import datetime

from ...core.bazi.calculator import FourPillars, Pillar, four_pillars
from ...core.bazi.compatibility import build_deep_compatibility
from ...core.bazi.constants import BRANCH_PINYIN, STEM_PINYIN
from ...core.bazi.elements import element_balance
from ...core.bazi.factors import five_factors
from ...core.bazi.guidance import ELEMENT_GUIDANCE, build_prevention_enhancement
from ...core.bazi.kua import compute_life_kua
from ...core.bazi.luck import annual_pillar, luck_pillars
from ...core.bazi.mansions import mansions_for
from ...core.bazi.nayin import nayin_for
from ...core.bazi.relations import chart_relations
from ...core.bazi.stars import STAR_HINT, find_stars, star_branches
from ...core.bazi.strength import day_master_strength
from ...core.bazi.ten_gods import (
    AREA_RULERS,
    TEN_GOD_HINT,
    TEN_GODS,
    branch_hidden_readings,
    ten_god_for,
)
from ..schemas import (
    AnnualLuckOut,
    BaZiReading,
    CompatibilityReading,
    DailyCalendarDay,
    DailyLuck,
    DayMasterAnalysis,
    DeepBaZiReading,
    DeepCompatibility,
    DeepNumerologyReading,
    DeepPillar,
    DirectionInfo,
    FiveFactor,
    HiddenStem,
    LifeKuaInfo,
    LuckPillarOut,
    NumerologyReading,
    PairAnalysisItem,
    PairInteractionOut,
    Pillar as PillarSchema,
    RelationItem,
    SpouseStarCheckSide,
    StarInfo,
)
from ...core.numerology.pairs import (
    LIFE_PATH_THEMES,
    analyse_pairs,
    explain_pair,
    life_path,
    suggest_better_number,
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


# --- Deep reading ---------------------------------------------------------

def _deep_pillar(label: str, pillar: Pillar, day_stem_index: int) -> DeepPillar:
    nayin_cn, _nayin_py, nayin_en = nayin_for(pillar)
    # Day pillar stem IS the Day Master; exclude its self-Ten-God ("friend")
    if label == "Day":
        stem_tg_cn = None
        stem_tg_en = None
    else:
        tg_key = ten_god_for(day_stem_index, pillar.stem_index)
        stem_tg_cn = TEN_GODS[tg_key]["cn"]
        stem_tg_en = TEN_GODS[tg_key]["en"]

    hidden = [
        HiddenStem(
            stem=h.stem,
            element=h.element,
            weight=round(h.weight, 2),
            ten_god_cn=h.ten_god_cn,
            ten_god_en=h.ten_god_en,
        )
        for h in branch_hidden_readings(pillar.branch_index, day_stem_index)
    ]
    return DeepPillar(
        label=label,
        stem=pillar.stem,
        branch=pillar.branch,
        stem_element=pillar.stem_element,
        branch_element=pillar.branch_element,
        pinyin=f"{STEM_PINYIN[pillar.stem_index]} {BRANCH_PINYIN[pillar.branch_index]}",
        sexagenary_index=pillar.sexagenary_index,
        nayin_cn=nayin_cn,
        nayin_en=nayin_en,
        stem_ten_god_cn=stem_tg_cn,
        stem_ten_god_en=stem_tg_en,
        hidden_stems=hidden,
    )


def _life_areas(pillars: FourPillars) -> dict[str, dict[str, float | list[str]]]:
    """Score each life area by the weighted presence of its ruling Ten Gods."""
    dm = pillars.day.stem_index
    # collect weighted contributions from visible stems + hidden stems
    tg_weights: dict[str, float] = {k: 0.0 for k in TEN_GODS}
    for p in (pillars.year, pillars.month, pillars.day, pillars.hour):
        if p is not pillars.day:
            tg_weights[ten_god_for(dm, p.stem_index)] += 1.0
        for h in branch_hidden_readings(p.branch_index, dm):
            tg_weights[h.ten_god_key] += h.weight

    out: dict[str, dict[str, float | list[str]]] = {}
    for area, rulers in AREA_RULERS.items():
        total = sum(tg_weights[k] for k in rulers)
        out[area] = {
            "strength": round(total, 2),
            "gods": [f"{TEN_GODS[k]['cn']} {TEN_GODS[k]['en']}" for k in rulers],
        }
    return out


_PERSONALITY_NOTES_I18N = {
    "en": {
        "wood":  "Growth-oriented, idealistic, forward-reaching; benevolent but can be stubborn.",
        "fire":  "Expressive, charismatic, quick to act; warm but burns out without fuel.",
        "earth": "Grounded, reliable, patient; trustworthy but can resist change.",
        "metal": "Precise, principled, decisive; clear-minded but can turn rigid.",
        "water": "Adaptive, reflective, strategic; deep thinker, risk of drifting without direction.",
    },
    "zh": {
        "wood":  "向上生长、理想主义、前瞻性强；仁慈但可能固执。",
        "fire":  "表达力强、有魅力、行动迅速；温暖但没有燃料会耗尽。",
        "earth": "脚踏实地、可靠、有耐心；值得信赖但抗拒变化。",
        "metal": "精准、有原则、果断；思路清晰但易变僵化。",
        "water": "灵活、内省、善战略；思虑深远，但缺乏方向会漂移。",
    },
    "ms": {
        "wood":  "Berorientasi pertumbuhan, idealistik, berpandangan jauh; baik hati tetapi boleh degil.",
        "fire":  "Ekspresif, berkarisma, pantas bertindak; hangat tetapi kehabisan tenaga tanpa bahan bakar.",
        "earth": "Berpijak di bumi, boleh dipercayai, sabar; amanah tetapi boleh menolak perubahan.",
        "metal": "Tepat, berprinsip, tegas; minda jelas tetapi boleh menjadi kaku.",
        "water": "Adaptif, reflektif, strategik; pemikir mendalam, berisiko hanyut tanpa arah.",
    },
}

_ELEMENT_AREA_I18N = {
    "en": {
        "wood": "vision, growth, learning",
        "fire": "enthusiasm, visibility, social presence",
        "earth": "stability, commitments, accumulation",
        "metal": "precision, boundaries, decisiveness",
        "water": "flexibility, intuition, depth",
    },
    "zh": {
        "wood": "愿景、成长、学习",
        "fire": "热情、曝光度、社交存在感",
        "earth": "稳定、承诺、积累",
        "metal": "精确、边界、果断",
        "water": "灵活、直觉、深度",
    },
    "ms": {
        "wood": "wawasan, pertumbuhan, pembelajaran",
        "fire": "semangat, keterlihatan, kehadiran sosial",
        "earth": "kestabilan, komitmen, pengumpulan",
        "metal": "ketepatan, sempadan, ketegasan",
        "water": "fleksibiliti, intuisi, kedalaman",
    },
}

_PERSONALITY_TPL = {
    "en": {
        "dm":       "Day Master is {elem}: {note}",
        "dominant": "Chart leans heavily {elem}: {trait} traits show strongly in lifestyle.",
        "weakest":  "Weakest element {elem}: that area ({area}) tends to be under-developed; conscious effort or environmental support recommended.",
    },
    "zh": {
        "dm":       "日主为{elem}：{note}",
        "dominant": "命局偏旺{elem}：{trait}的特质在生活中显著表现。",
        "weakest":  "最弱之行{elem}：该领域（{area}）较为欠缺；建议有意识地努力或借助环境支持。",
    },
    "ms": {
        "dm":       "Day Master ialah {elem}: {note}",
        "dominant": "Carta lebih berat ke {elem}: sifat {trait} menonjol dalam gaya hidup.",
        "weakest":  "Unsur paling lemah {elem}: bidang itu ({area}) cenderung kurang berkembang; usaha sedar atau sokongan persekitaran disyorkan.",
    },
}


def _personality_notes(pillars: FourPillars, elements: dict[str, float], lang: str = "en") -> list[str]:
    from ...core.bazi.guidance import ELEMENT_NAME
    notes = _PERSONALITY_NOTES_I18N.get(lang, _PERSONALITY_NOTES_I18N["en"])
    areas = _ELEMENT_AREA_I18N.get(lang, _ELEMENT_AREA_I18N["en"])
    name = ELEMENT_NAME.get(lang, ELEMENT_NAME["en"])
    tpl = _PERSONALITY_TPL.get(lang, _PERSONALITY_TPL["en"])

    dm_elem = pillars.day.stem_element
    out = [tpl["dm"].format(elem=name.get(dm_elem, dm_elem), note=notes[dm_elem])]

    dominant = max(elements.items(), key=lambda kv: kv[1])[0]
    weakest = min(elements.items(), key=lambda kv: kv[1])[0]
    if dominant != dm_elem:
        trait = notes[dominant].split(";")[0].split("；")[0].strip().lower()
        out.append(tpl["dominant"].format(elem=name.get(dominant, dominant), trait=trait))
    out.append(tpl["weakest"].format(elem=name.get(weakest, weakest), area=areas[weakest]))
    return out


_CAREER_LIBRARY = {
    "wood":  ["education", "publishing", "forestry", "wellness / herbs", "coaching", "non-profit"],
    "fire":  ["marketing", "performance / entertainment", "hospitality", "optics / beauty", "restaurants"],
    "earth": ["real estate", "construction", "agriculture", "HR / operations", "insurance"],
    "metal": ["finance", "law", "engineering", "precision manufacturing", "surgery", "military / police", "IT security"],
    "water": ["transport / logistics", "maritime", "consulting", "research", "writing", "trading", "fluid arts"],
}

_CAREER_LIBRARY_ZH = {
    "wood":  ["教育", "出版", "林业", "养生 / 中药", "教练咨询", "非营利"],
    "fire":  ["市场营销", "表演 / 娱乐", "酒店业", "美容 / 光学", "餐饮"],
    "earth": ["房地产", "建筑", "农业", "人力资源 / 运营", "保险"],
    "metal": ["金融", "法律", "工程", "精密制造", "外科", "军警", "IT 安全"],
    "water": ["运输 / 物流", "航海", "咨询", "研究", "写作", "贸易", "流体艺术"],
}

_CAREER_LIBRARY_MS = {
    "wood":  ["pendidikan", "penerbitan", "perhutanan", "kesihatan / herba", "bimbingan", "organisasi bukan untung"],
    "fire":  ["pemasaran", "persembahan / hiburan", "perhotelan", "optik / kecantikan", "restoran"],
    "earth": ["hartanah", "pembinaan", "pertanian", "HR / operasi", "insurans"],
    "metal": ["kewangan", "undang-undang", "kejuruteraan", "pembuatan tepat", "pembedahan", "tentera / polis", "keselamatan IT"],
    "water": ["pengangkutan / logistik", "maritim", "perundingan", "penyelidikan", "penulisan", "perdagangan", "seni bendalir"],
}


def _career_paths(useful: str, day_master_elem: str, lang: str = "en") -> list[str]:
    lib = {"zh": _CAREER_LIBRARY_ZH, "ms": _CAREER_LIBRARY_MS}.get(lang, _CAREER_LIBRARY)
    picks = list(lib.get(useful, []))
    picks += lib.get(day_master_elem, [])
    seen: set[str] = set()
    out: list[str] = []
    for p in picks:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out


_WEALTH_STRATEGY_TPL = {
    "en": {
        "strong": "Chart is strong enough to absorb risk — active wealth creation (business, investing) is favored over salaried accumulation.",
        "other":  "Chart benefits from steady, compound growth rather than speculation; dollar-cost averaging over decades produces the best outcome.",
        "useful": "Your Useful God ({useful}) sectors tend to bring money — favor investments/careers in those domains.",
        "avoid":  "Avoid concentration in {avoid}-heavy industries — they drain rather than feed your chart.",
    },
    "zh": {
        "strong": "命局够强，可以承担风险——主动创富（创业、投资）优于纯薪资积累。",
        "other":  "命局宜稳健复利成长而非投机；几十年的定期定额会带来最佳结果。",
        "useful": "您的用神（{useful}）领域最容易带来财运——投资和职业都优先此领域。",
        "avoid":  "避免集中于偏{avoid}的行业——它们会耗损而非滋养您的命局。",
    },
    "ms": {
        "strong": "Carta anda cukup kuat untuk menanggung risiko — penciptaan kekayaan aktif (perniagaan, pelaburan) diutamakan berbanding pengumpulan gaji.",
        "other":  "Carta anda sesuai dengan pertumbuhan mampan & bermajmuk, bukan spekulasi; purata dolar-kos selama dekad memberi hasil terbaik.",
        "useful": "Sektor Dewa Berguna anda ({useful}) cenderung membawa wang — utamakan pelaburan / kerjaya dalam domain ini.",
        "avoid":  "Elakkan tumpuan pada industri yang berat {avoid} — mereka menyusut, bukan menyubur carta anda.",
    },
}


def _wealth_strategy(dms, bal: dict[str, float], lang: str = "en") -> list[str]:
    tpl = _WEALTH_STRATEGY_TPL.get(lang, _WEALTH_STRATEGY_TPL["en"])
    from ...core.bazi.guidance import ELEMENT_NAME
    name = ELEMENT_NAME.get(lang, ELEMENT_NAME["en"])
    ug = name.get(dms.useful_god, dms.useful_god)
    ag = name.get(dms.avoid_god, dms.avoid_god)
    hints = []
    hints.append(tpl["strong"] if dms.level == "strong" else tpl["other"])
    hints.append(tpl["useful"].format(useful=ug))
    hints.append(tpl["avoid"].format(avoid=ag))
    return hints


_LOVE_OUTLOOK_TPL = {
    "en": {
        "compatible": "Most compatible Day Master: an {mother} Day Master partner, whose chart naturally nourishes yours.",
        "marriage_palace": "Day Branch (marriage palace): {branch} — hidden stems describe the partner's quality more than the visible stem.",
        "weak":     "Weak Day Master: you benefit from a grounded, mature partner; avoid high-drama relationships that drain you further.",
        "strong":   "Strong Day Master: you need a partner with their own center of gravity — someone who won't be overshadowed by your momentum.",
        "balanced": "Balanced Day Master: partnership flexibility is high; you can form durable bonds across several partner profiles.",
    },
    "zh": {
        "compatible": "最相配的日主：伴侣日主属{mother}——其命盘天然滋养您。",
        "marriage_palace": "日支（夫妻宫）：{branch}——藏干比天干更能描绘伴侣的素质。",
        "weak":     "身弱者：宜选沉稳成熟的伴侣；避免让您进一步耗损的高戏剧关系。",
        "strong":   "身强者：需有自身重心的伴侣——不会被您的节奏盖过的人。",
        "balanced": "身居中者：婚恋弹性高；可与多种伴侣类型建立持久关系。",
    },
    "ms": {
        "compatible": "Day Master paling serasi: pasangan yang Day Master-nya {mother}, kerana cartanya secara semula jadi menyuburkan anda.",
        "marriage_palace": "Cabang Hari (istana perkahwinan): {branch} — batang tersembunyi menggambarkan kualiti pasangan lebih daripada batang kelihatan.",
        "weak":     "Day Master lemah: pasangan yang tenang dan matang menguntungkan anda; elakkan hubungan bergelora yang melelahkan.",
        "strong":   "Day Master kuat: anda memerlukan pasangan yang berpusatkan diri — orang yang tidak terhimpit oleh momentum anda.",
        "balanced": "Day Master seimbang: fleksibiliti perhubungan tinggi; anda boleh membentuk ikatan tahan lama dengan pelbagai jenis pasangan.",
    },
}


def _love_outlook(fp: FourPillars, dms, lang: str = "en") -> list[str]:
    tpl = _LOVE_OUTLOOK_TPL.get(lang, _LOVE_OUTLOOK_TPL["en"])
    from ...core.bazi.guidance import ELEMENT_NAME
    name = ELEMENT_NAME.get(lang, ELEMENT_NAME["en"])
    mother_en = _ideal_partner_dm(fp.day.stem_element)
    mother = name.get(mother_en, mother_en)
    out = [
        tpl["compatible"].format(mother=mother),
        tpl["marriage_palace"].format(branch=fp.day.branch),
    ]
    out.append(tpl.get(dms.level, tpl["balanced"]))
    return out


def _ideal_partner_dm(dm_elem: str) -> str:
    # 'mother' element (the one that produces DM) is classically the
    # smoothest partner element for a single-axis chart.
    for e, v in PRODUCES.items():
        if v == dm_elem:
            return e
    return dm_elem


_TCM_ORGANS = {
    "en": {
        "wood":  "liver, gallbladder, eyes, tendons",
        "fire":  "heart, small intestine, cardiovascular, sleep",
        "earth": "spleen, stomach, digestion, muscles",
        "metal": "lungs, large intestine, skin, respiratory",
        "water": "kidney, bladder, bones, reproductive",
    },
    "zh": {
        "wood":  "肝、胆、眼、筋",
        "fire":  "心、小肠、心血管、睡眠",
        "earth": "脾、胃、消化、肌肉",
        "metal": "肺、大肠、皮肤、呼吸",
        "water": "肾、膀胱、骨骼、生殖",
    },
    "ms": {
        "wood":  "hati, pundi hempedu, mata, urat",
        "fire":  "jantung, usus kecil, kardiovaskular, tidur",
        "earth": "limpa, perut, penghadaman, otot",
        "metal": "paru-paru, usus besar, kulit, pernafasan",
        "water": "buah pinggang, pundi kencing, tulang, reproduktif",
    },
}

_HEALTH_WATCH_TPL = {
    "en": [
        "Day-Master organ system ({elem} → {tcm}) — stress shows up here first.",
        "Chart's weakest element ({elem} → {tcm}) — area most likely to under-function when rundown.",
    ],
    "zh": [
        "日主器官系统（{elem} → {tcm}）——压力最先在此显现。",
        "命局最弱之行（{elem} → {tcm}）——疲劳时最容易功能下降的部位。",
    ],
    "ms": [
        "Sistem organ Day Master ({elem} → {tcm}) — tekanan muncul di sini dahulu.",
        "Unsur paling lemah ({elem} → {tcm}) — bahagian paling berkemungkinan kurang berfungsi semasa letih.",
    ],
}


def _health_watch(dm_elem: str, weakest: str, lang: str = "en") -> list[str]:
    from ...core.bazi.guidance import ELEMENT_NAME
    tcm = _TCM_ORGANS.get(lang, _TCM_ORGANS["en"])
    name = ELEMENT_NAME.get(lang, ELEMENT_NAME["en"])
    tpl = _HEALTH_WATCH_TPL.get(lang, _HEALTH_WATCH_TPL["en"])
    return [
        tpl[0].format(elem=name.get(dm_elem, dm_elem), tcm=tcm[dm_elem]),
        tpl[1].format(elem=name.get(weakest, weakest), tcm=tcm[weakest]),
    ]


def build_deep_bazi(birth: datetime, gender: str | None, today: datetime | None = None, lang: str = "en") -> DeepBaZiReading:
    today = today or datetime.now()
    fp = four_pillars(birth)
    dm = fp.day.stem_index

    pillars_out = [
        _deep_pillar("Year", fp.year, dm),
        _deep_pillar("Month", fp.month, dm),
        _deep_pillar("Day", fp.day, dm),
        _deep_pillar("Hour", fp.hour, dm),
    ]

    bal = element_balance(fp)
    dms = day_master_strength(fp)
    dm_analysis = DayMasterAnalysis(
        element=fp.day_master_element,
        stem=fp.day_master,
        strength_score=dms.score,
        strength_level=dms.level,
        seasonal_influence=dms.seasonal_influence,
        supportive_elements=dms.supportive_elements,
        draining_elements=dms.draining_elements,
        useful_god=dms.useful_god,
        avoid_god=dms.avoid_god,
        explanation=dms.explanation,
    )

    factor_rows = [
        FiveFactor(key=r.key, label=r.label, element=r.element, amount=r.amount, percent=r.percent)
        for r in five_factors(fp)
    ]

    # Luck pillars
    lps = luck_pillars(fp, gender or "", count=8)
    luck_out = []
    for lp in lps:
        tg_key = ten_god_for(dm, lp.pillar.stem_index)
        _ny_cn, _ny_py, ny_en = nayin_for(lp.pillar)
        luck_out.append(
            LuckPillarOut(
                index=lp.index,
                start_age=lp.start_age,
                end_age=lp.end_age,
                stem=lp.pillar.stem,
                branch=lp.pillar.branch,
                stem_element=lp.pillar.stem_element,
                branch_element=lp.pillar.branch_element,
                pinyin=f"{STEM_PINYIN[lp.pillar.stem_index]} {BRANCH_PINYIN[lp.pillar.branch_index]}",
                nayin_en=ny_en,
                stem_ten_god_cn=TEN_GODS[tg_key]["cn"],
                stem_ten_god_en=TEN_GODS[tg_key]["en"],
            )
        )

    # Annual luck (solar year of today, resolved via calendar)
    from ...core.bazi.calendar import solar_month_for
    today_sm = solar_month_for(today)
    ap = annual_pillar(today_sm.solar_year)
    apg_key = ten_god_for(dm, ap.stem_index)
    annual_out = AnnualLuckOut(
        year=today_sm.solar_year,
        stem=ap.stem,
        branch=ap.branch,
        stem_element=ap.stem_element,
        branch_element=ap.branch_element,
        stem_ten_god_cn=TEN_GODS[apg_key]["cn"],
        stem_ten_god_en=TEN_GODS[apg_key]["en"],
        note=TEN_GOD_HINT[apg_key],
    )

    # Stars
    stars_present = find_stars(fp)
    stars_triggers = star_branches(fp)
    stars_out: dict[str, StarInfo] = {}
    for key in ("nobleman", "peach_blossom", "academic", "sky_horse"):
        stars_out[key] = StarInfo(
            trigger_branch=stars_triggers.get(key),
            present_in=stars_present.get(key, []),
        )

    # Life Kua + 8 Mansions
    life_kua_info: LifeKuaInfo | None = None
    lucky_dirs: list[DirectionInfo] = []
    unlucky_dirs: list[DirectionInfo] = []
    if gender:
        kua = compute_life_kua(pillars=_solar_year_for(fp), gender=gender) if False else compute_life_kua(_solar_year_for(fp), gender)
        life_kua_info = LifeKuaInfo(
            number=kua.number,
            trigram_cn=kua.trigram_cn,
            trigram_pinyin=kua.trigram_pinyin,
            element=kua.element,
            seated_direction=kua.seated_direction,
            group=kua.group,
        )
        mans = mansions_for(kua.number)
        for direction, info in mans["lucky"].items():
            lucky_dirs.append(DirectionInfo(
                direction=direction,
                direction_name=info["direction_name"],
                category_key=info["category_key"],
                cn=info["cn"],
                en=info["en"],
                meaning=info["meaning"],
            ))
        for direction, info in mans["unlucky"].items():
            unlucky_dirs.append(DirectionInfo(
                direction=direction,
                direction_name=info["direction_name"],
                category_key=info["category_key"],
                cn=info["cn"],
                en=info["en"],
                meaning=info["meaning"],
            ))
        # stable ordering (Sheng Qi first etc.)
        lucky_order = ["sheng_qi", "tian_yi", "yan_nian", "fu_wei"]
        unlucky_order = ["jue_ming", "wu_gui", "liu_sha", "huo_hai"]
        lucky_dirs.sort(key=lambda d: lucky_order.index(d.category_key))
        unlucky_dirs.sort(key=lambda d: unlucky_order.index(d.category_key))

    # Relations
    rels_raw = chart_relations(fp)
    rels_out: dict[str, list[RelationItem]] = {}
    for key, items in rels_raw.items():
        rels_out[key] = [
            RelationItem(
                kind=i.get("kind"),
                pillars=i.get("pillars"),
                branches=i["branches"],
                transforms_to=i.get("transforms_to"),
                note=i["note"],
            )
            for i in items
        ]

    chart_string = f"{fp.year} {fp.month} {fp.day} {fp.hour}"

    guide = build_prevention_enhancement(
        day_master=fp.day_master,
        useful_god=dms.useful_god,
        avoid_god=dms.avoid_god,
        strength_level=dms.level,
        weakest_element=bal.weakest(),
        lang=lang,
    )

    return DeepBaZiReading(
        pillars=pillars_out,
        chart_string=chart_string,
        zodiac=fp.zodiac,
        day_master=dm_analysis,
        elements=bal.as_dict,
        dominant_element=bal.dominant(),
        weakest_element=bal.weakest(),
        five_factors=factor_rows,
        stars=stars_out,
        life_kua=life_kua_info,
        lucky_directions=lucky_dirs,
        unlucky_directions=unlucky_dirs,
        relations=rels_out,
        luck_pillars=luck_out,
        annual_luck=annual_out,
        life_areas=_life_areas(fp),
        personality_notes=_personality_notes(fp, bal.as_dict, lang=lang),
        career_paths=_career_paths(dms.useful_god, fp.day_master_element, lang=lang),
        wealth_strategy=_wealth_strategy(dms, bal.as_dict, lang=lang),
        love_outlook=_love_outlook(fp, dms, lang=lang),
        health_watch=_health_watch(fp.day_master_element, bal.weakest(), lang=lang),
        prevention=guide["prevention"],
        enhancement=guide["enhancement"],
        color_palette_favor=guide["color_palette_favor"],
        color_palette_avoid=guide["color_palette_avoid"],
        foods_favor=guide["foods_favor"],
        foods_avoid=guide["foods_avoid"],
        gemstones=guide["gemstones"],
        lucky_numbers=guide["lucky_numbers"],
        best_direction=guide["best_direction"],
        best_careers=guide["best_careers"],
    )


def _solar_year_for(fp: FourPillars) -> int:
    """Reconstruct the Ba Zi solar year from the Year pillar.

    Year pillar (stem_index, branch_index) resolves to sexagenary_index, and
    solar_year = sexagenary_index + 60*k + 4. We use the era 1900-2100 and pick
    the single k that places the year in that window.
    """
    sex = fp.year.sexagenary_index
    for base in range(1900, 2100, 60):
        year = base + ((sex - (base - 4)) % 60)
        if 1900 <= year < 2100:
            return year
    return 1900 + sex


def build_calendar(birth: datetime, year: int, month: int) -> list[DailyCalendarDay]:
    """Daily-luck calendar for a whole month."""
    from calendar import monthrange
    _, days_in_month = monthrange(year, month)
    results: list[DailyCalendarDay] = []
    for d in range(1, days_in_month + 1):
        day_dt = datetime(year, month, d, 12, 0)
        luck = build_daily_luck(birth, day_dt)
        results.append(
            DailyCalendarDay(
                date=luck.date,
                score=luck.score,
                label=_score_label(luck.score),
                day_pillar_cn=f"{luck.day_pillar.stem}{luck.day_pillar.branch}",
                day_pillar_element=luck.day_pillar.stem_element,
            )
        )
    return results


def build_deep_compatibility_reading(
    a_name: str,
    a_birth: datetime,
    a_gender: str | None,
    b_name: str,
    b_birth: datetime,
    b_gender: str | None,
) -> DeepCompatibility:
    a_fp = four_pillars(a_birth)
    b_fp = four_pillars(b_birth)
    c = build_deep_compatibility(a_fp, b_fp, a_gender, b_gender)

    return DeepCompatibility(
        profile_a=a_name,
        profile_b=b_name,
        total_score=c.total_score,
        verdict=c.verdict,
        day_master_relation=c.day_master_relation,
        spouse_star_check={
            "a_checks_b": SpouseStarCheckSide(**c.spouse_star_check["a_checks_b"]),
            "b_checks_a": SpouseStarCheckSide(**c.spouse_star_check["b_checks_a"]),
        },
        useful_god_exchange=c.useful_god_exchange,
        branch_interactions=[
            PairInteractionOut(
                a_label=i.a_label, b_label=i.b_label,
                a_branch=i.a_branch, b_branch=i.b_branch,
                kind=i.kind, transforms_to=i.transforms_to, note=i.note,
            )
            for i in c.branch_interactions
        ],
        area_scores=c.area_scores,
        element_blend=c.element_blend,
        shared_weakness=c.shared_weakness,
        complementary_strengths=c.complementary_strengths,
        harmony=c.harmony,
        tension=c.tension,
    )


def _score_label(score: int) -> str:
    if score >= 75:
        return "excellent"
    if score >= 60:
        return "good"
    if score >= 45:
        return "neutral"
    if score >= 30:
        return "caution"
    return "difficult"


def build_deep_numerology(number: str, profile: "Profile | None" = None) -> DeepNumerologyReading:  # noqa: F821
    from ..schemas import NumberSuggestion

    scored = build_numerology_reading(number)
    lp = life_path(number)
    pairs = analyse_pairs(number)
    pair_items = [
        PairAnalysisItem(
            a=p.a,
            b=p.b,
            category_cn=p.category_cn,
            category_en=p.category_en,
            theme=p.theme,
            auspicious=p.auspicious,
            explanation=explain_pair(p.a, p.b),
        )
        for p in pairs
    ]
    ausp = sum(1 for p in pairs if p.auspicious)
    inausp = sum(1 for p in pairs if not p.auspicious)

    reading = DeepNumerologyReading(
        number=number,
        scores=scored,
        life_path=lp,
        life_path_theme=LIFE_PATH_THEMES.get(lp, ""),
        pairs=pair_items,
        auspicious_pair_count=ausp,
        inauspicious_pair_count=inausp,
    )

    if profile is not None:
        fp = four_pillars(profile.birth_datetime)
        dms = day_master_strength(fp)
        ug = ELEMENT_GUIDANCE.get(dms.useful_god, {})
        ag = ELEMENT_GUIDANCE.get(dms.avoid_god, {})
        preferred = list(ug.get("numbers", []))
        avoid_digits = list(ag.get("numbers", []))

        # Count preferred vs avoid digits in the number
        digits = [int(c) for c in number if c.isdigit()]
        pref_count = sum(1 for d in digits if d in preferred)
        avoid_count = sum(1 for d in digits if d in avoid_digits)
        total = len(digits) or 1

        personalized = (
            f"For {profile.name} ({fp.day_master} {fp.day_master_element} Day Master): "
            f"Useful God is {dms.useful_god}, so digits {preferred} amplify your luck. "
            f"Avoid God is {dms.avoid_god}, so digits {avoid_digits} drain you. "
            f"This number contains {pref_count}/{total} favored digits and "
            f"{avoid_count}/{total} draining digits."
        )

        suggestion_dict = suggest_better_number(number, dms.useful_god)
        suggestion = NumberSuggestion(**suggestion_dict)

        reading.profile_name = profile.name
        reading.profile_day_master = fp.day_master
        reading.profile_day_master_element = fp.day_master_element
        reading.profile_useful_god = dms.useful_god
        reading.personalized_note = personalized
        reading.preferred_digits = preferred
        reading.digits_to_avoid = avoid_digits
        reading.suggestion = suggestion

    return reading
