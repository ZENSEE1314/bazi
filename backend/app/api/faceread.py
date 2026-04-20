"""Face reading (面相) endpoint.

Flow: browser submits a photo → Ollama vision extracts the 10 traits →
deterministic rule engine renders the narrative. The engine, not the LLM,
writes the reading text, so we can't hallucinate palaces or scores.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api.history import save_reading
from ..db import get_db
from ..deps import get_current_user
from ..models import Profile, User
from ..quota import check_and_consume
from ..schemas import FaceFeatureOut, FaceReadingOut, FaceReadingRequest
from ...core.faceread.engine import analyse_face
from ...core.faceread.vision import extract_face_traits

router = APIRouter(prefix="/api/face", tags=["face-reading"])


@router.post("/reading", response_model=FaceReadingOut)
def face_reading(
    payload: FaceReadingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FaceReadingOut:
    profile_label = "self"
    if payload.profile_id is not None:
        profile = db.get(Profile, payload.profile_id)
        if profile is None or profile.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile_label = profile.name

    check_and_consume("faceread", user, db)

    # Step 1 — vision model looks at the photo and returns the 10 traits.
    try:
        traits = extract_face_traits(payload.image)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Step 2 — deterministic rule engine produces the reading narrative.
    r = analyse_face(
        face_shape=traits["face_shape"],
        forehead=traits["forehead"],
        brows=traits["brows"],
        eyes=traits["eyes"],
        nose=traits["nose"],
        mouth=traits["mouth"],
        ears=traits["ears"],
        chin=traits["chin"],
        cheeks=traits["cheeks"],
        skin=traits["skin"],
    )

    out = FaceReadingOut(
        face_shape=r.face_shape,
        governing_element=r.governing_element,
        personality_summary=r.personality_summary,
        features=[FaceFeatureOut(**f.__dict__) for f in r.features],
        career_score=r.career_score,
        wealth_score=r.wealth_score,
        relationships_score=r.relationships_score,
        health_score=r.health_score,
        family_score=r.family_score,
        overall_score=r.overall_score,
        san_ting_upper=r.san_ting_upper,
        san_ting_middle=r.san_ting_middle,
        san_ting_lower=r.san_ting_lower,
        strengths=r.strengths,
        watchouts=r.watchouts,
        recommendations=r.recommendations,
    )

    save_reading(
        db, user,
        kind="face",
        label=f"{profile_label} · {r.face_shape} face · {r.overall_score}",
        subtype=r.governing_element,
        payload=out.model_dump(mode="json"),
    )
    db.commit()
    return out
