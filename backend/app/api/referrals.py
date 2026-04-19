"""User-facing referral summary."""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Commission, User
from ..referral import MONTHLY_FEE_CENTS, TIER_BPS
from ..schemas import ReferralSummary, ReferredUserOut

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


def _public_base_url() -> str:
    return (
        os.environ.get("PUBLIC_BASE_URL")
        or "https://trustworthy-alignment-production-f6f4.up.railway.app"
    )


@router.get("/me", response_model=ReferralSummary)
def my_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReferralSummary:
    # Direct referrals (tier 1 downline)
    tier1 = (
        db.query(User)
        .filter(User.referred_by_id == user.id)
        .order_by(User.created_at.desc())
        .all()
    )
    tier1_ids = [u.id for u in tier1]

    # Tier 2: users whose referred_by is in tier1_ids
    tier2_count = 0
    tier3_count = 0
    if tier1_ids:
        tier2_ids = [
            r[0]
            for r in db.query(User.id)
            .filter(User.referred_by_id.in_(tier1_ids))
            .all()
        ]
        tier2_count = len(tier2_ids)
        if tier2_ids:
            tier3_count = (
                db.query(func.count(User.id))
                .filter(User.referred_by_id.in_(tier2_ids))
                .scalar()
                or 0
            )

    # Commission totals
    pending_rows = (
        db.query(Commission)
        .filter(Commission.earner_user_id == user.id, Commission.status == "pending")
        .all()
    )
    paid_rows = (
        db.query(Commission)
        .filter(Commission.earner_user_id == user.id, Commission.status == "paid")
        .all()
    )
    pending_cents = sum(c.amount_cents for c in pending_rows)
    paid_cents = sum(c.amount_cents for c in paid_rows)

    code = user.referral_code or ""
    share_url = f"{_public_base_url().rstrip('/')}/register?ref={code}"
    tier_percents = [bps // 100 for bps in TIER_BPS]

    return ReferralSummary(
        code=code,
        share_url=share_url,
        tier_percents=tier_percents,
        monthly_fee_usd=MONTHLY_FEE_CENTS / 100,
        direct_referrals=[ReferredUserOut.model_validate(u) for u in tier1],
        downline_tier_counts={
            "tier_1": len(tier1_ids),
            "tier_2": tier2_count,
            "tier_3": tier3_count,
        },
        pending_cents=pending_cents,
        paid_cents=paid_cents,
        pending_count=len(pending_rows),
        paid_count=len(paid_rows),
    )
