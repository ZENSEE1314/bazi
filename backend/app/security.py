"""Password hashing and JWT utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from .config import get_settings

# bcrypt limits secret to 72 bytes. We truncate before hashing and verifying so
# long passwords don't error; the trade-off is documented and acceptable since
# 72 bytes of entropy is more than enough.
_BCRYPT_MAX = 72


def hash_password(password: str) -> str:
    secret = password.encode("utf-8")[:_BCRYPT_MAX]
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        secret = password.encode("utf-8")[:_BCRYPT_MAX]
        return bcrypt.checkpw(secret, hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    """Return subject (user id as string) or raise JWTError."""
    settings = get_settings()
    data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    sub = data.get("sub")
    if not sub:
        raise JWTError("Missing subject")
    return sub
