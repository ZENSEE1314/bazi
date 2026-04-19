"""Saved history for numerology / Chinese-name readings."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import SavedReading, User
from ..schemas import HistoryItemOut

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryItemOut])
def list_history(
    kind: str = Query(..., pattern="^(numerology|name|face|palm)$"),
    q: str | None = Query(default=None, description="case-insensitive search on label"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedReading]:
    query = db.query(SavedReading).filter(
        SavedReading.user_id == user.id,
        SavedReading.kind == kind,
    )
    if q:
        query = query.filter(SavedReading.label.ilike(f"%{q.strip()}%"))
    return query.order_by(SavedReading.created_at.desc()).limit(100).all()


@router.get("/{item_id}")
def get_history_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    item = db.get(SavedReading, item_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="History item not found")
    try:
        payload = json.loads(item.payload)
    except json.JSONDecodeError:
        payload = {}
    return {
        "id": item.id,
        "kind": item.kind,
        "label": item.label,
        "subtype": item.subtype,
        "created_at": item.created_at.isoformat(),
        "payload": payload,
    }


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_history_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.get(SavedReading, item_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="History item not found")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- helper called from readings.py / name.py on successful reads --------

def save_reading(
    db: Session,
    user: User,
    kind: str,
    label: str,
    payload: dict | str,
    subtype: str | None = None,
) -> SavedReading:
    if not isinstance(payload, str):
        payload = json.dumps(payload, default=str, ensure_ascii=False)
    item = SavedReading(
        user_id=user.id,
        kind=kind,
        label=label[:120],
        subtype=subtype,
        payload=payload,
    )
    db.add(item)
    db.flush()
    return item
