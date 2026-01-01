"""FastAPI dependency injection helpers."""

from typing import Generator
from pathlib import Path
from functools import lru_cache

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..core.config import settings
from ..services.anthropic_service import AnthropicService
from ..services.workspace_service import WorkspaceService
from ..utils.document_parser import DocumentParser


# Workspace root from settings
WORKSPACE_ROOT = Path(settings.WORKSPACE_ROOT)


def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_anthropic_service() -> AnthropicService:
    """Get Anthropic service instance.

    Returns:
        Configured AnthropicService instance
    """
    return AnthropicService(api_key=settings.ANTHROPIC_API_KEY)


@lru_cache()
def get_workspace_service() -> WorkspaceService:
    """
    Get workspace service singleton.

    The service is cached using lru_cache to ensure a single instance
    is reused across all requests, improving performance.

    Returns:
        WorkspaceService instance configured with workspace root from settings
    """
    return WorkspaceService(WORKSPACE_ROOT)


@lru_cache()
def get_document_parser() -> DocumentParser:
    """
    Get document parser singleton.

    The parser is cached using lru_cache to ensure a single instance
    is reused across all requests.

    Returns:
        DocumentParser instance
    """
    return DocumentParser()
