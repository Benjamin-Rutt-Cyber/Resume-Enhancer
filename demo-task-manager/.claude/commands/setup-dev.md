# Setup Development Environment

Initialize the complete development environment for Demo Task Manager.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- PostgreSQL 14 or higher

## Setup Steps

### 1. Clone Repository (if needed)

```bash
git clone https://github.com/yourusername/demo-task-manager.git
cd demo-task-manager
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

### 3. Frontend Setup

```bash
cd ../frontend
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your API URL
```

### 4. Database Setup

```bash
# Create database
createdb demo-task-manager

# Run migrations
cd backend
alembic upgrade head

# Optional: Seed database with test data
python -m app.seeds.seed_data
```

### 5. Verify Installation

```bash
# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

```bash
# In another terminal, start frontend
cd frontend
npm start
```

### 6. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Required environment variables for Demo Task Manager:

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/demo-task-manager

# Security
SECRET_KEY=your-secret-key-here

# API
FRONTEND_URL=http://localhost:3000
API_PREFIX=/api/v1

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30

```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_PREFIX=/api/v1
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

Your development environment for Demo Task Manager is now ready!
