---
adr: 0007
title: YAML-Based Project Configuration
date: 2025-11-26
status: Accepted
---

# ADR-0007: YAML-Based Project Configuration

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

The Claude Code Generator needs configuration files to define:
- **Project types**: SaaS web app, API service, mobile app, hardware/IoT, data science
- **Template registry**: Which agents, skills, commands apply to which project types
- **Plugin recommendations**: Which Claude Code plugins to suggest for each project
- **Selection conditions**: Rules for when to include specific templates

These configurations need to be:
- **Human-readable**: Contributors should easily understand and modify them
- **Machine-parseable**: Code needs to load and process them efficiently
- **Version-controllable**: Changes tracked in git with clear diffs
- **Non-code**: Non-programmers should be able to add project types
- **Validatable**: Detect syntax errors before runtime
- **Extensible**: Easy to add new project types, templates, and plugins

Configuration locations:
- `templates/registry.yaml` - Master template registry (agents, skills, commands, docs)
- `templates/project-types/*.yaml` - Per-project-type configurations
- `templates/plugins/registry.yaml` - Plugin recommendations

The question: **What format should we use for these configuration files?**

## Decision

We will use **YAML** as the configuration format for all template and project type definitions.

**Example Structure** (`templates/project-types/saas-web-app.yaml`):
```yaml
project_type: saas-web-app
display_name: "SaaS Web Application"

agents:
  - api-development-agent
  - frontend-react-agent
  - database-postgresql-agent
  - testing-agent
  - security-agent

skills:
  - python-fastapi
  - react-typescript
  - postgresql
  - docker

commands:
  - run-dev
  - run-tests
  - deploy-docker

features:
  - authentication
  - api-endpoints
  - database-orm
  - docker-deployment
```

**Template Registry** (`templates/registry.yaml`):
```yaml
agents:
  - name: api-development-agent
    path: agents/api-development-agent.md
    type: reusable
    selection_conditions:
      project_types: [saas-web-app, api-service]

skills:
  - name: python-fastapi
    path: skills/library/python-fastapi/SKILL.md
    type: library
    selection_conditions:
      required_any: [python-fastapi, fastapi]
```

**Loading** (`src/generator/selector.py`):
```python
import yaml

with open('templates/registry.yaml') as f:
    registry = yaml.safe_load(f)
```

## Consequences

**Positive:**
- **Highly readable**: Clear, indented structure easy for humans to parse
- **Minimal syntax**: No brackets, quotes optional, very clean
- **Comments supported**: Can add documentation inline with `#`
- **Nested structures**: Natural representation of hierarchical data
- **Standard format**: Widely used in DevOps (Docker Compose, Kubernetes, GitHub Actions)
- **Git-friendly**: Diffs are clean and easy to review
- **Multi-line strings**: Support for |multi-line| and >folded> strings
- **Type inference**: Booleans, integers, strings auto-detected
- **Extensible**: Easy to add new fields without breaking existing configs
- **No compilation**: Edit and run immediately

**Negative:**
- **Indentation-sensitive**: Whitespace errors can be subtle (like Python)
- **Potential security issues**: `yaml.load()` can execute Python code (mitigated by using `safe_load()`)
- **Complex nested structures**: Deep nesting can become hard to read
- **No schema enforcement**: YAML itself doesn't validate structure (need separate validation)
- **Ambiguous values**: `true/True/TRUE`, `yes/no`, `on/off` all mean boolean (confusing)
- **Dependency**: Requires PyYAML library

**Neutral:**
- **Multiple documents**: Can have multiple YAML docs in one file (separated by `---`)
- **Anchors and aliases**: Can reuse config blocks with `&anchor` and `*alias`

## Alternatives Considered

### JSON
- **Example**:
  ```json
  {
    "project_type": "saas-web-app",
    "agents": ["api-development-agent", "frontend-react-agent"],
    "skills": ["python-fastapi", "react-typescript"]
  }
  ```
- **Pros**:
  - Standard interchange format
  - Built into Python (no dependency)
  - Strict syntax (less ambiguity)
  - JSON Schema for validation
  - Universal support
