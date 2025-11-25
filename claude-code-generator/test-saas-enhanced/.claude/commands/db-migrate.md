# Database Migrations

Manage database schema changes for Enhanced Test SaaS safely and consistently.


## Quick Migration Commands

### Using Alembic (FastAPI)

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file in alembic/versions/

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current migration version
alembic current
```


## Complete Migration Workflow

### 1. Create Migration

When you change your database models:

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add users table"

# Or create empty migration for manual SQL
alembic revision -m "custom data migration"
```

**Generated file:** `backend/alembic/versions/xxxx_add_users_table.py`

```python
"""add users table

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
```


### 2. Review Migration

**Always review generated migrations before applying!**

```bash
# Check what SQL will be executed
# View in the migration file: backend/alembic/versions/xxxx_*.py


# Test migration on development database first!
```

### 3. Apply Migration

```bash
# Backup database first (recommended for production)
pg_dump enhanced-test-saas > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migration
cd backend
alembic upgrade head

```

### 4. Verify Migration

```bash
# Check database schema
psql enhanced-test-saas -c "\dt"  # List tables
psql enhanced-test-saas -c "\d users"  # Describe table


# Verify migration was recorded
alembic current

```

## Common Migration Operations

### Add Column

```python
# In migration file
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```


### Rename Column

```python
def upgrade():
    op.alter_column('users', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('users', 'new_name', new_column_name='old_name')
```


### Add Index

```python
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_users_email')
```


### Data Migration

```python
# Create empty migration: alembic revision -m "migrate user data"

from alembic import op
from sqlalchemy import orm

def upgrade():
    # Get database session
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # Update data
    session.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
    session.commit()

def downgrade():
    # Reverse data changes if possible
    pass
```


## Migration Best Practices

### 1. Always Backup Before Migrating

```bash
# Backup PostgreSQL
pg_dump enhanced-test-saas > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore if needed
psql enhanced-test-saas < backup_TIMESTAMP.sql

```

### 2. Test Migrations Locally First

```bash
# 1. Apply migration on development database
alembic upgrade head


# 2. Test application works
/run-tests

# 3. Rollback to test downgrade
alembic downgrade -1


# 4. Re-apply to test upgrade again
alembic upgrade head
```

### 3. Make Migrations Reversible

Always implement the `downgrade`/`down` function:

```python
# ❌ BAD
def downgrade():
    pass  # Can't rollback!

# ✅ GOOD
def downgrade():
    op.drop_table('users')  # Properly reverses upgrade
```

### 4. Avoid Destructive Migrations in Production

```python
# ❌ DANGEROUS - loses data
def upgrade():
    op.drop_column('users', 'old_data')

# ✅ SAFER - deprecate gradually
def upgrade():
    # Step 1: Add new column (deploy this first)
    op.add_column('users', sa.Column('new_data', sa.String()))

    # Step 2: Migrate data (separate migration, deploy later)
    # op.execute("UPDATE users SET new_data = old_data")

    # Step 3: Drop old column (final migration, deploy last)
    # op.drop_column('users', 'old_data')
```

## Troubleshooting

### Migration Conflicts

```bash
# If multiple developers created migrations
alembic history
# Merge migrations or adjust revision IDs

```

### Migration Fails Midway

```bash
# Mark migration as failed
alembic stamp head-1

# Fix migration file
# Re-run
alembic upgrade head

```

### Database Out of Sync

```bash
# Compare database with models
alembic check

# Stamp database to match code
alembic stamp head

```

## Production Migration Checklist

- [ ] Backup database before migrating
- [ ] Test migration on staging environment
- [ ] Review migration SQL for performance impact
- [ ] Schedule during low-traffic window
- [ ] Have rollback plan ready
- [ ] Monitor application after migration
- [ ] Verify data integrity post-migration
- [ ] Update documentation

## Next Steps

- Run `/run-tests` to verify database changes
- Update API documentation if schema changed
- Deploy application with new migrations
- Monitor database performance

Database migrations completed for Enhanced Test SaaS! 📊
