# Build Package

Build the Claude Code Generator as a distributable Python package.

## Tasks to Complete

1. **Verify Build Environment**
   - Check Python version (3.10+)
   - Verify virtual environment is activated
   - Install/verify build tools: `pip install build twine`
   - Display versions of build tools

2. **Clean Previous Builds**
   - Remove `dist/` directory if it exists
   - Remove `build/` directory if it exists
   - Remove `*.egg-info` directories
   - Remove `__pycache__` directories
   - Display cleaned files count

3. **Run Pre-Build Checks**
   - Verify `pyproject.toml` is valid
   - Check all required fields are present:
     - name, version, description
     - authors, license, readme
     - dependencies
   - Run type checking: `mypy src/`
   - Run linting: `ruff check src/`
   - Run tests: `pytest` (should all pass)
   - Verify all tests pass before building

4. **Update Version Number**
   - Display current version from `pyproject.toml`
   - Ask if version should be updated
   - If yes, prompt for new version (semantic versioning)
   - Update version in `pyproject.toml`
   - Update version in `src/cli/main.py` (if hardcoded)

5. **Build Source Distribution**
   - Run: `python -m build --sdist`
   - Creates `.tar.gz` file in `dist/`
   - Verify archive contents:
     - All source files included
     - No unnecessary files (e.g., `__pycache__`)
     - Templates directory included
     - Documentation included

6. **Build Wheel Distribution**
   - Run: `python -m build --wheel`
   - Creates `.whl` file in `dist/`
   - Verify wheel contents:
     - Compiled Python files
     - Entry points configured correctly
     - Dependencies listed correctly

7. **Verify Package Metadata**
   - Run: `twine check dist/*`
   - Check for:
     - Valid README rendering
     - Valid description
     - Valid classifiers
     - No warnings or errors

8. **Test Installation Locally**
   - Create temporary virtual environment
   - Install from wheel: `pip install dist/claude_code_generator-*.whl`
   - Verify CLI command works: `claude-gen --version`
   - Test basic functionality: `claude-gen init --help`
   - Clean up temporary environment

9. **Generate Package Information**
   - Display package details:
     - Package name and version
     - File sizes (sdist and wheel)
     - Dependencies count
     - Python version requirement
   - List all files in the package

10. **Prepare for Distribution** (Optional)
    - Display commands for uploading to PyPI:
      ```bash
      # Test PyPI (recommended first)
      twine upload --repository testpypi dist/*

      # Production PyPI
      twine upload dist/*
      ```
    - Remind to test on TestPyPI first
    - Remind to create git tag for version
    - Suggest creating GitHub release

## Example Commands

```bash
# Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# Check package
twine check dist/*

# Test install
pip install dist/claude_code_generator-0.1.0-py3-none-any.whl

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Example Output

```
🔨 Building Claude Code Generator Package

✅ Build environment verified
   Python: 3.11.5
   build: 1.0.3
   twine: 4.0.2

✅ Cleaned previous builds
   Removed: dist/, build/, 1 .egg-info directory

✅ Pre-build checks passed
   Type checking: ✅ No errors
   Linting: ✅ No issues
   Tests: ✅ 45 passed

📦 Building distributions...

✅ Source distribution built
   File: dist/claude-code-generator-0.1.0.tar.gz
   Size: 156 KB

✅ Wheel distribution built
   File: dist/claude_code_generator-0.1.0-py3-none-any.whl
   Size: 142 KB

✅ Package metadata verified
   README: Valid reStructuredText
   Description: Valid
   No warnings

✅ Local installation test passed
   Command available: claude-gen
   Version: 0.1.0

================================
📊 Package Information
================================
Name: claude-code-generator
Version: 0.1.0
Python: >=3.10
Dependencies: 7 packages
Files in package: 47

Build artifacts:
  dist/claude-code-generator-0.1.0.tar.gz (156 KB)
  dist/claude_code_generator-0.1.0-py3-none-any.whl (142 KB)

✅ Package ready for distribution!

Next steps:
  1. Test on TestPyPI: twine upload --repository testpypi dist/*
  2. Create git tag: git tag v0.1.0
  3. Push tag: git push origin v0.1.0
  4. Upload to PyPI: twine upload dist/*
  5. Create GitHub release
```

## Notes

- Always increment version number for new releases
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Test on TestPyPI before uploading to production PyPI
- Create git tag matching version number
- Include changelog in GitHub release
- Verify package works on different platforms (Windows, macOS, Linux)
- Consider automating builds with GitHub Actions
- Keep `MANIFEST.in` updated if using non-Python files
- Ensure `.gitignore` excludes build artifacts
