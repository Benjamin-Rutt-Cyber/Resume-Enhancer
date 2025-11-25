# Setup Development Environment

Initialize the complete development environment for IoT Test.

## Prerequisites

- Git

## Setup Steps

### 1. Clone Repository (if needed)

```bash
git clone https://github.com/yourusername/iot-test.git
cd iot-test
```

### 2. Backend Setup



### 3. Database Setup


### 4. Verify Installation



### 5. Access Application

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Required environment variables for IoT Test:

### Backend (.env)
```bash
# Database
DATABASE_URL=None://user:password@localhost/iot-test

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

Your development environment for IoT Test is now ready!
