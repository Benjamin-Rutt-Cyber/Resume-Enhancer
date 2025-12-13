---
adr: 0008
title: Smart Template Selection with Conditions
date: 2025-11-26
status: Accepted
---

# ADR-0008: Smart Template Selection with Conditions

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

When generating a new project, the generator needs to select which templates to include:
- **Agents**: Which AI assistants to provide (.claude/agents/)
- **Skills**: Which technology skills to include (.claude/skills/)
- **Commands**: Which CLI commands to provide (.claude/commands/)

Selection must be intelligent and flexible:
- Include FastAPI agent only if using FastAPI backend
- Include React agent only if using React frontend
- Include PostgreSQL skill only if using PostgreSQL database
- Support multiple project types (SaaS, API, mobile, IoT, data science)
- Allow templates to declare their own applicability
- Enable adding new templates without code changes

Initial approach: Hardcoded lists per project type
```python
if project_type == 'saas-web-app':
    agents = ['api-agent', 'frontend-agent', 'db-agent', ...]
elif project_type == 'api-service':
    agents = ['api-agent', 'db-agent', ...]
```

Problems with hardcoded lists:
- Adding new template requires code change
- No flexibility for tech stack variations
- Duplicate logic across agent/skill/command selection
- Can't easily add new project types
- Doesn't scale as library grows

The question: **How should we determine which templates to include for a given project?**

## Decision

We will implement **condition-based smart template selection** where templates declare their own applicability in YAML.

**Three-Stage Filtering Algorithm** (`src/generator/selector.py:193-260`):

1. **Project Type Filter**: Must be in `project_types` list (if specified)
2. **Required Any (OR Logic)**: Must match at least one condition in `required_any`
3. **Required All (AND Logic)**: Must match all conditions in `required_all`

**Template Declaration** (`templates/registry.yaml`):
```yaml
agents:
  - name: frontend-react-agent
    path: agents/frontend-react-agent.md
    type: reusable
    selection_conditions:
      project_types: [saas-web-app, mobile-app]
      required_any:
        frontend_framework: [react-typescript, react-javascript, react-native]

  - name: database-postgresql-agent
    path: agents/database-postgresql-agent.md
    type: reusable
    selection_conditions:
      required_any:
        database: [postgresql, postgres]

  - name: api-development-agent
    path: agents/api-development-agent.md
    type: reusable
    selection_conditions:
      project_types: [saas-web-app, api-service, mobile-app]
```

**Selection Logic**:
```python
# Build tech stack from project config
tech_stack = {
    'backend': config.backend_framework,      # e.g., 'python-fastapi'
    'frontend_framework': config.frontend_framework,  # e.g., 'react-typescript'
    'database': config.database,              # e.g., 'postgresql'
    'deployment': config.deployment_platform, # e.g., 'docker'
}

for resource in resources:
    conditions = resource['selection_conditions']

    # Stage 1: Project type match
    if config.project_type not in conditions.get('project_types', []):
        continue  # Skip

    # Stage 2: OR logic (match ANY)
    required_any = conditions.get('required_any', {})
    if required_any and not any_match(tech_stack, required_any):
        continue  # Skip

    # Stage 3: AND logic (match ALL)
    required_all = conditions.get('required_all', {})
    if required_all and not all_match(tech_stack, required_all):
        continue  # Skip

    # All conditions passed - include template
    selected.append(resource)
```

## Consequences

**Positive:**
- **No code changes for new templates**: Just add YAML entry with conditions
- **Self-documenting**: Templates declare when they should be used
- **Flexible matching**: Supports OR and AND logic for complex conditions
- **Tech stack aware**: Matches on backend, frontend, database, deployment
- **Extensible**: Easy to add new selection fields (platform, features, etc.)
- **Testable**: Condition logic is isolated and unit testable
- **Declarative**: Configuration, not code
- **Multiple criteria**: Can match on project type AND tech stack
- **Graceful**: Templates without conditions are skipped (backwards compatible)

**Negative:**
- **More complex YAML**: Template definitions are more verbose
- **Indirection**: Must look in YAML to understand selection logic
- **Debugging**: Harder to trace why a template was/wasn't included
- **No visual tooling**: Can't easily see "what templates for project X?"
- **Learning curve**: Contributors must understand the condition syntax

**Neutral:**
- **Three-stage filter**: Project type → required_any → required_all
- **Empty conditions**: If no conditions, template is never selected (must be explicit)

## Alternatives Considered

### Hardcoded Lists (Original Approach)
- **Implementation**:
  ```python
  if project_type == 'saas-web-app':
      agents = ['api-agent', 'frontend-agent', 'db-agent']
      if config.backend_framework == 'python-fastapi':
          skills = ['python-fastapi']
  ```
- **Pros**:
  - Simple, direct, easy to understand
  - Clear logic flow
  - Easy to debug
- **Cons**:
  - Requires code change for every new template
  - Duplicate logic across agent/skill/command selection
  - Doesn't scale as library grows
  - Hard to add new project types
  - Tech stack variations require nested if/elif
