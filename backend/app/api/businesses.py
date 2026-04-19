"""Business profile CRUD + combined reading endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import get_current_user
from ..models import Business, Profile, User
from ..schemas import (
    BusinessCreate,
    BusinessOut,
    BusinessOwnerMatch,
    BusinessReading,
    BusinessUpdate,
    ChineseNameReadingOut,
    ChineseNameGridsOut,
    CharStroke,
    FengShuiReadingOut,
    LifeStageOut,
    NameGrid,
    RoomVerdictOut,
    ThreeTalents,
    YinYangBalance,
)
from ..services.readings import _solar_year_for, build_deep_bazi
from ...core.bazi.calculator import four_pillars
from ...core.bazi.compatibility import build_deep_compatibility
from ...core.bazi.elements import element_balance
from ...core.bazi.strength import day_master_strength
from ...core.bazi.ten_gods import CONTROLS, PRODUCES
from ...core.fengshui.house import analyse_home
from ...core.numerology.chinese_name import analyse_chinese_name

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


def _unset_main_except(db: Session, owner_id: int, except_id: int | None) -> None:
    q = db.query(Business).filter(Business.owner_id == owner_id, Business.is_main.is_(True))
    if except_id is not None:
        q = q.filter(Business.id != except_id)
    for b in q.all():
        b.is_main = False


def _owned(db: Session, user: User, biz_id: int) -> Business:
    b = db.get(Business, biz_id)
    if b is None or b.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    return b


@router.get("", response_model=list[BusinessOut])
def list_businesses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Business]:
    return (
        db.query(Business)
        .filter(Business.owner_id == user.id)
        .order_by(Business.is_main.desc(), Business.created_at.asc())
        .all()
    )


@router.post("", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(
    payload: BusinessCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    settings = get_settings()
    count = db.query(Business).filter(Business.owner_id == user.id).count()
    if not user.is_premium and count >= settings.free_business_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Free tier allows {settings.free_business_limit} business(es). "
                "Upgrade to Premium for unlimited businesses."
            ),
        )

    biz = Business(
        owner_id=user.id,
        name=payload.name,
        chinese_name=payload.chinese_name,
        open_datetime=payload.open_datetime,
        location=payload.location,
        facing_direction=(payload.facing_direction or None),
        industry=payload.industry,
        notes=payload.notes,
        is_main=payload.is_main,
    )
    db.add(biz)
    db.flush()
    if biz.is_main:
        _unset_main_except(db, user.id, biz.id)
    db.commit()
    db.refresh(biz)
    return biz


@router.get("/{biz_id}", response_model=BusinessOut)
def get_business(
    biz_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    return _owned(db, user, biz_id)


@router.patch("/{biz_id}", response_model=BusinessOut)
def update_business(
    biz_id: int,
    payload: BusinessUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    biz = _owned(db, user, biz_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(biz, field, value)
    if data.get("is_main"):
        _unset_main_except(db, user.id, biz.id)
    db.commit()
    db.refresh(biz)
    return biz


@router.delete("/{biz_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_business(
    biz_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    biz = _owned(db, user, biz_id)
    db.delete(biz)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Combined reading -----------------------------------------------------

def _compose_owner_reading(
    owner_name: str,
    owner_dm: str,
    owner_useful: str,
    owner_avoid: str,
    biz_dominant: str,
    ug_pct: float,
    ag_pct: float,
    feeds: bool,
    drains: bool,
    score: int,
    harmony: list[str],
    tension: list[str],
    lang: str,
) -> str:
    """Short personalised paragraph explaining business-vs-owner fit."""
    tpl = {
        "en": {
            "head_good":  "{name}, this business is a genuinely good match for you.",
            "head_ok":    "{name}, this business is workable for you with some care.",
            "head_bad":   "{name}, this business works against your chart on key axes.",
            "feeds":      "The business's dominant {biz} element produces your {own} Day Master — it feeds you energy.",
            "drains":     "The business's dominant {biz} element controls your {own} Day Master — it will feel draining over time.",
            "useful_hi":  "It supplies your Useful God ({useful}) at {pct}% of its chart — strongly supportive.",
            "useful_mid": "It supplies your Useful God ({useful}) at {pct}% — modest support.",
            "useful_low": "Your Useful God ({useful}) is thin ({pct}%) in this business — supplement with colours, rituals, or partners.",
            "avoid_hi":   "Watch out: it amplifies your Avoid God ({avoid}) at {pct}% — this will slowly wear you down.",
            "harmony":    "Harmony signals: {items}.",
            "tension":    "Friction signals: {items}.",
        },
        "zh": {
            "head_good":  "{name}，此事业与您的命盘契合良好。",
            "head_ok":    "{name}，此事业可行，但需要用心经营。",
            "head_bad":   "{name}，此事业在关键方面与您的命盘相冲。",
            "feeds":      "事业主导之{biz}行生您的日主{own}，能为您注入能量。",
            "drains":     "事业主导之{biz}行克您的日主{own}，长期经营会令您消耗。",
            "useful_hi":  "事业中您的用神（{useful}）占比高达 {pct}%，强有力地支持您。",
            "useful_mid": "事业中您的用神（{useful}）约 {pct}%，有一定助益。",
            "useful_low": "事业中您的用神（{useful}）仅 {pct}%，建议以色彩、仪式或合伙人补强。",
            "avoid_hi":   "留意：事业中您的忌神（{avoid}）占 {pct}%，长期会慢慢消耗您。",
            "harmony":    "和谐点：{items}。",
            "tension":    "冲突点：{items}。",
        },
        "ms": {
            "head_good":  "{name}, perniagaan ini benar-benar sesuai dengan anda.",
            "head_ok":    "{name}, perniagaan ini boleh dikendalikan dengan pengurusan sedar.",
            "head_bad":   "{name}, perniagaan ini bertentangan dengan carta anda pada paksi utama.",
            "feeds":      "Unsur dominan {biz} perniagaan menyuburkan Day Master {own} anda — ia memberi tenaga.",
            "drains":     "Unsur dominan {biz} perniagaan mengawal Day Master {own} anda — akan meletihkan dari masa ke masa.",
            "useful_hi":  "Ia membekalkan Dewa Berguna anda ({useful}) sebanyak {pct}% dari carta — sokongan kuat.",
            "useful_mid": "Ia membekalkan Dewa Berguna anda ({useful}) sebanyak {pct}% — sokongan sederhana.",
            "useful_low": "Dewa Berguna anda ({useful}) hanya {pct}% dalam perniagaan — lengkapkan dengan warna, ritual, atau rakan kongsi.",
            "avoid_hi":   "Perhatian: ia menguatkan Dewa Elakkan anda ({avoid}) sebanyak {pct}% — perlahan-lahan meletihkan anda.",
            "harmony":    "Isyarat harmoni: {items}.",
            "tension":    "Isyarat ketegangan: {items}.",
        },
    }[lang if lang in ("en", "zh", "ms") else "en"]

    from ...core.bazi.guidance import ELEMENT_NAME as EN
    names = EN.get(lang, EN["en"])
    own_name = names.get(owner_dm, owner_dm)
    biz_name = names.get(biz_dominant, biz_dominant)
    useful_name = names.get(owner_useful, owner_useful)
    avoid_name = names.get(owner_avoid, owner_avoid)

    head = tpl["head_good"] if score >= 65 else tpl["head_ok"] if score >= 45 else tpl["head_bad"]
    parts: list[str] = [head.format(name=owner_name)]

    if feeds:
        parts.append(tpl["feeds"].format(biz=biz_name, own=own_name))
    elif drains:
        parts.append(tpl["drains"].format(biz=biz_name, own=own_name))

    if ug_pct >= 25:
        parts.append(tpl["useful_hi"].format(useful=useful_name, pct=ug_pct))
    elif ug_pct >= 12:
        parts.append(tpl["useful_mid"].format(useful=useful_name, pct=ug_pct))
    else:
        parts.append(tpl["useful_low"].format(useful=useful_name, pct=ug_pct))

    if ag_pct >= 30:
        parts.append(tpl["avoid_hi"].format(avoid=avoid_name, pct=ag_pct))

    if harmony:
        parts.append(tpl["harmony"].format(items="; ".join(harmony[:2])))
    if tension:
        parts.append(tpl["tension"].format(items="; ".join(tension[:2])))

    return " ".join(parts)


def _verdict_from_score(score: int, lang: str = "en") -> str:
    tpl = {
        "en": [
            (80, "Excellent fit — this business amplifies the owner's strengths."),
            (65, "Strong fit — the business supports the owner's chart well."),
            (50, "Workable — the business is functional but requires conscious management."),
            (35, "Challenging — the business clashes with the owner on key axes."),
            (0,  "Poor fit — consider re-timing the opening or choosing another owner as frontperson."),
        ],
        "zh": [
            (80, "极佳契合——此事业能放大主事人的优势。"),
            (65, "良好契合——事业与主事人的命盘相辅相成。"),
            (50, "可行——但需要主事人有意识地经营。"),
            (35, "挑战——事业与主事人于关键面相冲克。"),
            (0,  "契合度低——建议重新择吉开业或由他人挂名。"),
        ],
        "ms": [
            (80, "Kesesuaian cemerlang — perniagaan menggandakan kekuatan pemilik."),
            (65, "Kesesuaian kukuh — perniagaan menyokong carta pemilik."),
            (50, "Boleh dikendalikan — memerlukan pengurusan sedar."),
            (35, "Mencabar — perniagaan berkonflik dengan pemilik di paksi utama."),
            (0,  "Kesesuaian lemah — pertimbang tarikh pembukaan lain atau pemilik lain."),
        ],
    }[lang if lang in ("en", "zh", "ms") else "en"]
    for threshold, text in tpl:
        if score >= threshold:
            return text
    return tpl[-1][1]


@router.get("/{biz_id}/reading", response_model=BusinessReading)
def business_reading(
    biz_id: int,
    lang: str = Query(default="en", pattern="^(en|zh|ms)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessReading:
    biz = _owned(db, user, biz_id)

    # Business chart (treat open datetime like a birth)
    chart = build_deep_bazi(biz.open_datetime, gender=None, lang=lang)

    # Chinese name reading (if provided)
    name_reading = None
    if biz.chinese_name:
        nr = analyse_chinese_name(biz.chinese_name)
        name_reading = ChineseNameReadingOut(
            name=nr.name,
            surname=nr.surname,
            given=nr.given,
            character_strokes=[CharStroke(**c) for c in nr.character_strokes],
            grids=ChineseNameGridsOut(
                heaven=NameGrid(**nr.grids.heaven),
                person=NameGrid(**nr.grids.person),
                earth=NameGrid(**nr.grids.earth),
                total=NameGrid(**nr.grids.total),
                outer=NameGrid(**nr.grids.outer),
            ),
            element_profile=nr.element_profile,
            dominant_element=nr.dominant_element,
            auspicious_grids=nr.auspicious_grids,
            inauspicious_grids=nr.inauspicious_grids,
            mixed_grids=nr.mixed_grids,
            summary=nr.summary,
            three_talents=ThreeTalents(**nr.three_talents),
            life_stages=[LifeStageOut(**s) for s in nr.life_stages],
            yin_yang=YinYangBalance(**nr.yin_yang),
            aspect_scores=nr.aspect_scores,
            aspect_notes=nr.aspect_notes,
            total_strokes=nr.total_strokes,
            surname_strokes=nr.surname_strokes,
            given_strokes=nr.given_strokes,
        )

    # Compute match between business chart and each of the user's personal profiles.
    profiles: list[Profile] = (
        db.query(Profile)
        .filter(Profile.owner_id == user.id)
        .order_by(Profile.is_main.desc(), Profile.created_at.asc())
        .all()
    )
    biz_fp = four_pillars(biz.open_datetime)
    biz_bal = element_balance(biz_fp).as_dict
    biz_total = sum(biz_bal.values()) or 1.0
    biz_dominant = max(biz_bal, key=biz_bal.get)

    matches: list[BusinessOwnerMatch] = []
    best: BusinessOwnerMatch | None = None
    for p in profiles:
        p_fp = four_pillars(p.birth_datetime)
        c = build_deep_compatibility(p_fp, biz_fp, p.gender, None)

        dms = day_master_strength(p_fp)
        ug_pct = round(biz_bal.get(dms.useful_god, 0.0) / biz_total * 100.0, 1)
        ag_pct = round(biz_bal.get(dms.avoid_god, 0.0) / biz_total * 100.0, 1)

        feeds = PRODUCES.get(biz_dominant) == p_fp.day_master_element
        drains = CONTROLS.get(biz_dominant) == p_fp.day_master_element

        ai = _compose_owner_reading(
            owner_name=p.name,
            owner_dm=p_fp.day_master_element,
            owner_useful=dms.useful_god,
            owner_avoid=dms.avoid_god,
            biz_dominant=biz_dominant,
            ug_pct=ug_pct,
            ag_pct=ag_pct,
            feeds=feeds,
            drains=drains,
            score=c.total_score,
            harmony=c.harmony,
            tension=c.tension,
            lang=lang,
        )

        m = BusinessOwnerMatch(
            profile_id=p.id,
            profile_name=p.name,
            score=c.total_score,
            verdict=_verdict_from_score(c.total_score, lang),
            dm_relation=c.day_master_relation,
            harmony=c.harmony,
            tension=c.tension,
            harmony_count=len(c.harmony),
            tension_count=len(c.tension),
            element_blend=c.element_blend,
            owner_useful_god=dms.useful_god,
            owner_avoid_god=dms.avoid_god,
            business_supplies_useful_god_pct=ug_pct,
            business_amplifies_avoid_god_pct=ag_pct,
            business_feeds_owner=feeds,
            business_drains_owner=drains,
            area_scores=c.area_scores,
            shared_weakness=c.shared_weakness,
            complementary_strengths=c.complementary_strengths,
            ai_reading=ai,
        )
        matches.append(m)
        if best is None or m.score > best.score:
            best = m

    # Feng shui reading: uses main profile's Life Kua + business facing direction.
    fs_out = None
    if biz.facing_direction:
        main_profile = next((p for p in profiles if p.is_main), profiles[0] if profiles else None)
        if main_profile is not None and main_profile.gender:
            owner_fp = four_pillars(main_profile.birth_datetime)
            owner_solar_year = _solar_year_for(owner_fp)
            try:
                fs = analyse_home(
                    solar_year=owner_solar_year,
                    gender=main_profile.gender,
                    house_facing=biz.facing_direction.upper(),
                    rooms={},
                )
                fs_out = FengShuiReadingOut(
                    life_kua_number=fs.life_kua_number,
                    life_kua_group=fs.life_kua_group,
                    house_facing=fs.house_facing,
                    house_sitting=fs.house_sitting,
                    house_group=fs.house_group,
                    person_house_match=fs.person_house_match,
                    match_note=fs.match_note,
                    lucky_directions=fs.lucky_directions,
                    unlucky_directions=fs.unlucky_directions,
                    room_verdicts=[RoomVerdictOut(**rv.__dict__) for rv in fs.room_verdicts],
                    overall_score=fs.overall_score,
                    summary=fs.summary,
                    recommendations=fs.recommendations,
                )
            except ValueError:
                fs_out = None

    summary_bits: list[str] = []
    if best is not None:
        summary_bits.append(f"Best-matched owner: {best.profile_name} ({best.score}/100 — {best.verdict})")
    if name_reading is not None:
        summary_bits.append(
            f"Business name {biz.chinese_name}: {name_reading.auspicious_grids}/5 auspicious grids."
        )
    if fs_out is not None:
        summary_bits.append(
            f"Premises feng shui score: {fs_out.overall_score}/100 — {fs_out.summary}"
        )
    if not summary_bits:
        summary_bits.append("Add an owner profile, Chinese name, or facing direction for a full reading.")

    return BusinessReading(
        business=BusinessOut.model_validate(biz),
        chart=chart,
        name_reading=name_reading,
        feng_shui=fs_out,
        owner_matches=matches,
        best_match_profile_id=best.profile_id if best else None,
        summary=" · ".join(summary_bits),
    )
