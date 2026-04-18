"""Reading endpoints: Ba Zi chart, numerology, daily luck, compatibility."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..schemas import (
    BaZiReading,
    CompatibilityReading,
    CompatibilityRequest,
    DailyLuck,
    NumerologyReading,
    NumerologyRequest,
)
from ..services.readings import (
    build_bazi_reading,
    build_compatibility,
    build_daily_luck,
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyLuck:
    profile = _owned_profile(db, user, profile_id)
    return build_daily_luck(profile.birth_datetime, datetime.now())


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
