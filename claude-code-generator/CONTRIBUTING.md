# Contributing to Claude Code Generator

Thank you for your interest in contributing to the Claude Code Generator! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [How to Contribute](#how-to-contribute)
6. [Creating Templates](#creating-templates)
7. [Documenting Architectural Decisions](#documenting-architectural-decisions)
8. [Testing Guidelines](#testing-guidelines)
9. [Code Style](#code-style)
10. [Pull Request Process](#pull-request-process)
11. [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Background
- Identity
- Perspective

### Expected Behavior

- **Be respectful** - Value differing viewpoints and experiences
- **Be collaborative** - Work together towards common goals
- **Be constructive** - Provide helpful feedback
- **Be patient** - Help newcomers learn

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

**Report issues:** Contact maintainers at conduct@example.com

---

## Getting Started

### What Can I Contribute?

We welcome contributions in many forms:

1. **Bug Reports** - Found a bug? Let us know!
2. **Feature Requests** - Have an idea? Share it!
3. **Code Contributions** - Fix bugs or add features
4. **Template Contributions** - Create new agents, skills, or commands
5. **Documentation** - Improve guides and examples
6. **Testing** - Write tests or improve coverage
7. **Design** - Improve CLI output or user experience

### First-Time Contributors

Look for issues labeled:
- `good first issue` - Great for newcomers
- `help wanted` - We need assistance
- `documentation` - Docs improvements

---

## Development Setup

### Prerequisites

- Python 3.9+ (3.14 recommended)
- Git
- pip
- Virtual environment tool (venv, virtualenv, or conda)

### Clone and Install

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/claude-code-generator.git
cd claude-code-generator

# 3. Add upstream remote
git remote add upstream https://github.com/anthropics/claude-code-generator.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install in development mode with dev dependencies
pip install -e ".[dev]"

# 6. Verify installation
claude-gen --version
```

### Set Up API Key (Optional)

For testing AI features:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_analyzer.py -v

# Run specific test
pytest tests/unit/test_analyzer.py::TestProjectConfig::test_valid_config_with_all_fields
```

### Development Tools

```bash
# Format code
black src/ tests/

# Lint code
pylint src/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

---

## Project Structure

```
claude-code-generator/
├── src/
│   ├── cli/
│   │   └── main.py                    # CLI commands
│   └── generator/
│       ├── analyzer.py                # Project analysis
│       ├── selector.py                # Template selection
│       ├── renderer.py                # Template rendering
│       ├── plugin_analyzer.py         # Plugin recommendations
│       └── file_generator.py          # File generation
│
├── templates/
│   ├── agents/
│   │   └── library/                   # Reusable agent files
│   ├── skills/
│   │   └── library/                   # Reusable skill directories
│   ├── commands/                      # Command templates (.j2)
│   ├── docs/                          # Doc templates (.j2)
│   ├── project-types/                 # Project type configs (.yaml)
│   ├── plugins/
│   │   └── registry.yaml              # Plugin catalog
│   └── registry.yaml                  # Template registry
│
├── tests/
│   ├── unit/                          # Unit tests
│   │   ├── test_analyzer.py           # 64 tests
│   │   ├── test_cli.py                # 29 tests
│   │   ├── test_file_generator.py     # 34 tests
│   │   ├── test_plugin_analyzer.py    # 33 tests
│   │   ├── test_renderer.py           # 65 tests
│   │   └── test_selector.py           # 13 tests
│   └── integration/                   # Integration tests
│
├── docs/                              # Documentation
│   ├── USER_GUIDE.md
│   ├── CONTRIBUTING.md                # This file
│   └── ARCHITECTURE.md
│
├── pyproject.toml                     # Project config
├── setup.py                           # Package setup
└── README.md                          # Main readme
```

---

## How to Contribute

### 1. Pick or Create an Issue

**Option A: Work on Existing Issue**
1. Browse [open issues](https://github.com/yourusername/claude-code-generator/issues)
2. Comment: "I'd like to work on this"
3. Wait for assignment (prevents duplicate work)

**Option B: Create New Issue**
1. Search existing issues first
2. Create issue with clear description
3. Wait for discussion/approval
4. Then start working

### 2. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/add-rust-support

# Or for bug fixes
git checkout -b fix/slug-generation-bug
```

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Test improvements
- `refactor/` - Code refactoring

### 3. Make Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and focused

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Check coverage
pytest --cov=src --cov-report=term-missing

# Ensure all tests pass
# Aim for 90%+ coverage on new code
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "Add Rust backend framework support

- Add rust-axum skill template
- Update analyzer to detect Rust keywords
- Add tests for Rust project type
- Update documentation"
```

**Commit Message Guidelines:**
- First line: Brief summary (50 chars max)
- Blank line
- Detailed explanation if needed
- Reference issues: "Fixes #123"

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/add-rust-support

# Create Pull Request on GitHub
# Fill out the PR template
# Wait for review
```

---

## Creating Templates

### Creating a New Agent

**1. Create Agent File**

```bash
# Create in templates/agents/library/
touch templates/agents/library/rust-agent.md
```

**2. Write Agent Content**

```markdown
---
name: rust-agent
display_name: Rust Development Agent
version: 1.0.0
priority: medium
description: Expert in Rust development with focus on safety and performance
---

# Rust Development Agent

You are an expert Rust developer specializing in safe, performant systems programming.

## Core Competencies

- Rust language and toolchain (cargo, rustc)
- Memory safety and ownership
- Concurrency and async/await
- Error handling (Result, Option)
- Testing with cargo test

## Development Workflow

[... detailed instructions ...]
```

**3. Register in registry.yaml**

```yaml
# templates/registry.yaml
agents:
  - name: rust-agent
    type: library  # or 'template'
    file: agents/library/rust-agent.md
    selection_conditions:
      project_types:
        - api-service
        - saas-web-app
      required_any:
        - backend_framework: rust-axum
        - backend_framework: rust-actix
```

**4. Add Tests**

```python
# tests/unit/test_selector.py
def test_rust_backend_selection(self):
    """Test Rust backend framework selection."""
    config = ProjectConfig(
        project_name="API",
        project_slug="api",
        project_type="api-service",
        description="Rust API with Axum framework",
        backend_framework="rust-axum",
    )

    selector = TemplateSelector(templates_dir)
    agents = selector.select_agents(config)

    agent_names = [Path(a).stem for a in agents]
    assert "rust-agent" in agent_names
```

---

### Creating a New Skill

**1. Create Skill Directory**

```bash
mkdir -p templates/skills/library/rust-axum
cd templates/skills/library/rust-axum
```

**2. Create SKILL.md**

```markdown
---
name: rust-axum
display_name: Rust Axum Web Framework
version: 1.0.0
category: backend
framework: rust
description: Modern, ergonomic web framework for Rust
---

# Rust Axum Web Framework

## Overview

Axum is a web framework built on top of Tokio and Hyper, designed for ergonomic and modular web applications.

## Key Concepts

### 1. Handlers
[... examples and explanations ...]

### 2. Routing
[... examples and explanations ...]
```

**3. Add Example Files**

```bash
# templates/skills/library/rust-axum/examples/
touch examples/basic_server.rs
touch examples/with_state.rs
touch examples/error_handling.rs
```

**4. Register in registry.yaml**

```yaml
# templates/registry.yaml
skills:
  - name: rust-axum
    type: library
    directory: skills/library/rust-axum
    selection_conditions:
      required_all:
        - backend_framework: rust-axum
```

---

### Creating a New Command

**1. Create Command Template**

```bash
touch templates/commands/build-release.md.j2
```

**2. Write Template**

```markdown
---
name: build-release
description: Build production release
---

# Build Release

Builds an optimized production release.

## Usage

```bash
/build-release
```

## Steps

{% if backend_framework == 'rust-axum' %}
1. Run cargo build --release
2. Run cargo test
3. Verify binary at target/release/
{% elif backend_framework == 'python-fastapi' %}
1. Install dependencies: pip install -r requirements.txt
2. Run tests: pytest
3. Build Docker image: docker build -t {{ project_slug }}:latest .
{% endif %}

[... more content ...]
```

**3. Register in project-type config**

```yaml
# templates/project-types/api-service.yaml
commands:
  - setup-dev
  - run-server
  - run-tests
  - build-release  # Add here
  - deploy
```

---

### Creating a New Project Type

**1. Create Config File**

```bash
touch templates/project-types/cli-tool.yaml
```

**2. Define Configuration**

```yaml
name: cli-tool
display_name: CLI Tool
description: Command-line interface application

agents:
  - cli-development
  - testing-agent
  - documentation-agent

skills:
  - python-click
  - rust-clap
  - go-cobra

commands:
  - setup-dev
  - run-tests
  - build-binary

docs:
  - README
  - USAGE
```

**3. Update Selector**

The selector will automatically recognize new project types!

**4. Add Detection Keywords**

Update analyzer to detect your new type:

```python
# src/generator/analyzer.py
elif any(word in desc_lower for word in ['cli', 'command line', 'terminal']):
    project_type = 'cli-tool'
    backend_framework = 'python-click'
```

---

## Documenting Architectural Decisions

### What are ADRs?

Architecture Decision Records (ADRs) document important architectural decisions made in the project. They help contributors understand:
- Why certain technologies were chosen
- What alternatives were considered
- What trade-offs were accepted

### When to Create an ADR

Create an ADR when making:
- **Technology choices**: Selecting a framework, library, or tool
- **Design patterns**: Adopting a particular architectural pattern
- **Security decisions**: Implementing security measures or policies
- **Performance trade-offs**: Choosing performance vs. other concerns
- **API design**: Defining major API structures or interfaces

**Examples**:
- Choosing between FastAPI and Django for backend
- Deciding on YAML vs. JSON for configuration files
- Implementing a caching strategy
- Selecting a template engine

### How to Create an ADR

**1. Copy the Template**

```bash
# Get next number (e.g., if 0008 exists, use 0009)
ls docs/adr/
cp docs/adr/template.md docs/adr/0009-short-descriptive-title.md
```

**2. Fill Out the Template**

```markdown
---
adr: 0009
title: Use Redis for Caching
date: 2025-11-26
status: Proposed
---

# ADR-0009: Use Redis for Caching

## Status

🚧 **Proposed**

## Context

We need a caching solution to improve API response times.
Our current approach loads data from PostgreSQL on every request,
causing 500ms+ latency for frequently accessed resources.

## Decision

We will use Redis as an in-memory cache for frequently accessed data.

## Consequences

**Positive:**
- Reduces database load by 70%
- Improves response times from 500ms to ~50ms
- Battle-tested and widely used

**Negative:**
- Adds operational complexity (one more service)
- Cache invalidation complexity
- Additional dependency

## Alternatives Considered

### Memcached
- Pros: Simpler, faster for pure caching
- Cons: No data structures, no persistence
- Why rejected: Need sorted sets for leaderboards

### In-Memory Python Dict
- Pros: No dependencies, simple
- Cons: Not shared across processes, lost on restart
- Why rejected: Doesn't work with multi-process deployments

## References

- File(s): `src/cache/redis_client.py`
- Related ADRs: None
- External: https://redis.io/docs/
```

**3. Update the Index**

Add your ADR to `docs/adr/README.md`:

```markdown
| [0009](0009-use-redis-for-caching.md) | Use Redis for Caching | 🚧 Proposed | 2025-11-26 |
```

**4. Submit for Review**

- Create a pull request with your ADR
- ADRs should be discussed and approved before implementation
- Status starts as **Proposed**, becomes **Accepted** when implemented

### ADR Status Lifecycle

- 🚧 **Proposed**: Under discussion, not yet decided
- ✅ **Accepted**: Decision made and implemented
- ❌ **Deprecated**: No longer recommended (but may still be in use)
- ⚠️ **Superseded**: Replaced by a newer ADR (link to it)

### Tips for Writing Good ADRs

**Do:**
- Explain the problem context clearly
- List real alternatives that were considered
- Be honest about trade-offs (every decision has cons)
- Link to code that implements the decision
- Use objective, factual language

**Don't:**
- Document trivial decisions (use `console.log` vs `print`)
- Write implementation details (that belongs in code comments)
- Skip the "Alternatives Considered" section
- Be vague ("we chose X because it's better")

### Example ADRs in This Project

See `docs/adr/` for examples:
- ADR-0001: Use Jinja2 for Template Rendering
- ADR-0003: Dual-Mode Analysis (AI + Keyword Fallback)
- ADR-0005: Path Traversal Security Model

---

## Testing Guidelines

### Test Requirements

All contributions must include tests:

1. **New Features** - Add unit tests covering all code paths
2. **Bug Fixes** - Add regression test demonstrating the fix
3. **Templates** - Ensure templates render correctly
4. **Coverage Goal** - Maintain 90%+ coverage on new code

### Writing Tests

**Unit Test Example:**

```python
# tests/unit/test_new_feature.py
import pytest
from src.generator.new_module import NewClass

class TestNewFeature:
    """Test new feature functionality."""

    def test_basic_functionality(self):
        """Test basic use case."""
        obj = NewClass()
        result = obj.do_something("input")

        assert result == "expected_output"

    def test_edge_case(self):
        """Test edge case handling."""
        obj = NewClass()

        with pytest.raises(ValueError, match="Invalid input"):
            obj.do_something("")
```

**Testing Templates:**

```python
def test_new_template_renders(self, tmp_path):
    """Test new template renders correctly."""
    renderer = TemplateRenderer(templates_dir)

    context = {
        "project_name": "Test",
        "backend_framework": "rust-axum",
    }

    result = renderer.render_template("new-template.md.j2", context)

    assert "expected content" in result
    assert "{{ variable }}" not in result  # No unrendered vars
```

### Running Tests Locally

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/unit/test_analyzer.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

---

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

**Formatting:**
- Line length: 100 characters (not 79)
- Use Black for formatting
- Use isort for import sorting

**Naming:**
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names (avoid single letters except in loops)

**Docstrings:**
```python
def analyze_project(description: str, project_name: Optional[str] = None) -> ProjectConfig:
    """
    Analyze project description and extract configuration.

    Args:
        description: Natural language project description
        project_name: Optional project name override

    Returns:
        ProjectConfig with extracted information

    Raises:
        ValueError: If description is empty or invalid
    """
    # Implementation...
```

**Type Hints:**
- Use type hints for all function parameters and returns
- Use `Optional[T]` for optional parameters
- Use `list[T]`, `dict[K, V]` (not `List`, `Dict`)

**Imports:**
```python
# Standard library
import os
from pathlib import Path
from typing import Optional

# Third-party
import click
from anthropic import Anthropic

# Local
from src.generator.analyzer import ProjectAnalyzer
```

### Template Style Guide

**Jinja2 Templates:**
- Use `{{ variable }}` for substitution
- Use `{% if condition %}` for conditionals
- Use `{% for item in items %}` for loops
- Keep logic simple - complex logic belongs in Python

**Markdown:**
- Use ATX-style headers (`#`, `##`, not underlines)
- One blank line before/after headers
- Use fenced code blocks with language identifier
- Use `**bold**` and `*italic*`, not `__` or `_`

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] Type hints added
- [ ] Commit messages are clear
- [ ] No merge conflicts with main
- [ ] Branch is up-to-date with upstream/main

### PR Template

When creating a PR, fill out:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Test improvement

## Related Issues
Fixes #123
Relates to #456

## Testing
Describe how you tested this

## Screenshots (if applicable)
Add CLI output or visual changes

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

### Review Process

1. **Automated Checks** - CI runs tests and linting
2. **Code Review** - Maintainer reviews code
3. **Feedback** - Address review comments
4. **Approval** - Maintainer approves PR
5. **Merge** - Maintainer merges to main

**Response Time:**
- First response: Within 2-3 days
- Full review: Within 1 week

### After Merge

- Your contribution will be in the next release
- You'll be added to CONTRIBUTORS.md
- Close related issues if not auto-closed

---

## Community

### Communication Channels

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas, showcase
- **Discord** - Real-time chat (link in README)
- **Email** - maintainers@example.com

### Getting Help

**Stuck?** We're here to help!

1. Check documentation (USER_GUIDE.md, README.md)
2. Search existing issues
3. Ask in GitHub Discussions
4. Join our Discord

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

---

## Development Tips

### Debugging the Generator

```python
# Add print statements
print(f"Config: {config}")

# Use pdb for debugging
import pdb; pdb.set_trace()

# Run with verbose output
claude-gen init --project "Test" --description "..." -v
```

### Testing Template Rendering

```bash
# Generate test project
claude-gen init \
  --project "TestProject" \
  --description "Test project for template validation" \
  --output /tmp/test-project

# Inspect output
ls -la /tmp/test-project/.claude/
cat /tmp/test-project/.claude/agents/api-development-agent.md
```

### Iterating on Templates

1. Edit template file
2. Delete test output: `rm -rf /tmp/test-project`
3. Regenerate: `claude-gen init --output /tmp/test-project ...`
4. Verify changes
5. Repeat

---

## License

By contributing to Claude Code Generator, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

- 📖 Read [USER_GUIDE.md](USER_GUIDE.md) for usage help
- 🏗️ Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
- 💬 Ask in [GitHub Discussions](https://github.com/yourusername/claude-code-generator/discussions)
- 📧 Email maintainers@example.com

---

**Thank you for contributing!** 🎉

Your contributions help make Claude Code Generator better for everyone.
