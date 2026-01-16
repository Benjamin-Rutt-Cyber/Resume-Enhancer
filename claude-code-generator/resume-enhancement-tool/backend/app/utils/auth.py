"""Authentication utilities for JWT token and password management.

Security Implementation:
- Access tokens: Short-lived (30 minutes) for API authentication
- Refresh tokens: Long-lived (7 days) for obtaining new access tokens
- Token revocation: user_version encoded in JWT, checked against DB
- Password hashing: bcrypt with automatic salt generation

SECURITY NOTE: Refresh tokens should be stored in HttpOnly, Secure, SameSite=Strict cookies.
Access tokens can be sent in Authorization header for API calls.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

from ..core.config import settings

logger = logging.getLogger(__name__)

# JWT settings - SECURITY: Short-lived access tokens reduce window of compromise
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # SECURITY: 30 minutes as per spec (was 7 days)
REFRESH_TOKEN_EXPIRE_DAYS = 7    # SECURITY: 7 days for refresh token

# Token type identifiers for validation
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Password policy - SECURITY: 12 character minimum, no complexity requirements (allows passphrases)
MIN_PASSWORD_LENGTH = 12


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password meets security requirements.

    SECURITY: Enforces 12 character minimum as per spec.
    Does NOT enforce complexity requirements to allow passphrases.

    Args:
        password: Plain text password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"

    # SECURITY: Check for common weak passwords (basic check)
    weak_passwords = [
        "password1234",
        "123456789012",
        "qwertyuiopas",
    ]
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password."

    return True, ""


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    SECURITY: Uses bcrypt with automatic salt generation.
    Work factor is default (12 rounds), providing ~250ms hash time.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    user_version: int = 1
) -> str:
    """Create a short-lived JWT access token.

    SECURITY: Access tokens are short-lived (30 min) and include user_version
    for revocation support. The user_version is checked against the database
    on each request - if they don't match, the token is rejected.

    Args:
        data: Dictionary containing the token payload (must include 'sub' key with user_id)
        expires_delta: Optional custom expiration time
        user_version: User's current version for revocation support

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TOKEN_TYPE_ACCESS,
        "ver": user_version,  # SECURITY: For token revocation
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    user_version: int = 1,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a long-lived JWT refresh token.

    SECURITY: Refresh tokens are long-lived (7 days) and should ONLY be stored
    in HttpOnly, Secure, SameSite=Strict cookies. Never expose to JavaScript.

    Args:
        user_id: User's unique identifier
        user_version: User's current version for revocation support
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TOKEN_TYPE_REFRESH,
        "ver": user_version,  # SECURITY: For token revocation
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    SECURITY: This validates the token signature and expiration.
    The caller MUST also verify the user_version against the database.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload dictionary

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # SECURITY: Verify this is an access token, not a refresh token
        token_type = payload.get("type")
        if token_type != TOKEN_TYPE_ACCESS:
            logger.warning(f"Token type mismatch: expected {TOKEN_TYPE_ACCESS}, got {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> dict:
    """Decode and verify a JWT refresh token.

    SECURITY: This validates the token signature and expiration.
    The caller MUST also verify the user_version against the database.

    Args:
        token: JWT refresh token string

    Returns:
        Decoded token payload dictionary

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # SECURITY: Verify this is a refresh token, not an access token
        token_type = payload.get("type")
        if token_type != TOKEN_TYPE_REFRESH:
            logger.warning(f"Token type mismatch: expected {TOKEN_TYPE_REFRESH}, got {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    except JWTError as e:
        logger.debug(f"Refresh token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


def verify_token_version(token_version: int, user_version: int) -> bool:
    """Verify that the token version matches the user's current version.

    SECURITY: This is the core of our token revocation mechanism.
    When a user changes their password or explicitly logs out all sessions,
    their user_version is incremented, invalidating all existing tokens.

    Args:
        token_version: Version encoded in the JWT token
        user_version: Current version stored in the database

    Returns:
        True if versions match, False if token should be rejected
    """
    return token_version == user_version
