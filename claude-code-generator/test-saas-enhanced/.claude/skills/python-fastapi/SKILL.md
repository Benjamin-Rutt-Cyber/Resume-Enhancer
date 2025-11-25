---
name: python-fastapi
description: Expert knowledge in Python FastAPI web framework including routing, dependencies, async operations, Pydantic models, and best practices for building high-performance APIs.
allowed-tools: [Read, Write, Edit, Bash]
---

# Python FastAPI Skill

Comprehensive knowledge for building modern, fast Python APIs with FastAPI.

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI and Uvicorn
pip install fastapi uvicorn[standard]
pip install python-multipart  # For form data

# Optional dependencies
pip install sqlalchemy pydantic[email] python-jose[cryptography] passlib[bcrypt]
```

### Minimal Application

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="A FastAPI application",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run with:**
```bash
uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API documentation

---

## Core Concepts

### 1. Path Operations (Routes)

```python
from fastapi import FastAPI, Path, Query, Body
from typing import Optional
from enum import Enum

app = FastAPI()

# GET endpoint with path parameter
@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., gt=0, description="The ID of the item"),
    q: Optional[str] = Query(None, max_length=50, description="Search query")
):
    return {"item_id": item_id, "q": q}

# POST endpoint with request body
@app.post("/items/", status_code=201)
async def create_item(
    item: Item,
    user_agent: Optional[str] = Header(None)
):
    return {"item": item, "user_agent": user_agent}

# PUT endpoint
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    return {"item_id": item_id, **item.dict(exclude_unset=True)}

# PATCH endpoint
@app.patch("/items/{item_id}")
async def partial_update(item_id: int, item: ItemUpdate):
    return {"item_id": item_id, **item.dict(exclude_unset=True)}

# DELETE endpoint
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    # Delete logic here
    return None

# Enum path parameter
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model_name": model_name, "message": f"Model is {model_name.value}"}
```

### 2. Pydantic Models

```python
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    hashed_password: str

    class Config:
        orm_mode = True  # Allows reading from ORM models

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Nested models
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None

class UserWithAddress(UserResponse):
    address: Optional[Address] = None

# List responses
class PaginatedUsers(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
```

### 3. Dependency Injection

```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await verify_token(token, db)
    if user is None:
        raise credentials_exception
    return user

# Authorization dependency
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Admin check dependency
async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Use dependencies in routes
@app.get("/users/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### 4. Async Operations

```python
import httpx
import asyncio
from fastapi import FastAPI

app = FastAPI()

# Async HTTP request
@app.get("/fetch-data")
async def fetch_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# Multiple concurrent requests
@app.get("/fetch-multiple")
async def fetch_multiple():
    async with httpx.AsyncClient() as client:
        # Concurrent requests
        responses = await asyncio.gather(
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/posts"),
            client.get("https://api.example.com/comments")
        )
        return {
            "users": responses[0].json(),
            "posts": responses[1].json(),
            "comments": responses[2].json()
        }

# Async database query
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # With async SQLAlchemy
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 5. Error Handling

```python
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Raise HTTP exceptions
@app.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item

# Custom exception
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

# Custom exception handler
@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )

# Override validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Generic error handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 6. Background Tasks

```python
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

def send_email(email: str, message: str):
    """Long-running background task."""
    logger.info(f"Sending email to {email}")
    # Email sending logic here
    time.sleep(5)  # Simulate slow operation
    logger.info(f"Email sent to {email}")

def write_log(message: str):
    with open("log.txt", mode="a") as log_file:
        log_file.write(message + "\n")

@app.post("/send-notification")
async def send_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, message)
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification will be sent in background"}

@app.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_user = create_user_in_db(db, user)
    background_tasks.add_task(send_email, user.email, "Welcome!")
    return db_user
```

### 7. Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status code: {response.status_code}")
    return response
```

---

## Database Integration

### SQLAlchemy Setup

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "postgresql://user:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    author = relationship("User", back_populates="posts")

# Create tables
Base.metadata.create_all(bind=engine)
```

### CRUD Operations

```python
from sqlalchemy.orm import Session

# Create
@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pwd = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Read one
@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Read many with pagination
@app.get("/users/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Update
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Delete
@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
```

---

## Common Patterns

### Pagination

```python
from fastapi import Query

@app.get("/items/")
async def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * per_page
    total = db.query(Item).count()
    items = db.query(Item).offset(skip).limit(per_page).all()

    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

### File Uploads

```python
from fastapi import File, UploadFile
import shutil

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "content_type": file.content_type}

@app.post("/upload-multiple/")
async def upload_multiple(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return {"filenames": filenames}
```

### JWT Authentication

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Testing

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI"}

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "username": "testuser", "password": "Test1234"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_read_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data

def test_authentication():
    # Login
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "Test1234"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Use token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

---

## Best Practices

1. **Use async when possible** - For I/O-bound operations (database, HTTP requests)
2. **Proper status codes** - 201 for creation, 204 for no content, 404 for not found
3. **Dependency injection** - Share database sessions, authentication
4. **Response models** - Always define response schemas with Pydantic
5. **Error handling** - Use HTTPException with appropriate status codes
6. **Validation** - Let Pydantic handle input validation
7. **Documentation** - FastAPI auto-generates interactive docs
8. **Security** - Use environment variables for secrets, never hardcode
9. **Database connections** - Always close connections (use dependencies with yield)
10. **Pagination** - Always paginate list endpoints

---

## Project Structure

```
my-fastapi-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── items.py
│   ├── core/                # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py        # Settings
│   │   └── security.py      # Auth utilities
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/                # CRUD operations
│   │   ├── __init__.py
│   │   └── user.py
│   └── db/                  # Database
│       ├── __init__.py
│       └── database.py
├── tests/
│   ├── __init__.py
│   └── test_users.py
├── requirements.txt
└── .env
```

---

## Troubleshooting

**Issue: CORS errors**
```python
# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue: Validation errors**
- Check Pydantic model field types
- Use `response.json()` to see detailed error messages
- Add `@validator` decorators for custom validation

**Issue: Database connection errors**
- Verify DATABASE_URL is correct
- Check database is running
- Use `pool_pre_ping=True` in create_engine

**Issue: Import errors**
- Use relative imports within app package
- Add `__init__.py` files in all directories

---

## Quick Reference

**Run development server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Run with workers:**
```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Auto-generated documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Testing:**
```bash
pytest tests/ -v
pytest tests/ --cov=app
```

---

## Resources

- Official Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Awesome FastAPI: https://github.com/mjhea0/awesome-fastapi
