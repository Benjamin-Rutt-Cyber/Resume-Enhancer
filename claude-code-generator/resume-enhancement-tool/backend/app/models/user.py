"""User database model for authentication and authorization.

Security Features:
- user_version: Token revocation via version increment (invalidates all active JWTs)
- role: RBAC support (user, admin)
- totp_secret: Encrypted MFA secret storage (prepared for future TOTP implementation)
- accepted_terms_at: Compliance tracking for consent
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class User(Base):
    """User model for authentication, authorization, and data ownership.

    Security-critical columns:
    - user_version: Incremented on password change/logout to invalidate all active tokens.
                   This value is encoded in JWTs and checked on each request.
    - role: Used for RBAC. Default 'user', can be 'admin' for elevated privileges.
    - totp_secret: Encrypted TOTP secret for MFA (when implemented). Uses Fernet encryption.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # SECURITY: Token revocation support - increment to invalidate all active JWTs for this user
    # This is checked in JWT validation; if token's version doesn't match, reject the token
    user_version = Column(Integer, default=1, nullable=False)

    # SECURITY: RBAC role - 'user' (default) or 'admin'
    # Admin routes must check this via RequiresRole("admin") dependency
    role = Column(String(50), default="user", nullable=False)

    # SECURITY: Encrypted TOTP secret for MFA (Fernet-encrypted)
    # Null means MFA not enabled. When enabled, stores encrypted secret.
    totp_secret_encrypted = Column(Text, nullable=True)

    # COMPLIANCE: Track when user accepted terms of service
    # Null means terms not yet accepted (for legacy users, require re-acceptance)
    accepted_terms_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def increment_version(self):
        """Increment user_version to invalidate all active tokens.

        SECURITY: Call this on:
        - Password change
        - Explicit logout (invalidate all sessions)
        - Security-critical account changes
        """
        self.user_version = (self.user_version or 0) + 1

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role}, is_active={self.is_active})>"
