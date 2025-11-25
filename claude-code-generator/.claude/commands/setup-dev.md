# Setup Development Environment

Initialize the complete development environment for the Claude Code Generator project.

## Tasks to Complete

1. **Verify Python Version**
   - Check Python 3.10+ is installed
   - Display current Python version

2. **Create Virtual Environment**
   - Create `.venv` directory if it doesn't exist
   - Use `python -m venv .venv` for cross-platform compatibility

3. **Activate Virtual Environment**
   - Provide activation instructions for user's platform
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`

4. **Install Dependencies**
   - Install production dependencies: `pip install -e .`
   - Install development dependencies: `pip install -e ".[dev]"`
   - This includes:
     - click, jinja2, pyyaml, anthropic, rich, pydantic, questionary
     - pytest, pytest-cov, black, ruff, mypy

5. **Verify Installation**
   - Run `claude-gen --version` to verify CLI is available
   - Run `pip list` to show installed packages

6. **Create Required Directories**
   - Ensure all project directories exist:
     - `src/generator/`
     - `src/cli/`
     - `tests/unit/`
     - `tests/integration/`
     - `templates/agents/`
     - `templates/skills/`
     - `templates/commands/`
     - `templates/docs/`
     - `templates/boilerplate/`

7. **Configure Development Tools**
   - Verify `pytest.ini` exists
   - Verify `pyproject.toml` configuration is valid
   - Run type checking: `mypy src/`
   - Run linting: `ruff check src/`

8. **Display Next Steps**
   - Show user what commands are available
   - Suggest running tests: `/run-tests`
   - Suggest testing generator: `/test-generator`

## Example Output

```
✅ Python 3.11.5 detected
✅ Virtual environment created at .venv
✅ Dependencies installed (15 packages)
✅ CLI command 'claude-gen' available
✅ All project directories created
✅ Type checking passed
✅ Linting passed

🚀 Development environment ready!

Next steps:
  - Run tests: /run-tests
  - Test generator: /test-generator
  - Build package: /build-package
```

## Notes

- This command should be idempotent (safe to run multiple times)
- Skip steps that are already complete (e.g., if venv exists)
- Provide helpful error messages if dependencies fail to install
- Check for ANTHROPIC_API_KEY environment variable and warn if missing
