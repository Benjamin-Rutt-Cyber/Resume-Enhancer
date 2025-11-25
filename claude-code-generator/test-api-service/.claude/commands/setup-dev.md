# Setup Development Environment

Initialize the complete development environment for DataAPI.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- PostgreSQL 14 or higher

## Setup Steps

### 1. Clone Repository (if needed)

```bash
git clone https://github.com/yourusername/dataapi.git
cd dataapi
```

### 2. Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```


### 3. Database Setup

```bash
# Create database
createdb dataapi

# Run migrations
cd backend
alembic upgrade head

# Optional: Seed database with test data
python -m app.seeds.seed_data
```

### 4. Verify Installation

```bash
# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```


### 5. Access Application

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Required environment variables for DataAPI:

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dataapi

# Security
SECRET_KEY=your-secret-key-here

# API
API_PREFIX=/api/v1


```


## Troubleshooting

### Database Connection Error
- Verify database is running
- Check DATABASE_URL in .env
- Ensure database exists

### Port Already in Use
- Change port in command: `--port 8001`
- Or kill process using the port

### Module Not Found
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## Next Steps

- Run `/run-tests` to execute test suite
- Run `/run-server` to start development server
- Read docs/ARCHITECTURE.md for system overview
- See docs/API.md for API documentation

## Common Development Commands

```bash
# Run tests
/run-tests

# Start server
/run-server

# Run database migrations
/db-migrate

# Format code
/format-code

# Lint code
/lint-code
```

Your development environment for DataAPI is now ready!
