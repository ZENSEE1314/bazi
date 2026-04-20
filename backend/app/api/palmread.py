"""Palm reading (手相) endpoint.

Flow: browser submits a photo of an outstretched palm → Ollama vision
extracts the 12 traits → deterministic rule engine renders the narrative.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api.history import save_reading
from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..quota import check_and_consume
from ..schemas import PalmLineOut, PalmReadingOut, PalmReadingRequest
from ...core.palmread.engine import analyse_palm
from ...core.palmread.vision import extract_palm_traits

router = APIRouter(prefix="/api/palm", tags=["palm-reading"])


@router.post("/reading", response_model=PalmReadingOut)
def palm_reading(
    payload: PalmReadingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PalmReadingOut:
    profile_label = "self"
    if payload.profile_id is not None:
        profile = db.get(Profile, payload.profile_id)
        if profile is None or profile.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile_label = profile.name

    check_and_consume("palmread", user, db)

    try:
        t = extract_palm_traits(payload.image)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    r = analyse_palm(
        hand_shape=t["hand_shape"],
        dominant_hand=t["dominant_hand"],
        finger_length=t["finger_length"],
        life_length=t["life_length"],   life_depth=t["life_depth"],
        heart_length=t["heart_length"], heart_depth=t["heart_depth"],
        head_length=t["head_length"],   head_depth=t["head_depth"],
        fate_length=t["fate_length"],   fate_depth=t["fate_depth"],
        marriage_lines=t["marriage_lines"],
    )

    out = PalmReadingOut(
        hand_shape=r.hand_shape,
        hand_shape_label=r.hand_shape_label,
        governing_element=r.governing_element,
        personality_summary=r.personality_summary,
        dominant_hand=r.dominant_hand,
        finger_interpretation=r.finger_interpretation,
        lines=[PalmLineOut(**ln.__dict__) for ln in r.lines],
        vitality_score=r.vitality_score,
        love_score=r.love_score,
        intellect_score=r.intellect_score,
        career_score=r.career_score,
        marriage_score=r.marriage_score,
        overall_score=r.overall_score,
        life_path=r.life_path,
        love_path=r.love_path,
        career_path=r.career_path,
        strengths=r.strengths,
        watchouts=r.watchouts,
        recommendations=r.recommendations,
    )

    save_reading(
        db, user,
        kind="palm",
        label=f"{profile_label} · {r.hand_shape} hand · {r.overall_score}",
        subtype=r.hand_shape,
        payload=out.model_dump(mode="json"),
    )
    db.commit()
    return out
