"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-01-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create resumes table
    op.create_table('resumes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('original_format', sa.String(length=10), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('extracted_text_path', sa.Text(), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('file_size_bytes', sa.Integer(), nullable=False),
    sa.Column('word_count', sa.Integer(), nullable=True),
    sa.Column('selected_style', sa.String(length=50), nullable=True),
    sa.Column('style_previews_generated', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Create jobs table
    op.create_table('jobs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('company', sa.String(length=255), nullable=True),
    sa.Column('description_text', sa.Text(), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Create enhancements table
    op.create_table('enhancements',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('enhancement_type', sa.String(length=50), nullable=False),
    sa.Column('instructions_path', sa.Text(), nullable=False),
    sa.Column('enhanced_resume_path', sa.Text(), nullable=True),
    sa.Column('metadata_path', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('ats_score', sa.Integer(), nullable=True),
    sa.Column('keyword_matches', sa.Integer(), nullable=True),
    sa.Column('suggestions', sa.Text(), nullable=True),
    sa.Column('cover_letter_path', sa.Text(), nullable=True),
    sa.Column('cover_letter_status', sa.String(length=20), nullable=True),
    sa.Column('cover_letter_error', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('enhancements')
    op.drop_table('jobs')
    op.drop_table('resumes')
