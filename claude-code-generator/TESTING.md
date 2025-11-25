# Testing Documentation

## Overview

This document describes the comprehensive test suite for the Claude Code Generator project, covering all core components with 95% overall coverage.

## Quick Summary

**Test Suite Status:** ✅ 238 tests passing | 95% coverage | 16.01s runtime

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| **CLI** | **29** | **99%** | ⭐⭐⭐ Perfect |
| **ProjectAnalyzer** | **64** | **100%** | ⭐⭐⭐ Perfect |
| **TemplateRenderer** | 65 | 100% | ⭐⭐⭐ Perfect |
| **PluginAnalyzer** | 33 | 95% | ⭐⭐ Excellent |
| **FileGenerator** | 34 | 90% | ⭐ Excellent |
| **TemplateSelector** | 13 | 87% | ⭐ Very Good |
| **Overall** | **238** | **95%** | ⭐⭐⭐ Excellent |

## Test Structure

```
tests/
├── unit/
│   ├── test_analyzer.py            # 64 tests, 100% coverage (Sprint 4) ⭐
│   ├── test_cli.py                  # 29 tests, 99% coverage (Sprint 4) ⭐
│   ├── test_file_generator.py     # 34 tests, 90% coverage (Sprint 2)
│   ├── test_plugin_analyzer.py    # 33 tests, 95% coverage (Sprint 3)
│   ├── test_renderer.py            # 65 tests, 100% coverage (Sprint 3)
│   └── test_selector.py            # 13 tests, 87% coverage (Week 3)
└── integration/
    └── test_validation.py          # End-to-end validation tests
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_file_generator.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test Class

```bash
pytest tests/unit/test_file_generator.py::TestGenerateProject
```

### Run Specific Test

```bash
pytest tests/unit/test_file_generator.py::TestGenerateProject::test_generate_project_success
```

## FileGenerator Test Suite

**Location:** `tests/unit/test_file_generator.py`
**Tests:** 34 tests
**Coverage:** 90% of file_generator.py
**Status:** ✅ All passing

### Test Categories

#### 1. Project Generation Orchestration (6 tests)

Tests the main `generate_project()` method that coordinates the entire project generation process.

**Coverage:**
- ✅ Successful project generation
- ✅ Directory exists with overwrite=False (raises FileExistsError)
- ✅ Directory exists with overwrite=True (succeeds)
- ✅ Empty directory with overwrite=False (allowed)
- ✅ Project generation without plugins
- ✅ Directory structure creation

**Key Tests:**
- `test_generate_project_success`: Verifies complete project generation
- `test_generate_project_directory_exists_no_overwrite`: Tests error handling
- `test_generate_project_creates_directory_structure`: Validates Python package setup

#### 2. Agent Generation (3 tests)

Tests the `_generate_agent()` method that creates agent files.

**Coverage:**
- ✅ Reusable agents (copy as-is, no .j2 extension)
- ✅ Template agents (render .j2 files)
- ✅ Directory creation

**Key Tests:**
- `test_generate_reusable_agent`: Verifies direct file copying
- `test_generate_template_agent`: Validates Jinja2 template rendering
- `test_generate_agent_creates_directory`: Ensures `.claude/agents/` is created

#### 3. Skill Generation (3 tests)

Tests the `_generate_skill()` method that creates skill directories.

**Coverage:**
- ✅ Library skills (copy as-is)
- ✅ Additional file copying
- ✅ Duplicate file prevention

**Key Tests:**
- `test_generate_library_skill`: Verifies skill directory creation
- `test_generate_library_skill_copies_additional_files`: Tests helper file copying
- `test_generate_skill_skips_skill_md_files`: Prevents SKILL.md duplication

#### 4. Command Generation (3 tests)

Tests the `_generate_command()` method that creates command files.

**Coverage:**
- ✅ Command template rendering
- ✅ Extension removal (.j2 → .md)
- ✅ Directory creation

**Key Tests:**
- `test_generate_command`: Validates template rendering
- `test_generate_command_removes_j2_extension`: Ensures proper file naming
- `test_generate_command_creates_directory`: Verifies `.claude/commands/` creation

#### 5. Documentation Generation (5 tests)

Tests the `_generate_doc()` method that creates documentation files.

**Coverage:**
- ✅ Template docs (render .j2)
- ✅ Library docs (copy as-is)
- ✅ Library README skipping
- ✅ Missing library doc handling
- ✅ Missing template handling

**Key Tests:**
- `test_generate_template_doc`: Validates Jinja2 rendering
- `test_generate_library_doc`: Tests direct file copying
- `test_generate_doc_handles_missing_library_doc`: Graceful error handling

#### 6. README Generation (3 tests)

Tests the `_generate_readme()` method that creates project READMEs.

**Coverage:**
- ✅ Library template usage
- ✅ Fallback to basic template
- ✅ Feature inclusion

**Key Tests:**
- `test_generate_readme_with_library_template`: Uses project-type-specific READMEs
- `test_generate_readme_fallback_to_basic`: Tests fallback logic
- `test_generate_basic_readme_includes_features`: Validates feature listing

#### 7. Gitignore Generation (2 tests)

Tests the `_generate_gitignore()` method that creates `.gitignore` files.

**Coverage:**
- ✅ File creation
- ✅ Comprehensive pattern coverage (Python, Node, IDE, env, DB, build, test, OS)

**Key Tests:**
- `test_generate_gitignore`: Validates basic patterns
- `test_generate_gitignore_comprehensive_coverage`: Ensures all categories covered

#### 8. Plugin Configuration (2 tests)

Tests the `_generate_plugin_config()` method that creates plugin recommendations.

**Coverage:**
- ✅ Plugin config generation with mocked analyzer
- ✅ Directory creation

**Key Tests:**
- `test_generate_plugin_config`: Validates YAML generation
- `test_generate_plugin_config_creates_claude_directory`: Ensures `.claude/` exists

#### 9. Directory Structure (3 tests)

Tests the `_create_directory_structure()` method that sets up project directories.

**Coverage:**
- ✅ Basic directory creation
- ✅ `__init__.py` file creation for Python projects
- ✅ No duplicate `__init__.py` files

**Key Tests:**
- `test_create_directory_structure_basic`: Validates directory creation
- `test_create_directory_structure_creates_init_files_for_python`: Tests Python package setup
- `test_create_directory_structure_no_duplicate_init_files`: Prevents overwrites

#### 10. Error Handling & Edge Cases (4 tests)

Tests error scenarios and edge cases.

**Coverage:**
- ✅ FileExistsError with non-empty directory
- ✅ Special characters in project names (Unicode)
- ✅ Empty features list
- ✅ Path normalization (string vs Path objects)

**Key Tests:**
- `test_file_exists_error_with_non_empty_directory`: Validates error raising
- `test_handles_special_characters_in_project_name`: Unicode support
- `test_path_normalization`: Path object handling

## Test Fixtures

### Temporary Directories

- `temp_output_dir`: Clean temporary directory for each test
- `templates_dir`: Path to actual templates directory
- `mock_templates_dir`: Isolated mock templates for unit tests

### Configuration

- `sample_config`: Standard ProjectConfig for testing
- `file_generator`: FileGenerator instance with mock templates

### Mock Templates

The `mock_templates_dir` fixture creates a complete mock template structure:

```
templates/
├── agents/
│   ├── library/
│   │   └── testing-agent.md
│   └── testing-template-agent.md.j2
├── skills/
│   └── library/
│       └── python-fastapi/
│           ├── SKILL.md
│           └── helper.py
├── commands/
│   ├── run-tests.md.j2
│   └── deploy.md.j2
├── docs/
│   ├── library/
│   │   ├── README-saas-web-app.md
│   │   └── TESTING.md
│   └── API.md.j2
└── project-types/
    └── saas-web-app.yaml
