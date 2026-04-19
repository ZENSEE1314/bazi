"""Chinese name reading endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends as DependsType  # noqa: F401

from sqlalchemy.orm import Session

from ..api.history import save_reading
from ..db import get_db
from ..deps import get_current_user
from ..models import User
from ..quota import check_and_consume
from ..schemas import (
    ChineseNameRequest,
    ChineseNameReadingOut,
    ChineseNameGridsOut,
    CharStroke,
    LifeStageOut,
    NameGrid,
    ThreeTalents,
    YinYangBalance,
)
from ...core.numerology.chinese_name import analyse_chinese_name

router = APIRouter(prefix="/api/name", tags=["name"])


@router.post("/chinese", response_model=ChineseNameReadingOut)
def chinese_name(
    payload: ChineseNameRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChineseNameReadingOut:
    check_and_consume("name", user, db)
    try:
        r = analyse_chinese_name(payload.name, payload.surname_length)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def _grid(g: dict) -> NameGrid:
        return NameGrid(
            number=g["number"],
            en=g["en"],
            quality=g["quality"],
            theme=g["theme"],
        )

    out = ChineseNameReadingOut(
        name=r.name,
        surname=r.surname,
        given=r.given,
        character_strokes=[CharStroke(**c) for c in r.character_strokes],
        grids=ChineseNameGridsOut(
            heaven=_grid(r.grids.heaven),
            person=_grid(r.grids.person),
            earth=_grid(r.grids.earth),
            total=_grid(r.grids.total),
            outer=_grid(r.grids.outer),
        ),
        element_profile=r.element_profile,
        dominant_element=r.dominant_element,
        auspicious_grids=r.auspicious_grids,
        inauspicious_grids=r.inauspicious_grids,
        mixed_grids=r.mixed_grids,
        summary=r.summary,
        three_talents=ThreeTalents(**r.three_talents),
        life_stages=[LifeStageOut(**s) for s in r.life_stages],
        yin_yang=YinYangBalance(**r.yin_yang),
        aspect_scores=r.aspect_scores,
        aspect_notes=r.aspect_notes,
        total_strokes=r.total_strokes,
        surname_strokes=r.surname_strokes,
        given_strokes=r.given_strokes,
    )
    save_reading(
        db, user,
        kind="name",
        label=payload.name,
        payload=out.model_dump(mode="json"),
    )
    db.commit()
    return out
