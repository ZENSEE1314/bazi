"""Reading endpoints: Ba Zi chart, numerology, daily luck, compatibility."""

from __future__ import annotations

from datetime import date as _date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..schemas import (
    BaZiReading,
    CompatibilityReading,
    CompatibilityRequest,
    DailyCalendarDay,
    DailyLuck,
    DeepBaZiReading,
    DeepCompatibility,
    DeepNumerologyReading,
    NumerologyReading,
    NumerologyRequest,
)
from ..services.readings import (
    build_bazi_reading,
    build_calendar,
    build_compatibility,
    build_daily_luck,
    build_deep_bazi,
    build_deep_compatibility_reading,
    build_deep_numerology,
    build_numerology_reading,
)

router = APIRouter(prefix="/api", tags=["readings"])


def _owned_profile(db: Session, user: User, profile_id: int) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None or profile.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/profiles/{profile_id}/bazi", response_model=BaZiReading)
def profile_bazi(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BaZiReading:
    profile = _owned_profile(db, user, profile_id)
    return build_bazi_reading(profile.birth_datetime)


@router.get("/profiles/{profile_id}/daily", response_model=DailyLuck)
def profile_daily(
    profile_id: int,
    date: _date | None = Query(default=None, description="YYYY-MM-DD; defaults to today"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyLuck:
    profile = _owned_profile(db, user, profile_id)
    when = datetime.combine(date, datetime.min.time().replace(hour=12)) if date else datetime.now()
    return build_daily_luck(profile.birth_datetime, when)


@router.get("/profiles/{profile_id}/calendar", response_model=list[DailyCalendarDay])
def profile_calendar(
    profile_id: int,
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DailyCalendarDay]:
    profile = _owned_profile(db, user, profile_id)
    return build_calendar(profile.birth_datetime, year, month)


@router.get("/profiles/{profile_id}/deep", response_model=DeepBaZiReading)
def profile_deep(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeepBaZiReading:
    profile = _owned_profile(db, user, profile_id)
    return build_deep_bazi(profile.birth_datetime, profile.gender)


@router.post("/numerology/deep", response_model=DeepNumerologyReading)
def deep_numerology(payload: NumerologyRequest, user: User = Depends(get_current_user)) -> DeepNumerologyReading:
    try:
        return build_deep_numerology(payload.number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/numerology", response_model=NumerologyReading)
def numerology(payload: NumerologyRequest, user: User = Depends(get_current_user)) -> NumerologyReading:
    try:
        return build_numerology_reading(payload.number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/compatibility", response_model=CompatibilityReading)
def compatibility(
    payload: CompatibilityRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompatibilityReading:
    if payload.profile_a_id == payload.profile_b_id:
        raise HTTPException(status_code=400, detail="Pick two different profiles")
    profile_a = _owned_profile(db, user, payload.profile_a_id)
    profile_b = _owned_profile(db, user, payload.profile_b_id)
    return build_compatibility(profile_a.birth_datetime, profile_b.birth_datetime)


@router.post("/compatibility/deep", response_model=DeepCompatibility)
def compatibility_deep(
    payload: CompatibilityRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeepCompatibility:
    if payload.profile_a_id == payload.profile_b_id:
        raise HTTPException(status_code=400, detail="Pick two different profiles")
    profile_a = _owned_profile(db, user, payload.profile_a_id)
    profile_b = _owned_profile(db, user, payload.profile_b_id)
    return build_deep_compatibility_reading(
        profile_a.name, profile_a.birth_datetime, profile_a.gender,
        profile_b.name, profile_b.birth_datetime, profile_b.gender,
    )
