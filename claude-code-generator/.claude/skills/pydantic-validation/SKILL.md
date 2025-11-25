---
name: pydantic-validation
description: Expert knowledge in data validation, parsing, and serialization using Pydantic v2, including model definition, field validation, custom validators, nested models, configuration, error handling, and JSON schema generation. Use this skill when defining data models, validating API responses, parsing configuration files, implementing data validation logic, or working with structured data in Python.
allowed-tools: [Read, Write]
---

# Pydantic Data Validation Skill

Comprehensive knowledge for building robust data validation with Pydantic v2, specialized for API responses, configuration parsing, and data integrity.

## Basic Models

### Simple Model Definition

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    """User model with validation."""
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = True

# Usage
user = User(
    id=1,
    name="John Doe",
    email="john@example.com",
    age=30
)

print(user.name)  # "John Doe"
print(user.model_dump())  # Dict representation
print(user.model_dump_json())  # JSON string
```

### Field Constraints

```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl, constr, conint

class Project(BaseModel):
    """Project configuration with field constraints."""

    # String constraints
    name: str = Field(..., min_length=3, max_length=100)
    slug: constr(pattern=r'^[a-z0-9-]+$')  # Regex pattern
    description: str = Field(default="", max_length=500)

    # Numeric constraints
    priority: conint(ge=1, le=10) = 5  # Between 1-10
    budget: float = Field(..., gt=0)  # Greater than 0

    # Special types
    email: EmailStr  # Validated email
    website: HttpUrl  # Validated URL

    # Enums
    status: Literal['draft', 'active', 'completed']
```

## Validators

### Field Validators

```python
from pydantic import BaseModel, field_validator, ValidationError

class ProjectConfig(BaseModel):
    project_name: str
    project_slug: str

    @field_validator('project_slug')
    @classmethod
    def validate_slug(cls, v):
        """Ensure slug is lowercase with hyphens only."""
        if not v:
            raise ValueError('Slug cannot be empty')

        if not all(c.isalnum() or c == '-' for c in v):
            raise ValueError('Slug can only contain letters, numbers, and hyphens')

        if not v.islower():
            raise ValueError('Slug must be lowercase')

        return v

    @field_validator('project_name')
    @classmethod
    def validate_name(cls, v):
        """Validate project name."""
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')

        return v.strip()

# Usage
try:
    config = ProjectConfig(
        project_name="My Project",
        project_slug="MY-PROJECT"  # Invalid: uppercase
    )
except ValidationError as e:
    print(e.errors())
```

### Model Validators

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def validate_date_range(self):
        """Ensure end_date is after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        return self

class Config(BaseModel):
    backend: Optional[str] = None
    frontend: Optional[str] = None

    @model_validator(mode='after')
    def validate_at_least_one(self):
        """Ensure at least one framework is specified."""
        if not self.backend and not self.frontend:
            raise ValueError('Must specify at least backend or frontend')
        return self
```

### Custom Validation Functions

```python
from pydantic import field_validator
import re

def validate_kebab_case(v: str) -> str:
    """Validate and convert to kebab-case."""
    if not v:
        raise ValueError('Value cannot be empty')

    # Convert to kebab-case
    slug = v.lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = slug.strip('-')
    slug = re.sub(r'-+', '-', slug)

    return slug

class Project(BaseModel):
    name: str
    slug: str

    @field_validator('slug', mode='before')
    @classmethod
    def ensure_kebab_case(cls, v):
        return validate_kebab_case(v)
```

## Nested Models

### Basic Nesting

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class User(BaseModel):
    name: str
    email: str
    address: Address  # Nested model
    tags: List[str] = []  # List of strings

# Usage
user = User(
    name="John",
    email="john@example.com",
    address={
        "street": "123 Main St",
        "city": "New York",
        "country": "USA",
        "zip_code": "10001"
    },
    tags=["developer", "python"]
)

print(user.address.city)  # "New York"
```

### Complex Nesting

```python
class TechStack(BaseModel):
    backend: str
    frontend: Optional[str] = None
    database: str
    cache: Optional[str] = None

class Feature(BaseModel):
    name: str
    enabled: bool = True

class ProjectConfig(BaseModel):
    project_name: str
    project_slug: str
    project_type: Literal['saas', 'api', 'mobile', 'hardware']
    tech_stack: TechStack
    features: List[Feature] = []
    metadata: dict[str, any] = {}

# Usage
config = ProjectConfig(
    project_name="My App",
    project_slug="my-app",
    project_type="saas",
    tech_stack={
        "backend": "python-fastapi",
        "frontend": "react-typescript",
        "database": "postgresql"
    },
    features=[
        {"name": "authentication", "enabled": True},
        {"name": "payments", "enabled": False}
    ]
)
```

## Default Values and Factories

### Simple Defaults

```python
from pydantic import BaseModel, Field
from datetime import datetime

