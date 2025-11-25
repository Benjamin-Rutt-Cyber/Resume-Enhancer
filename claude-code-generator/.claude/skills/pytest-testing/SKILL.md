---
name: pytest-testing
description: Expert knowledge in writing tests with pytest, including test structure, fixtures, parametrization, mocking, async tests, coverage, and best practices. Use this skill when writing unit tests, integration tests, creating test fixtures, implementing test coverage, mocking dependencies, or debugging test failures.
allowed-tools: [Read, Write, Bash]
---

# Pytest Testing Skill

Comprehensive knowledge for writing robust, maintainable tests with pytest.

## Basic Test Structure

### Simple Tests

```python
# test_calculator.py
def add(a, b):
    return a + b

def test_add():
    """Test addition function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_add_negative():
    """Test with negative numbers."""
    assert add(-5, -3) == -8
```

### Test Classes

```python
class TestCalculator:
    """Group related tests in a class."""

    def test_add(self):
        assert add(2, 3) == 5

    def test_subtract(self):
        assert subtract(5, 3) == 2

    def test_multiply(self):
        assert multiply(3, 4) == 12
```

## Fixtures

### Basic Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    """Test using fixture."""
    assert sum(sample_data) == 15

def test_length(sample_data):
    """Another test using same fixture."""
    assert len(sample_data) == 5
```

### Setup/Teardown Fixtures

```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file for testing."""
    # Setup
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    yield file_path  # Provide to test

    # Teardown (runs after test)
    if file_path.exists():
        file_path.unlink()

def test_file_content(temp_file):
    content = temp_file.read_text()
    assert content == "test content"
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: New for each test
def function_fixture():
    return create_resource()

@pytest.fixture(scope="class")  # Shared across class
def class_fixture():
    return create_resource()

@pytest.fixture(scope="module")  # Shared across module
def module_fixture():
    return create_expensive_resource()

@pytest.fixture(scope="session")  # Shared across entire test session
def session_fixture():
    return create_database_connection()
```

### Fixture Dependencies

```python
@pytest.fixture
def database():
    """Database connection."""
    db = connect_to_db()
    yield db
    db.close()

@pytest.fixture
def user(database):
    """Create test user (depends on database fixture)."""
    user = database.create_user("test@example.com")
    yield user
    database.delete_user(user.id)

def test_user_creation(user):
    """Test with dependent fixtures."""
    assert user.email == "test@example.com"
```

## Parametrization

### Basic Parametrization

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input, expected):
    """Test square function with multiple inputs."""
    assert square(input) == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 3, 8),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

### Parametrizing Fixtures

```python
@pytest.fixture(params=['postgresql', 'mysql', 'sqlite'])
def database(request):
    """Test with multiple database backends."""
    db = connect_to_database(request.param)
    yield db
    db.close()

def test_query(database):
    """This test runs 3 times with different databases."""
    result = database.query("SELECT 1")
    assert result
```

## Mocking

### Basic Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mock object."""
    mock_api = Mock()
    mock_api.get_data.return_value = {"status": "success"}

    result = process_data(mock_api)

    assert result == {"status": "success"}
    mock_api.get_data.assert_called_once()
```

### Patching Functions

```python
@patch('module.expensive_function')
def test_with_patch(mock_expensive):
    """Test with patched function."""
    mock_expensive.return_value = "mocked result"

    result = call_expensive_function()

    assert result == "mocked result"
    mock_expensive.assert_called()
```

### Patching Classes

```python
@patch('module.APIClient')
def test_api_integration(mock_client_class):
    """Test with mocked class."""
    # Configure mock
    mock_instance = Mock()
    mock_instance.fetch.return_value = {"data": "test"}
    mock_client_class.return_value = mock_instance

    # Test
    client = APIClient()
    result = client.fetch()

    assert result == {"data": "test"}
