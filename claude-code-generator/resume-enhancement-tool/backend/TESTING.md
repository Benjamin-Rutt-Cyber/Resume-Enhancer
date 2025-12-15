# Testing Guide - Resume Enhancement Tool

## Overview

This document provides comprehensive guidance on testing the Resume Enhancement Tool backend. The test suite ensures code quality, catches regressions, and validates production readiness.

## Test Infrastructure

### Technologies

- **pytest**: Test framework
- **pytest-cov**: Code coverage reporting
- **FastAPI TestClient**: API endpoint testing
- **SQLAlchemy**: In-memory SQLite for test database
- **pytest markers**: Test categorization

### Test Organization

```
backend/tests/
├── conftest.py                 # Shared fixtures and configuration
├── utils.py                     # Test utilities and data generation
├── test_document_parser.py      # Document parsing tests
├── test_workspace_service.py    # Workspace management tests
├── test_api_resumes.py          # Resume API tests
├── test_api_jobs.py             # Job API tests
├── test_api_enhancements.py     # Enhancement API tests
├── test_integration_workflow.py # End-to-end workflow tests
├── test_models.py               # Database model tests
└── fixtures/                    # Test data files
    ├── sample_resume.pdf
    ├── sample_resume.docx
    └── sample_job.txt
```

## Running Tests

### Basic Commands

```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_document_parser.py

# Run specific test class
pytest tests/test_api_resumes.py::TestResumeUpload

# Run specific test
pytest tests/test_api_resumes.py::TestResumeUpload::test_upload_resume_pdf_success
```

### Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View HTML report (opens in browser)
# Open: backend/htmlcov/index.html

# Fail if coverage below threshold (70%)
pytest --cov=app --cov-fail-under=70
```

### Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run only integration tests
pytest -m integration

# Run specific categories
pytest -m "parser or database"

# Exclude slow tests
pytest -m "not slow"
```

Available markers:
- `unit`: Unit tests (isolated component testing)
- `integration`: Integration tests (multiple components)
- `api`: API endpoint tests
- `database`: Database interaction tests
- `parser`: Document parser tests
- `workspace`: Workspace service tests
- `slow`: Long-running tests

## Test Fixtures

### Database Fixtures

**`test_db`** - In-memory SQLite database:
```python
def test_my_function(test_db):
    # test_db is a fresh database session
    # Tables are created before test, dropped after
```

**`client`** - FastAPI test client:
```python
def test_api_endpoint(client):
    response = client.get("/api/resumes")
    assert response.status_code == 200
```

### Model Fixtures

**`test_resume`** - Pre-created resume record:
```python
def test_with_resume(test_db, test_resume):
    assert test_resume.word_count >= 50
```

**`test_job`** - Pre-created job record
**`test_enhancement`** - Pre-created enhancement record

### Workspace Fixtures

**`temp_workspace`** - Temporary workspace directory:
```python
def test_file_operations(temp_workspace):
    # temp_workspace is a Path object
    # Cleaned up after test
```

**`workspace_service`** - WorkspaceService instance with temp workspace

### Sample Data Fixtures

**`sample_resume_text`** - Sample resume text (100+ words)
**`sample_pdf`** - Sample PDF file
**`sample_docx`** - Sample DOCX file
**`sample_job_description`** - Sample job description

### Parser Fixtures

**`document_parser`** - DocumentParser instance

## Writing Tests

### Test Structure

```python
import pytest
from tests.utils import create_test_pdf, SAMPLE_RESUME_VALID

class TestMyFeature:
    """Test suite for my feature."""

    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        input_data = "test data"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"

    @pytest.mark.api
    def test_api_endpoint(self, client):
        """Test API endpoint."""
        response = client.get("/api/my-endpoint")

        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

### Best Practices

1. **Use Descriptive Names**
   ```python
   # Good
   def test_upload_resume_rejects_files_over_10mb(client):

   # Bad
   def test_upload(client):
   ```

2. **Test One Thing**
   ```python
   # Good - tests one specific behavior
   def test_word_count_validation_rejects_short_resumes(client):

   # Bad - tests multiple things
   def test_resume_upload(client):  # uploads, validates, stores, etc.
   ```

3. **Use Fixtures for Setup**
   ```python
   # Good - use fixture
   def test_get_resume(client, test_resume):
       response = client.get(f"/api/resumes/{test_resume.id}")

   # Bad - manual setup in every test
   def test_get_resume(client, test_db):
       resume = Resume(...)
       test_db.add(resume)
       test_db.commit()
       ...
   ```

4. **Test Error Cases**
   ```python
   def test_upload_resume_invalid_format(client):
       """Verify that .txt files are rejected."""
       response = client.post("/api/resumes/upload", files={...})
       assert response.status_code == 400
   ```

## Test Utilities

### Creating Test Files

```python
from tests.utils import (
    create_test_pdf,
    create_test_docx,
    create_empty_pdf,
    SAMPLE_RESUME_VALID,
)

