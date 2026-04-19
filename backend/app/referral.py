"""Referral code generation + commission posting logic.

3-tier commission structure (percentages apply to whatever the payer paid,
whether it's the $88/mo subscription or a one-off credit / profile slot):
  Tier 1 (direct referrer)       : 20%
  Tier 2 (referrer's referrer)   : 10%
  Tier 3 (grand-grand-referrer)  :  5%
"""

from __future__ import annotations

import secrets

from sqlalchemy.orm import Session

from .models import Commission, SubscriptionPayment, User

MONTHLY_FEE_CENTS = 8800  # $88.00
TIER_BPS = (2000, 1000, 500)  # basis points: 20%, 10%, 5%

# Human-readable ambiguous-free alphabet (no 0/O/1/I).
_ALPHA = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generate_referral_code(length: int = 6) -> str:
    return "".join(secrets.choice(_ALPHA) for _ in range(length))


def ensure_unique_referral_code(db: Session) -> str:
    for _ in range(50):
        code = generate_referral_code()
        if not db.query(User).filter(User.referral_code == code).first():
            return code
    # Fall-back: longer
    return generate_referral_code(10)


def find_user_by_referral_code(db: Session, code: str) -> User | None:
    code = (code or "").strip().upper()
    if not code:
        return None
    return db.query(User).filter(User.referral_code == code).first()


def record_payment_and_commissions(
    db: Session,
    user: User,
    period_month: str,
    amount_cents: int = MONTHLY_FEE_CENTS,
    note: str | None = None,
) -> SubscriptionPayment:
    """Record a subscription payment for ``user`` and create pending commissions
    for up to three ancestors in the referral tree.

    The caller is expected to commit the session.
    """
    payment = SubscriptionPayment(
        user_id=user.id,
        amount_cents=amount_cents,
        period_month=period_month,
        note=note,
    )
    db.add(payment)
    db.flush()

    # Walk up to 3 ancestors
    current = user
    for tier_idx in range(3):
        parent_id = current.referred_by_id
        if parent_id is None:
            break
        parent = db.get(User, parent_id)
        if parent is None or parent.id == user.id:
            break
        bps = TIER_BPS[tier_idx]
        commission_amount = (amount_cents * bps) // 10000
        if commission_amount > 0 and parent.is_active:
            db.add(
                Commission(
                    earner_user_id=parent.id,
                    source_payment_id=payment.id,
                    payer_user_id=user.id,
                    tier=tier_idx + 1,
                    amount_cents=commission_amount,
                    period_month=period_month,
                    status="pending",
                )
            )
        current = parent

    return payment
