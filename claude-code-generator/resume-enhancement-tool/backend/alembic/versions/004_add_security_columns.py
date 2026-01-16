"""Add security columns for authentication and authorization

Revision ID: 004_security_columns
Revises: 003_content_columns
Create Date: 2026-01-16 12:00:00.000000

This migration adds security-critical columns to the users table:
- user_version: Token revocation support (increment to invalidate all active JWTs)
- role: RBAC support (default 'user', can be 'admin')
- totp_secret_encrypted: Encrypted MFA secret storage (Fernet encrypted)
- accepted_terms_at: Compliance tracking for terms of service acceptance

SECURITY NOTES:
- user_version defaults to 1, existing users will have all tokens valid
- role defaults to 'user', no existing users become admin
- totp_secret_encrypted is nullable (MFA not required)
- accepted_terms_at is nullable (legacy users may need to re-accept)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_security_columns'
down_revision = '003_content_columns'
branch_labels = None
depends_on = None


def upgrade():
    """Add security columns to users table."""

    # SECURITY: user_version for token revocation
    # When this is incremented, all existing JWTs for the user become invalid
    # Default to 1 so existing tokens remain valid after migration
    op.add_column('users', sa.Column(
        'user_version',
        sa.Integer(),
        nullable=False,
        server_default='1'
    ))

    # SECURITY: role for RBAC
    # Default to 'user', admin must be explicitly granted
    op.add_column('users', sa.Column(
        'role',
        sa.String(50),
        nullable=False,
        server_default='user'
    ))

    # SECURITY: totp_secret_encrypted for MFA (prepared for future implementation)
    # Stores Fernet-encrypted TOTP secret
    # Nullable because MFA is optional
    op.add_column('users', sa.Column(
        'totp_secret_encrypted',
        sa.Text(),
        nullable=True
    ))

    # COMPLIANCE: accepted_terms_at for consent tracking
    # Records when user accepted terms of service
    # Nullable for existing users (they may need to re-accept)
    op.add_column('users', sa.Column(
        'accepted_terms_at',
        sa.DateTime(),
        nullable=True
    ))

    # Create index on role for efficient admin queries
    op.create_index('ix_users_role', 'users', ['role'])


def downgrade():
    """Remove security columns from users table."""

    # Drop index first
    op.drop_index('ix_users_role', table_name='users')

    # Remove columns in reverse order
    op.drop_column('users', 'accepted_terms_at')
    op.drop_column('users', 'totp_secret_encrypted')
    op.drop_column('users', 'role')
    op.drop_column('users', 'user_version')
