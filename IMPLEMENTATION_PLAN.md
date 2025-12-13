# Claude Code Project Generator - Implementation Plan

## Project Goal
Build a tool that automatically creates complete Claude Code project environments from a simple project description.

---

## What We Know

### Claude Code Agent Format (from finance-tracker example)
```markdown
---
name: agent-name
description: When and how to use this agent (with examples)
model: sonnet | opus | haiku
---

[Agent prompt and instructions]
```

### Directory Structure
```
.claude/
  agents/
    - agent-name.md
  skills/
    - skill-name.md
  commands/
    - command-name.md
```

---

## What We Need to Figure Out

### 1. Skills Format
- [ ] What's the format for skill files?
- [ ] Do they have frontmatter like agents?
- [ ] How do agents reference/use skills?

### 2. Commands Format
- [ ] What's the format for slash commands?
- [ ] How do they differ from agents?
- [ ] Can commands invoke agents?

### 3. Agent Invocation
- [ ] How do agents get triggered automatically?
- [ ] What's the exact syntax in the description field?
- [ ] Can agents call other agents?

### 4. Plugin System
- [ ] Is there an official plugin/sharing mechanism?
- [ ] Or do we need to build it from scratch?

---

## Step-by-Step Implementation Plan

### PHASE 1: Research & Setup (Days 1-2)

#### Step 1.1: Understand Claude Code Format ✓ (CURRENT)
**Goal:** Fully understand agent/skill/command format

**Tasks:**
- [x] Study existing agent example (bank-statement-categorizer)
- [ ] Check Claude Code docs for skill format
- [ ] Check Claude Code docs for command format
- [ ] Understand how agents are invoked
- [ ] Document all format specifications

**Deliverable:** `CLAUDE_CODE_FORMAT_SPEC.md`

---

#### Step 1.2: Create Project Architecture
**Goal:** Design the complete system architecture

**Tasks:**
- [ ] Define all components (CLI, analyzer, template engine, etc.)
- [ ] Design data flow
- [ ] Choose tech stack (Python + Click/Typer + Jinja2)
- [ ] Design template format
- [ ] Plan database/storage (YAML files? SQLite?)

**Deliverable:** `ARCHITECTURE.md`

---

#### Step 1.3: Set Up Project Structure
**Goal:** Create the directory structure for our generator project

**Tasks:**
- [ ] Create project directory: `claude-code-generator/`
- [ ] Create initial directory structure
- [ ] Initialize git repo
- [ ] Create Python project (pyproject.toml)
- [ ] Set up virtual environment

**Deliverable:** Working project skeleton

---

### PHASE 2: Dogfooding - Create .claude/ for THIS Project (Days 3-4)

#### Step 2.1: Create Agents We Need
**Goal:** Build agents that will help us build the generator

**Agents to Create:**
1. **architect-agent.md**
   - Helps design system architecture
   - Makes technical decisions
   - Reviews design docs

2. **python-cli-agent.md**
   - Builds CLI interfaces with Click/Typer
   - Handles argument parsing
   - Creates interactive prompts

3. **template-engine-agent.md**
   - Works with Jinja2 templates
   - Designs template formats
   - Handles template rendering

4. **llm-integration-agent.md**
   - Integrates Claude API
   - Designs prompts for project analysis
   - Handles API responses

5. **file-generator-agent.md**
   - Creates files and directories
   - Handles file permissions
   - Manages project structure creation

6. **testing-agent.md**
   - Writes pytest tests
   - Creates test fixtures
   - Ensures coverage

7. **documentation-agent.md**
   - Writes clear documentation
   - Creates examples
   - Maintains README

**Deliverable:** 7 agent files in `.claude/agents/`

---

#### Step 2.2: Create Skills We Need
**Goal:** Build reusable knowledge for our tech stack

**Skills to Create:**
1. **python-cli.md**
   - Click/Typer best practices
   - Argument parsing patterns
   - Interactive prompts
   - Rich formatting for terminal

2. **jinja2-templating.md**
   - Template syntax
   - Filters and functions
   - Template inheritance
   - Custom filters

3. **yaml-config.md**
   - YAML parsing
   - Schema validation
   - Configuration management

4. **file-operations.md**
   - Creating files/directories
   - File permissions
   - Path handling (cross-platform)
   - Atomic file operations

5. **anthropic-api.md**
   - Claude API usage
   - Prompt engineering
   - Rate limiting
   - Error handling

6. **python-packaging.md**
   - PyPI publishing
   - Entry points
   - Dependencies
   - Versioning