```

## Coverage Report

### Overall Coverage: 41%

```
Name                               Stmts   Miss  Cover
----------------------------------------------------------------
src\generator\file_generator.py      166     17    90%
src\generator\selector.py            115     52    55%
src\generator\renderer.py             53     23    57%
src\generator\analyzer.py            129     89    31%
src\generator\plugin_analyzer.py     140    108    23%
src\cli\main.py                      171    171     0%
```

### FileGenerator Coverage: 90%

**Covered:**
- ✅ Project generation orchestration
- ✅ Agent file generation (reusable and template)
- ✅ Skill directory generation
- ✅ Command file generation
- ✅ Documentation generation
- ✅ README generation (library and fallback)
- ✅ Gitignore generation
- ✅ Plugin configuration generation
- ✅ Directory structure creation
- ✅ Error handling (FileExistsError)

**Not Covered (10%):**
- Lines 87-88, 92-93, 97-98, 102-103: Empty template lists (edge case)
- Lines 115-118: Plugin generation branch (tested via mocking)
- Lines 173-177: Template skill rendering (rare edge case)
- Lines 193, 201-202: Skill directory iteration edge cases
- Line 320: Backend framework check (rare conditional)

## Test Principles

### 1. Isolation

Each test is isolated with:
- Temporary directories (cleaned up after each test)
- Mock templates (no dependency on actual template files)
- Independent fixtures

### 2. Clarity

Tests are:
- Named descriptively (`test_<what>_<scenario>`)
- Organized into logical test classes
- Documented with docstrings

### 3. Coverage

Tests cover:
- **Happy paths**: Normal successful operations
- **Error paths**: Expected failures and exceptions
- **Edge cases**: Empty lists, special characters, missing files
- **Integration**: End-to-end workflows

### 4. Maintainability

Tests are:
- DRY (Don't Repeat Yourself) with shared fixtures
- Easy to understand and modify
- Fast (all 34 tests run in ~3 seconds)

## Adding New Tests

### Template for New Test

```python
def test_new_feature(self, file_generator, temp_output_dir):
    """Test description of what this validates."""
    # Setup
    context = {'project_name': 'Test Project'}

    # Execute
    result = file_generator.some_method(context, temp_output_dir)

    # Verify
    assert result.exists()
    assert result.name == 'expected_name'
    content = result.read_text()
    assert 'expected_content' in content
