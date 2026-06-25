"""Application configuration loaded from environment variables."""

import os

from pydantic import BaseSettings, validator

DEFAULT_SECRET_KEY = "change-me-in-production"


class Settings(BaseSettings):
    """Runtime settings for TeamSpace."""

    DATABASE_URL: str
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    SESSION_LIFETIME_HOURS: int = 8
    MAX_UPLOAD_BYTES: int = 10485760
    PORT: int = 8000
    BASE_URL: str = ""

    @validator("BASE_URL", pre=True, always=True)
    def set_base_url(cls, v):
        """Use BASE_URL env or derive from RAILWAY_PUBLIC_DOMAIN."""
        if v:
            return v.rstrip("/")
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
        if domain:
            return f"https://{domain}"
        return ""

    @validator("DATABASE_URL", pre=True)
    def normalize_database_url(cls, value: str) -> str:
        """Convert Railway-style postgres:// URLs to postgresql://."""
        if value and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def validate_settings() -> None:
    """Ensure critical settings are configured before startup."""
    if settings.SECRET_KEY == DEFAULT_SECRET_KEY:
        raise ValueError("SECRET_KEY must be set to a non-default value")
    if not settings.DATABASE_URL.startswith("postgresql://"):
        raise ValueError("DATABASE_URL must start with postgresql://")
