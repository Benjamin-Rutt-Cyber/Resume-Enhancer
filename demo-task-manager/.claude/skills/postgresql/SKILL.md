---
name: postgresql
description: Expert knowledge in PostgreSQL database including schema design, query optimization, indexing, migrations, and advanced features like JSONB and full-text search.
allowed-tools: [Read, Write, Edit, Bash]
---

# PostgreSQL Skill

Comprehensive knowledge for working with PostgreSQL databases.

## Quick Start

### Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Docker
docker run --name postgres -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres:15

# Verify installation
psql --version
```

### Initial Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE myapp;

# Create user
CREATE USER myuser WITH PASSWORD 'mypassword';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;

# Connect to database
\c myapp

# List databases
\l

# List tables
\dt

# Describe table
\d tablename

# Exit
\q
```

### Connection String

```bash
# Format
postgresql://username:password@host:port/database

# Examples
postgresql://myuser:mypassword@localhost:5432/myapp
postgresql://user:pass@db.example.com:5432/production
```

---

## Core Concepts

### 1. Data Types

```sql
-- Numeric types
CREATE TABLE products (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing integer
    price DECIMAL(10, 2),                -- Fixed precision
    quantity INTEGER,
    rating REAL,                         -- Floating point
    bignum BIGINT
);

-- String types
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,                            -- Unlimited length
    role CHAR(1) DEFAULT 'U'             -- Fixed length
);

-- Date/Time types
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ,              -- With timezone
    event_date DATE,
    event_time TIME,
    duration INTERVAL
);

-- Boolean
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- JSON types
CREATE TABLE metadata (
    id SERIAL PRIMARY KEY,
    data JSON,                           -- JSON (stored as text)
    details JSONB                        -- JSONB (binary, indexable)
);

-- Array types
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    labels TEXT[],                       -- Array of text
    numbers INTEGER[]
);

-- UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER,
    token TEXT
);
```

### 2. Schema Design

```sql
-- One-to-Many relationship
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    published_date DATE,
    isbn VARCHAR(13) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-Many relationship
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE
);

CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade CHAR(2),
    PRIMARY KEY (student_id, course_id)
);

-- Self-referencing (tree structure)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Constraints
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total DECIMAL(10, 2) CHECK (total >= 0),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_total CHECK (total >= 0)
);
```

### 3. Indexing

```sql
-- B-tree index (default, good for equality and range queries)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index (filtered)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = TRUE;

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- GIN index (for JSONB, arrays, full-text search)
CREATE INDEX idx_metadata_data ON metadata USING GIN (details);
CREATE INDEX idx_tags_labels ON tags USING GIN (labels);

-- GiST index (for geometric data, full-text search)
CREATE INDEX idx_locations ON places USING GIST (location);

-- Hash index (equality only, rarely used)
CREATE INDEX idx_sessions_token ON sessions USING HASH (token);

-- List indexes
\di

-- Drop index
DROP INDEX idx_users_email;

-- Reindex
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
```

### 4. Query Optimization

```sql
-- EXPLAIN shows query plan
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- EXPLAIN ANALYZE shows actual execution time
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Optimize with proper indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Use LIMIT for pagination
SELECT * FROM users ORDER BY created_at DESC LIMIT 20 OFFSET 40;

-- Avoid SELECT * - specify columns
SELECT id, name, email FROM users WHERE is_active = TRUE;

-- Use EXISTS instead of IN for subqueries
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Analyze table statistics
ANALYZE users;
VACUUM ANALYZE users;  -- Also reclaim space
```

---

## Migrations

### Alembic (Python)

```bash
# Install
pip install alembic psycopg2-binary

# Initialize
alembic init alembic

# Configure alembic.ini
sqlalchemy.url = postgresql://user:pass@localhost/mydb

# Create migration
alembic revision -m "create users table"

# Edit migration file
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_table('users')

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Prisma (Node.js/TypeScript)

```prisma
// schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())

  @@index([email])
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  authorId  Int
  author    User     @relation(fields: [authorId], references: [id])
  createdAt DateTime @default(now())

  @@index([authorId])
}
```

```bash
# Generate migration
npx prisma migrate dev --name init

# Apply migrations
npx prisma migrate deploy

# Reset database
npx prisma migrate reset
```

### SQL Migrations (Raw)

```sql
-- migrations/001_create_users.up.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- migrations/001_create_users.down.sql
DROP INDEX IF EXISTS idx_users_email;
DROP TABLE IF EXISTS users;
```

---

## Advanced Features

### JSONB

```sql
-- Create table with JSONB
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    attributes JSONB
);

-- Insert JSONB data
INSERT INTO products (name, attributes) VALUES
('Laptop', '{"brand": "Dell", "ram": "16GB", "storage": "512GB SSD"}'),
('Phone', '{"brand": "Apple", "model": "iPhone 14", "color": "black"}');

-- Query JSONB
SELECT * FROM products WHERE attributes->>'brand' = 'Dell';
SELECT * FROM products WHERE attributes @> '{"brand": "Apple"}';

-- Extract JSONB field
SELECT name, attributes->>'brand' as brand FROM products;

-- Update JSONB
UPDATE products
SET attributes = attributes || '{"warranty": "2 years"}'
WHERE id = 1;

-- Index JSONB
CREATE INDEX idx_products_attributes ON products USING GIN (attributes);

-- Query with JSONB path
SELECT * FROM products WHERE attributes->'specs'->>'processor' = 'Intel i7';
```

### Full-Text Search

```sql
-- Add tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Update search vector
UPDATE articles
SET search_vector = to_tsvector('english', title || ' ' || content);

