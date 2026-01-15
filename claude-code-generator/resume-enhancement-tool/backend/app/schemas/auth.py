"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str | None = Field(None, description="User's full name (optional)")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""

    user_id: str | None = None


class AuthResponse(BaseModel):
    """Schema for authentication response (login/signup)."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
