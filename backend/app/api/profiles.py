"""Profile CRUD with freemium limit."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..schemas import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _unset_main_flag_except(db: Session, owner_id: int, except_id: int | None) -> None:
    q = db.query(Profile).filter(Profile.owner_id == owner_id, Profile.is_main.is_(True))
    if except_id is not None:
        q = q.filter(Profile.id != except_id)
    for p in q.all():
        p.is_main = False


@router.get("", response_model=list[ProfileOut])
def list_profiles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Profile]:
    return (
        db.query(Profile)
        .filter(Profile.owner_id == user.id)
        .order_by(Profile.is_main.desc(), Profile.created_at.asc())
        .all()
    )


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: ProfileCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    settings = get_settings()
    existing_count = db.query(Profile).filter(Profile.owner_id == user.id).count()

    if not user.is_premium and existing_count >= settings.free_profile_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Free tier is limited to {settings.free_profile_limit} profiles. "
                "Upgrade to Premium for unlimited profiles."
            ),
        )

    profile = Profile(
        owner_id=user.id,
        name=payload.name,
        birth_datetime=payload.birth_datetime,
        relationship_label=payload.relationship_label,
        birth_location=payload.birth_location,
        gender=payload.gender,
        is_main=payload.is_main,
        notes=payload.notes,
    )
    db.add(profile)
    db.flush()

    if profile.is_main:
        _unset_main_flag_except(db, user.id, profile.id)

    db.commit()
    db.refresh(profile)
    return profile


def _get_owned_profile(db: Session, user: User, profile_id: int) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None or profile.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    return _get_owned_profile(db, user, profile_id)


@router.patch("/{profile_id}", response_model=ProfileOut)
def update_profile(
    profile_id: int,
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = _get_owned_profile(db, user, profile_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)

    if data.get("is_main"):
        _unset_main_flag_except(db, user.id, profile.id)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_owned_profile(db, user, profile_id)
    db.delete(profile)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
