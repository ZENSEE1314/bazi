"""Admin endpoints: membership / commission / user management."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_admin_user
from ..models import Commission, SubscriptionPayment, User
from ..referral import MONTHLY_FEE_CENTS, record_payment_and_commissions
from ..schemas import (
    AdminUserOut,
    CommissionOut,
    MarkPremiumRequest,
    UserOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _annotate(user: User, db: Session) -> AdminUserOut:
    pending = (
        db.query(Commission)
        .filter(Commission.earner_user_id == user.id, Commission.status == "pending")
        .all()
    )
    paid = (
        db.query(Commission)
        .filter(Commission.earner_user_id == user.id, Commission.status == "paid")
        .all()
    )
    out = AdminUserOut.model_validate(user)
    out.total_pending_cents = sum(c.amount_cents for c in pending)
    out.total_paid_cents = sum(c.amount_cents for c in paid)
    return out


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    q: str | None = Query(default=None, description="Search by email or name"),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[AdminUserOut]:
    query = db.query(User)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(User.email.ilike(like), User.display_name.ilike(like)))
    rows = query.order_by(User.created_at.desc()).limit(500).all()
    return [_annotate(u, db) for u in rows]


@router.post("/users/{user_id}/ban", response_model=UserOut)
def ban_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    user = _get(user_id, db)
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unban", response_model=UserOut)
def unban_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    user = _get(user_id, db)
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/admin", response_model=UserOut)
def make_admin(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    user = _get(user_id, db)
    user.is_admin = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unadmin", response_model=UserOut)
def revoke_admin(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    user = _get(user_id, db)
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot revoke your own admin access here")
    user.is_admin = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/set_premium", response_model=UserOut)
def set_premium(
    user_id: int,
    payload: MarkPremiumRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    """Mark user as paid for a given period; records a SubscriptionPayment
    and creates pending commissions for the referral chain."""
    user = _get(user_id, db)

    period = payload.period_month or datetime.utcnow().strftime("%Y-%m")

    # Idempotency: if a payment already exists for this user+period, skip.
    existing = (
        db.query(SubscriptionPayment)
        .filter(
            SubscriptionPayment.user_id == user.id,
            SubscriptionPayment.period_month == period,
        )
        .first()
    )
    if existing is None:
        record_payment_and_commissions(
            db, user, period, amount_cents=MONTHLY_FEE_CENTS, note=payload.note
        )
    user.is_premium = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unset_premium", response_model=UserOut)
def unset_premium(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> User:
    """Mark user as no longer paid (does not revert past commissions)."""
    user = _get(user_id, db)
    user.is_premium = False
    db.commit()
    db.refresh(user)
    return user


# --- Commission management ------------------------------------------------

@router.get("/commissions", response_model=list[CommissionOut])
def list_commissions(
    status_filter: str | None = Query(default=None, alias="status", pattern="^(pending|paid)$"),
    earner_id: int | None = None,
    period_month: str | None = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[Commission]:
    query = db.query(Commission)
    if status_filter:
        query = query.filter(Commission.status == status_filter)
    if earner_id is not None:
        query = query.filter(Commission.earner_user_id == earner_id)
    if period_month:
        query = query.filter(Commission.period_month == period_month)
    return query.order_by(Commission.created_at.desc()).limit(1000).all()


@router.post("/commissions/{commission_id}/mark_paid", response_model=CommissionOut)
def mark_commission_paid(
    commission_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> Commission:
    c = db.get(Commission, commission_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Commission not found")
    if c.status != "paid":
        c.status = "paid"
        c.paid_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(c)
    return c


@router.post("/commissions/pay_all", response_model=dict)
def pay_all_pending(
    period_month: str | None = Query(default=None),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    """Mark every pending commission (optionally for a given period) as paid."""
    query = db.query(Commission).filter(Commission.status == "pending")
    if period_month:
        query = query.filter(Commission.period_month == period_month)
    rows = query.all()
    now = datetime.now(timezone.utc)
    for c in rows:
        c.status = "paid"
        c.paid_at = now
    db.commit()
    total_cents = sum(c.amount_cents for c in rows)
    return {"count": len(rows), "amount_cents": total_cents}


def _get(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
