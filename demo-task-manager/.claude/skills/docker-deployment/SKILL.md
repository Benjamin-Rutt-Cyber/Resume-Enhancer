---
name: docker-deployment
description: Expert knowledge in Docker containerization including Dockerfile creation, multi-stage builds, Docker Compose, orchestration, security best practices, and production deployment.
allowed-tools: [Read, Write, Edit, Bash]
---

# Docker Deployment Skill

Comprehensive guide for containerizing applications with Docker and deploying to production.

## Quick Start

### Installation

```bash
# Install Docker (Linux)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify installation
docker --version
docker-compose --version

# Run without sudo (Linux)
sudo usermod -aG docker $USER
```

### Basic Commands

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d -p 3000:3000 --name myapp myapp:latest

# List containers
docker ps
docker ps -a  # Include stopped containers

# View logs
docker logs myapp
docker logs -f myapp  # Follow

# Stop/Start/Restart
docker stop myapp
docker start myapp
docker restart myapp

# Remove container
docker rm myapp
docker rm -f myapp  # Force remove running container

# List images
docker images

# Remove image
docker rmi myapp:latest

# Execute command in container
docker exec -it myapp bash
docker exec myapp ls /app

# Inspect container
docker inspect myapp
```

---

## Dockerfile

### Node.js Application

```dockerfile
# Basic Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
```

### Multi-Stage Build (Node.js)

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy built app from builder stage
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Python FastAPI Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Django Application

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1001 django && \
    chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

### React Application

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /static {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## .dockerignore

```
# .dockerignore
node_modules
npm-debug.log
.env
.env.local
.git
.gitignore
README.md
.vscode
.idea
*.md
dist
build
coverage
.pytest_cache
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
.DS_Store
```

---

## Docker Compose

### Development Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: npm run dev

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Full Stack Application

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
      - /app/node_modules

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### Production Setup

```yaml
version: '3.8'

services:
  app:
    image: myregistry.com/myapp:${VERSION:-latest}
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## Docker Compose Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# View logs
docker-compose logs
docker-compose logs -f app
docker-compose logs --tail=100 app

# Execute command
docker-compose exec app bash
docker-compose exec app npm test

# Run one-off command
docker-compose run app npm install
docker-compose run --rm app python manage.py migrate

# Scale services
docker-compose up -d --scale app=3

# List services
docker-compose ps

# Restart service
docker-compose restart app
```

---

## Environment Variables

### .env File

```bash
# .env
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@db:5432/myapp
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=https://example.com,https://www.example.com
```

### Docker Compose with .env

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    environment:
      - NODE_ENV=${NODE_ENV}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env
      - .env.local
```

### Secrets Management

```yaml
# Docker Swarm secrets
version: '3.8'

services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
```

```bash
# Create secrets
echo "my_db_password" | docker secret create db_password -
echo "my_jwt_secret" | docker secret create jwt_secret -

# List secrets
docker secret ls

# Remove secret
docker secret rm db_password
```

---

## Volumes and Data Persistence

### Named Volumes

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    volumes:
      - app_data:/app/data
      - uploads:/app/uploads

volumes:
  app_data:
  uploads:
```

### Bind Mounts

```yaml
services:
  app:
    image: myapp:latest
    volumes:
      - ./app:/app              # Current directory
      - ./config:/app/config:ro # Read-only
      - /var/log:/app/logs      # Absolute path
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect postgres_data

# Remove volume
docker volume rm postgres_data

# Remove unused volumes
docker volume prune

# Create volume
docker volume create my_volume

# Backup volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

---

## Networking

### Bridge Network (Default)

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    networks:
      - app_network

  db:
    image: postgres:15
    networks:
      - app_network

networks:
  app_network:
    driver: bridge
```

### Custom Networks

```yaml
version: '3.8'

services:
  frontend:
    image: frontend:latest
    networks:
      - frontend_network
      - backend_network

  backend:
    image: backend:latest
    networks:
      - backend_network
      - database_network

  db:
    image: postgres:15
    networks:
      - database_network

networks:
  frontend_network:
  backend_network:
  database_network:
    internal: true  # No external access
```

### Network Commands

```bash
# List networks
docker network ls

