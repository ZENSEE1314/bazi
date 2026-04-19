"""App configuration pulled from environment."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    database_url: str = Field(
        default="sqlite:///./dev.db",
        description="PostgreSQL URL in production; SQLite for dev.",
    )
    jwt_secret: str = Field(default="dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24  # 24h

    free_profile_limit: int = 1
    free_numerology_uses: int = 1
    free_compatibility_uses: int = 1
    free_name_uses: int = 1
    free_fengshui_uses: int = 1
    free_chat_messages: int = 1
    cors_origins: str = "*"

    static_dir: str = "frontend/dist"

    # Stripe integration (all optional; the billing endpoints return a clear
    # error when keys are missing).
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""            # recurring $19/mo Price ID
    stripe_success_path: str = "/referrals?upgraded=1"
    stripe_cancel_path: str = "/referrals?upgraded=0"
    public_base_url: str = ""            # e.g. https://your-app.up.railway.app


@lru_cache
def get_settings() -> Settings:
    return Settings()
