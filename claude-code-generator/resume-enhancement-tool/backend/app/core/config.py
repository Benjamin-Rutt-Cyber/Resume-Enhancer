"""
Application configuration settings.
"""

import logging
from typing import List
from pathlib import Path
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
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://resume-enhancement-tool-frontend.onrender.com", # Placeholder, ideally use env var
        "https://www.re-vsion.com",
        "https://re-vsion.com",
    ]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = ""  # OPTIONAL - Only needed if ENABLE_STYLE_PREVIEW_API=true

    # API Cost Controls
    # API Cost Controls
    ENABLE_STYLE_PREVIEW_API: bool = True  # Enabled for automatic enhancements

    # File Storage
    # Default to 'workspace' in the project root (absolute path)
    WORKSPACE_ROOT: str = str(Path(__file__).parent.parent.parent.resolve() / "workspace")

    @validator('ALLOWED_ORIGINS')
    def validate_cors_origins(cls, v):
        """Warn if wildcard CORS is enabled."""
        if '*' in v:
            logger.warning(
                "Wildcard CORS origin detected! "
                "This is insecure for production. "
                "Use specific origins instead."
            )
        return v

    @validator('WORKSPACE_ROOT')
    def validate_workspace_root(cls, v):
        """Ensure workspace root is a valid directory path."""
        from pathlib import Path
        workspace_path = Path(v)
        if not workspace_path.exists():
            logger.warning(
                f"Workspace directory does not exist: {v}. "
                "It will be created on startup."
            )
        return v

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

    def validate_production_config(self) -> List[str]:
        """
        Validate production configuration and return list of issues.

        Returns:
            list[str]: List of configuration issues (empty if no issues)
        """
        issues = []

        if self.DEBUG:
            issues.append("CRITICAL: DEBUG mode enabled")

        if "sqlite" in self.DATABASE_URL.lower():
            issues.append("WARNING: Using SQLite (recommend PostgreSQL for production)")

        if len(self.SECRET_KEY) < 32:
            issues.append("CRITICAL: SECRET_KEY too short (minimum 32 characters)")

        if self.ENABLE_STYLE_PREVIEW_API and not self.ANTHROPIC_API_KEY:
            issues.append("WARNING: ENABLE_STYLE_PREVIEW_API=true but ANTHROPIC_API_KEY not set")

        if '*' in self.ALLOWED_ORIGINS:
            issues.append("CRITICAL: Wildcard CORS origin detected (security risk)")

        return issues

    def is_production_ready(self) -> bool:
        """
        Check if configuration is production-ready.

        Returns:
            bool: True if configuration meets production requirements
        """
        issues = self.validate_production_config()

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
