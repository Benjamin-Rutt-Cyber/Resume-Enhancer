"""add_cover_letter_fields_to_enhancements

Revision ID: b1bb9c5ce84e
Revises: 67e0c4908822
Create Date: 2025-12-29 15:15:19.103354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1bb9c5ce84e'
down_revision = '67e0c4908822'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add cover letter fields to enhancements table
    op.add_column('enhancements', sa.Column('cover_letter_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('cover_letter_pdf_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('cover_letter_docx_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('cover_letter_status', sa.String(50), nullable=False, server_default='pending'))
    op.add_column('enhancements', sa.Column('cover_letter_error', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove cover letter fields from enhancements table
    op.drop_column('enhancements', 'cover_letter_error')
    op.drop_column('enhancements', 'cover_letter_status')
    op.drop_column('enhancements', 'cover_letter_docx_path')
    op.drop_column('enhancements', 'cover_letter_pdf_path')
    op.drop_column('enhancements', 'cover_letter_path')
