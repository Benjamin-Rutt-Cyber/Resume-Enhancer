"""FastAPI dependency injection helpers."""

from typing import Generator
from pathlib import Path
from functools import lru_cache

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..core.config import settings
from ..services.anthropic_service import AnthropicService
from ..services.workspace_service import WorkspaceService
from ..utils.document_parser import DocumentParser
from ..utils.auth import decode_access_token
from ..models.user import User


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


# Authentication
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Verify JWT token and return current user.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    # Decode JWT token
    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Active user object

    Raises:
        HTTPException 400: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    return current_user