```

### Mock Responses

```python
def test_api_call():
    """Test with mock API responses."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    with patch('requests.get', return_value=mock_response):
        response = make_api_call()
        assert response['result'] == "success"
```

## Async Tests

### Basic Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_add(2, 3)
    assert result == 5
```

### Async Fixtures

```python
@pytest.fixture
async def async_client():
    """Async fixture."""
    client = AsyncClient()
    await client.connect()
    yield client
    await client.disconnect()

@pytest.mark.asyncio
async def test_async_api(async_client):
    result = await async_client.fetch_data()
    assert result
```

## Test Organization

### conftest.py

```python
# tests/conftest.py - Shared fixtures
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_config():
    """Sample configuration."""
    return {
        'name': 'test',
        'value': 42
    }

@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    # Runs automatically before each test
    clear_cache()
    yield
    # Cleanup after test
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_analyzer.py
│   ├── test_renderer.py
│   └── test_utils.py
├── integration/          # Integration tests
│   ├── test_full_flow.py
│   └── test_api_integration.py
└── fixtures/             # Test data
    ├── sample_data.py
    └── mock_responses.py
```

## Assertions

### Basic Assertions

```python
def test_assertions():
    # Equality
    assert value == expected
    assert value != other

    # Truthiness
    assert is_true
    assert not is_false

    # Membership
    assert item in collection
    assert item not in collection

    # Type checking
    assert isinstance(obj, MyClass)

    # Exceptions
    with pytest.raises(ValueError):
        raise ValueError("error")

    with pytest.raises(ValueError, match="specific message"):
        raise ValueError("specific message here")
```

### Custom Assertions

```python
def assert_valid_config(config):
    """Custom assertion for config validation."""
    assert 'name' in config, "Config must have 'name'"
    assert config['name'], "Name cannot be empty"
    assert 'type' in config, "Config must have 'type'"

def test_config():
    config = {'name': 'test', 'type': 'saas'}
    assert_valid_config(config)
```

## Markers

### Built-in Markers

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_feature():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_known_issue():
    assert False  # Expected to fail

@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)
```

### Custom Markers

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests

# Usage
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

# Run specific markers
# pytest -m unit
# pytest -m "not slow"
```

## Coverage

### Running with Coverage

```bash
# Install
pip install pytest-cov

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html

# Fail if below threshold
pytest --cov=src --cov-fail-under=80
```

### Configuration

```ini
# pytest.ini
[pytest]
addopts =
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

## Testing Patterns

### AAA Pattern

```python
def test_user_creation():
    # Arrange - Set up test data
    user_data = {
        'name': 'John',
        'email': 'john@example.com'
    }

    # Act - Perform the action
    user = create_user(user_data)

    # Assert - Verify the result
    assert user.name == 'John'
    assert user.email == 'john@example.com'
```

### Test Isolation

```python
# Good: Each test is independent
def test_add_user():
    user = create_user("test@example.com")
    assert user_exists(user.id)

def test_delete_user():
    user = create_user("test@example.com")  # Create fresh data
    delete_user(user.id)
    assert not user_exists(user.id)

# Bad: Tests depend on each other
shared_user = None

def test_create():
    global shared_user
    shared_user = create_user("test@example.com")

def test_delete():
    # Depends on test_create running first!
    delete_user(shared_user.id)
```

## Real-World Example

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_claude_client():
    """Mock Claude API client."""
    from unittest.mock import Mock
    import json

    client = Mock()
    client.create_message.return_value = json.dumps({
        'project_name': 'Test Project',
        'project_type': 'saas-web-app',
        'tech_stack': {'backend': 'python-fastapi'},
        'features': [],
        'agents': [],
        'skills': []
    })
    return client

# tests/unit/test_analyzer.py
import pytest
from src.generator.analyzer import ProjectAnalyzer

class TestProjectAnalyzer:
    """Test project analyzer."""

    def test_analyze_saas_project(self, mock_claude_client):
        """Should analyze SaaS project correctly."""
        analyzer = ProjectAnalyzer(mock_claude_client)

        config = analyzer.analyze("Build a SaaS platform")

        assert config.project_type == 'saas-web-app'
        assert mock_claude_client.create_message.called

    def test_analyze_with_empty_description(self, mock_claude_client):
        """Should raise error for empty description."""
        analyzer = ProjectAnalyzer(mock_claude_client)

        with pytest.raises(ValueError, match="Description cannot be empty"):
            analyzer.analyze("")

    @pytest.mark.parametrize("description,expected_type", [
        ("Build a REST API", "api-service"),
        ("Create mobile app", "mobile-app"),
        ("IoT sensor device", "hardware-iot"),
    ])
    def test_analyze_different_types(
        self, mock_claude_client, description, expected_type
    ):
        """Should identify different project types."""
        mock_claude_client.create_message.return_value = json.dumps({
            'project_type': expected_type,
            # ... other fields
        })

        analyzer = ProjectAnalyzer(mock_claude_client)
        config = analyzer.analyze(description)

        assert config.project_type == expected_type

# tests/integration/test_full_generation.py
def test_full_project_generation(temp_dir):
    """Test complete project generation."""
    from src.generator.main import Generator

    generator = Generator()
    config = {
        'project_name': 'Test Project',
        'project_slug': 'test-project',
        'project_type': 'saas-web-app',
        'tech_stack': {'backend': 'python-fastapi'},
        'agents': ['api-development-agent'],
        'skills': ['python-fastapi']
    }

    output_path = temp_dir / 'test-project'
    generator.generate(config, output_path)

    # Verify structure
    assert (output_path / '.claude').exists()
    assert (output_path / '.claude' / 'agents').exists()
    assert (output_path / 'README.md').exists()

    # Verify content
    agent_file = output_path / '.claude' / 'agents' / 'api-development-agent.md'
    assert agent_file.exists()
    content = agent_file.read_text()
    assert 'name: test-project-api-agent' in content
```

## Best Practices

1. **One assertion per test (when possible)**
```python
# Good
def test_name():
    assert user.name == "John"

def test_email():
    assert user.email == "john@example.com"

# Acceptable for related assertions
def test_user_properties():
    assert user.name == "John"
    assert user.email == "john@example.com"
```

2. **Clear test names**
```python
# Good
def test_analyzer_raises_error_with_empty_description():
    pass

# Bad
def test_analyzer():
    pass
```

3. **Use fixtures for setup**
```python
# Good
@pytest.fixture
def user():
    return create_user()

def test_user(user):
    assert user.name

# Bad
def test_user():
    user = create_user()  # Setup in test
    assert user.name
```

4. **Test edge cases**
```python
def test_add():
    assert add(2, 3) == 5      # Normal case
    assert add(0, 0) == 0      # Edge: zeros
    assert add(-1, 1) == 0     # Edge: negatives
    assert add(1000, 2000) == 3000  # Edge: large numbers
```

5. **Mock external dependencies**
```python
@patch('requests.get')
def test_api_call(mock_get):
    # Don't make real API calls in tests
    mock_get.return_value.json.return_value = {'result': 'success'}
    result = fetch_data()
    assert result['result'] == 'success'
```

## Quick Reference

**Run tests:**
```bash
pytest                  # All tests
pytest test_file.py    # Specific file
pytest -k test_name    # Match by name
pytest -m marker       # By marker
pytest -v              # Verbose
pytest -x              # Stop on first failure
pytest --lf            # Last failed
pytest --sw            # Stepwise
```

**Fixtures:**
```python
@pytest.fixture(scope="function|class|module|session")
def my_fixture():
    # setup
    yield value
    # teardown
```

**Markers:**
```python
@pytest.mark.skip
@pytest.mark.skipif(condition)
@pytest.mark.xfail
@pytest.mark.parametrize
```

**Assertions:**
```python
assert condition
pytest.raises(Exception)
pytest.warns(Warning)
pytest.approx(value, rel=0.01)
```