**Deliverable:** 6 skill files in `.claude/skills/`

---

#### Step 2.3: Create Commands We Need
**Goal:** Build workflow automation

**Commands to Create:**
1. **setup-dev.md**
   - Set up virtual environment
   - Install dependencies
   - Configure development tools

2. **run-tests.md**
   - Run pytest
   - Check coverage
   - Run linters (ruff, mypy)

3. **test-generator.md**
   - Test the generator on sample projects
   - Validate output
   - Check generated files

4. **build-package.md**
   - Build Python package
   - Run pre-publish checks

5. **add-template.md**
   - Add new agent/skill template to library
   - Validate template format
   - Update registry

**Deliverable:** 5 command files in `.claude/commands/`

---

### PHASE 3: Build Template Library (Days 5-7)

#### Step 3.1: Design Template Format
**Goal:** Create the template structure that will be used to generate projects

**Tasks:**
- [ ] Design Jinja2 template format for agents
- [ ] Design Jinja2 template format for skills
- [ ] Design Jinja2 template format for commands
- [ ] Design Jinja2 template format for docs
- [ ] Create template validation schema

**Example Template Structure:**
```markdown
---
# Template metadata
template_name: api-development-agent
category: backend
applies_to:
  - saas
  - api-service
variables:
  - backend_framework
  - database
  - auth_method
---

# Agent content with Jinja2 variables
---
name: {{ project_slug }}-api-agent
description: API development agent for {{ project_name }}
model: sonnet
---

You are an API development expert for {{ backend_framework }} projects.

## Your Tech Stack
- Framework: {{ backend_framework }}
- Database: {{ database }}
- Authentication: {{ auth_method }}

[... rest of template ...]
```

**Deliverable:** Template format specification

---

#### Step 3.2: Create Agent Templates
**Goal:** Build library of reusable agent templates

**Priority Agent Templates (Start with 10):**
1. architect-agent.template.md
2. api-development-agent.template.md
3. frontend-ui-agent.template.md
4. database-agent.template.md
5. security-audit-agent.template.md
6. testing-agent.template.md
7. deployment-agent.template.md
8. hardware-iot-agent.template.md
9. mobile-app-agent.template.md
10. performance-optimization-agent.template.md

**Deliverable:** `templates/agents/` directory with 10 templates

---

#### Step 3.3: Create Skill Templates
**Goal:** Build library of reusable skill templates

**Priority Skill Templates (Start with 15):**

Languages:
1. python.template.md
2. javascript.template.md
3. typescript.template.md

Frameworks:
4. fastapi.template.md
5. django.template.md
6. express.template.md
7. react.template.md
8. nextjs.template.md

Domains:
9. authentication.template.md
10. api-security.template.md
11. database-design.template.md
12. testing.template.md
13. stripe-payments.template.md
14. websockets.template.md
15. micropython.template.md

**Deliverable:** `templates/skills/` directory with 15 templates

---

#### Step 3.4: Create Command Templates
**Goal:** Build library of reusable command templates

**Priority Command Templates (Start with 8):**
1. setup-dev.template.md
2. run-tests.template.md
3. db-migrate.template.md
4. deploy-staging.template.md
5. deploy-production.template.md
6. lint-fix.template.md
7. security-scan.template.md
8. generate-docs.template.md

**Deliverable:** `templates/commands/` directory with 8 templates

---

#### Step 3.5: Create Documentation Templates
**Goal:** Build library of documentation templates

**Priority Doc Templates (Start with 6):**
1. ARCHITECTURE.template.md
2. API.template.md
3. DATABASE_SCHEMA.template.md
4. DEPLOYMENT.template.md
5. SECURITY.template.md
6. CONTRIBUTING.template.md

**Deliverable:** `templates/docs/` directory with 6 templates

---

#### Step 3.6: Create Project Type Configurations
**Goal:** Define configurations for different project types

**Project Types to Support:**
1. saas-web-app.yaml
2. api-service.yaml
3. hardware-iot.yaml
4. mobile-app.yaml
5. data-science.yaml

