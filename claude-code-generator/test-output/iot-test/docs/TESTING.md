# Testing Strategy

Comprehensive testing guide for IoT Test.

## Testing Philosophy

Our testing strategy follows the **Testing Pyramid**:

```
      /\
     /E2E\        10% - End-to-End Tests
    /------\
   /  Integ \     20% - Integration Tests
  /----------\
 /   Unit     \   70% - Unit Tests
/--------------\
```

## Test Types

### 1. Unit Tests (70%)

Test individual functions and components in isolation.

**Purpose:**
- Fast feedback
- Catch bugs early
- Document behavior
- Enable refactoring

**What to Test:**
- Business logic
- Utility functions
- Pure functions
- Edge cases

**Example:**
```python
def test_calculate_total():
    cart = Cart()
    cart.add_item(Item(price=10.00, quantity=2))
    cart.add_item(Item(price=5.00, quantity=1))
    assert cart.calculate_total() == 25.00
```

### 2. Integration Tests (20%)

Test interactions between components.

**Purpose:**
- Verify components work together
- Test database interactions
- Test API integrations
- Validate workflows

**What to Test:**
- Database operations
- External API calls
- File I/O
- Multi-component workflows

**Example:**
```python
def test_user_registration_flow():
    # Create user via API
    response = client.post('/api/users', json={
        'email': 'test@example.com',
        'password': 'secure123'
    })
    assert response.status_code == 201

    # Verify user in database
    user = db.query(User).filter_by(email='test@example.com').first()
    assert user is not None
    assert user.is_active
```

### 3. End-to-End Tests (10%)

Test complete user workflows.

**Purpose:**
- Validate critical user journeys
- Test system as a whole
- Catch integration issues

**What to Test:**
- Critical business flows
- User registration → login → use feature
- Payment processing
- Data pipeline end-to-end

**Example:**

## Test Coverage Goals

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Business Logic | 90%+ | High |
| API Endpoints | 85%+ | High |
| Database Models | 80%+ | Medium |
| Utilities | 90%+ | Medium |
| UI Components | 70%+ | Medium |
| Integration Flows | 60%+ | Low |

**Minimum Acceptable:** 80% overall coverage

## Running Tests

### Quick Commands

```bash
# Run all tests
/run-tests

# Run specific test file
```

### Watch Mode

```bash
```

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_workflows.py
├── e2e/
│   ├── test_user_journey.py
│   └── test_critical_flows.py
├── fixtures/
│   ├── users.json
│   └── sample_data.sql
└── conftest.py  # Shared fixtures
```

### Naming Conventions

- **Test files:** `test_*.py` or `*.test.js`
- **Test functions:** `test_<what>_<when>_<expected>`
- **Test classes:** `Test<Feature>`

**Examples:**
- `test_user_login_with_valid_credentials_succeeds`
- `test_payment_with_insufficient_funds_fails`
- `test_api_returns_404_for_nonexistent_resource`

## Writing Good Tests

### The AAA Pattern

```python
def test_feature():
    # Arrange - Setup test data
    user = User(email='test@example.com')
    cart = Cart()

    # Act - Perform action
    cart.add_item(Item(price=10.00))
    total = cart.calculate_total_for_user(user)

    # Assert - Verify result
    assert total == 10.00
```

### Test Fixtures


### Mocking


## Testing Best Practices

### 1. **Tests Should Be Fast**
- Aim for < 0.1s per unit test
- Use in-memory databases
- Mock external services
- Run tests in parallel

### 2. **Tests Should Be Independent**
- No shared state between tests
- Each test sets up its own data
- Tests can run in any order

### 3. **Tests Should Be Deterministic**
- Same input → same output
- No reliance on current time (mock it)
- No random data (use seeds)

### 4. **Tests Should Be Readable**
```python
# ❌ BAD
def test_1():
    u = User('a@b.c')
    assert u.e == 'a@b.c'

# ✅ GOOD
def test_user_email_is_stored_correctly():
    user = User(email='test@example.com')
    assert user.email == 'test@example.com'
```

### 5. **One Assertion Per Test (Generally)**
```python
# ❌ BAD - Testing too much
def test_user():
    user = create_user()
    assert user.email == 'test@example.com'
    assert user.is_active
    assert user.created_at is not None
    assert user.can_login()

# ✅ GOOD - Focused tests
def test_user_email_is_set():
    user = create_user()
    assert user.email == 'test@example.com'

def test_user_is_active_by_default():
    user = create_user()
    assert user.is_active
```

## Continuous Integration

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: /run-tests
        language: system
        pass_filenames: false
```

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          /run-tests
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Data Management

### Factories


### Test Databases

```bash
```

## Performance Testing

### Load Testing

```bash
```

### Profiling

```bash
```

## Security Testing

### Vulnerability Scanning

```bash
# Python dependencies
pip install safety
safety check

# Node dependencies
npm audit

# Container scanning
docker scan iot-test:latest
```

### Penetration Testing

- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication bypass
- Authorization flaws

**Tools:**
- OWASP ZAP
- Burp Suite
- SQLMap

## Troubleshooting Tests

### Tests Fail Randomly
- Check for race conditions
- Look for shared state
- Verify proper cleanup
- Add retry logic for flaky tests

### Tests Are Slow
- Profile test execution
- Mock external services
- Use in-memory databases
- Run tests in parallel

### Low Coverage
- Identify untested code
- Focus on critical paths first
- Set up coverage reports
- Add pre-commit coverage checks

## Test Metrics

Track these metrics:
- **Coverage:** Aim for 80%+
- **Test Count:** Growing with codebase
- **Pass Rate:** Should be 100%
- **Execution Time:** < 5 minutes total
- **Flakiness:** < 1% flaky tests

## Resources

- Testing documentation: `/docs/TESTING.md`
- Run tests: `/run-tests`
- CI/CD: `.github/workflows/test.yml`
- Coverage reports: `htmlcov/index.html`

---

**Remember:** Tests are documentation. Write them clearly!
