"""Feng Shui home analysis endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..schemas import FengShuiReadingOut, FengShuiRequest, RoomVerdictOut
from ...core.fengshui.house import analyse_home
from ..services.readings import _solar_year_for
from ...core.bazi.calculator import four_pillars

router = APIRouter(prefix="/api/fengshui", tags=["fengshui"])


@router.post("/home", response_model=FengShuiReadingOut)
def home_reading(
    payload: FengShuiRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FengShuiReadingOut:
    profile = db.get(Profile, payload.profile_id)
    if profile is None or profile.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not profile.gender:
        raise HTTPException(
            status_code=400,
            detail="Life Kua requires the profile's gender. Edit the profile to add it."
        )

    fp = four_pillars(profile.birth_datetime)
    solar_year = _solar_year_for(fp)

    try:
        r = analyse_home(
            solar_year=solar_year,
            gender=profile.gender,
            house_facing=payload.house_facing.upper(),
            rooms={k: v.upper() for k, v in payload.rooms.items()},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FengShuiReadingOut(
        life_kua_number=r.life_kua_number,
        life_kua_group=r.life_kua_group,
        house_facing=r.house_facing,
        house_sitting=r.house_sitting,
        house_group=r.house_group,
        person_house_match=r.person_house_match,
        match_note=r.match_note,
        lucky_directions=r.lucky_directions,
        unlucky_directions=r.unlucky_directions,
        room_verdicts=[RoomVerdictOut(**rv.__dict__) for rv in r.room_verdicts],
        overall_score=r.overall_score,
        summary=r.summary,
        recommendations=r.recommendations,
    )
