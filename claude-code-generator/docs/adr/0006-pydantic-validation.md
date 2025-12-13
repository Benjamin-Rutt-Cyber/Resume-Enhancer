---
adr: 0006
title: Use Pydantic for Configuration Validation
date: 2025-11-26
status: Accepted
---

# ADR-0006: Use Pydantic for Configuration Validation

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

The Claude Code Generator processes project configuration dictionaries extracted from either:
- Claude API analysis (AI-generated structured data)
- Keyword-based analysis (regex-extracted data)
- User CLI inputs (interactive or command-line arguments)

This configuration needs validation to ensure:
- **Type safety**: project_name is a string, has_auth is a boolean, etc.
- **Constraints**: project_name is 3-50 chars, project_slug matches pattern `^[a-z0-9-]+$`
- **Required fields**: project_name, project_type, description must be present
- **Optional fields**: backend_framework, database, platform can be None
- **Auto-generation**: project_slug auto-generated from project_name if not provided
- **Consistency**: Both AI and keyword analysis produce the same structure

Without validation:
- Runtime errors from missing or incorrect types
- Security issues from malformed input
- Confusing errors when templates fail to render
- No single source of truth for config structure

The question: **How should we validate and type-check configuration data?**

## Decision

We will use **Pydantic** for declarative configuration validation with the `ProjectConfig` model.

**Implementation** (`src/generator/analyzer.py:25-58`):
```python
from pydantic import BaseModel, Field, field_validator, ValidationInfo

class ProjectConfig(BaseModel):
    """Validated project configuration."""

    project_name: str = Field(..., min_length=3, max_length=50)
    project_slug: str = Field(..., pattern=r'^[a-z0-9-]+$')
    project_type: str = Field(..., pattern=r'^[a-z-]+$')
    description: str = Field(..., min_length=10)
    backend_framework: Optional[str] = None
    frontend_framework: Optional[str] = None
    # ... other fields
    has_auth: bool = False
    has_api: bool = True

    @field_validator('project_slug', mode='before')
    @classmethod
    def generate_slug(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Generate slug from project name if not provided."""
        if v is None and 'project_name' in info.data:
            # Auto-generate from project_name
            # ...
        return v
```

**Usage**:
```python
# Both AI and keyword analysis return dict
config_dict = self._analyze_with_claude(description, project_name)
# Pydantic validates and converts to ProjectConfig
return ProjectConfig(**config_dict)
```

## Consequences

**Positive:**
- **Type safety**: IDE autocompletion and type checking with mypy/pyright
- **Declarative validation**: Constraints defined once in the model, not scattered in code
- **Clear error messages**: Pydantic provides detailed validation errors with field names
- **Auto-conversion**: Strings → booleans, integers, enums automatically
- **Field validators**: Custom logic for computed fields (slug generation)
- **Single source of truth**: ProjectConfig defines the complete contract
- **JSON Schema**: Can auto-generate JSON schema for documentation/tooling
- **Immutable by default**: Config objects are frozen after creation (with ConfigDict)
- **Ecosystem**: Works with FastAPI, SQLAlchemy, and other modern Python tools

**Negative:**
- **Dependency**: Adds pydantic as a required dependency (~1MB)
- **Learning curve**: Contributors need to learn Pydantic syntax
- **Validation overhead**: Small performance cost (negligible for our use case)
- **Migration pain**: Changing field names/types requires coordinated updates

**Neutral:**
- **V2 syntax**: Using Pydantic V2 (Field, field_validator) not V1 (validator)

## Alternatives Considered

### dataclasses (Standard Library)
- **Pros**:
  - Built into Python 3.7+, no dependency
  - Simple, Pythonic syntax
  - Type hints for IDE support
  - Works with type checkers
- **Cons**:
  - **No validation**: Type hints are not enforced at runtime
  - **No constraints**: Can't express min_length, pattern, etc.
  - **No auto-conversion**: "true" string stays string, not converted to bool
  - **No custom validators**: Would need to write manual validation code
  - **No error messages**: Would need to write error handling manually
- **Why rejected**: Type hints alone don't prevent runtime errors. We need actual validation.

### attrs
- **Pros**:
  - More powerful than dataclasses
  - Has validators and converters
  - Less heavy than Pydantic
  - Good performance
- **Cons**:
  - Less popular than Pydantic (smaller community)
  - No built-in JSON schema generation
  - Validators are less intuitive than Pydantic
  - No built-in pattern matching (would need custom regex validators)
  - Less integration with modern web frameworks
- **Why rejected**: Pydantic is more popular, better documented, and has richer features for our use case.

### marshmallow
- **Pros**:
  - Mature library (10+ years old)
  - Powerful serialization/deserialization
  - Good for API validation
- **Cons**:
  - Separate Schema class (not a model)
  - More verbose than Pydantic
  - Less modern API
  - Primarily designed for serialization, not models
  - Less integration with type checkers
- **Why rejected**: Pydantic provides better developer experience and is the modern standard for Python validation.

### Manual Validation
- **Implementation**:
  ```python
  def validate_config(config_dict: dict) -> dict:
      if 'project_name' not in config_dict:
          raise ValueError("project_name is required")
      if len(config_dict['project_name']) < 3:
          raise ValueError("project_name must be at least 3 characters")
      # ... 50 more lines of validation logic
  ```
- **Pros**:
  - No dependencies
  - Full control
  - Simple to understand
- **Cons**:
  - **Extremely verbose**: 100+ lines of boilerplate
  - **Error-prone**: Easy to forget validations
  - **No type safety**: dict[str, Any] provides no IDE help
  - **Hard to maintain**: Adding a field requires updating multiple places
  - **Poor error messages**: Would need to manually format errors
- **Why rejected**: Way too much boilerplate and maintenance burden. Pydantic provides all this for free.

## References

- **File(s)**:
  - `src/generator/analyzer.py:25-58` - ProjectConfig model definition
  - `src/generator/analyzer.py:77-102` - Validation usage in analysis
- **Related ADRs**:
  - ADR-0003 (Dual-Mode Analysis) - Both modes produce ProjectConfig
- **External Links**:
  - [Pydantic Documentation](https://docs.pydantic.dev/)
  - [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)

## Notes

**Key Pydantic Features Used**:
- `Field(...)`: Required fields with validation constraints
- `Field(..., min_length=3, max_length=50)`: String length constraints
- `Field(..., pattern=r'^[a-z0-9-]+$')`: Regex pattern matching
- `Optional[str] = None`: Optional fields with defaults
- `bool = False`: Boolean fields with default values
- `@field_validator`: Custom validators for computed fields
- `ValidationInfo`: Access to other fields during validation

**Validation Workflow**:
1. Analyzer creates config_dict (from AI or keywords)
2. `ProjectConfig(**config_dict)` triggers validation
3. Pydantic checks types, constraints, and runs custom validators
4. If invalid: raises ValidationError with detailed field-level errors
5. If valid: returns ProjectConfig instance with type-safe attributes

**Auto-Generation Example**:
```python
# Input: {"project_name": "My Cool App"}
# Output: ProjectConfig(
#   project_name="My Cool App",
#   project_slug="my-cool-app",  ← auto-generated!
# )
```

**Future Enhancements**:
- Could use Pydantic's `model_config` for strict mode (no extra fields)
- Could generate JSON schema for documentation
- Could use Pydantic for YAML config validation (project types, templates)
