"""Chinese name reading endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_current_user
from ..models import User
from ..schemas import (
    ChineseNameRequest,
    ChineseNameReadingOut,
    ChineseNameGridsOut,
    CharStroke,
    NameGrid,
)
from ...core.numerology.chinese_name import analyse_chinese_name

router = APIRouter(prefix="/api/name", tags=["name"])


@router.post("/chinese", response_model=ChineseNameReadingOut)
def chinese_name(
    payload: ChineseNameRequest,
    user: User = Depends(get_current_user),
) -> ChineseNameReadingOut:
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

    return ChineseNameReadingOut(
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
    )
