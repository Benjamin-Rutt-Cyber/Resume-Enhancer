"""Authentication routes for user signup, login, token refresh, and profile.

Security Implementation:
- Signup/Login: Returns access token in body, sets refresh token in HttpOnly cookie
- Refresh: Uses HttpOnly cookie to issue new access token (token rotation)
- Logout: Clears cookie and increments user_version to invalidate all tokens
- Password change: Increments user_version to invalidate all existing sessions

SECURITY NOTES:
- Refresh token stored in HttpOnly, Secure, SameSite=Strict cookie
- Access token lifetime: 30 minutes
- Refresh token lifetime: 7 days
- Token revocation via user_version increment

RATE LIMITS (per spec):
- Auth routes (signup, login): 5/minute to prevent brute force
- Refresh: 10/minute (less strict, user is authenticated via cookie)
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.config import settings
from ...core.security import limiter, AUTH_RATE_LIMIT
from ...models.user import User
from ...schemas.auth import (
    UserCreate, UserLogin, AuthResponse, UserResponse,
    RefreshResponse, PasswordChangeRequest, LogoutResponse
)
from ...utils.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_refresh_token, verify_token_version, validate_password_strength,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# SECURITY: Rate limiting is applied via decorators below

# Cookie settings for refresh token
# SECURITY: HttpOnly prevents XSS access, Secure requires HTTPS, SameSite prevents CSRF
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set the refresh token as an HttpOnly cookie.

    SECURITY: This is the secure way to store refresh tokens:
    - HttpOnly: JavaScript cannot access the cookie (XSS protection)
    - Secure: Cookie only sent over HTTPS
    - SameSite=Strict: Cookie not sent with cross-site requests (CSRF protection)
    """
    # Determine if we're in production (HTTPS) or development (HTTP)
    is_production = not settings.DEBUG

    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_TOKEN_MAX_AGE,
        httponly=True,  # SECURITY: Prevents XSS access
        secure=is_production,  # SECURITY: HTTPS only in production
        samesite="strict",  # SECURITY: Prevents CSRF
        path="/api/auth",  # SECURITY: Only sent to auth endpoints
    )