-- Create GIN index
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- Search query
SELECT title, ts_rank(search_vector, query) AS rank
FROM articles, plainto_tsquery('english', 'postgresql tutorial') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- Trigger to auto-update search vector
CREATE FUNCTION articles_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', NEW.title || ' ' || NEW.content);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW EXECUTE FUNCTION articles_search_trigger();
```

### Partitioning

```sql
-- Create partitioned table
CREATE TABLE measurements (
    id SERIAL,
    measure_date DATE NOT NULL,
    value NUMERIC
) PARTITION BY RANGE (measure_date);

-- Create partitions
CREATE TABLE measurements_2023_q1 PARTITION OF measurements
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE measurements_2023_q2 PARTITION OF measurements
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

-- Insert data (automatically routes to correct partition)
INSERT INTO measurements (measure_date, value) VALUES
('2023-02-15', 42.5),
('2023-05-20', 38.2);
```

### Window Functions

```sql
-- Row number
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as rank
FROM employees;

-- Rank with partitioning
SELECT
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;

-- Running total
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;

-- Moving average
SELECT
    date,
    price,
    AVG(price) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7day
FROM stock_prices;
```

---

## Transactions

```sql
-- Basic transaction
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Rollback on error
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    -- Error occurs here
    UPDATE accounts SET balance = balance + 100 WHERE id = 999;  -- Invalid ID
ROLLBACK;  -- Undo all changes

-- Savepoints
BEGIN;
    UPDATE users SET balance = balance - 10 WHERE id = 1;
    SAVEPOINT my_savepoint;
    UPDATE users SET balance = balance + 10 WHERE id = 2;
    ROLLBACK TO SAVEPOINT my_savepoint;  -- Only rollback to savepoint
    UPDATE users SET balance = balance + 10 WHERE id = 3;  -- This still executes
COMMIT;

-- Isolation levels
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;    -- Default
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

---

## Common Patterns

### Pagination

```sql
-- Offset-based (simple but slower for large offsets)
SELECT * FROM products
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;  -- Page 3 (20 items per page)

-- Cursor-based (better performance)
SELECT * FROM products
WHERE created_at < '2023-01-15 10:30:00'
ORDER BY created_at DESC
LIMIT 20;
```

### Upsert (INSERT ... ON CONFLICT)

```sql
-- Update if exists, insert if not
INSERT INTO users (email, name)
VALUES ('user@example.com', 'John Doe')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP;

-- Do nothing if conflict
INSERT INTO users (email, name)
VALUES ('user@example.com', 'John Doe')
ON CONFLICT (email) DO NOTHING;
```

### Soft Delete

```sql
-- Add deleted_at column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- Soft delete
UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = 1;

-- Query active records
SELECT * FROM users WHERE deleted_at IS NULL;

-- Create view for active users
CREATE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;
```

### Audit Trail

```sql
-- Create audit table
CREATE TABLE user_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_by INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function
CREATE OR REPLACE FUNCTION audit_users() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO user_audit (user_id, action, old_data, new_data)
        VALUES (OLD.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO user_audit (user_id, action, old_data)
        VALUES (OLD.id, 'DELETE', row_to_json(OLD));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER users_audit_trigger
AFTER UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_users();
```

---

## Best Practices

1. **Use SERIAL or IDENTITY for auto-increment** - Prefer IDENTITY in PostgreSQL 10+
2. **Add indexes on foreign keys** - Improves JOIN performance
3. **Use TIMESTAMPTZ** - Stores timezone information
4. **Normalize your schema** - Avoid data duplication
5. **Use constraints** - NOT NULL, UNIQUE, CHECK, FOREIGN KEY
6. **Analyze queries** - Use EXPLAIN ANALYZE before optimizing
7. **Regular VACUUM** - Reclaim storage and update statistics
8. **Backup regularly** - Use pg_dump or continuous archiving
9. **Use connection pooling** - PgBouncer or application-level pooling
10. **Monitor slow queries** - Enable pg_stat_statements extension

---

## Performance Tips

```sql
-- Enable extensions for monitoring
CREATE EXTENSION pg_stat_statements;

-- Find slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT
    table_name,
    pg_size_pretty(pg_total_relation_size(table_name::regclass)) as size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(table_name::regclass) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Unused indexes (candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE '%_pkey';
```

---

## Troubleshooting

**Connection refused:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check port
sudo netstat -tuln | grep 5432
```

**Permission denied:**
```sql
-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myuser;
```

**Slow queries:**
- Add indexes on WHERE clause columns
- Use EXPLAIN ANALYZE to find bottlenecks
- Consider partitioning for very large tables
- Run VACUUM ANALYZE regularly

**Connection limit reached:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- Modify max connections (requires restart)
ALTER SYSTEM SET max_connections = 200;
```

---

## Backup & Restore

```bash
# Backup single database
pg_dump -U username -d mydb > backup.sql
pg_dump -U username -d mydb -F c > backup.dump  # Custom format

# Backup all databases
pg_dumpall -U postgres > all_databases.sql

# Restore
psql -U username -d mydb < backup.sql
pg_restore -U username -d mydb backup.dump  # Custom format

# Backup with compression
pg_dump -U username -d mydb | gzip > backup.sql.gz

# Restore compressed backup
gunzip -c backup.sql.gz | psql -U username -d mydb
```

---

## Resources

- Official Documentation: https://www.postgresql.org/docs/
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- Use The Index Luke: https://use-the-index-luke.com/
- pgAdmin: https://www.pgadmin.org/
- Awesome PostgreSQL: https://github.com/dhamaniasad/awesome-postgres
