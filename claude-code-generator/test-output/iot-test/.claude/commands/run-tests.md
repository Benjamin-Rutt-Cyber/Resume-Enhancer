# Run Tests

Execute the test suite for IoT Test to ensure code quality and correctness.

## Quick Test Commands

### Backend Tests



## Comprehensive Test Suite

### Run All Tests

```bash
# Return to project root
cd ..
```

### Run with Coverage

```bash

# View coverage reports
# Backend: open backend/htmlcov/index.html
# Frontend: open frontend/coverage/lcov-report/index.html
```

## Test Types

### Unit Tests
Test individual functions and components in isolation.


### Integration Tests
Test interactions between components and external services.


### End-to-End Tests
Test complete user workflows through the application.


## Continuous Integration

### Pre-commit Tests
Run before committing code:

```bash
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


### Frontend Test Config


## Debugging Failed Tests

### View Detailed Output

```bash
```

### Common Test Failures

**Import errors:**

**Database errors:**

**Timeout errors:**
- Increase timeout in test config
- Check for async/await issues
- Look for hanging promises or connections

## Test Data Management


### Mock External Services

```bash
# Use mock server for external APIs
# Mock payment gateway responses
# Mock email service
```

## Performance Testing


## Test Reports

### Generate HTML Report

```bash
```

### View Coverage

```bash
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


### Flaky Tests

- Identify timing dependencies
- Add proper waits/retries
- Check for shared state
- Run test 100 times: `npm test -- --repeat=100`
## Next Steps

After running tests:
- Fix any failing tests immediately
- Review coverage reports for gaps
- Add tests for new features
- Update CI/CD pipeline if needed
- Run `/deploy` once all tests pass

Tests are passing for IoT Test! 🎉
