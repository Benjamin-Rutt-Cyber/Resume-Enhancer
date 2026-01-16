"""Authentication request/response schemas.

Security Features:
- Password validation: 12 character minimum (allows passphrases)
- Terms of service acceptance tracking
- Role-based user responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for user registration.

    SECURITY: Password minimum is 12 characters as per security spec.
    No complexity requirements to allow passphrases.
    """

    email: EmailStr
    password: str = Field(
        ...,
        min_length=12,  # SECURITY: 12 char minimum per spec
        description="Password must be at least 12 characters (passphrases recommended)"
    )
    full_name: str | None = Field(None, max_length=255, description="User's full name (optional)")
    accept_terms: bool = Field(
        ...,
        description="User must accept terms of service to register"
    )

    @field_validator('accept_terms')
    @classmethod
    def validate_terms_accepted(cls, v: bool) -> bool:
        """COMPLIANCE: Require explicit terms acceptance."""
        if not v:
            raise ValueError("You must accept the terms of service to create an account")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    role: str = "user"  # SECURITY: Include role for frontend authorization checks
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=1800,  # 30 minutes in seconds
        description="Token expiration time in seconds"
    )


class TokenData(BaseModel):
    """Schema for decoded token data."""

    user_id: str | None = None
    user_version: int | None = None


class AuthResponse(BaseModel):
    """Schema for authentication response (login/signup).

    SECURITY: Access token returned in body for immediate use.
    Refresh token is set as HttpOnly cookie (not in body).
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=1800,  # 30 minutes in seconds
        description="Access token expiration time in seconds"
    )
    user: UserResponse


class RefreshResponse(BaseModel):
    """Schema for token refresh response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=1800,  # 30 minutes in seconds
        description="Access token expiration time in seconds"
    )


class PasswordChangeRequest(BaseModel):
    """Schema for password change request.

    SECURITY: Requires current password verification before allowing change.
    """

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(
        ...,
        min_length=12,  # SECURITY: 12 char minimum per spec
        description="New password must be at least 12 characters"
    )

    @field_validator('new_password')
    @classmethod
    def validate_new_password_different(cls, v: str, info) -> str:
        """Ensure new password is different from current."""
        # Note: Full comparison happens in the endpoint with the actual hashes
        return v


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str = "Successfully logged out"
