# REST API Service

A production-ready RESTful API service built with industry best practices for performance, security, and scalability.

## Overview

This API service provides a robust backend infrastructure with:
- RESTful endpoints with comprehensive documentation
- Authentication and authorization
- Database integration with ORM
- Input validation and error handling
- Rate limiting and security features
- Monitoring and logging
- Comprehensive testing

## Tech Stack

### Core
- Modern web framework (FastAPI/Express/Django)
- RESTful API design principles
- OpenAPI/Swagger documentation
- JSON request/response handling

### Database
- Relational database with ORM
- Migration management
- Connection pooling
- Query optimization

### Authentication
- JWT token-based authentication
- OAuth2 support (optional)
- API key authentication (optional)
- Role-based access control (RBAC)

### Infrastructure
- Docker containerization
- Environment-based configuration
- Logging and monitoring
- Health check endpoints

## Features

- RESTful API with versioning support
- Comprehensive API documentation (OpenAPI/Swagger)
- JWT authentication
- Role-based permissions
- Input validation and error handling
- Rate limiting
- CORS configuration
- Database migrations
- Logging and monitoring
- Health checks and metrics
- Automated testing
- API key management (optional)

## Getting Started

### Prerequisites

- Python 3.10+ (for Python-based APIs) or Node.js 18+
- Database (PostgreSQL, MySQL, MongoDB)
- Docker (optional, recommended)
- Redis (optional, for caching/sessions)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Set up environment**
   ```bash
   # Python
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Node.js
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create database
   createdb api_service

   # Run migrations
   # Python/Alembic
   alembic upgrade head

   # Python/Django
   python manage.py migrate

   # Node.js
   npm run migrate
   ```

### Running the Service

#### Development Mode

```bash
# Python/FastAPI
uvicorn main:app --reload --port 8000

# Python/Django
python manage.py runserver

# Node.js/Express
npm run dev
```

Access the API:
- API Base: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### Production Mode with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Project Structure

```
.
├── api/                    # API application
│   ├── routes/            # API endpoints
│   │   ├── auth.py       # Authentication routes
│   │   ├── users.py      # User routes
│   │   └── ...           # Other routes
│   ├── models/           # Database models
│   ├── schemas/          # Request/response schemas
│   ├── services/         # Business logic
│   ├── middleware/       # Custom middleware
│   ├── utils/           # Helper functions
│   └── deps.py          # Dependencies
│
├── database/             # Database configuration
│   ├── migrations/      # Database migrations
│   └── seeds/          # Sample data
│
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Test fixtures
│
├── config/             # Configuration files
│   ├── settings.py    # Application settings
│   └── logging.py     # Logging configuration
│
├── docker/            # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/              # Additional documentation
├── .env.example      # Environment template
├── requirements.txt  # Python dependencies
├── package.json      # Node.js dependencies
└── README.md        # This file
```

## API Documentation

### Authentication

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### Resource Endpoints

#### List Resources
```http
GET /api/v1/resources
Authorization: Bearer <access_token>
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 10, max: 100)
  - sort: string (e.g., "created_at:desc")
  - filter: string (e.g., "status:active")
```

#### Get Resource
```http
GET /api/v1/resources/:id
Authorization: Bearer <access_token>
```

#### Create Resource
```http
POST /api/v1/resources
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Resource Name",
  "description": "Resource description",
  "properties": {}
}
```

#### Update Resource
```http
PUT /api/v1/resources/:id
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Resource
```http
DELETE /api/v1/resources/:id
Authorization: Bearer <access_token>
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Resource",
    ...
  },
  "meta": {
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

### Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `204 No Content` - Resource deleted
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

For complete API documentation, visit `/docs` (Swagger UI) or `/redoc` (ReDoc) when running the service.

## Testing

### Run All Tests
```bash
# Python
pytest

# With coverage
pytest --cov=api --cov-report=html

# Node.js
npm test

# With coverage
npm test -- --coverage
```

### Run Specific Tests
```bash
# Python
pytest tests/test_auth.py
pytest tests/test_auth.py::test_login

# Node.js
npm test -- auth.test.js
```

### Integration Tests
```bash
# Python
pytest tests/integration/

# Node.js
npm run test:integration
```

### API Testing with HTTPie/curl
```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Access protected endpoint
curl http://localhost:8000/api/v1/resources \
  -H "Authorization: Bearer <your_token>"
```

## Configuration

### Environment Variables

```bash
# Application
APP_NAME=API Service
APP_ENV=development
APP_DEBUG=true
API_VERSION=v1

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/api_db

# Authentication
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## Security

- All passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- CORS properly configured
- Input validation on all endpoints
- SQL injection protection via ORM/parameterized queries
- Rate limiting on all endpoints
- Secure headers (HSTS, CSP, etc.)
- API versioning for backward compatibility
- HTTPS enforced in production

## Performance

- Database connection pooling
- Query optimization with indexes
- Response caching (Redis)
- Pagination for list endpoints
- Async/await for I/O operations
- Gzip compression
- CDN for static assets (if any)

## Monitoring

### Health Checks
```http
GET /health
GET /health/db        # Database connectivity
GET /health/redis     # Redis connectivity (if used)
```

### Metrics
- Request count and latency
- Error rates
- Database query performance
- Active connections
- Memory usage

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging
- Error tracking with stack traces
- Audit logging for sensitive operations

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t api-service .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name api-service \
  api-service

# View logs
docker logs -f api-service
```

### Docker Compose
```bash
docker-compose up -d
```

### Cloud Deployment
See deployment guides in `/docs/deployment/` for specific platforms.

## API Versioning

The API uses URL-based versioning:
- Current version: `/api/v1/`
- When breaking changes are introduced, a new version will be created: `/api/v2/`
- Old versions are supported for a deprecation period (typically 6-12 months)

## Rate Limiting

Default rate limits:
- Anonymous: 30 requests/minute
- Authenticated: 60 requests/minute
- Premium: 300 requests/minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/api-endpoint`)
3. Write tests for your changes
4. Implement your changes
5. Run tests and ensure they pass
6. Commit your changes (`git commit -m 'Add new endpoint'`)
7. Push to the branch (`git push origin feature/api-endpoint`)
8. Open a Pull Request

## License

[Your License Here]

## Support

- Documentation: [API Docs URL]
- Issues: [GitHub Issues URL]
- Email: api-support@your-company.com

---

**Built with Claude Code Generator** - Enterprise-grade API development made simple.
