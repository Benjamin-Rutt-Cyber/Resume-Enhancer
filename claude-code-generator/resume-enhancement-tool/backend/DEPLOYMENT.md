# Deployment Guide - Resume Enhancement Tool

## Overview

This guide covers deploying the Resume Enhancement Tool to production, including security hardening, environment configuration, and best practices.

## Pre-Deployment Checklist

### Security

- [ ] **SECRET_KEY**: Changed to strong, random 32+ character string
- [ ] **DEBUG**: Set to `False` in production `.env`
- [ ] **Database**: Using PostgreSQL (not SQLite)
- [ ] **CORS Origins**: Limited to production domain(s) only
- [ ] **.env file**: Secured with proper permissions (`chmod 600 .env`)
- [ ] **.env file**: Added to `.gitignore` (never committed to version control)
- [ ] **Secrets**: Not hardcoded in code
- [ ] **Input validation**: File size limits in place
- [ ] **Error handling**: Database rollback on errors

### Testing

- [ ] **All tests passing**: `pytest` shows 0 failures
- [ ] **Coverage**: >70% on critical paths
- [ ] **Integration tests**: End-to-end workflows tested
- [ ] **Security tests**: Verify all security fixes applied

### Code Quality

- [ ] **No print statements**: All replaced with logging
- [ ] **Logging configured**: Proper log levels and file output
- [ ] **Error messages**: No sensitive information exposed
- [ ] **Code review**: All changes reviewed

### Infrastructure

- [ ] **Health check**: Endpoint responding correctly
- [ ] **Database backups**: Automated backup strategy in place
- [ ] **Monitoring**: Error tracking configured (e.g., Sentry)
- [ ] **Logging**: Centralized logging configured

## Environment Configuration

### Required Environment Variables

Create a production `.env` file in `backend/`:

```bash
# ============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# ============================================================================

# Database - PostgreSQL (REQUIRED for production)
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
# Example: postgresql://resume_user:SecurePassword123@localhost:5432/resume_enhancement_tool

# Security - SECRET_KEY (REQUIRED)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-production-secret-key-at-least-32-characters-random

# Debug Mode (MUST be False in production)
DEBUG=False

# CORS Origins (limit to your production domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================================================
# OPTIONAL CONFIGURATIONS
# ============================================================================

# Application
APP_NAME=Resume Enhancement Tool
APP_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/resume-tool/app.log

# File Upload Limits (already set in code, can override)
# MAX_FILE_SIZE=10485760  # 10 MB in bytes

# ============================================================================
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output: kJ8mN_pQ2rS-tU3vW4xY5zA6bC7dE8fG9hI0jK1lM2nO

# Use this value in your .env file:
# SECRET_KEY=kJ8mN_pQ2rS-tU3vW4xY5zA6bC7dE8fG9hI0jK1lM2nO
```

### File Permissions

```bash
# Secure .env file
chmod 600 backend/.env

# Verify permissions
ls -la backend/.env
# Should show: -rw------- (only owner can read/write)
```

## Database Setup

### PostgreSQL Installation

#### Ubuntu/Debian

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS

```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

### Database Creation

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL console:
CREATE DATABASE resume_enhancement_tool;
CREATE USER resume_user WITH PASSWORD 'SecurePassword123';
GRANT ALL PRIVILEGES ON DATABASE resume_enhancement_tool TO resume_user;
\q
```

### Run Migrations

```bash
cd backend

# Using Alembic
alembic upgrade head

# Or run init script
python init_db.py
```

### Verify Database Connection

```bash
# Test connection
python -c "
from app.core.config import settings
from app.core.database import engine
try:
    with engine.connect() as conn:
        print('Database connection successful!')
        print(f'Connected to: {settings.DATABASE_URL}')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

## Deployment Options

### Option 1: Traditional Server (systemd)

#### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Create systemd Service

Create `/etc/systemd/system/resume-tool.service`:

```ini
[Unit]
Description=Resume Enhancement Tool API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/resume-tool/backend
Environment="PATH=/var/www/resume-tool/backend/venv/bin"
ExecStart=/var/www/resume-tool/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

# Security
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/resume-tool/backend/workspace

# Restart policy
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start resume-tool

# Enable on boot
sudo systemctl enable resume-tool

# Check status
sudo systemctl status resume-tool

# View logs
sudo journalctl -u resume-tool -f
```

### Option 2: Docker

#### 1. Build Docker Image

```bash
# Build backend image
docker build -t resume-tool-backend -f Dockerfile .

# Build with docker-compose
docker-compose build
```

#### 2. Run with Docker Compose

```bash
# Start all services (backend, database, frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
# Stop services
docker-compose down

### Option 3: Render (PaaS)

#### Configuration

**Backend Service:**
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `mkdir -p workspace && python worker.py > workspace/worker.log 2>&1 & uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `backend` (if using monorepo)

**Important Notes:**
1. The **Start Command** is critical! It runs the background worker (`worker.py`) *alongside* the web API (`uvicorn`). Without this, enhancements will stay "Pending" forever.
2. Ensure `ANTHROPIC_API_KEY` is set in the Environment Variables under the **Environment** tab.
3. If using Docker runtime on Render, standard `Dockerfile` instructions apply, but ensuring `start.sh` is used is recommended.

#### Environment Variables
Add these in the Render Dashboard:
- `ANTHROPIC_API_KEY`: starting with `sk-ant...`
- `SECRET_KEY`: (generated random string)
- `ALLOWED_ORIGINS`: `https://your-frontend-url.onrender.com`
- `DEBUG`: `False`
```

#### 3. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: resume_enhancement_tool
      POSTGRES_USER: resume_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://resume_user:${DB_PASSWORD}@db:5432/resume_enhancement_tool
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
    volumes:
      - ./backend/workspace:/app/workspace
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
```

