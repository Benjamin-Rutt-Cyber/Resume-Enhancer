# Project Structure Documentation

## Overview

This document explains the directory structure of the Claude Code Generator project and the purpose of each component.

## Directory Layout

```
claude-code-generator/
├── .claude/                    # Claude Code configuration for THIS project
│   ├── agents/                 # Agents that help us BUILD the generator
│   ├── skills/                 # Skills for our tech stack (Python, Jinja2, etc.)
│   └── commands/               # Commands for development workflow
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── generator/              # Core generator logic
│   │   ├── __init__.py
│   │   ├── analyzer.py         # Project description analyzer (uses Claude API)
│   │   ├── selector.py         # Template selector
│   │   ├── renderer.py         # Jinja2 template renderer
│   │   ├── file_generator.py   # File/directory creator
│   │   └── boilerplate.py      # Boilerplate code generator
│   └── cli/                    # CLI interface
│       ├── __init__.py
│       ├── main.py             # Click-based CLI entry point
│       └── interactive.py      # Interactive prompts (questionary)
│
├── templates/                  # Template library (used to GENERATE other projects)
│   ├── agents/                 # Agent templates
│   │   ├── api-development.template.md
│   │   ├── security-audit.template.md
│   │   ├── frontend-ui.template.md
│   │   └── ...
│   ├── skills/                 # Skill templates
│   │   ├── python-fastapi.template/
│   │   │   ├── SKILL.md.template
│   │   │   └── scripts/
│   │   └── ...
│   ├── commands/               # Command templates
│   │   ├── setup-dev.template.md
│   │   ├── run-tests.template.md
│   │   └── ...
│   ├── docs/                   # Documentation templates
│   │   ├── ARCHITECTURE.template.md
│   │   ├── API.template.md
│   │   └── ...
│   └── boilerplate/            # Code boilerplate templates
│       ├── python-fastapi/
│       ├── react-typescript/
│       └── ...
│
├── config/                     # Configuration files
│   └── project-types/          # Project type definitions
│       ├── saas-web-app.yaml
│       ├── api-service.yaml
│       ├── hardware-iot.yaml
│       └── ...
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── test_analyzer.py
│   │   ├── test_renderer.py
│   │   └── ...
│   └── integration/            # Integration tests
│       ├── __init__.py
│       ├── test_full_generation.py
│       └── ...
│
├── examples/                   # Generated example projects
│   ├── saas-example/
│   ├── api-example/
│   └── ...
│
├── docs/                       # Project documentation
│   ├── adr/                    # Architecture Decision Records
│   │   ├── README.md           # ADR index
│   │   ├── template.md         # Template for new ADRs
│   │   ├── 0001-jinja2-templates.md
│   │   ├── 0002-click-cli-framework.md
│   │   └── ...                 # 8 ADRs total
│   ├── ARCHITECTURE.md
│   ├── TEMPLATE_GUIDE.md
│   └── ...
│
├── pyproject.toml              # Python project configuration
├── README.md                   # Project overview
├── .gitignore                  # Git ignore rules
└── LICENSE                     # MIT License

```

## Component Purposes

### .claude/ (Our Development Environment)

**Purpose:** Contains agents, skills, and commands that help US build THIS generator.

**Key Files:**
- `agents/architect-agent.md` - Helps design system architecture
- `agents/python-cli-agent.md` - Builds CLI components
- `agents/template-engine-agent.md` - Works with Jinja2 templates
- `skills/python-cli/` - Click/Typer expertise
- `skills/jinja2-templating/` - Template rendering knowledge
- `commands/setup-dev.md` - Initialize development environment
- `commands/test-generator.md` - Test the generator

**This is "dogfooding" - using Claude Code to build a Claude Code tool!**

---

### src/ (Source Code)

#### src/generator/ (Core Logic)

**Purpose:** The heart of the generator - analyzes project descriptions and creates files.

**Modules:**

1. **analyzer.py**
   - Analyzes project description using Claude API
   - Extracts: project type, tech stack, features, requirements
   - Returns: ProjectConfig object

