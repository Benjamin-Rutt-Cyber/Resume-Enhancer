"""Add content columns for database-based file storage

Revision ID: 003_content_columns
Revises: 002_authentication
Create Date: 2026-01-15 12:00:00.000000

This migration adds columns to store file contents directly in the database,
solving the issue with Render's ephemeral filesystem where files are lost
on deployment but database persists.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_content_columns'
down_revision = '002_authentication'
branch_labels = None
depends_on = None


def upgrade():
    # Add extracted_text column to resumes table
    # Stores the extracted text content from uploaded PDF/DOCX files
    op.add_column('resumes', sa.Column('extracted_text', sa.Text(), nullable=True))

    # Add content columns to enhancements table
    # instructions_text: The INSTRUCTIONS.md content for Claude
    op.add_column('enhancements', sa.Column('instructions_text', sa.Text(), nullable=True))
    # enhanced_content: The generated enhanced.md content
    op.add_column('enhancements', sa.Column('enhanced_content', sa.Text(), nullable=True))
    # cover_letter_content: The generated cover_letter.md content
    op.add_column('enhancements', sa.Column('cover_letter_content', sa.Text(), nullable=True))


def downgrade():
    # Remove content columns from enhancements table
    op.drop_column('enhancements', 'cover_letter_content')
    op.drop_column('enhancements', 'enhanced_content')
    op.drop_column('enhancements', 'instructions_text')

    # Remove extracted_text column from resumes table
    op.drop_column('resumes', 'extracted_text')
