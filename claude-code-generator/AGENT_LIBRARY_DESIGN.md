# Agent Library Design - Reusable vs. Generated

## The Problem with Current Approach

**Current (wasteful):**
- Generate a new "api-development-agent" for EVERY project
- Same agent content, just different project name
- Wastes tokens, time, and creates unnecessary files
- Hard to maintain (bug fixes require regenerating all projects)

**Better Approach:**
- Create ONE comprehensive, reusable agent
- Copy it as-is to new projects when needed
- Only customize project-specific details in agent description
- Build a growing library of battle-tested agents

---

## New Architecture

```
templates/
├── agents/
│   ├── reusable/              ← Generic, copy as-is
│   │   ├── api-development-agent.md
│   │   ├── frontend-react-agent.md
│   │   ├── database-postgresql-agent.md
│   │   ├── testing-agent.md
│   │   ├── deployment-docker-agent.md
│   │   ├── security-agent.md
│   │   ├── python-fastapi-agent.md
│   │   ├── graphql-agent.md
│   │   └── ... (library grows over time)
│   └── project-specific/      ← Templates for unique needs
│       ├── domain-expert-agent.md.j2
│       └── business-logic-agent.md.j2
└── registry.yaml
```

---

## Agent Categories

### Type 1: Reusable Generic Agents (95% of cases)

These are **complete, in-depth agents** that don't need project-specific customization:

**Examples:**
- `api-development-agent.md` - Works for ANY REST API project
- `frontend-react-agent.md` - Works for ANY React project
- `database-postgresql-agent.md` - Works for ANY PostgreSQL project
- `testing-pytest-agent.md` - Works for ANY Python testing
- `security-agent.md` - Works for ANY web application
- `deployment-docker-agent.md` - Works for ANY Docker deployment

**Key Characteristics:**
- Technology-focused (not project-focused)
- Generic examples that work everywhere
- Deep expertise in ONE technology/domain
- No project name references needed
- Can be 1000+ lines of comprehensive knowledge

**How they're used:**
```python
# Just copy the file as-is
shutil.copy(
    'templates/agents/reusable/api-development-agent.md',
    'my-project/.claude/agents/api-development-agent.md'
)
```

### Type 2: Project-Specific Generated Agents (5% of cases)

Only when truly unique to the project:

**Examples:**
- `domain-expert-agent.md.j2` - E-commerce vs Healthcare vs Finance domain logic
- `business-logic-agent.md.j2` - Project-specific business rules
- `custom-integration-agent.md.j2` - Specific third-party API integration

**How they're used:**
```python
# Render template with project details
content = render_template(
    'templates/agents/project-specific/domain-expert-agent.md.j2',
    context={'project_type': 'healthcare', 'regulations': ['HIPAA']}
)
```

---

## Comprehensive Agent Structure

### Example: `api-development-agent.md`

```markdown
---
name: api-development-agent
description: |
  Use this agent PROACTIVELY when working on REST API development tasks including:
  - Designing RESTful endpoints and resource models
  - Implementing API routes and request handlers
  - Validating request/response schemas
  - Handling authentication and authorization
  - Writing API documentation (OpenAPI/Swagger)
  - Optimizing API performance and caching
  - Testing API endpoints

  Activate when you see tasks like "create endpoint", "add API route", "implement authentication",
  or when working with API frameworks (FastAPI, Express, Django REST, etc.).

  This agent works with any REST API project regardless of framework or language.
model: sonnet
tools: Read, Write, Edit, Bash, Grep, Glob
---

# API Development Agent

**Expert in REST API design, implementation, and best practices across all frameworks.**

## Core Responsibilities

### 1. API Design & Architecture

**RESTful Design Principles:**
- Resource-based URLs (`/users`, `/posts`, `/comments`)
- Proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Appropriate status codes (200, 201, 204, 400, 401, 403, 404, 500)
- Consistent response formats
- API versioning strategies (`/api/v1/`, headers, content negotiation)

**Resource Modeling:**
```
Users
  ├── GET    /users          - List users (paginated)
  ├── POST   /users          - Create user
  ├── GET    /users/{id}     - Get user details
  ├── PUT    /users/{id}     - Update user (full)
  ├── PATCH  /users/{id}     - Update user (partial)
  └── DELETE /users/{id}     - Delete user

Nested Resources:
  ├── GET    /users/{id}/posts        - User's posts
  └── GET    /posts/{id}/comments     - Post's comments
