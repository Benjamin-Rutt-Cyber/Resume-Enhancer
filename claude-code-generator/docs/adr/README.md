# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Claude Code Generator project.

## What are ADRs?

Architecture Decision Records document important architectural decisions made in this project, along with their context and consequences. They help new contributors understand:
- Why certain technologies were chosen
- What alternatives were considered
- What trade-offs were accepted
- How key architectural patterns evolved

## ADR Index

### Tier 1: Critical Decisions

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-jinja2-templates.md) | Use Jinja2 for Template Rendering | ✅ Accepted | 2025-11-26 |
| [0002](0002-click-cli-framework.md) | Choose Click over Typer for CLI | ✅ Accepted | 2025-11-26 |
| [0003](0003-dual-mode-analysis.md) | Dual-Mode Analysis (AI + Keyword Fallback) | ✅ Accepted | 2025-11-26 |
| [0004](0004-reusable-agent-library.md) | Reusable Agent Library Approach | ✅ Accepted | 2025-11-26 |
| [0005](0005-path-traversal-security.md) | Path Traversal Security Model | ✅ Accepted | 2025-11-26 |

### Tier 2: Important Decisions

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0006](0006-pydantic-validation.md) | Use Pydantic for Configuration Validation | ✅ Accepted | 2025-11-26 |
| [0007](0007-yaml-configuration.md) | YAML-Based Project Configuration | ✅ Accepted | 2025-11-26 |
| [0008](0008-smart-template-selection.md) | Smart Template Selection with Conditions | ✅ Accepted | 2025-11-26 |

## How to Create a New ADR

### 1. Determine if you need an ADR

Create an ADR when making:
- Significant architectural decisions
- Technology or framework choices
- Design pattern adoptions
- Security or performance decisions
- Trade-offs between competing approaches

### 2. Copy the template

```bash
cp docs/adr/template.md docs/adr/XXXX-short-title.md
```

Replace `XXXX` with the next available number (e.g., 0009) and `short-title` with a brief, hyphenated description.

### 3. Fill out the ADR

- **Title**: Use imperative mood ("Use X", "Choose Y")
- **Context**: Explain the problem objectively
- **Decision**: State clearly what was decided
- **Consequences**: Be honest about pros and cons
- **Alternatives**: Show what else was considered and why it wasn't chosen
- **References**: Link to relevant code, commits, and documentation

### 4. Get it reviewed

- Submit as part of a pull request
- Get review from at least one team member
- Ensure references are accurate and complete

### 5. Update this index

Add your ADR to the appropriate table above.

## ADR Status Lifecycle

- 🚧 **Proposed**: Under consideration, not yet implemented
- ✅ **Accepted**: Implemented and in use
- ❌ **Deprecated**: No longer recommended, but might still be in use
- ⚠️ **Superseded**: Replaced by another ADR (reference the new one)

## Further Reading

- [Michael Nygard's ADR format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - The original ADR pattern
- [ADR GitHub organization](https://adr.github.io/) - Collection of ADR resources and tooling
- [ARCHITECTURE_REVIEW.md](../../ARCHITECTURE_REVIEW.md) - Full architectural analysis of this project