2. **selector.py**
   - Loads project type configuration
   - Selects appropriate agent/skill/command templates
   - Matches tech stack to skills

3. **renderer.py**
   - Renders Jinja2 templates with project context
   - Custom filters for formatting
   - Validates template variables

4. **file_generator.py**
   - Creates directory structure
   - Writes files with proper permissions
   - Handles conflicts (skip, overwrite, merge)

5. **boilerplate.py**
   - Generates starter code
   - Tech-stack-specific boilerplate
   - Configuration files (docker-compose.yml, etc.)

#### src/cli/ (User Interface)

**Purpose:** Command-line interface for the generator.

**Modules:**

1. **main.py**
   - Click-based CLI
   - Commands: init, list, add-template, validate
   - Entry point: `claude-gen`

2. **interactive.py**
   - Questionary-based interactive prompts
   - Project type selection
   - Tech stack configuration
   - Feature selection

---

### templates/ (Template Library)

**Purpose:** Templates used to GENERATE other projects (not for this project).

**Structure:**

Each template is a Jinja2 template with variables like:
- `{{ project_name }}`
- `{{ backend_framework }}`
- `{{ database }}`

**Example:**
```jinja2
---
name: {{ project_slug }}-api-agent
description: API development agent for {{ project_name }}
model: sonnet
---

You are an API development expert for {{ backend_framework }}.
```

---

### config/project-types/ (Project Configurations)

**Purpose:** Define what agents/skills/commands each project type needs.

**Example: saas-web-app.yaml**
```yaml
name: saas-web-app
agents:
  required:
    - api-development-agent
    - frontend-ui-agent
    - database-agent
skills:
  required:
    - authentication
    - api-design
tech_stack_options:
  backend: [python-fastapi, node-express]
  frontend: [react-typescript, nextjs]
```

---

### tests/ (Test Suite)

**Purpose:** Ensure generator works correctly.

**Types:**
- **Unit tests:** Test individual modules (analyzer, renderer, etc.)
- **Integration tests:** Test full generation workflow
- **Template tests:** Validate template syntax and variables

---

### examples/ (Generated Projects)

**Purpose:** Example projects generated by the tool.

**Use Cases:**
- Demonstration
- Testing
- Documentation
- Validation

---

## Development Workflow

### 1. Initial Setup
```bash
cd claude-code-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Using Our Agents
```
# In Claude Code, our agents help us build:
- Use architect-agent for design decisions
- Use python-cli-agent for CLI development
- Use template-engine-agent for Jinja2 work
```

### 3. Development Commands
```bash
# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### 4. Testing the Generator
```bash
# Test CLI
python -m src.cli.main --help
python -m src.cli.main init

# Test generation
python -m src.cli.main init --project "Test Project" --type saas
```

---

## Key Concepts

### Dogfooding

We're using Claude Code to build a Claude Code generator:
- `.claude/agents/` - Agents that help us code
- `templates/agents/` - Agent templates we'll generate for others

### Two Levels of Templates

1. **Our Project** (`.claude/`): Real agents/skills for building the generator
2. **Template Library** (`templates/`): Jinja2 templates that generate agents/skills for OTHER projects

### Meta-Project

This is a "meta-project" - a tool that creates tools. It requires careful distinction between:
- What we use (`.claude/`)
- What we create (`templates/`)
- What gets generated (`examples/`)

---

## Next Steps

1. ✅ Create project structure
2. 🔄 Create dogfooding agents in `.claude/agents/`
3. Create dogfooding skills in `.claude/skills/`
4. Create template library in `templates/`
5. Implement generator logic in `src/generator/`
6. Build CLI in `src/cli/`
7. Write tests in `tests/`
8. Generate examples in `examples/`

---

## Questions?

See also:
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - Detailed step-by-step plan
- [CLAUDE_CODE_FORMAT_SPEC.md](../CLAUDE_CODE_FORMAT_SPEC.md) - Format specifications
- [README.md](./README.md) - Project overview
