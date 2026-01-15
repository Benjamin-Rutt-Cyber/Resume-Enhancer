"""Add authentication and user ownership

Revision ID: 002_authentication
Revises: 001_initial
Create Date: 2026-01-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_authentication'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create index on email for fast lookups
    op.create_index('ix_users_email', 'users', ['email'])

    # Add missing 'source' column to jobs table
    op.add_column('jobs', sa.Column('source', sa.String(length=50), nullable=False, server_default='upload'))

    # Update enhancements table columns to match current model
    # Drop columns that no longer exist
    op.drop_column('enhancements', 'instructions_path')
    op.drop_column('enhancements', 'enhanced_resume_path')
    op.drop_column('enhancements', 'metadata_path')
    op.drop_column('enhancements', 'ats_score')
    op.drop_column('enhancements', 'keyword_matches')
    op.drop_column('enhancements', 'suggestions')

    # Add new columns to match current Enhancement model
    op.add_column('enhancements', sa.Column('industry', sa.String(length=100), nullable=True))
    op.add_column('enhancements', sa.Column('output_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('pdf_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('docx_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('cover_letter_pdf_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('cover_letter_docx_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('run_analysis', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('enhancements', sa.Column('ats_analysis', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('job_match_score', sa.Integer(), nullable=True))
    op.add_column('enhancements', sa.Column('achievement_suggestions', sa.Text(), nullable=True))

    # Update cover_letter_status default
    op.alter_column('enhancements', 'cover_letter_status',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=50),
                    nullable=False,
                    server_default='pending')

    # Update status column length
    op.alter_column('enhancements', 'status',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=50),
                    existing_nullable=False)

    # Add user_id columns to resumes, jobs, and enhancements tables
    # Note: These are added as nullable first, then we'll make them NOT NULL after populating
    op.add_column('resumes', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('jobs', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('enhancements', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Create indexes on user_id columns for performance
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('ix_enhancements_user_id', 'enhancements', ['user_id'])

    # Note: In a production migration with existing data, you would:
    # 1. Create a default/migration user
    # 2. Update all existing records to reference that user
    # 3. Then alter the columns to be NOT NULL
    # For now, we'll leave them nullable and handle this in the application layer

    # Add foreign key constraints
    op.create_foreign_key('fk_resumes_user_id', 'resumes', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_jobs_user_id', 'jobs', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_enhancements_user_id', 'enhancements', 'users', ['user_id'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_enhancements_user_id', 'enhancements', type_='foreignkey')
    op.drop_constraint('fk_jobs_user_id', 'jobs', type_='foreignkey')
    op.drop_constraint('fk_resumes_user_id', 'resumes', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_enhancements_user_id', 'enhancements')
    op.drop_index('ix_jobs_user_id', 'jobs')
    op.drop_index('ix_resumes_user_id', 'resumes')

    # Drop user_id columns
    op.drop_column('enhancements', 'user_id')
    op.drop_column('jobs', 'user_id')
    op.drop_column('resumes', 'user_id')

    # Revert enhancements table changes
    op.drop_column('enhancements', 'achievement_suggestions')
    op.drop_column('enhancements', 'job_match_score')
    op.drop_column('enhancements', 'ats_analysis')
    op.drop_column('enhancements', 'run_analysis')
    op.drop_column('enhancements', 'cover_letter_docx_path')
    op.drop_column('enhancements', 'cover_letter_pdf_path')
    op.drop_column('enhancements', 'docx_path')
    op.drop_column('enhancements', 'pdf_path')
    op.drop_column('enhancements', 'output_path')
    op.drop_column('enhancements', 'industry')

    # Restore old columns
    op.add_column('enhancements', sa.Column('suggestions', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('keyword_matches', sa.Integer(), nullable=True))
    op.add_column('enhancements', sa.Column('ats_score', sa.Integer(), nullable=True))
    op.add_column('enhancements', sa.Column('metadata_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('enhanced_resume_path', sa.Text(), nullable=True))
    op.add_column('enhancements', sa.Column('instructions_path', sa.Text(), nullable=False))

    # Revert column type changes
    op.alter_column('enhancements', 'status',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=20),
                    existing_nullable=False)

    op.alter_column('enhancements', 'cover_letter_status',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=20),
                    nullable=True,
                    server_default=None)

    # Drop source column from jobs
    op.drop_column('jobs', 'source')

    # Drop users table
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
