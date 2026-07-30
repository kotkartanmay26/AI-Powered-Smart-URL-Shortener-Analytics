import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
_LOCALHOST_DB_DEFAULT = (
    "postgresql+psycopg2://postgres:tanmay%40123@localhost:5432/smart_url_shortener_db"
)


def _resolve_database_url() -> str:
    """
    Resolve DATABASE_URL in precedence order:
    1. DATABASE_URL  env var     (Render injects this via fromDatabase.connectionString)
    2. POSTGRES_URL  env var     (Render sometimes exposes this directly)
    3. DATABASE_URL  from .env   (local development)
    4. localhost:5432 fallback   (only used when running locally without env/.env)

    CRITICAL: We MUST prefer environment variables over the localhost default
    so that Render's PostgreSQL is never bypassed on the managed environment.
    """
    env_db = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if env_db:
        return env_db
    return _LOCALHOST_DB_DEFAULT


class Settings(BaseSettings):
    APP_NAME: str = "Smart URL Shortener & Analytics Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-this-secret-key-before-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Use the env-var-first resolver before passing to Pydantic. Pydantic will
    # still be able to override via env/.env, but this guarantees we never
    # silently fall back to localhost when DATABASE_URL is set in the shell
    # environment (Render's case).
    DATABASE_URL: str = _resolve_database_url()
    BACKEND_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    AUTO_CREATE_TABLES: bool = True
    ADMIN_EMAILS: list[str] = []
    RATE_LIMIT_PER_MINUTE: int = 120

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", "ADMIN_EMAILS", mode="before")
    @classmethod
    def split_csv(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