- **Cons**:
  - **Verbose**: Requires quotes around all keys/strings
  - **No comments**: Cannot add inline documentation
  - **Trailing commas**: Common source of errors
  - **Less readable**: Brackets and quotes clutter
  - **No multi-line strings**: Must use \n escape sequences
- **Why rejected**: Too verbose for human-edited config files. YAML is much cleaner for this use case.

### TOML
- **Example**:
  ```toml
  project_type = "saas-web-app"
  agents = ["api-development-agent", "frontend-react-agent"]
  skills = ["python-fastapi", "react-typescript"]
  ```
- **Pros**:
  - More explicit than YAML (less ambiguity)
  - Comments supported
  - Used by Python (pyproject.toml, Cargo.toml)
  - Simpler than YAML (no complex features)
  - Good error messages
- **Cons**:
  - Less support for nested structures
  - Array-of-tables syntax is verbose
  - Less familiar to developers than YAML
  - Not as widely used outside Rust/Python packaging
- **Why rejected**: While TOML is great for flat configs, YAML handles nested structures better. Our registry has deep nesting (agents → conditions → project_types).

### Python Modules
- **Example**:
  ```python
  # templates/project_types/saas_web_app.py
  PROJECT_TYPE = "saas-web-app"
  AGENTS = ["api-development-agent", "frontend-react-agent"]
  SKILLS = ["python-fastapi", "react-typescript"]
  ```
- **Pros**:
  - No parsing needed (just import)
  - Can include logic and computed values
  - Type checking with mypy
  - IDE autocomplete
  - No dependency
- **Cons**:
  - **Security risk**: Executing untrusted Python code
  - **Not data**: Requires Python knowledge to edit
  - **Poor git diffs**: Python syntax changes are noisier
  - **No validation**: Typos become runtime errors
  - **Harder for non-programmers**: Can't ask designers to edit Python
- **Why rejected**: Configurations should be data, not code. YAML is safer and more accessible.

### XML
- **Example**:
  ```xml
  <project-type name="saas-web-app">
    <agents>
      <agent>api-development-agent</agent>
      <agent>frontend-react-agent</agent>
    </agents>
  </project-type>
  ```
- **Pros**:
  - Schema validation (XSD)
  - Universal standard
  - Good tooling
- **Cons**:
  - **Extremely verbose**: Opening and closing tags everywhere
  - **Poor readability**: Hard to scan visually
  - **Outdated**: Less common in modern projects
  - **Overkill**: Too heavyweight for simple configs
- **Why rejected**: XML is unnecessarily verbose for our needs. YAML is far more readable.

## References

- **File(s)**:
  - `src/generator/selector.py:193-260` - YAML registry loading and parsing
  - `templates/registry.yaml` - Master template registry
  - `templates/project-types/*.yaml` - Per-project-type configurations
  - `templates/plugins/registry.yaml` - Plugin recommendations
- **Related ADRs**:
  - ADR-0008 (Smart Template Selection) - Uses YAML for selection conditions
- **External Links**:
  - [YAML Specification](https://yaml.org/spec/)
  - [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

## Notes

**Security Best Practices**:
- Always use `yaml.safe_load()` instead of `yaml.load()` to prevent code execution
- Validate structure after loading (check required fields, types)
- Don't load untrusted YAML from user input

**YAML Features We Use**:
- **Lists**: `agents: [agent1, agent2]` or multi-line with `-`
- **Dictionaries**: `name: value` mappings
- **Comments**: `# This is a comment`
- **Multi-line strings**: `description: |` for literal blocks
- **Booleans**: `enabled: true` or `enabled: false`

**YAML Features We Don't Use** (yet):
- Anchors/aliases (`&anchor`, `*alias`)
- Multiple documents in one file (`---` separator)
- Custom tags (`!!python/object`)
- Merge keys (`<<: *base`)

**Validation Strategy**:
After loading YAML, we validate:
- Required keys are present (`project_type`, `agents`, `skills`)
- Types are correct (lists, strings, booleans)
- Referenced templates exist in filesystem
- Syntax errors caught by PyYAML during load

**Future Enhancements**:
- Could add JSON Schema validation for YAML files
- Could generate TypeScript types from YAML schemas
- Could add YAML linting in CI/CD (yamllint)