class Project(BaseModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)  # Mutable default
    status: str = "draft"  # Immutable default
    priority: int = 5
```

### Complex Defaults

```python
from pydantic import BaseModel, Field
from typing import List
import uuid

def generate_id() -> str:
    """Generate unique ID."""
    return str(uuid.uuid4())

def default_config() -> dict:
    """Generate default configuration."""
    return {
        "timeout": 30,
        "retry": 3,
        "verbose": False
    }

class Task(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    config: dict = Field(default_factory=default_config)
    tags: List[str] = Field(default_factory=list)
```

## Model Configuration

### Config Options

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        # Validation
        validate_assignment=True,  # Validate on attribute assignment
        validate_default=True,     # Validate default values
        str_strip_whitespace=True, # Strip whitespace from strings
        str_min_length=1,          # Minimum string length

        # Serialization
        use_enum_values=True,      # Use enum values instead of enum objects
        populate_by_name=True,     # Allow field population by alias or name

        # Other
        frozen=False,              # Make model immutable if True
        extra='forbid',            # Forbid extra fields ('allow', 'ignore', 'forbid')
        arbitrary_types_allowed=False,  # Allow arbitrary types
    )

    name: str
    email: str
```

### Alias and Field Names

```python
from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    """Map API field names to Python names."""

    project_id: int = Field(..., alias='projectId')
    user_name: str = Field(..., alias='userName')
    is_active: bool = Field(True, alias='isActive')

    model_config = ConfigDict(populate_by_name=True)

# Parse API response
data = {
    "projectId": 123,
    "userName": "john",
    "isActive": True
}
response = APIResponse(**data)

# Access with Python names
print(response.project_id)  # 123

# Serialize with aliases
print(response.model_dump(by_alias=True))
# {"projectId": 123, "userName": "john", "isActive": True}
```

## Parsing and Serialization

### From Dict/JSON

```python
from pydantic import BaseModel, ValidationError
import json

class Config(BaseModel):
    name: str
    value: int

# From dict
config = Config(**{"name": "test", "value": 42})

# From JSON string
json_str = '{"name": "test", "value": 42}'
config = Config.model_validate_json(json_str)

# From file
with open('config.json') as f:
    data = json.load(f)
    config = Config(**data)
```

### To Dict/JSON

```python
config = Config(name="test", value=42)

# To dict
dict_data = config.model_dump()

# To dict with exclusions
dict_data = config.model_dump(exclude={'value'})
dict_data = config.model_dump(include={'name'})

# To JSON string
json_str = config.model_dump_json()

# To JSON with indentation
json_str = config.model_dump_json(indent=2)

# To file
with open('config.json', 'w') as f:
    f.write(config.model_dump_json(indent=2))
```

## Error Handling

### Catching Validation Errors

```python
from pydantic import ValidationError

try:
    config = ProjectConfig(
        project_name="",  # Invalid: too short
        project_slug="INVALID SLUG",  # Invalid: spaces and uppercase
        project_type="invalid"  # Invalid: not in literal choices
    )
except ValidationError as e:
    print(e.errors())
    # List of error dicts with loc, msg, type

    # Formatted error message
    print(str(e))

    # JSON format
    print(e.json())
```

### Custom Error Messages

```python
from pydantic import BaseModel, field_validator

class Project(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError(
                'Project name must be at least 3 characters. '
                f'Got: "{v}" ({len(v)} characters)'
            )
        return v
```

## Advanced Patterns

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

    @computed_field
    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

rect = Rectangle(width=10, height=5)
print(rect.area)  # 50.0
print(rect.perimeter)  # 30.0
```

### Root Validators

```python
from pydantic import BaseModel, model_validator

class Credentials(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @model_validator(mode='after')
    def validate_identity(self):
        """Ensure either username or email is provided."""
        if not self.username and not self.email:
            raise ValueError('Must provide either username or email')
        return self
```

### Generic Models

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool
    data: T
    error: Optional[str] = None

class User(BaseModel):
    id: int
    name: str

# Usage
response: APIResponse[User] = APIResponse(
    success=True,
    data=User(id=1, name="John")
)

response_list: APIResponse[List[User]] = APIResponse(
    success=True,
    data=[
        User(id=1, name="John"),
        User(id=2, name="Jane")
    ]
)
```

## Real-World Example: Project Configuration

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
import re

class TechStack(BaseModel):
    """Technology stack configuration."""
    backend: str
    frontend: Optional[str] = None
    database: str
    cache: Optional[str] = None
    queue: Optional[str] = None

class ProjectConfig(BaseModel):
    """Complete project configuration with validation."""

    # Basic info
    project_name: str = Field(..., min_length=3, max_length=100)
    project_slug: str = Field(..., pattern=r'^[a-z0-9-]+$')
    description: str = Field(default="")

    # Project type
    project_type: Literal['saas-web-app', 'api-service', 'hardware-iot', 'mobile-app']

    # Tech stack
    tech_stack: TechStack

    # Features
    features: List[str] = Field(default_factory=list)

    # Agents and skills
    agents: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

    # Custom requirements
    custom_requirements: dict = Field(default_factory=dict)

    # Configuration
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    @field_validator('project_slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Auto-generate slug from name if not provided."""
        if not v and 'project_name' in info.data:
            name = info.data['project_name']
            v = re.sub(r'[\s_]+', '-', name.lower())
            v = re.sub(r'[^a-z0-9-]', '', v)
            v = v.strip('-')
            v = re.sub(r'-+', '-', v)
        return v

    @model_validator(mode='after')
    def ensure_required_agents(self):
        """Add required agents based on project type."""
        required_agents = {
            'saas-web-app': ['api-development-agent', 'frontend-ui-agent', 'database-agent'],
            'api-service': ['api-development-agent', 'database-agent'],
            'hardware-iot': ['firmware-agent', 'hardware-iot-agent'],
            'mobile-app': ['mobile-app-agent', 'api-development-agent']
        }

        if self.project_type in required_agents:
            for agent in required_agents[self.project_type]:
                if agent not in self.agents:
                    self.agents.append(agent)

        return self

    @model_validator(mode='after')
    def ensure_tech_stack_skills(self):
        """Add skills based on tech stack."""
        # Map tech stack to skills
        if self.tech_stack.backend:
            skill = self.tech_stack.backend.replace('-', '-')
            if skill not in self.skills:
                self.skills.append(skill)

        if self.tech_stack.frontend:
            skill = self.tech_stack.frontend.replace('-', '-')
            if skill not in self.skills:
                self.skills.append(skill)

        return self

# Usage
config = ProjectConfig(
    project_name="My SaaS App",
    # slug auto-generated
    project_type="saas-web-app",
    tech_stack={
        "backend": "python-fastapi",
        "frontend": "react-typescript",
        "database": "postgresql",
        "cache": "redis"
    },
    features=["authentication", "payments"]
)

print(config.project_slug)  # "my-saas-app"
print(config.agents)  # Includes required agents
print(config.skills)  # Includes tech stack skills

# Serialize
print(config.model_dump_json(indent=2))

# Save to file
Path('config.json').write_text(config.model_dump_json(indent=2))
```

## Testing with Pydantic

```python
import pytest
from pydantic import ValidationError

def test_valid_config():
    """Test valid configuration."""
    config = ProjectConfig(
        project_name="Test",
        project_slug="test",
        project_type="saas-web-app",
        tech_stack={"backend": "fastapi", "database": "postgresql"}
    )
    assert config.project_name == "Test"

def test_invalid_slug():
    """Test invalid slug raises error."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectConfig(
            project_name="Test",
            project_slug="INVALID SLUG",  # Spaces and uppercase
            project_type="saas-web-app",
            tech_stack={"backend": "fastapi", "database": "postgresql"}
        )

    errors = exc_info.value.errors()
    assert any(e['loc'] == ('project_slug',) for e in errors)

def test_auto_slug_generation():
    """Test automatic slug generation."""
    config = ProjectConfig(
        project_name="My Test Project",
        project_slug="",  # Empty, should auto-generate
        project_type="saas-web-app",
        tech_stack={"backend": "fastapi", "database": "postgresql"}
    )
    assert config.project_slug == "my-test-project"
```

## Best Practices

1. **Use Field for metadata**
```python
name: str = Field(..., min_length=1, description="User's name")
```

2. **Provide helpful error messages**
```python
@field_validator('email')
@classmethod
def validate_email(cls, v):
    if '@' not in v:
        raise ValueError(f"Invalid email: '{v}'. Must contain '@'")
    return v
```

3. **Use Literal for known values**
```python
status: Literal['draft', 'active', 'completed']  # Not just str
```

4. **Validate on assignment**
```python
model_config = ConfigDict(validate_assignment=True)
```

5. **Use default_factory for mutable defaults**
```python
tags: List[str] = Field(default_factory=list)  # NOT = []
```

## Quick Reference

**Field Types:**
- `str`, `int`, `float`, `bool`
- `List[T]`, `Dict[K, V]`, `Set[T]`
- `Optional[T]`, `Union[T1, T2]`
- `Literal['a', 'b']`
- `EmailStr`, `HttpUrl`

**Field Constraints:**
- `min_length`, `max_length` (str)
- `ge`, `gt`, `le`, `lt` (numbers)
- `pattern` (regex)
- `default`, `default_factory`

**Validators:**
- `@field_validator` - Validate single field
- `@model_validator` - Validate entire model
- `mode='before'` - Before parsing
- `mode='after'` - After parsing

**Methods:**
- `model_validate()` - Parse dict
- `model_validate_json()` - Parse JSON
- `model_dump()` - To dict
- `model_dump_json()` - To JSON
