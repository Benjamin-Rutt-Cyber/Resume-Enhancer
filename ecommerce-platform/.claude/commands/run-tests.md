# Run Tests

Execute the test suite for E-Commerce Platform to ensure code quality and correctness.

## Quick Test Commands

### Backend Tests

```bash
# Run all tests with pytest
cd backend
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py

# Run tests matching pattern
pytest -k "test_auth"

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Frontend Tests

```bash
# Run frontend tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run E2E tests (if configured)
npm run test:e2e
```


## Comprehensive Test Suite

### Run All Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd ../frontend
npm test -- --watchAll=false

# Return to project root
cd ..
```

### Run with Coverage

```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing

# Frontend coverage
cd frontend
npm test -- --coverage --watchAll=false
cd ..

# View coverage reports
# Backend: open backend/htmlcov/index.html
# Frontend: open frontend/coverage/lcov-report/index.html
```

## Test Types

### Unit Tests
Test individual functions and components in isolation.

```bash
# Run unit tests only
pytest tests/unit/
```

### Integration Tests
Test interactions between components and external services.

```bash
# Run integration tests
pytest tests/integration/
```

### End-to-End Tests
Test complete user workflows through the application.

```bash
# Run E2E tests with Cypress/Playwright
cd frontend
npm run test:e2e

# Run E2E in headed mode
npm run test:e2e:headed
```

## Continuous Integration

### Pre-commit Tests
Run before committing code:

```bash
# Quick backend tests
cd backend
pytest tests/unit/ -x

# Lint code
black . --check
flake8 .

# Quick frontend tests
cd frontend
npm run lint
npm test -- --watchAll=false --bail

```

### Full CI Pipeline
What runs in CI/CD:

```bash
# Install dependencies
# Run linters
# Run all tests with coverage
# Check coverage thresholds
# Build application
# Run security scans
```

## Test Configuration

### Backend Test Config

**File:** `backend/pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

**File:** `backend/.coveragerc`
```ini
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Frontend Test Config

**File:** `frontend/jest.config.js`
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

## Debugging Failed Tests

### View Detailed Output

```bash
# Verbose pytest output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

### Common Test Failures

**Import errors:**
- Ensure virtual environment is activated
- Check PYTHONPATH includes project root
- Reinstall dependencies: `pip install -r requirements.txt`

**Database errors:**
- Ensure test database is created
- Check database connection in test config
- Run migrations: `/db-migrate`

**Timeout errors:**
- Increase timeout in test config
- Check for async/await issues
- Look for hanging promises or connections

## Test Data Management

### Database Test Fixtures

```python
# conftest.py
import pytest
from app.database import init_db

@pytest.fixture
def db_session():
    """Provide clean database for each test."""
    init_db()
    yield
    # Cleanup after test
```

### Mock External Services

```bash
# Use mock server for external APIs
# Mock payment gateway responses
# Mock email service
```

## Performance Testing

```bash
# Load testing with locust
cd backend
locust -f tests/load/locustfile.py

```

## Test Reports

### Generate HTML Report

```bash
# Generate pytest HTML report
pytest --html=report.html --self-contained-html

```

### View Coverage

```bash
# Terminal coverage report
pytest --cov=app --cov-report=term-missing

# HTML coverage report
pytest --cov=app --cov-report=html
# Open: htmlcov/index.html

```

## Best Practices

1. **Write Tests First (TDD)**
   - Define expected behavior
   - Write failing test
   - Implement feature
   - Verify test passes

2. **Keep Tests Fast**
   - Mock external services
   - Use in-memory databases for unit tests
   - Parallelize test execution

3. **Test Coverage Goals**
   - Aim for 80%+ coverage
   - Focus on critical paths
   - Don't obsess over 100%

4. **Isolate Tests**
   - Each test should be independent
   - Use fixtures/factories for setup
   - Clean up after each test

5. **Descriptive Test Names**
   - test_user_login_with_valid_credentials
   - test_api_returns_404_for_missing_resource
   - test_payment_fails_with_invalid_card

## Troubleshooting

### Tests Pass Locally but Fail in CI

- Check environment variables
- Verify dependency versions match
- Look for timing/race conditions
- Check for file system differences

### Slow Test Suite

```bash
# Profile slow tests
pytest --durations=10

# Run tests in parallel
pytest -n auto  # requires pytest-xdist
```

### Flaky Tests

- Identify timing dependencies
- Add proper waits/retries
- Check for shared state
- Run test 100 times: `pytest --count=100`
## Next Steps

After running tests:
- Fix any failing tests immediately
- Review coverage reports for gaps
- Add tests for new features
- Update CI/CD pipeline if needed
- Run `/deploy` once all tests pass

Tests are passing for E-Commerce Platform! 🎉