- **Why rejected**: Doesn't scale. As the template library grows (50+ agents, 100+ skills), hardcoded lists become unmaintainable.

### Tags/Labels System
- **Implementation**:
  ```yaml
  agents:
    - name: frontend-react-agent
      tags: [frontend, react, typescript, web]
  # Select by: "Give me all agents tagged 'frontend' and 'react'"
  ```
- **Pros**:
  - Simple tag-based filtering
  - Easy to add new tags
  - Flexible querying
- **Cons**:
  - No logic (can't express OR/AND)
  - Tag explosion (need tags for every combination)
  - No project type concept
  - Ambiguous (is 'react' required or optional?)
  - Would still need selection code
- **Why rejected**: Too simple. Can't express "Include if FastAPI OR Django" or "Include if SaaS AND React".

### Rule Engine (e.g., python-rules, business-rules)
- **Implementation**:
  ```python
  Rule(
      name="include-react-agent",
      condition=lambda config: config.frontend_framework in ['react-typescript', 'react-native'],
      action=lambda: include('frontend-react-agent')
  )
  ```
- **Pros**:
  - Very powerful and flexible
  - Can express complex logic
  - Turing-complete (if needed)
- **Cons**:
  - **Overkill**: Don't need Turing-complete rules
  - **Security risk**: Executing arbitrary code
  - **Complex**: High learning curve
  - **Dependencies**: Requires rule engine library
  - **Debugging**: Hard to understand rule interactions
- **Why rejected**: Too complex for our needs. The three-stage filter (project_types → required_any → required_all) is sufficient.

### Scoring System
- **Implementation**:
  ```yaml
  agents:
    - name: frontend-react-agent
      scoring:
        project_type==saas-web-app: 10
        frontend_framework==react-typescript: 20
        has_api==true: 5
  # Include templates with score > 15
  ```
- **Pros**:
  - Handles relevance levels (not just yes/no)
  - Could prioritize templates
  - Flexible weighting
- **Cons**:
  - **Too complex**: Need to tune weights
  - **Ambiguous**: What score threshold to use?
  - **Overkill**: Binary include/exclude is sufficient
  - **Hard to maintain**: Changing weights affects many templates
- **Why rejected**: We don't need ranked relevance, just "include or not". Binary conditions are simpler and clearer.

### Function-Based Selection (Convention over Configuration)
- **Implementation**:
  ```python
  # Each template has a Python function
  def should_include_react_agent(config):
      return (config.project_type in ['saas-web-app', 'mobile-app'] and
              config.frontend_framework in ['react-typescript', 'react-native'])
  ```
- **Pros**:
  - Maximum flexibility (full Python)
  - Type checking with mypy
  - IDE autocomplete
- **Cons**:
  - **Requires code changes**: Can't add templates without Python code
  - **Security risk**: Executing untrusted code
  - **Not data-driven**: Configuration is code, not YAML
  - **Hard for non-programmers**: Can't ask designers to write Python
- **Why rejected**: We want template selection to be data-driven (YAML), not code. This also has security implications.

## References

- **File(s)**:
  - `src/generator/selector.py:193-260` - Smart selection algorithm implementation
  - `templates/registry.yaml` - Template declarations with conditions
  - `templates/project-types/*.yaml` - Project type configurations
- **Related ADRs**:
  - ADR-0007 (YAML Configuration) - YAML format for template declarations
- **External Links**: None

## Notes

**Selection Condition Examples**:

1. **Project Type Only**:
   ```yaml
   selection_conditions:
     project_types: [saas-web-app, api-service]
   ```
   Included if project is SaaS OR API service

2. **Tech Stack Match (OR)**:
   ```yaml
   selection_conditions:
     required_any:
       backend: [python-fastapi, django, flask]
   ```
   Included if backend is FastAPI OR Django OR Flask

3. **Tech Stack Match (AND)**:
   ```yaml
   selection_conditions:
     required_all:
       database: [postgresql]
       deployment: [docker]
   ```
   Included if database is PostgreSQL AND deployment is Docker

4. **Combined (Type + Stack)**:
   ```yaml
   selection_conditions:
     project_types: [saas-web-app]
     required_any:
       frontend_framework: [react-typescript, react-javascript]
   ```
   Included if project is SaaS AND frontend is React (TypeScript OR JavaScript)

**Why Three Stages?**:
1. **Project Type**: Broad categorization (SaaS vs API vs Mobile)
2. **Required Any (OR)**: Flexible matching (FastAPI OR Django OR Flask)
3. **Required All (AND)**: Strict matching (PostgreSQL AND Docker AND Auth)

This progression from broad → flexible → strict provides good expressiveness without complexity.

**Future Enhancements**:
- Could add `excluded_if` conditions for negative matching
- Could add version constraints (`frontend_framework: react>=18`)
- Could add feature-based matching (`required_features: [authentication, payments]`)
- Could add dry-run mode to preview template selection