def clear_refresh_token_cookie(response: Response) -> None:
    """Clear the refresh token cookie on logout."""
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path="/api/auth",
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_RATE_LIMIT)  # SECURITY: 5/minute to prevent abuse
async def signup(
    request: Request,  # Required for rate limiter
    user_data: UserCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user.

    SECURITY:
    - Password validated for 12+ characters
    - Terms acceptance required and tracked
    - Refresh token set in HttpOnly cookie

    Args:
        user_data: User registration data (email, password, full_name, accept_terms)
        response: FastAPI response for setting cookies
        db: Database session

    Returns:
        AuthResponse with access_token and user info

    Raises:
        HTTPException 400: If email already registered or password too weak
    """
    # SECURITY: Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create new user with compliance tracking
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        is_active=True,
        user_version=1,  # SECURITY: Initial version for token revocation
        role="user",  # SECURITY: Default role
        accepted_terms_at=datetime.utcnow(),  # COMPLIANCE: Track terms acceptance
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # AUDIT: Log successful signup
    logger.info(f"New user registered: {new_user.email}", extra={
        "event": "user_signup",
        "user_id": str(new_user.id),
        "email": new_user.email,
    })

    # Create tokens with user_version for revocation support
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        user_version=new_user.user_version
    )
    refresh_token = create_refresh_token(
        user_id=str(new_user.id),
        user_version=new_user.user_version
    )

    # SECURITY: Set refresh token in HttpOnly cookie
    set_refresh_token_cookie(response, refresh_token)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active,
            role=new_user.role,
            created_at=new_user.created_at
        )
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit(AUTH_RATE_LIMIT)  # SECURITY: 5/minute to prevent brute force
async def login(
    request: Request,  # Required for rate limiter
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token.

    SECURITY:
    - Generic error message prevents user enumeration
    - Refresh token set in HttpOnly cookie
    - Login attempt logged for audit trail

    Args:
        credentials: Login credentials (email, password)
        response: FastAPI response for setting cookies
        db: Database session

    Returns:
        AuthResponse with access_token and user info

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    # SECURITY: Generic error message prevents user enumeration
    if not user:
        # AUDIT: Log failed login attempt
        logger.warning("Login attempt for non-existent email", extra={
            "event": "login_failed",
            "reason": "user_not_found",
            "email": credentials.email,
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # AUDIT: Log failed login attempt
        logger.warning(f"Failed login attempt for user: {user.email}", extra={
            "event": "login_failed",
            "reason": "invalid_password",
            "user_id": str(user.id),
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {user.email}", extra={
            "event": "login_failed",
            "reason": "inactive_account",
            "user_id": str(user.id),
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # AUDIT: Log successful login
    logger.info(f"User logged in: {user.email}", extra={
        "event": "login_success",
        "user_id": str(user.id),
    })

    # Create tokens with user_version for revocation support
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_version=user.user_version
    )
    refresh_token = create_refresh_token(
        user_id=str(user.id),
        user_version=user.user_version
    )

    # SECURITY: Set refresh token in HttpOnly cookie
    set_refresh_token_cookie(response, refresh_token)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role=user.role,
            created_at=user.created_at
        )
    )


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("10/minute")  # SECURITY: Higher limit for authenticated refresh
async def refresh_token(
    request: Request,  # Required for rate limiter
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME)
):
    """Refresh access token using refresh token from cookie.

    SECURITY:
    - Refresh token read from HttpOnly cookie (not request body)
    - User version verified to check for revocation
    - New tokens issued (token rotation)

    Args:
        response: FastAPI response for setting new cookie
        db: Database session
        refresh_token: Refresh token from HttpOnly cookie

    Returns:
        RefreshResponse with new access_token

    Raises:
        HTTPException 401: If refresh token is invalid or revoked
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    # Decode and validate refresh token
    payload = decode_refresh_token(refresh_token)
    user_id = payload.get("sub")
    token_version = payload.get("ver", 1)

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # SECURITY: Verify token version for revocation check
    if not verify_token_version(token_version, user.user_version):
        logger.warning(f"Revoked refresh token used for user: {user.email}", extra={
            "event": "token_revoked",
            "user_id": str(user.id),
            "token_version": token_version,
            "user_version": user.user_version,
        })
        # Clear the invalid cookie
        clear_refresh_token_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )

    # SECURITY: Issue new tokens (token rotation)
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        user_version=user.user_version
    )
    new_refresh_token = create_refresh_token(
        user_id=str(user.id),
        user_version=user.user_version
    )

    # Set new refresh token cookie
    set_refresh_token_cookie(response, new_refresh_token)

    logger.debug(f"Token refreshed for user: {user.email}")

    return RefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    logout_all: bool = False
):
    """Logout user and optionally invalidate all sessions.

    SECURITY:
    - Clears refresh token cookie
    - If logout_all=true, increments user_version to invalidate all tokens

    Args:
        response: FastAPI response for clearing cookie
        current_user: Current authenticated user
        db: Database session
        logout_all: If true, invalidate all sessions across all devices

    Returns:
        LogoutResponse with success message
    """
    # Clear the refresh token cookie
    clear_refresh_token_cookie(response)

    if logout_all:
        # SECURITY: Invalidate all active tokens by incrementing user_version
        current_user.increment_version()
        db.commit()

        logger.info(f"User logged out all sessions: {current_user.email}", extra={
            "event": "logout_all",
            "user_id": str(current_user.id),
            "new_version": current_user.user_version,
        })

        return LogoutResponse(message="Successfully logged out from all devices")

    logger.info(f"User logged out: {current_user.email}", extra={
        "event": "logout",
        "user_id": str(current_user.id),
    })

    return LogoutResponse(message="Successfully logged out")


@router.post("/change-password", response_model=LogoutResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password and invalidate all existing sessions.

    SECURITY:
    - Requires current password verification
    - Validates new password strength
    - Increments user_version to invalidate all tokens (force re-login)
    - Clears current refresh token cookie

    Args:
        password_data: Current and new password
        response: FastAPI response for clearing cookie
        current_user: Current authenticated user
        db: Database session

    Returns:
        LogoutResponse indicating password changed

    Raises:
        HTTPException 400: If current password is wrong or new password is weak
    """
    # SECURITY: Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        logger.warning(f"Failed password change attempt for user: {current_user.email}", extra={
            "event": "password_change_failed",
            "reason": "invalid_current_password",
            "user_id": str(current_user.id),
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # SECURITY: Validate new password strength
    is_valid, error_message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # SECURITY: Ensure new password is different from current
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.password_hash = hash_password(password_data.new_password)

    # SECURITY: Invalidate all existing tokens by incrementing version
    current_user.increment_version()

    db.commit()

    # Clear the refresh token cookie
    clear_refresh_token_cookie(response)

    # AUDIT: Log password change
    logger.info(f"Password changed for user: {current_user.email}", extra={
        "event": "password_change",
        "user_id": str(current_user.id),
        "new_version": current_user.user_version,
    })

    return LogoutResponse(message="Password changed successfully. Please log in again.")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user's information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        UserResponse with user info
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=current_user.role,
        created_at=current_user.created_at
    )
