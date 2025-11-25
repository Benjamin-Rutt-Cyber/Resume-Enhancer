---
name: dataapi-python-fastapi
description: Expert knowledge in Python FastAPI web framework including routing, dependencies, async operations, Pydantic models, and best practices for building high-performance APIs.
allowed-tools: [Read, Write, Edit, Bash]
---

# Python FastAPI Skill

Comprehensive knowledge for building modern, fast Python APIs with FastAPI.

## Quick Start

```python
from fastapi import FastAPI

app = FastAPI(title="DataAPI")

@app.get("/")
async def root():
    return {"message": "Welcome to DataAPI"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

Run with: `uvicorn main:app --reload`

## Core Concepts

### 1. Path Operations

```python
from fastapi import FastAPI, Path, Query
from typing import Optional

app = FastAPI()

# GET endpoint
@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., gt=0, description="The ID of the item"),
    q: Optional[str] = Query(None, max_length=50)
):
    return {"item_id": item_id, "q": q}

# POST endpoint
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    return item

# PUT endpoint
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# DELETE endpoint
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"message": "Item deleted"}
```

### 2. Pydantic Models

```python
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Allows reading from ORM models
```

### 3. Dependency Injection

```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

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
        detail="Could not validate credentials"
    )
    # Validate token and get user
    user = await verify_token(token, db)
    if user is None:
        raise credentials_exception
    return user

# Use dependencies
@app.get("/users/me")
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

### 4. Async Operations

```python
import httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/fetch-data")
async def fetch_external_data():
    """Async HTTP request."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

@app.post("/process")
async def process_data(data: dict):
    """Async processing."""
    result = await long_running_task(data)
    return {"result": result}
```

### 5. Error Handling

```python
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

# Raise HTTP exceptions
@app.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item

# Custom exception handler
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )
```

### 6. Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """Long-running task."""
    # Send email logic
    print(f"Sending email to {email}: {message}")

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification will be sent"}
```

### 7. Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Database Integration (SQLAlchemy)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@localhost/dataapi"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# CRUD operations
@app.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## Best Practices

1. **Use async when possible** - For I/O operations
2. **Proper status codes** - 201 for creation, 204 for no content
3. **Dependency injection** - Share database sessions, auth
4. **Response models** - Always define response schemas
5. **Error handling** - Use HTTPException with proper status codes
6. **Documentation** - FastAPI auto-generates docs at `/docs`

## Quick Reference

**Run server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Auto-generated docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Project structure:**
```
dataapi/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── api/             # API routes
│   │   └── v1/
│   ├── core/            # Config, security
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
└── tests/
```

This skill provides FastAPI expertise for building DataAPI.
