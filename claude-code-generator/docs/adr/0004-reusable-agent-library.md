---
adr: 0004
title: Reusable Agent Library Approach
date: 2025-11-26
status: Accepted
---

# ADR-0004: Reusable Agent Library Approach

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

When generating Claude Code projects, we need to provide agents (specialized AI assistants) to help users with different aspects of development:
- Technology-specific agents (FastAPI, React, PostgreSQL, Docker)
- Domain-specific agents (API development, frontend, testing, security)
- Project-specific agents (business logic, domain expertise, custom integrations)

Initial approach was to **generate all agents as templates** with project-specific context. This had problems:
- **Wasteful**: Same agent content generated repeatedly for every project
- **Maintenance burden**: Fixing a bug in the "api-development-agent" requires regenerating all projects
- **Token cost**: Using Claude API to generate identical content
- **Slow**: Template rendering for 40+ files adds unnecessary latency
- **Hard to improve**: Library doesn't accumulate knowledge over time

The question: **Should agents be templates rendered with project context, or reusable library files copied as-is?**

## Decision

We will implement a **hybrid approach**: technology-focused agents are reusable library files (95%), project-specific agents are templates (5%).

**File Extension Determines Behavior**:
- **`.md` (no .j2)**: Reusable agent/skill - copy as-is, no templating
- **`.md.j2`**: Template agent/skill - render with Jinja2 and project context

**Implementation**:
```python
# Agents (file_generator.py:241-254)
if template_path.endswith('.j2'):
    # GENERATED: Render template with project context
    content = self.renderer.render_template(template_path, context)
else:
    # REUSABLE: Copy as-is (no templating)
    shutil.copy2(template_file, output_path)

# Skills (file_generator.py:286-296)
is_library_skill = template_path.endswith('SKILL.md') and not template_path.endswith('.j2')
```

**Directory Structure**:
```
templates/
├── agents/
│   ├── api-development-agent.md      (reusable)
│   ├── frontend-react-agent.md       (reusable)
│   ├── database-postgresql-agent.md  (reusable)
│   ├── testing-agent.md              (reusable)
│   └── domain-expert-agent.md.j2     (template)
├── skills/
│   ├── library/python-fastapi/SKILL.md  (reusable)
│   └── python-fastapi/SKILL.md.j2       (template)
```

## Consequences

**Positive:**
- **Single source of truth**: One authoritative version of each generic agent
- **Easy maintenance**: Fix once, benefits all future projects
- **Fast generation**: No template rendering for 90%+ of agents/skills
- **Zero API cost**: No Claude tokens spent on identical content
- **Growing library**: Can accumulate comprehensive, battle-tested agents over time
- **Quality improvement**: Can continuously refine agents without regenerating projects
- **Technology-focused**: Agents specialize in tech (FastAPI, React) not projects
- **Flexible**: Still supports project-specific agents when truly needed

**Negative:**
- **No project name references**: Reusable agents can't mention the specific project name
- **Two code paths**: Different logic for library vs template resources
- **File extension convention**: `.j2` suffix is critical - easy to forget
- **Mixed content**: Same directory contains both reusable and template files
- **Documentation needed**: Contributors must understand the distinction

**Neutral:**
- **95/5 split**: Vast majority of agents/skills are reusable (only domain-specific ones need templating)
- **Extension as signal**: Clear visual indicator of reusable vs template

## Alternatives Considered

### All Generated (Template Everything)
- **Pros**:
  - Simple mental model - everything is a template
  - Can customize every file with project context
  - Single code path - no special cases
  - Project name in every file if desired
- **Cons**:
  - Wastes Claude API tokens on identical content
  - Slower project generation (40+ template renders)
  - Maintenance nightmare (bugs require regenerating all projects)
  - No single source of truth
  - Library doesn't improve over time
- **Why rejected**: Wasteful and doesn't scale. As the library grows, cost and time would become prohibitive.

### All Reusable (No Templates)
- **Pros**:
  - Maximum speed - just copy files
  - Zero API cost
  - Easy maintenance
  - Single code path
- **Cons**:
  - Can't customize for project-specific needs
  - Can't generate domain-expert agents (e-commerce vs healthcare)
  - Can't inject project name or custom context
  - Too inflexible for edge cases
- **Why rejected**: Some agents genuinely need project context (domain expert, business logic). Pure library approach is too restrictive.

### Runtime Selection (Detect During Generation)
- **Pros**:
  - Agents explicitly declare if they need context
  - Could use YAML frontmatter: `needs_context: true/false`
  - More explicit than file extension
- **Cons**:
  - Requires parsing every file to check metadata
  - Slower (read all files at startup)
  - More complex than file extension check
  - YAML frontmatter in markdown feels heavy
- **Why rejected**: File extension is simpler, faster, and more conventional (`.j2` is widely understood).

### Separate Directories (library/ vs templates/)
- **Pros**:
  - Physical separation makes distinction obvious
  - No file extension convention needed
  - Easier to find all library agents
- **Cons**:
  - More complex directory structure
  - Template selector needs to search multiple locations
  - registry.yaml paths become more complex
  - Harder to convert library → template or vice versa
- **Why rejected**: File extension is simpler and keeps related agents together.

## References

- **File(s)**:
  - `src/generator/file_generator.py:241-254` - Agent reusable vs template logic
  - `src/generator/file_generator.py:286-296` - Skill library detection
  - `AGENT_LIBRARY_DESIGN.md:1-80` - Full design rationale document
- **Related ADRs**:
  - ADR-0001 (Jinja2 Templates) - Template rendering for `.j2` files
- **External Links**: None

## Notes

**Examples of Reusable Agents** (Technology-focused, generic):
- `api-development-agent.md` - REST API development (FastAPI, Express, Django)
- `frontend-react-agent.md` - React development (any React project)
- `database-postgresql-agent.md` - PostgreSQL (any project using Postgres)
- `testing-agent.md` - Testing practices (pytest, jest, any language)
- `security-agent.md` - Security best practices (any web app)

**Examples of Template Agents** (Project-specific, custom):
- `domain-expert-agent.md.j2` - E-commerce vs Healthcare domain logic
- `business-logic-agent.md.j2` - Project-specific business rules
- `custom-integration-agent.md.j2` - Specific third-party API (Stripe, Twilio)

**Conversion is Easy**:
- Library → Template: Rename `agent.md` → `agent.md.j2`, add Jinja2 variables
- Template → Library: Rename `agent.md.j2` → `agent.md`, remove variables

**Future Enhancements**:
- Could build a public library of community-contributed agents
- Could version agents separately from the generator tool
- Could allow users to override library agents with project-specific versions
