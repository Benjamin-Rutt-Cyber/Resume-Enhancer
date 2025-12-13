# Run Development Server

Start the development server for Demo Task Manager.

## Quick Start

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment (if not already activated)
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows

# Run server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Frontend (in separate terminal)

```bash
cd frontend
npm start
```

## Server Access

- **Backend API:** http://localhost:8000
- **API Documentation (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Frontend:** http://localhost:3000

## Environment Check

Before starting the server, verify:

1. **Database is running**
   ```bash
   # Check PostgreSQL status
   pg_isready
   ```

2. **Environment variables are set**
   ```bash
   # Backend .env file should exist
   cat backend/.env
   ```

3. **Dependencies are installed**
   ```bash
   pip list  # Should show fastapi, uvicorn, etc.
   ```

## Development Options

### Run with Custom Port

```bash
uvicorn app.main:app --reload --port 8001
```

### Run with Debug Logging

```bash
uvicorn app.main:app --reload --log-level debug
```

### Run Workers for Production-like Environment

```bash
uvicorn app.main:app --workers 4
```

## Using Docker (Alternative)

```bash
# Run entire stack with Docker Compose
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Monitoring Server

### Watch Server Logs

The development server will show:
- Incoming requests
- Response status codes
- Errors and stack traces
- Auto-reload notifications

### Test API with curl

```bash
# Health check
curl http://localhost:8000/health

# Get API documentation JSON
curl http://localhost:8000/openapi.json

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Test with httpie (Alternative)

```bash
# Install httpie
pip install httpie

# Make requests
http GET localhost:8000/health
http POST localhost:8000/api/v1/auth/login email=user@example.com password=password
```

## Hot Reload

The server automatically reloads when you make changes to:
- Python/JavaScript files
- Configuration files
- Template files

**Note:** Database schema changes require manual migration.

## Troubleshooting

### Server Won't Start

1. **Check if port is already in use:**
   ```bash
   # Unix/macOS
   lsof -i :8000

   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill process using port:**
   ```bash
   # Unix/macOS
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   ```

### Database Connection Error

```bash
# Verify database is running
psql -U postgres -c "SELECT 1"

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify virtual environment is activated
which python  # Should show .venv path
```

### Module Not Found

- Ensure virtual environment is activated
- Check PYTHONPATH includes project root

## Performance Monitoring

Monitor server performance:

```bash
# Install monitoring tools
pip install py-spy

# Profile running server
py-spy top --pid <uvicorn-pid>
```

## Next Steps

- Visit http://localhost:8000/docs to explore API
- Make API requests to test endpoints
- Run `/run-tests` to verify everything works
- Check logs for any warnings or errors

Server is now running for Demo Task Manager!
