"""FastAPI dependency injection helpers.

Security Features:
- Token version verification for revocation support
- Role-based access control (RBAC) dependencies
- Secure service initialization

SECURITY NOTE: All authentication checks verify user_version against database
to support token revocation on password change/logout.
"""

import logging
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
from ..utils.auth import decode_access_token, verify_token_version
from ..models.user import User

logger = logging.getLogger(__name__)

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

    SECURITY: This function performs critical security checks:
    1. Validates JWT signature and expiration
    2. Verifies user exists in database
    3. Verifies token version matches user_version (revocation check)

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException 401: If token is invalid, revoked, or user not found
    """
    # Decode JWT token
    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub")
    token_version: int = payload.get("ver", 1)

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

    # SECURITY: Verify token version for revocation check
    # If user changed password or logged out all sessions, this will fail
    if not verify_token_version(token_version, user.user_version):
        logger.warning(f"Revoked token used for user: {user.email}", extra={
            "event": "token_revoked",
            "user_id": str(user.id),
            "token_version": token_version,
            "user_version": user.user_version,
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
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


class RequiresRole:
    """RBAC dependency for protecting admin routes.

    SECURITY: Use this to protect routes that require specific roles.

    Example:
        @router.get("/admin/users")
        async def list_all_users(
            current_user: User = Depends(RequiresRole("admin"))
        ):
            ...
    """

    def __init__(self, required_role: str):
        """Initialize with required role.

        Args:
            required_role: Role required to access the route (e.g., "admin")
        """
        self.required_role = required_role

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has required role.

        Args:
            current_user: Current authenticated and active user

        Returns:
            User if they have the required role

        Raises:
            HTTPException 403: If user doesn't have required role
        """
        if current_user.role != self.required_role:
            logger.warning(
                f"Access denied: user {current_user.email} attempted to access "
                f"{self.required_role}-only resource",
                extra={
                    "event": "access_denied",
                    "user_id": str(current_user.id),
                    "user_role": current_user.role,
                    "required_role": self.required_role,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user


# Convenience dependency for admin routes
get_admin_user = RequiresRole("admin")