## Nginx Configuration

### Reverse Proxy Setup

Create `/etc/nginx/sites-available/resume-tool`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;

        # Increase body size for file uploads
        client_max_body_size 10M;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend/api/health/ready;
        access_log off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/resume-tool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/TLS Setup

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured by default
# Test renewal:
sudo certbot renew --dry-run
```

## Monitoring and Logging

### Application Logging

Configure logging in `backend/app/core/logging_config.py`:

```python
import logging
from pathlib import Path

def setup_production_logging():
    log_file = Path("/var/log/resume-tool/app.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
```

### Error Tracking (Sentry)

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

In `backend/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if not settings.DEBUG:
    sentry_sdk.init(
        dsn="your-sentry-dsn-here",
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment="production"
    )
```

### Health Checks

Monitor application health:

```bash
# Check API health
curl https://yourdomain.com/api/health/ready

# Should return:
# {"status": "ready", "database": "connected", ...}
```

Set up monitoring (e.g., UptimeRobot, Pingdom):
- URL: `https://yourdomain.com/api/health/ready`
- Interval: 5 minutes
- Alert on non-200 response

## Backup Strategy

### Database Backups

#### Automated Daily Backups

Create `/usr/local/bin/backup-resume-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/resume-tool"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="resume_db_${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"

# Backup database
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h localhost \
    -U resume_user \
    -d resume_enhancement_tool \
    | gzip > "$BACKUP_DIR/$FILENAME"

# Keep only last 30 days
find "$BACKUP_DIR" -name "resume_db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

#### Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-resume-db.sh >> /var/log/resume-tool/backup.log 2>&1
```

### File Backups

```bash
# Backup workspace directory
tar -czf /var/backups/resume-tool/workspace_$(date +%Y%m%d).tar.gz \
    /var/www/resume-tool/backend/workspace
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_resumes_created_at ON resumes(created_at DESC);
CREATE INDEX idx_enhancements_status ON enhancements(status);
CREATE INDEX idx_enhancements_resume_id ON enhancements(resume_id);
```

### Caching

Consider adding Redis for caching:

```python
# Install Redis
pip install redis

# Configure caching for frequently accessed data
from redis import Redis

cache = Redis(host='localhost', port=6379, db=0)
```

### Application Tuning

In production, use multiple workers:

```bash
# Uvicorn with workers
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --access-log \
    --proxy-headers
```

## Troubleshooting

### Common Issues

**1. Database connection fails**
```bash
# Check DATABASE_URL in .env
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U resume_user -d resume_enhancement_tool
```

**2. File upload fails**
```bash
# Check workspace directory permissions
ls -la backend/workspace

# Should be writable by application user
sudo chown -R www-data:www-data backend/workspace
```

**3. SECRET_KEY validation error**
```bash
# Error: SECRET_KEY must be at least 32 characters
# Generate new key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**4. CORS errors in browser**
```bash
# Check ALLOWED_ORIGINS in .env
# Must include your frontend domain
ALLOWED_ORIGINS=https://yourdomain.com
```

## Security Hardening

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Application Security

- Keep dependencies updated: `pip list --outdated`
- Regular security audits: `pip-audit`
- Monitor CVE databases
- Use security headers (configured in Nginx)
- Rate limiting (configure in Nginx or application)

## Post-Deployment Verification

### Deployment Checklist

After deployment, verify:

```bash
# 1. Health check passes
curl https://yourdomain.com/api/health/ready

# 2. API responds
curl https://yourdomain.com/api/

# 3. Frontend loads
curl https://yourdomain.com/

# 4. Resume upload works (manual test in browser)
# 5. Database backups running (check cron logs)
# 6. Monitoring alerts configured
# 7. SSL certificate valid (check in browser)
```

### Monitoring Dashboards

Set up dashboards to monitor:
- API response times
- Error rates
- Database performance
- Disk usage (workspace directory)
- Memory/CPU usage

## Rollback Plan

If deployment fails:

```bash
# 1. Stop new version
sudo systemctl stop resume-tool

# 2. Restore database backup
gunzip -c /var/backups/resume-tool/resume_db_YYYYMMDD.sql.gz | \
    psql -h localhost -U resume_user -d resume_enhancement_tool

# 3. Revert code
git checkout previous-stable-tag

# 4. Restart service
sudo systemctl start resume-tool
```

## Support and Maintenance

### Regular Maintenance Tasks

- **Weekly**: Review logs for errors
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Yearly**: Review and update SSL certificates (automated with certbot)

### Resources

- Application logs: `/var/log/resume-tool/app.log`
- Service logs: `sudo journalctl -u resume-tool`
- Nginx logs: `/var/log/nginx/`

---

**Last Updated**: December 15, 2025
**Deployment Status**: Production-ready
**Recommended Infrastructure**: VPS with 2GB+ RAM, PostgreSQL, Nginx
