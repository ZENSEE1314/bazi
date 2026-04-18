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

    free_profile_limit: int = 3
    cors_origins: str = "*"

    static_dir: str = "frontend/dist"


@lru_cache
def get_settings() -> Settings:
    return Settings()
