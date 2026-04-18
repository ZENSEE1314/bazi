"""Wraps the pure calculation engines as API-shaped responses."""

from __future__ import annotations

from datetime import datetime

from ...core.bazi.calculator import FourPillars, Pillar, four_pillars
from ...core.bazi.constants import BRANCH_PINYIN, STEM_PINYIN
from ...core.bazi.elements import element_balance
from ...core.bazi.factors import five_factors
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
    DeepNumerologyReading,
    DeepPillar,
    DirectionInfo,
    FiveFactor,
    HiddenStem,
    LifeKuaInfo,
    LuckPillarOut,
    NumerologyReading,
    PairAnalysisItem,
    Pillar as PillarSchema,
    RelationItem,
    StarInfo,
)
from ...core.numerology.pairs import LIFE_PATH_THEMES, analyse_pairs, life_path
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


def _personality_notes(pillars: FourPillars, elements: dict[str, float]) -> list[str]:
    dm_elem = pillars.day.stem_element
    notes = {
        "wood": "Growth-oriented, idealistic, forward-reaching; benevolent but can be stubborn.",
        "fire": "Expressive, charismatic, quick to act; warm but burns out without fuel.",
        "earth": "Grounded, reliable, patient; trustworthy but can resist change.",
        "metal": "Precise, principled, decisive; clear-minded but can turn rigid.",
        "water": "Adaptive, reflective, strategic; deep thinker, risk of drifting without direction.",
    }
    out = [f"Day Master is {dm_elem}: {notes[dm_elem]}"]

    dominant = max(elements.items(), key=lambda kv: kv[1])[0]
    weakest = min(elements.items(), key=lambda kv: kv[1])[0]
    if dominant != dm_elem:
        out.append(
            f"Chart leans heavily {dominant}: {notes[dominant].split(';')[0].strip().lower()} "
            f"traits show strongly in lifestyle."
        )
    out.append(
        f"Weakest element {weakest}: that area ({_element_area_hint(weakest)}) "
        f"tends to be under-developed; conscious effort or environmental support recommended."
    )
    return out


_ELEMENT_AREA = {
    "wood": "vision, growth, learning",
    "fire": "enthusiasm, visibility, social presence",
    "earth": "stability, commitments, accumulation",
    "metal": "precision, boundaries, decisiveness",
    "water": "flexibility, intuition, depth",
}


def _element_area_hint(elem: str) -> str:
    return _ELEMENT_AREA.get(elem, elem)


_CAREER_LIBRARY = {
    "wood":  ["education", "publishing", "forestry", "wellness / herbs", "coaching", "non-profit"],
    "fire":  ["marketing", "performance / entertainment", "hospitality", "optics / beauty", "restaurants"],
    "earth": ["real estate", "construction", "agriculture", "HR / operations", "insurance"],
    "metal": ["finance", "law", "engineering", "precision manufacturing", "surgery", "military / police", "IT security"],
    "water": ["transport / logistics", "maritime", "consulting", "research", "writing", "trading", "fluid arts"],
}


def _career_paths(useful: str, day_master_elem: str) -> list[str]:
    picks = list(_CAREER_LIBRARY.get(useful, []))
    picks += _CAREER_LIBRARY.get(day_master_elem, [])
    seen: set[str] = set()
    out: list[str] = []
    for p in picks:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out


def _wealth_strategy(dms, bal: dict[str, float]) -> list[str]:
    hints = []
    wealth_elem_strong = dms.level == "strong"
    if wealth_elem_strong:
        hints.append("Chart is strong enough to absorb risk — active wealth creation (business, investing) is favored over salaried accumulation.")
    else:
        hints.append("Chart benefits from steady, compound growth rather than speculation; dollar-cost averaging over decades produces the best outcome.")
    hints.append(f"Your Useful God ({dms.useful_god}) sectors tend to bring money — favor investments/careers in those domains.")
    hints.append(f"Avoid concentration in {dms.avoid_god}-heavy industries — they drain rather than feed your chart.")
    return hints


def _love_outlook(fp: FourPillars, dms) -> list[str]:
    out = []
    out.append(
        "Most compatible Day Master: an " + _ideal_partner_dm(fp.day.stem_element) +
        " Day Master partner, whose chart naturally nourishes yours."
    )
    out.append(
        "Day Branch (marriage palace): " + fp.day.branch +
        f" — hidden stems describe the partner's quality more than the visible stem."
    )
    if dms.level == "weak":
        out.append("Weak Day Master: you benefit from a grounded, mature partner; avoid high-drama relationships that drain you further.")
    elif dms.level == "strong":
        out.append("Strong Day Master: you need a partner with their own center of gravity — someone who won't be overshadowed by your momentum.")
    else:
        out.append("Balanced Day Master: partnership flexibility is high; you can form durable bonds across several partner profiles.")
    return out


def _ideal_partner_dm(dm_elem: str) -> str:
    # 'mother' element (the one that produces DM) is classically the
    # smoothest partner element for a single-axis chart.
    for e, v in PRODUCES.items():
        if v == dm_elem:
            return e
    return dm_elem


def _health_watch(dm_elem: str, weakest: str) -> list[str]:
    tcm = {
        "wood":  "liver, gallbladder, eyes, tendons",
        "fire":  "heart, small intestine, cardiovascular, sleep",
        "earth": "spleen, stomach, digestion, muscles",
        "metal": "lungs, large intestine, skin, respiratory",
        "water": "kidney, bladder, bones, reproductive",
    }
    return [
        f"Day-Master organ system ({dm_elem} → {tcm[dm_elem]}) — stress shows up here first.",
        f"Chart's weakest element ({weakest} → {tcm[weakest]}) — area most likely to under-function when rundown.",
    ]


def build_deep_bazi(birth: datetime, gender: str | None, today: datetime | None = None) -> DeepBaZiReading:
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
        personality_notes=_personality_notes(fp, bal.as_dict),
        career_paths=_career_paths(dms.useful_god, fp.day_master_element),
        wealth_strategy=_wealth_strategy(dms, bal.as_dict),
        love_outlook=_love_outlook(fp, dms),
        health_watch=_health_watch(fp.day_master_element, bal.weakest()),
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


def build_deep_numerology(number: str) -> DeepNumerologyReading:
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
        )
        for p in pairs
    ]
    ausp = sum(1 for p in pairs if p.auspicious)
    inausp = sum(1 for p in pairs if not p.auspicious)
    return DeepNumerologyReading(
        number=number,
        scores=scored,
        life_path=lp,
        life_path_theme=LIFE_PATH_THEMES.get(lp, ""),
        pairs=pair_items,
        auspicious_pair_count=ausp,
        inauspicious_pair_count=inausp,
    )