```

### Fixture Usage

```python
# Use file_generator for FileGenerator instance
def test_something(self, file_generator):
    generator = file_generator  # Already initialized

# Use temp_output_dir for temporary directory
def test_file_creation(self, temp_output_dir):
    file_path = temp_output_dir / 'test.txt'
    file_path.write_text('content')
    assert file_path.exists()

# Use sample_config for ProjectConfig
def test_with_config(self, sample_config):
    assert sample_config.project_type == 'saas-web-app'
```

## Continuous Integration

### Pre-commit Checks

Before committing, run:

```bash
# Run all tests
pytest

# Check coverage
pytest --cov=src --cov-report=term-missing

# Lint code
ruff check src tests

# Format code
black src tests
```

### CI Pipeline (Recommended)

```yaml
# .github/workflows/test.yml
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
          python-version: 3.11
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail with "Module not found"

```bash
# Install package in editable mode
pip install -e ".[dev]"
```

### Tests Fail with "Template not found"

- Verify `mock_templates_dir` fixture includes the template
- Check template path in test (should be relative to templates/)

### Coverage Report Not Generated

```bash
# Install coverage dependencies
pip install pytest-cov

# Run with coverage flags
pytest --cov=src --cov-report=html
```

### Tests Run Slowly

- Check for tests not using fixtures properly
- Ensure temporary directories are being cleaned up
- Use `pytest -v` to identify slow tests

## Future Testing Improvements

### Potential Additions

1. **Integration Tests**
   - End-to-end project generation with real templates
   - Template validation tests
   - CLI integration tests

2. **Performance Tests**
   - Large project generation benchmarks
   - Template rendering performance
   - File I/O optimization tests

3. **Parameterized Tests**
   - Test multiple project types in one test
   - Test various framework combinations
   - Test different feature sets

4. **Property-Based Tests**
   - Use `hypothesis` for property testing
   - Generate random valid ProjectConfig instances
   - Validate invariants across random inputs

## References

- **pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Testing Best Practices**: https://docs.python-guide.org/writing/tests/

---

**Last Updated:** 2025-11-19
**Test Suite Version:** Sprint 2 (Week 4)
**Maintained by:** Claude Code Generator Team