```

**API Design Checklist:**
- [ ] Resources identified and modeled
- [ ] URL structure follows REST conventions
- [ ] HTTP methods used correctly
- [ ] Status codes documented
- [ ] Error responses standardized
- [ ] Pagination strategy defined
- [ ] Filtering/sorting parameters planned
- [ ] Rate limiting considered
- [ ] Versioning strategy chosen

### 2. Request/Response Handling

**Request Validation:**

*FastAPI Example:*
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=13, le=120)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Validation happens automatically
    # Implementation here
    pass
```

*Express Example:*
```javascript
const { body, validationResult } = require('express-validator');

app.post('/users',
  body('email').isEmail().normalizeEmail(),
  body('username').isLength({ min: 3, max: 50 }).matches(/^[a-zA-Z0-9_-]+$/),
  body('password').isLength({ min: 8 }).matches(/[A-Z]/).matches(/[0-9]/),
  body('age').isInt({ min: 13, max: 120 }),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // Implementation here
  }
);
```

**Response Formatting:**

Standardized success response:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "v1"
  }
}
```

Standardized error response:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "metadata": {
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### 3. Authentication & Authorization

**JWT Authentication Implementation:**

*Token Generation:*
```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

*Login Endpoint:*
```python
@app.post("/auth/login")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800
    }
```

*Protected Endpoints:*
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

# Use in endpoints
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Role-Based Access Control:**
```python
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def require_role(required_role: Role):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Admin-only endpoint
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(Role.ADMIN))
):
    await delete_user_from_db(user_id)
    return {"message": "User deleted"}
```

### 4. Database Integration

**Connection Management:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**CRUD Operations:**
```python
# Create
async def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Read (with pagination)
async def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# Update
async def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# Delete
async def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
```

**Query Optimization:**
```python
# Bad: N+1 query problem
users = db.query(User).all()
for user in users:
    print(user.posts)  # Triggers query for each user

# Good: Eager loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # No additional queries
```

### 5. Error Handling

**Global Exception Handler:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request.state.request_id
            }
        }
    )

# Custom exceptions
class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": f"{exc.resource} with id {exc.id} not found"
            }
        }
    )
```

### 6. Pagination, Filtering, Sorting

**Pagination:**
```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int

@app.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(User).count()
    users = db.query(User).offset((page - 1) * per_page).limit(per_page).all()

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )
```

**Filtering & Sorting:**
```python
@app.get("/users")
async def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(User)

    # Filtering
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Sorting
    if sort_order == "asc":
        query = query.order_by(getattr(User, sort_by).asc())
    else:
        query = query.order_by(getattr(User, sort_by).desc())

    return query.all()
```

### 7. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, credentials: OAuth2PasswordRequestForm = Depends()):
    # Login logic
    pass

@app.get("/api/data")
@limiter.limit("100/hour")  # Max 100 requests per hour
async def get_data(request: Request):
    # Data retrieval logic
    pass
```

### 8. Caching

**Response Caching with Redis:**
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(key: str, ttl: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Try to get from cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@app.get("/users/{user_id}")
@cache_response(key="user:{user_id}", ttl=600)
async def get_user(user_id: int):
    # Expensive database query
    return await fetch_user_from_db(user_id)
```

### 9. API Documentation (OpenAPI/Swagger)

**Enhanced Documentation:**
```python
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with the provided information. Email and username must be unique.",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "created_at": "2025-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    },
    tags=["users"]
)
async def create_user(user: UserCreate):
    pass
```

### 10. Testing API Endpoints

**Unit Tests:**
```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_duplicate_email():
    # Create first user
    client.post("/users", json={
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "SecurePass123"
    })

    # Attempt duplicate
    response = client.post("/users", json={
        "email": "duplicate@example.com",
        "username": "user2",
        "password": "SecurePass123"
    })
    assert response.status_code == 400

