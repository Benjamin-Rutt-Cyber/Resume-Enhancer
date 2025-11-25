# Deploy to Production

Deploy DataAPI to production environment.

## Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] Code reviewed and merged to main branch
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Backup created
- [ ] Deployment plan reviewed

## Deployment Steps

### 1. Pre-Deployment Verification

```bash
# Run all tests
/run-tests

# Build production artifacts
/build-release

# Verify Docker images build
docker-compose -f docker-compose.prod.yml build

# Check for security vulnerabilities
pip-audit
```

### 2. Backup Current Production

```bash
# Backup database
pg_dump dataapi_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup environment configuration
cp .env.production .env.production.backup
```

### 3. Deploy with Docker

```bash
# Pull latest changes
git pull origin main

# Build images
docker-compose -f docker-compose.prod.yml build

# Stop current containers
docker-compose -f docker-compose.prod.yml down

# Start new containers
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
# Verify deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=50
```



### 5. Run Database Migrations

```bash
# Production migrations should be carefully reviewed
alembic upgrade head
```

### 6. Verify Deployment

```bash
# Health check
curl https://dataapi.com/health

# API check
curl https://dataapi.com/api/v1/

# Check metrics/monitoring
# Access monitoring dashboard (Grafana, etc.)
```

### 7. Post-Deployment Tasks

```bash
# Monitor application logs
docker-compose -f docker-compose.prod.yml logs -f

# Monitor error rates
# Check application metrics
# Verify all features working

# Notify team
echo "Deployment completed successfully at $(date)"
```

## Rollback Procedure

If deployment fails:

```bash
# Restore previous Docker containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Rollback database (if needed)
alembic downgrade -1

# Restore from backup if necessary
psql dataapi_prod < backup_TIMESTAMP.sql
```

## Environment Configuration

Ensure production environment variables are set:

```bash
# Critical variables
DATABASE_URL=postgresql://user:pass@prod-db/dataapi
SECRET_KEY=<strong-random-secret>
DEBUG=false
ENVIRONMENT=production


# External services


# Monitoring
SENTRY_DSN=<sentry-dsn>
```

## Monitoring After Deployment

Monitor these metrics:

1. **Application Health**
   - Response times
   - Error rates
   - Throughput

2. **System Resources**
   - CPU usage
   - Memory usage
   - Disk space

3. **Database Performance**
   - Query times
   - Connection pool
   - Lock waits

4. **User Impact**
   - Active users
   - Failed requests
   - Latency

## Automated Deployment (CI/CD)

For automated deployments with GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

      - name: Build and deploy
        run: |
          # Deployment commands here
```

## Security Checks

Before deploying:

- [ ] SSL/TLS certificates valid
- [ ] Secrets not exposed in code
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Database connections encrypted
- [ ] Firewall rules updated

## Troubleshooting

### Deployment Fails

1. Check logs for errors
2. Verify environment variables
3. Check database connectivity
4. Verify disk space
5. Check for port conflicts

### Zero Downtime Deployment

For zero downtime:

1. Use rolling updates (Kubernetes)
2. Blue-green deployment
3. Health check endpoints configured
4. Graceful shutdown implemented

## Next Steps

- Monitor application for 30 minutes
- Check error tracking (Sentry, etc.)
- Review performance metrics
- Update deployment documentation
- Notify stakeholders

Deployment of DataAPI completed!
