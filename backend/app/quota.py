"""Free-tier usage quotas. Ignored for is_premium users."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .models import User

FEATURE_FIELD = {
    "numerology":    ("free_numerology_uses",    "free_numerology_uses"),
    "compatibility": ("free_compatibility_uses", "free_compatibility_uses"),
    "name":          ("free_name_uses",          "free_name_uses"),
    "fengshui":      ("free_fengshui_uses",      "free_fengshui_uses"),
    "chat":          ("free_chat_messages",      "free_chat_messages"),
}

FEATURE_LIMIT_ATTR = {
    "numerology":    "free_numerology_uses",
    "compatibility": "free_compatibility_uses",
    "name":          "free_name_uses",
    "fengshui":      "free_fengshui_uses",
    "chat":          "free_chat_messages",
}


def check_and_consume(
    feature: str,
    user: User,
    db: Session,
    consume: bool = True,
) -> None:
    """Raise 402 if the free user has hit the limit for ``feature``. Increments
    the counter (when consume=True) so the next call will be blocked."""
    if user.is_premium:
        return
    attr = FEATURE_LIMIT_ATTR.get(feature)
    if attr is None:
        return
    used: int = getattr(user, attr, 0) or 0
    settings = get_settings()
    limit: int = getattr(settings, attr, 0)
    if used >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Free tier allows {limit} use(s) of {feature}. "
                "Upgrade to Premium for unlimited access."
            ),
        )
    if consume:
        setattr(user, attr, used + 1)
        db.add(user)
        db.flush()