# Inspect network
docker network inspect app_network

# Create network
docker network create my_network

# Connect container to network
docker network connect my_network myapp

# Disconnect from network
docker network disconnect my_network myapp

# Remove network
docker network rm my_network
```

---

## Health Checks

### Dockerfile Health Check

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node healthcheck.js

CMD ["node", "index.js"]
```

```javascript
// healthcheck.js
const http = require('http');

const options = {
  host: 'localhost',
  port: 3000,
  path: '/health',
  timeout: 2000
};

const request = http.request(options, (res) => {
  console.log(`STATUS: ${res.statusCode}`);
  process.exit(res.statusCode === 200 ? 0 : 1);
});

request.on('error', (err) => {
  console.log('ERROR:', err);
  process.exit(1);
});

request.end();
```

### Docker Compose Health Check

```yaml
services:
  app:
    image: myapp:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Multi-Stage Builds

### Advanced Example

```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Test
FROM builder AS test
RUN npm run test

# Stage 4: Production
FROM node:18-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
COPY package*.json ./

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Build Specific Stage

```bash
# Build specific stage
docker build --target test -t myapp:test .
docker build --target production -t myapp:latest .

# Run tests
docker run --rm myapp:test
```

---

## Security Best Practices

### 1. Use Official Base Images

```dockerfile
# ✅ GOOD
FROM node:18-alpine

# ❌ BAD
FROM random-user/node-custom
```

### 2. Non-Root User

```dockerfile
# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001

# Switch to non-root user
USER appuser
```

### 3. Minimize Layers

```dockerfile
# ✅ GOOD - Single layer
RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*

# ❌ BAD - Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
```

### 4. Scan for Vulnerabilities

```bash
# Docker scan (requires Docker Hub login)
docker scan myapp:latest

# Trivy scanner
trivy image myapp:latest
```

### 5. Use Specific Tags

```dockerfile
# ✅ GOOD
FROM node:18.16.0-alpine

# ❌ BAD
FROM node:latest
```

### 6. Secrets Management

```dockerfile
# ❌ BAD - Don't hardcode secrets
ENV API_KEY=secret123

# ✅ GOOD - Use build args (for build-time secrets)
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && \
    npm install && \
    rm .npmrc

# ✅ GOOD - Use runtime environment variables
ENV API_KEY=${API_KEY}
```

### 7. Read-Only Root Filesystem

```yaml
services:
  app:
    image: myapp:latest
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### GitLab CI

```yaml
# .gitlab-ci.yml
variables:
  DOCKER_DRIVER: overlay2
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG

test:
  stage: test
  image: $IMAGE_TAG
  script:
    - npm test

deploy:
  stage: deploy
  only:
    - main
  script:
    - docker pull $IMAGE_TAG
    - docker-compose up -d
```

---

## Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml myapp

# List stacks
docker stack ls

# List services
docker stack services myapp

# Remove stack
docker stack rm myapp

# Scale service
docker service scale myapp_app=3

# Update service
docker service update --image myapp:v2 myapp_app
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry.com/myapp:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

---

## Troubleshooting

### Container Logs

```bash
# View logs
docker logs myapp

# Follow logs
docker logs -f myapp

# Last 100 lines
docker logs --tail 100 myapp

# Since timestamp
docker logs --since 2023-01-01T00:00:00 myapp
```

### Debugging

```bash
# Execute shell in running container
docker exec -it myapp sh
docker exec -it myapp bash

# Run container with shell
docker run -it myapp sh

# Inspect container
docker inspect myapp

# View resource usage
docker stats
docker stats myapp

# View processes
docker top myapp
```

### Common Issues

```bash
# Issue: Port already in use
# Solution: Find and kill process
lsof -i :3000
kill -9 <PID>

# Issue: Cannot remove container
docker rm -f myapp

# Issue: Disk space
docker system df
docker system prune -a

# Issue: Network conflict
docker network prune

# Issue: Permission denied
sudo chmod 666 /var/run/docker.sock
```

---

## Resources

- Docker Documentation: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Dockerfile Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Docker Security: https://docs.docker.com/engine/security/
- Kubernetes: https://kubernetes.io/docs/