def test_login():
    # Create user
    client.post("/users", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "SecurePass123"
    })

    # Login
    response = client.post("/auth/login", data={
        "username": "login@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint():
    # Create and login
    client.post("/users", json={
        "email": "protected@example.com",
        "username": "protected",
        "password": "SecurePass123"
    })
    login_response = client.post("/auth/login", data={
        "username": "protected@example.com",
        "password": "SecurePass123"
    })
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## Best Practices Summary

### API Design
- Use plural nouns for resources
- Use HTTP methods correctly (GET=read, POST=create, PUT/PATCH=update, DELETE=delete)
- Return appropriate status codes
- Version your API from the start
- Design for scalability and future changes

### Security
- Always validate input
- Use HTTPS in production
- Implement rate limiting
- Hash passwords with bcrypt/Argon2
- Use JWT with appropriate expiration
- Implement CORS properly
- Never expose sensitive data in responses

### Performance
- Use database connection pooling
- Implement caching for expensive operations
- Paginate large result sets
- Use eager loading to avoid N+1 queries
- Add database indexes on frequently queried fields

### Error Handling
- Use consistent error response format
- Provide helpful error messages
- Log errors with context
- Don't expose internal errors to clients
- Use HTTP status codes correctly

### Documentation
- Document all endpoints with OpenAPI/Swagger
- Provide request/response examples
- Document authentication requirements
- Keep documentation up to date
- Include rate limits and pagination details

### Testing
- Write tests for all endpoints
- Test success and error cases
- Test authentication and authorization
- Use test database for integration tests
- Aim for high test coverage

## Related Skills

- **python-fastapi**: FastAPI-specific patterns
- **rest-api-design**: RESTful API design principles
- **authentication**: JWT and OAuth2 implementation
- **database-optimization**: Query optimization techniques
- **api-testing**: Testing strategies for APIs

## Framework-Specific Notes

This agent provides general REST API guidance. Refer to framework-specific skills for implementation details:
- FastAPI: See `python-fastapi` skill
- Express: See `node-express` skill
- Django REST: See `django-rest-framework` skill
- Go: See `go-gin` or `go-fiber` skill
```

This is 500+ lines and we're only halfway through what this agent should know!

---

## Benefits of This Approach

### 1. **Reusability**
- Write once, use in thousands of projects
- No duplication

### 2. **Maintainability**
- Fix a bug → Update ONE file
- All future projects get the fix

### 3. **Depth**
- Each agent can be 1000-2000+ lines
- Comprehensive coverage of the domain
- Battle-tested over many projects

### 4. **Token Efficiency**
- No generation cost for reusable agents
- Just file copy operation

### 5. **Growing Library**
- Start with 10 agents
- Add more as you encounter new technologies
- Community can contribute

---

## Implementation Changes Needed

```python
# file_generator.py

def _generate_agent(self, agent_spec: dict, context: dict, output_dir: Path):
    """Generate or copy agent based on type."""

    if agent_spec['type'] == 'reusable':
        # Just copy the complete agent as-is
        source = self.templates_dir / agent_spec['file']
        dest = output_dir / '.claude' / 'agents' / Path(agent_spec['file']).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, dest)

    elif agent_spec['type'] == 'generated':
        # Render template with project context
        content = self.renderer.render_template(agent_spec['template'], context)
        dest = output_dir / '.claude' / 'agents' / agent_spec['output_name']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding='utf-8')
```

```yaml
# registry.yaml

agents:
  - name: api-development-agent
    type: reusable                    # ← Just copy as-is
    file: agents/reusable/api-development-agent.md
    technologies: [rest-api, http]

  - name: frontend-react-agent
    type: reusable                    # ← Just copy as-is
    file: agents/reusable/frontend-react-agent.md
    technologies: [react, frontend]

  - name: domain-expert-agent
    type: generated                   # ← Generate from template
    template: agents/project-specific/domain-expert-agent.md.j2
    output_name: "{project_slug}-domain-agent.md"
```

## ✅ IMPLEMENTATION STATUS

**This approach has been IMPLEMENTED!**

### What Was Done

1. ✅ Created `templates/agents/reusable/` and `templates/agents/project-specific/` directories
2. ✅ Created 3 comprehensive reusable agents:
   - `api-development-agent.md` (1500+ lines)
   - `testing-agent.md` (1400+ lines)
   - `deployment-agent.md` (1200+ lines)
3. ✅ Updated `file_generator.py` to support both agent types
4. ✅ Updated `registry.yaml` with `type: reusable` and `type: generated` specifications

### How It Works Now

When generating a project:

1. **Reusable agents** (`.md` files): Copied as-is to `.claude/agents/`
   - No templating
   - No project-specific references
   - Comprehensive, battle-tested content
   - Example: `api-development-agent.md` → `.claude/agents/api-development-agent.md`

2. **Generated agents** (`.md.j2` files): Rendered with Jinja2
   - Project-specific variables
   - Custom for each project
   - Example: `frontend-agent.md.j2` → `.claude/agents/frontend-agent.md`

### Benefits Achieved

- **Token Efficiency**: No generation cost for reusable agents (just file copy)
- **Depth**: Each reusable agent is 1000-1500+ lines of comprehensive guidance
- **Maintainability**: Fix once, all future projects benefit
- **Growing Library**: Can add more reusable agents over time

### Next Steps

1. Add more reusable agents as needed:
   - `security-agent.md` (security best practices)
   - `database-agent.md` (database optimization)
   - `frontend-react-agent.md` (React-specific)
   - `frontend-vue-agent.md` (Vue-specific)
   - etc.

2. Convert existing templated agents to reusable when they don't need project-specific customization

3. Build the library organically as projects use the generator
