# Template Library

This directory contains all templates used by the Claude Code Generator to create project environments.

## Directory Structure

```
templates/
├── project-types/        # Project type configurations
│   ├── saas-web-app.yaml
│   ├── api-service.yaml
│   ├── hardware-iot.yaml
│   ├── mobile-app.yaml
│   └── data-science.yaml
├── agents/              # Agent templates (.md.j2)
│   ├── api-development-agent.md.j2
│   ├── frontend-agent.md.j2
│   ├── database-agent.md.j2
│   └── ...
├── skills/              # Skill templates (directories with SKILL.md.j2)
│   ├── python-fastapi/
│   ├── react-typescript/
│   ├── postgresql/
│   └── ...
├── commands/            # Command templates (.md.j2)
│   ├── setup-dev.md.j2
│   ├── run-server.md.j2
│   ├── deploy.md.j2
│   └── ...
├── docs/                # Documentation templates (.md.j2)
│   ├── ARCHITECTURE.md.j2
│   ├── API.md.j2
│   ├── SETUP.md.j2
│   └── ...
├── boilerplate/         # Boilerplate code templates
│   ├── python-fastapi/
│   ├── react-typescript/
│   └── ...
├── examples/            # Example rendered outputs
│   └── saas-web-app/
└── registry.yaml        # Template registry

## Template Types

### Agent Templates

Agent templates define specialized AI assistants for different development tasks.

**Format:** Jinja2 templates with frontmatter
**Extension:** `.md.j2`
**Variables:**
- `{{ project_name }}` - Human-readable project name
- `{{ project_slug }}` - Kebab-case identifier
- `{{ project_type }}` - Project type
- `{{ tech_stack }}` - Technology choices

**Available Agents:**
- `api-development-agent` - RESTful API development
- `frontend-agent` - UI/UX development
- `database-agent` - Database design and optimization
- `testing-agent` - Test automation
- `deployment-agent` - CI/CD and deployment
- `security-agent` - Security audits and penetration testing
- `embedded-agent` - Embedded systems (IoT, hardware)
- `mobile-agent` - Mobile app development
- `data-science-agent` - ML/AI and data analysis
- `documentation-agent` - Technical documentation

### Skill Templates

Skill templates provide reusable knowledge and capabilities.

**Format:** Directory with `SKILL.md.j2`
**Variables:** Same as agents

**Available Skills:**
- `python-fastapi` - FastAPI web framework
- `react-typescript` - React with TypeScript
- `postgresql` - PostgreSQL database
- `docker-deployment` - Docker containerization
- `pytest-testing` - Python testing
- `rest-api-design` - RESTful API design
- `authentication` - Auth patterns (JWT, OAuth)
- `micropython` - MicroPython for embedded
- `react-native` - Mobile development
- `pandas-numpy` - Data analysis

### Command Templates

Command templates define slash commands for common workflows.

**Format:** Markdown with Jinja2
**Extension:** `.md.j2`

**Available Commands:**
- `setup-dev` - Initialize development environment
- `run-server` - Start development server
- `run-tests` - Execute test suite
- `deploy` - Deploy to production
- `db-migrate` - Run database migrations
- `build-release` - Build production release
- `lint-code` - Run linters
- `format-code` - Format code

### Documentation Templates

Documentation templates create standard project documentation.

**Format:** Markdown with Jinja2
**Extension:** `.md.j2`

**Available Docs:**
- `ARCHITECTURE.md` - System architecture
- `API.md` - API documentation
- `SETUP.md` - Setup instructions
- `CONTRIBUTING.md` - Contribution guidelines
- `DEPLOYMENT.md` - Deployment guide
- `TESTING.md` - Testing guide

## Project Type Configurations

Each project type has a YAML configuration that defines which templates to use.

**Example: saas-web-app.yaml**
```yaml
name: saas-web-app
display_name: SaaS Web Application
description: Full-stack web application with subscription model

agents:
  - api-development-agent
  - frontend-agent
  - database-agent
  - testing-agent
  - deployment-agent

skills:
  - python-fastapi
  - react-typescript
  - postgresql
  - docker-deployment
  - pytest-testing
  - authentication

commands:
  - setup-dev
  - run-server
  - run-tests
  - deploy
  - db-migrate

docs:
  - ARCHITECTURE
  - API
  - SETUP
  - CONTRIBUTING

tech_stack_options:
  backend:
    - python-fastapi
    - node-express
    - go-gin
  frontend:
    - react-typescript
    - vue-typescript
    - svelte
  database:
    - postgresql
    - mysql
    - mongodb

boilerplate:
  - backend-structure
  - frontend-structure
  - docker-compose
```

## Template Variables

All templates have access to these variables:

### Required Variables
- `project_name` - Human-readable name (e.g., "My SaaS App")
- `project_slug` - Kebab-case identifier (e.g., "my-saas-app")
- `project_type` - Type identifier (e.g., "saas-web-app")
- `author` - Project author name
- `year` - Current year

### Tech Stack Variables
- `backend_framework` - Backend choice (e.g., "python-fastapi")
- `frontend_framework` - Frontend choice (e.g., "react-typescript")
- `database` - Database choice (e.g., "postgresql")
- `deployment_platform` - Deployment target (e.g., "aws")

### Feature Variables
- `features` - List of selected features
- `has_auth` - Boolean for authentication
- `has_api` - Boolean for REST API
- `has_websockets` - Boolean for real-time features
- `has_payments` - Boolean for payment integration

### Custom Variables
Templates can define custom variables in their config YAML files.

## Using Templates

Templates use Jinja2 syntax:

### Variables
```jinja2
Project name: {{ project_name }}
Slug: {{ project_slug }}
```

### Conditionals
```jinja2
{% if has_auth %}
Authentication is enabled
{% endif %}
```

### Loops
```jinja2
{% for feature in features %}
- {{ feature }}
{% endfor %}
```

### Filters
```jinja2
{{ project_name | upper }}
{{ project_slug | slugify }}
```

## Template Registry

The `registry.yaml` file indexes all available templates for discovery:

```yaml
agents:
  - name: api-development-agent
    file: agents/api-development-agent.md.j2
    config: agents/api-development-agent.yaml
    category: development
    project_types: [saas-web-app, api-service]

skills:
  - name: python-fastapi
    directory: skills/python-fastapi/
    config: skills/python-fastapi/config.yaml
    category: backend
    project_types: [saas-web-app, api-service]

commands:
  - name: setup-dev
    file: commands/setup-dev.md.j2
    config: commands/setup-dev.yaml
    category: development
    project_types: [all]

docs:
  - name: ARCHITECTURE
    file: docs/ARCHITECTURE.md.j2
    project_types: [all]
```

## Adding New Templates

Use the `/add-template` command to add new templates interactively:

```bash
/add-template
```

Or manually:

1. Create template file with `.j2` extension
2. Add frontmatter (for agents/skills)
3. Use Jinja2 variables for dynamic content
4. Create config YAML if needed
5. Add to registry.yaml
6. Test with `/test-generator`

## Template Best Practices

1. **Single Responsibility:** Each template should have one clear purpose
2. **Clear Documentation:** Include when to use and what it does
3. **Sensible Defaults:** Provide defaults for optional variables
4. **Error Handling:** Command templates should handle errors gracefully
5. **Examples:** Include code examples in skill templates
6. **Validation:** Agents should validate inputs
7. **Security:** Follow security best practices
8. **Testing:** Include test patterns

## Examples

See `examples/` directory for rendered template outputs.

## Version

Template library version: 0.1.0

Last updated: 2025-11-15
