"""
Application configuration settings.
"""

import logging
from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Resume Enhancement Tool"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False  # Default to False for production safety
    SECRET_KEY: str  # No default - MUST be provided via .env

    # API
    API_PREFIX: str = "/api"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY meets security requirements."""
        if not v:
            raise ValueError("SECRET_KEY is required and cannot be empty")
        if v == "dev-secret-key-change-in-production":
            raise ValueError(
                "Production SECRET_KEY must be changed! "
                "Do not use the default development key."
            )
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters (got {len(v)}). "
                "Use a strong, randomly generated key."
            )
        return v

    @validator('DEBUG')
    def warn_debug_production(cls, v):
        """Warn if DEBUG mode is enabled."""
        if v:
            logger.warning(
                "DEBUG mode is enabled! "
                "This should be False in production for security."
            )
        return v

    def is_production_ready(self) -> bool:
        """
        Check if configuration is production-ready.

        Returns:
            bool: True if configuration meets production requirements
        """
        issues = []

        if self.DEBUG:
            issues.append("DEBUG mode is enabled")

        if "sqlite" in self.DATABASE_URL.lower():
            issues.append("Using SQLite (consider PostgreSQL for production)")

        if len(self.SECRET_KEY) < 32:
            issues.append("SECRET_KEY is too short")

        if issues:
            logger.warning(
                f"Production readiness check failed: {', '.join(issues)}"
            )
            return False

        return True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields for security


settings = Settings()
