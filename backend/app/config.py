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
    free_business_limit: int = 1
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
    stripe_price_id: str = ""                # recurring $88/mo Price ID (unlimited plan)
    stripe_price_id_credit: str = ""         # one-time $8 Price ID (1 feature credit)
    stripe_price_id_profile_slot: str = ""   # one-time $16 Price ID (+1 profile slot)
    stripe_success_path: str = "/upgrade?purchased=1"
    stripe_cancel_path: str = "/upgrade?purchased=0"
    public_base_url: str = ""            # e.g. https://your-app.up.railway.app

    # Per-unit pricing (display + internal fallback when Stripe is off).
    monthly_unlimited_cents: int = 8800      # $88.00
    feature_credit_cents: int = 800          # $8.00 per credit
    profile_slot_cents: int = 1600           # $16.00 per extra profile slot


@lru_cache
def get_settings() -> Settings:
    return Settings()