**Example Configuration:**
```yaml
# config/project-types/saas-web-app.yaml
name: saas-web-app
display_name: "SaaS Web Application"
description: "Full-stack web application with subscription model"

agents:
  required:
    - architect-agent
    - api-development-agent
    - frontend-ui-agent
    - database-agent
    - testing-agent
    - deployment-agent
  recommended:
    - security-audit-agent
    - performance-optimization-agent

skills:
  required:
    - authentication
    - api-design
    - database-design
  tech_stack_based: true  # Add skills based on chosen stack

commands:
  - setup-dev
  - run-tests
  - db-migrate
  - deploy-staging
  - deploy-production

docs:
  - ARCHITECTURE.md
  - API.md
  - DATABASE_SCHEMA.md
  - DEPLOYMENT.md
  - SECURITY.md

boilerplate:
  enabled: true
  includes:
    - docker-compose.yml
    - .env.example
    - .gitignore
    - README.md

tech_stack_options:
  backend:
    - python-fastapi
    - python-django
    - node-express
    - node-nestjs
  frontend:
    - react-typescript
    - nextjs
    - vue
  database:
    - postgresql
    - mysql
    - mongodb
  cache:
    - redis
    - memcached
```

**Deliverable:** `config/project-types/` directory with 5 YAML files

---

### PHASE 4: Build Core Generator (Days 8-12)

#### Step 4.1: Build Project Analyzer
**Goal:** Analyze project description and extract requirements

**Component:** `src/generator/analyzer.py`

**Features:**
- Uses Claude API to analyze project description
- Extracts: project type, tech stack, features, special requirements
- Returns structured ProjectConfig object

**Example:**
```python
analyzer = ProjectAnalyzer()
config = analyzer.analyze(
    "Build SecureAPI Guardian - an API security testing SaaS with "
    "FastAPI backend, React frontend, and Stripe payments"
)

# Returns:
# config.project_type = "saas-web-app"
# config.tech_stack = {
#     "backend": "python-fastapi",
#     "frontend": "react-typescript",
#     "database": "postgresql",
#     "payment": "stripe"
# }
# config.features = ["authentication", "payments", "api-scanning"]
```

**Deliverable:** Working analyzer module

---

#### Step 4.2: Build Template Selector
**Goal:** Select appropriate templates based on project config

**Component:** `src/generator/selector.py`

**Features:**
- Loads project type configuration
- Selects required agents based on project type
- Adds tech-stack-specific skills
- Adds feature-specific agents/skills

**Deliverable:** Working selector module

---

#### Step 4.3: Build Template Renderer
**Goal:** Render templates with project-specific context

**Component:** `src/generator/renderer.py`

**Features:**
- Jinja2 template rendering
- Custom filters for formatting
- Variable validation
- Error handling for missing variables

**Deliverable:** Working renderer module

---

#### Step 4.4: Build File Generator
**Goal:** Create files and directories

**Component:** `src/generator/file_generator.py`

**Features:**
- Creates directory structure
- Writes files with proper permissions
- Handles existing files (skip, overwrite, merge)
- Cross-platform path handling

**Deliverable:** Working file generator module

---

#### Step 4.5: Build CLI Interface
**Goal:** Create user-friendly CLI

**Component:** `src/cli/main.py`

**Features:**
- Interactive mode with prompts
- Non-interactive mode with flags
- Beautiful terminal output (Rich library)
- Progress indicators
- Error messages

**Commands:**
```bash
# Interactive mode
claude-gen init

# Non-interactive mode
claude-gen init \
  --project "My Project" \
  --type saas-web-app \
  --backend python-fastapi \
  --frontend react-typescript \
  --database postgresql

# List available templates
claude-gen list agents
claude-gen list skills
claude-gen list project-types

# Add custom template
claude-gen add-template agent my-custom-agent.md

# Validate template
claude-gen validate-template agents/my-agent.md
```

**Deliverable:** Working CLI

---

#### Step 4.6: Build Boilerplate Generator
**Goal:** Generate starter code for projects

**Component:** `src/generator/boilerplate.py`

**Features:**
- Creates basic project structure (src/, tests/, docs/)
- Generates config files (docker-compose.yml, .env.example)
- Creates starter code files (main.py, app.tsx, etc.)
- Tech-stack-specific boilerplate

**Deliverable:** Working boilerplate generator

---

### PHASE 5: Testing & Validation (Days 13-14)

#### Step 5.1: Create Test Suite
**Goal:** Comprehensive testing

**Tests Needed:**
- Unit tests for each module
- Integration tests for full workflow
- Template validation tests
- CLI tests
- Cross-platform tests

**Deliverable:** 80%+ test coverage

---

#### Step 5.2: Generate Example Projects
**Goal:** Validate the generator works end-to-end

**Test Projects:**
1. SaaS web app (FastAPI + React)
2. API service (Node + Express)
3. Hardware IoT (Pico-W + MicroPython)
4. Mobile app (React Native)
5. Data science (Python + Jupyter)

