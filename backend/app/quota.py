"""Free-tier usage quotas.

Policy:
  1. Premium (unlimited monthly) — always allowed.
  2. Free use available — use it (increment free_* counter).
  3. Feature credit available — spend 1 credit.
  4. Otherwise — 402 Payment Required with the buy-options summary.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .models import User

FEATURE_LIMIT_ATTR = {
    "numerology":    "free_numerology_uses",
    "compatibility": "free_compatibility_uses",
    "name":          "free_name_uses",
    "fengshui":      "free_fengshui_uses",
    "chat":          "free_chat_messages",
    # face/palm share the numerology free slot by policy — or leave untracked
    # so they're always allowed on free tier. We leave them untracked for now
    # so existing users keep today's behaviour (no regression).
}


def check_and_consume(
    feature: str,
    user: User,
    db: Session,
    consume: bool = True,
) -> None:
    """Allow the call or raise 402. Consumes a free use or a credit when needed."""
    if user.is_premium:
        return
    attr = FEATURE_LIMIT_ATTR.get(feature)
    if attr is None:
        return  # feature not quota-tracked

    used: int = getattr(user, attr, 0) or 0
    settings = get_settings()
    limit: int = getattr(settings, attr, 0)

    if used < limit:
        if consume:
            setattr(user, attr, used + 1)
            db.add(user)
            db.flush()
        return

    # Free exhausted — try a credit.
    credits = user.feature_credits or 0
    if credits > 0:
        if consume:
            user.feature_credits = credits - 1
            db.add(user)
            db.flush()
        return

    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=(
            f"Free tier allows {limit} use of {feature}. "
            f"Buy a ${settings.feature_credit_cents / 100:.0f} credit for one more read, "
            f"or upgrade to the ${settings.monthly_unlimited_cents / 100:.0f}/month unlimited plan."
        ),
    )
