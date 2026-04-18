"""Database engine, session factory, and Base class."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()

# Railway/Heroku-style postgres:// URLs need rewriting, and we prefer the
# psycopg (v3) driver since psycopg2 has no Python 3.14 wheels yet.
_url = _settings.database_url
if _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql+psycopg://", 1)
elif _url.startswith("postgresql://") and "+" not in _url.split("://", 1)[0]:
    _url = _url.replace("postgresql://", "postgresql+psycopg://", 1)

_connect_args: dict = {}
if _url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(_url, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