**Validation:**
- All files generated correctly
- Agents are properly formatted
- Skills are relevant
- Commands work
- Documentation is complete

**Deliverable:** 5 validated example projects

---

#### Step 5.3: User Testing
**Goal:** Get feedback from real users

**Tasks:**
- Share with 5-10 developers
- Collect feedback on:
  - CLI usability
  - Template quality
  - Generated project usefulness
- Iterate based on feedback

**Deliverable:** User feedback report

---

### PHASE 6: Documentation & Polish (Days 15-16)

#### Step 6.1: Write Documentation
**Goal:** Comprehensive user and developer docs

**Documentation Needed:**
- README.md (quick start)
- INSTALLATION.md
- USAGE.md (all CLI commands)
- TEMPLATE_GUIDE.md (how to create templates)
- CONTRIBUTING.md
- API_REFERENCE.md
- EXAMPLES.md

**Deliverable:** Complete documentation

---

#### Step 6.2: Create Demo Content
**Goal:** Show people how it works

**Create:**
- Demo video (2-3 min)
- Blog post
- Tweet thread
- GitHub repo with examples

**Deliverable:** Marketing materials

---

#### Step 6.3: Package for Distribution
**Goal:** Make it easy to install

**Tasks:**
- Publish to PyPI
- Create releases on GitHub
- Set up CI/CD (GitHub Actions)
- Create installation instructions

**Commands:**
```bash
pip install claude-code-generator
claude-gen --version
```

**Deliverable:** Published package

---

## What We're Potentially Missing

### Technical Unknowns
- [ ] **Skills format specification** - Need to research
- [ ] **Commands format specification** - Need to research
- [ ] **Agent invocation mechanism** - How does Claude Code actually trigger agents?
- [ ] **Plugin system** - Is there an official one?
- [ ] **MCP integration** - Should we support Model Context Protocol?

### Feature Gaps
- [ ] **Versioning** - How to version templates and handle updates?
- [ ] **Conflicts** - What if user has existing .claude/ directory?
- [ ] **Customization** - How to let users modify generated files?
- [ ] **Updates** - How to update projects when templates change?
- [ ] **Sharing** - GitHub integration for community templates?

### Edge Cases
- [ ] **Large projects** - What if project description is too complex?
- [ ] **Unknown tech stacks** - What if we don't have templates for their stack?
- [ ] **Conflicts with existing files** - Merge strategy?
- [ ] **Multi-language projects** - How to handle?

---

## Immediate Next Steps (Right Now)

### Step 1: Research Skills & Commands Format (30 min)
Let's check the Claude Code docs to understand:
- Skills format and usage
- Commands format and usage
- How agents reference skills
- Whether there's an official plugin system

**Action:** I'll fetch the docs and create `CLAUDE_CODE_FORMAT_SPEC.md`

---

### Step 2: Create Project Structure (15 min)
Set up the basic directory structure:
```bash
claude-code-generator/
  .claude/
    agents/
    skills/
    commands/
  src/
    generator/
    cli/
  templates/
    agents/
    skills/
    commands/
    docs/
  config/
    project-types/
  tests/
  docs/
  examples/
  README.md
  pyproject.toml
```

**Action:** Create the directory structure

---

### Step 3: Create First Agent (30 min)
Create `architect-agent.md` that will help us design the system

**Action:** Write the agent file

---

## Success Criteria

By the end of this project, we should have:

✅ **Working CLI tool** that generates complete Claude Code environments
✅ **Template library** with 10+ agents, 15+ skills, 8+ commands
✅ **5 project types** supported (SaaS, API, Hardware, Mobile, Data Science)
✅ **Documentation** comprehensive and clear
✅ **Tests** with 80%+ coverage
✅ **Published package** on PyPI
✅ **Example projects** to showcase

---

## Timeline

- **Days 1-2:** Research & Setup
- **Days 3-4:** Create .claude/ for this project
- **Days 5-7:** Build template library
- **Days 8-12:** Build core generator
- **Days 13-14:** Testing & validation
- **Days 15-16:** Documentation & polish

**Total: ~16 days (2-3 weeks)**

---

## Ready to Start?

I recommend we start with:

1. **Research skills/commands format** (I'll do this now)
2. **Create project directory structure**
3. **Write our first agent** (architect-agent.md)
4. **Use that agent to help us design the system**

This way we're "dogfooding" from the start - using Claude Code agents to build a Claude Code generator!

**Should I proceed with Step 1 (research format specs)?**