def test_with_pdf(tmp_path):
    # Create PDF with custom content
    pdf_path = create_test_pdf(
        "My custom resume content...",
        tmp_path / "resume.pdf"
    )

    # Use predefined sample
    pdf_path = create_test_pdf(
        SAMPLE_RESUME_VALID,
        tmp_path / "valid_resume.pdf"
    )
```

### Creating Database Records

```python
from tests.utils import (
    create_test_resume_in_db,
    create_test_job_in_db,
    create_test_enhancement_in_db,
)

def test_with_data(test_db):
    # Create resume
    resume = create_test_resume_in_db(
        test_db,
        filename="custom.pdf",
        word_count=200
    )

    # Create job
    job = create_test_job_in_db(
        test_db,
        title="Software Engineer",
        company="Tech Corp"
    )

    # Create enhancement
    enhancement = create_test_enhancement_in_db(
        test_db,
        resume_id=resume.id,
        job_id=job.id
    )
```

## Coverage Goals

### Target Coverage

- **Overall**: 70%+ (enforced by pytest.ini)
- **Critical Paths**: 90%+
  - `app/utils/document_parser.py`
  - `app/services/workspace_service.py`
  - `app/api/routes/`
- **Models**: 80%+
- **Configuration**: 60%+ (harder to test all edge cases)

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# Output shows:
# Name                              Stmts   Miss  Cover   Missing
# ---------------------------------------------------------------
# app/utils/document_parser.py        120      12    90%   45-47, 89-92
# app/api/routes/resumes.py           150       8    95%   12, 67-70
```

### Improving Coverage

1. **Identify uncovered lines**: Use `--cov-report=term-missing`
2. **Write targeted tests**: Focus on uncovered code paths
3. **Check for dead code**: Lines that can never be reached
4. **Test error paths**: Exception handling often uncovered

## Continuous Integration

### Pre-commit Checks

Before committing:
```bash
# Run all tests
pytest

# Check coverage
pytest --cov=app --cov-fail-under=70

# Verify no failures
echo $?  # Should be 0
```

### CI/CD Pipeline

Example GitHub Actions workflow:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**1. Import errors**
```bash
# Error: ModuleNotFoundError: No module named 'app'
# Solution: Ensure you're in backend/ directory
cd backend
pytest
```

**2. Database errors**
```bash
# Error: Table already exists
# Solution: Fixtures should clean up automatically
# If not, delete test database:
rm backend/test.db
```

**3. Fixture not found**
```bash
# Error: fixture 'test_resume' not found
# Solution: Check conftest.py is in tests/ directory
# and pytest can find it
```

**4. Tests pass locally but fail in CI**
```bash
# Common causes:
# - Missing dependencies in requirements.txt
# - Environment variable differences
# - File path issues (use Path, not string concatenation)
```

### Debug Mode

```bash
# Run with verbose output and stop on first failure
pytest -vv -x

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Full traceback
pytest --tb=long
```

## Dependencies

### Required for Testing

```txt
# Core testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0

# Test utilities (optional, graceful fallback)
reportlab>=4.0.0      # For creating test PDFs
python-docx>=1.0.0    # For creating test DOCX files
```

### Installing Test Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For better test file generation
pip install reportlab python-docx
```

## Next Steps

After setting up tests:

1. **Run full test suite**: `pytest -v`
2. **Check coverage**: `pytest --cov=app`
3. **Add more tests**: Focus on uncovered code
4. **Set up pre-commit hooks**: Auto-run tests before commit
5. **Configure CI/CD**: Automated testing on every push

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Last Updated**: December 15, 2025
**Test Coverage Target**: 70%+ (90%+ on critical paths)
**Status**: Production-ready test infrastructure
