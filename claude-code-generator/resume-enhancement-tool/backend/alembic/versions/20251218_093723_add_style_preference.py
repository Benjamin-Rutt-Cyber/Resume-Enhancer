"""add style preference

Revision ID: 20251218_093723
Revises:
Create Date: 2025-12-18 09:37:23.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251218_093723'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add style preference columns to resumes table."""
    # Add selected_style column
    op.add_column('resumes', sa.Column('selected_style', sa.String(50), nullable=True))

    # Add style_previews_generated column
    op.add_column('resumes', sa.Column('style_previews_generated', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Remove style preference columns from resumes table."""
    op.drop_column('resumes', 'style_previews_generated')
    op.drop_column('resumes', 'selected_style')
