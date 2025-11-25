# Run Test Suite

Execute the complete pytest test suite with coverage reporting.

## Tasks to Complete

1. **Verify Test Environment**
   - Check that virtual environment is activated
   - Verify pytest and pytest-cov are installed
   - Display pytest version

2. **Run Unit Tests**
   - Execute all unit tests in `tests/unit/`
   - Use verbose mode: `pytest tests/unit/ -v`
   - Display test results with pass/fail counts

3. **Run Integration Tests**
   - Execute all integration tests in `tests/integration/`
   - Use verbose mode: `pytest tests/integration/ -v`
   - These may take longer as they test full workflows

4. **Run Full Test Suite with Coverage**
   - Execute: `pytest --cov=src --cov-report=term-missing --cov-report=html -v`
   - Generate coverage report showing:
     - Overall coverage percentage
     - Missing lines (lines not covered by tests)
     - HTML report in `htmlcov/` directory

5. **Display Coverage Summary**
   - Show coverage percentage for each module:
     - `src/cli/` - CLI commands coverage
     - `src/generator/` - Generator logic coverage
   - Highlight modules below 80% coverage threshold

6. **Run Specific Test Categories** (if requested)
   - Unit tests only: `pytest tests/unit/`
   - Integration tests only: `pytest tests/integration/`
   - Specific test file: `pytest tests/unit/test_analyzer.py`
   - Specific test function: `pytest tests/unit/test_analyzer.py::test_analyze_saas_project`
   - Tests matching pattern: `pytest -k "test_template"`

7. **Check for Test Failures**
   - If failures exist, display detailed failure information
   - Show assertion errors and tracebacks
   - Suggest running failed tests only: `pytest --lf` (last failed)
   - Suggest stepwise mode: `pytest --sw` (stop on first failure)

8. **Performance Analysis**
   - Show slowest tests: `pytest --durations=10`
   - Identify tests taking > 1 second
   - Suggest optimization opportunities

9. **Generate Test Reports**
   - Create HTML coverage report: `htmlcov/index.html`
   - Display link to open report in browser
   - Optionally generate JUnit XML for CI: `pytest --junitxml=test-results.xml`

## Example Commands

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run tests matching pattern
pytest -k "analyzer" -v

# Run last failed tests
pytest --lf -v

# Run with stepwise (stop on first failure)
pytest --sw -v

# Show slowest tests
pytest --durations=10
```

## Example Output

```
================================ test session starts ================================
platform win32 -- Python 3.11.5, pytest-7.4.3, pluggy-1.3.0
collected 45 items

tests/unit/test_analyzer.py::test_analyze_saas_project PASSED                  [  2%]
tests/unit/test_analyzer.py::test_analyze_empty_description PASSED             [  4%]
tests/unit/test_selector.py::test_select_saas_templates PASSED                 [  6%]
...

---------- coverage: platform win32, python 3.11.5 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/cli/main.py                      45      2    96%   78-79
src/generator/analyzer.py            67      0   100%
src/generator/selector.py            54      3    94%   45, 67, 89
src/generator/renderer.py            82      5    94%   123-127
---------------------------------------------------------------
TOTAL                               248      10   96%

HTML coverage report: htmlcov/index.html

================================ 45 passed in 2.34s ================================

✅ All tests passed!
✅ Coverage: 96%
✅ HTML report generated

🎯 Coverage above 80% threshold
```

## Notes

- Always run tests before committing code
- Aim for 80%+ code coverage
- Integration tests may require ANTHROPIC_API_KEY
- Use markers to skip slow tests: `pytest -m "not slow"`
- Configure pytest options in `pytest.ini`
