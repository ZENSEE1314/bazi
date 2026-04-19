"""FastAPI application entry point."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import admin, auth, chat, fengshui, name, profiles, readings, referrals
from .config import get_settings
from .db import Base, engine

settings = get_settings()

app = FastAPI(
    title="Metaphysical Analysis & Numerology Suite",
    version="0.1.0",
    description="Ba Zi (Four Pillars) and Universal Numerology APIs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _init_db() -> None:
    # For production, prefer alembic migrations. This is a safety net for
    # first boot and for dev SQLite.
    Base.metadata.create_all(bind=engine)
    _ensure_profile_columns()
    _ensure_user_columns()
    _bootstrap_admin()


def _ensure_profile_columns() -> None:
    """Idempotent migration: add columns introduced after 0.1.0."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    try:
        cols = {c["name"] for c in inspector.get_columns("profiles")}
    except Exception:
        return

    additions = [("chinese_name", "VARCHAR(60)")]
    with engine.begin() as conn:
        for col_name, ddl in additions:
            if col_name not in cols:
                conn.execute(text(f"ALTER TABLE profiles ADD COLUMN {col_name} {ddl}"))


def _ensure_user_columns() -> None:
    """Add referral / admin / active columns to the users table if missing."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    try:
        cols = {c["name"] for c in inspector.get_columns("users")}
    except Exception:
        return

    additions = [
        ("is_active", "BOOLEAN NOT NULL DEFAULT TRUE"),
        ("is_admin", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("referral_code", "VARCHAR(16)"),
        ("referred_by_id", "INTEGER"),
        ("free_numerology_uses", "INTEGER NOT NULL DEFAULT 0"),
        ("free_compatibility_uses", "INTEGER NOT NULL DEFAULT 0"),
        ("free_name_uses", "INTEGER NOT NULL DEFAULT 0"),
        ("free_fengshui_uses", "INTEGER NOT NULL DEFAULT 0"),
        ("free_chat_messages", "INTEGER NOT NULL DEFAULT 0"),
    ]
    with engine.begin() as conn:
        for col_name, ddl in additions:
            if col_name not in cols:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {ddl}"))
        # Backfill referral codes for any user without one.
        from .referral import generate_referral_code

        rows = list(conn.execute(text("SELECT id FROM users WHERE referral_code IS NULL")))
        for row in rows:
            code = generate_referral_code()
            conn.execute(
                text("UPDATE users SET referral_code = :c WHERE id = :id"),
                {"c": code, "id": row[0]},
            )


def _bootstrap_admin() -> None:
    """Promote the ADMIN_EMAIL user to admin on every startup."""
    admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    if not admin_email:
        return
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET is_admin = TRUE WHERE LOWER(email) = :email"),
            {"email": admin_email},
        )


app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(readings.router)
app.include_router(name.router)
app.include_router(fengshui.router)
app.include_router(chat.router)
app.include_router(referrals.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# --- Static frontend serving ---------------------------------------------
_static_dir = Path(settings.static_dir)
if _static_dir.is_dir():
    _assets = _static_dir / "assets"
    if _assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def _spa_catchall(full_path: str):
        # Serve files directly if they exist (e.g. /favicon.ico), otherwise
        # fall back to index.html for SPA client-side routing.
        if full_path:
            candidate = _static_dir / full_path
            if candidate.is_file():
                return FileResponse(str(candidate))
        index = _static_dir / "index.html"
        if index.is_file():
            return FileResponse(str(index))
        return {"detail": "Frontend not built. Run `npm --prefix frontend run build`."}
