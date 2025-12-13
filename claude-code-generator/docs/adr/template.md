---
adr: [NUMBER]
title: [DECISION TITLE]
date: [YYYY-MM-DD]
status: Accepted | Proposed | Deprecated | Superseded
---

# ADR-[NUMBER]: [Title]

## Status

✅ Accepted | 🚧 Proposed | ❌ Deprecated | ⚠️ Superseded

**Date**: [YYYY-MM-DD]

## Context

[What is the issue we're seeing that is motivating this decision or change?]

[Describe the forces at play, including technological, political, social, and project local. These forces are probably in tension, and should be called out as such. The language in this section is value-neutral. It is simply describing facts.]

## Decision

[What is the change that we're actually proposing or have agreed to?]

[This section describes our response to these forces. It is stated in full sentences, with active voice. "We will..."]

## Consequences

**Positive:**
- [Benefit 1: What becomes easier or better with this decision?]
- [Benefit 2]
- [Benefit 3]

**Negative:**
- [Trade-off 1: What becomes harder or what do we lose?]
- [Trade-off 2]

**Neutral:**
- [Impact 1: Changes that are neither good nor bad]

## Alternatives Considered

### [Alternative 1 Name]
- **Pros**: [What are the advantages of this approach?]
- **Cons**: [What are the disadvantages?]
- **Why rejected**: [Specific reason we didn't choose this]

### [Alternative 2 Name]
- **Pros**: [What are the advantages of this approach?]
- **Cons**: [What are the disadvantages?]
- **Why rejected**: [Specific reason we didn't choose this]

## References

- **File(s)**: `path/to/file.py:line-number`
- **Related ADRs**: ADR-XXXX
- **External Links**: [Relevant documentation, blog posts, papers]
- **Commits**: [If a specific commit implements or motivates this decision]

---

## Notes for ADR Authors

**When to write an ADR:**
- Significant architectural decisions that impact the project structure
- Technology choices (frameworks, libraries, tools)
- Design patterns or approaches adopted
- Security or performance decisions
- Trade-offs between competing approaches

**How to write a good ADR:**
1. **Title**: Use imperative mood ("Use X", "Choose Y", not "Using X")
2. **Context**: Explain the problem, not the solution. Be objective.
3. **Decision**: Be clear and specific about what was decided
4. **Consequences**: Be honest about trade-offs. Every decision has pros and cons.
5. **Alternatives**: Show you considered other options. Explain why they weren't chosen.
6. **References**: Link to code, commits, and related documentation

**Status lifecycle:**
- 🚧 **Proposed**: Under consideration, not yet implemented
- ✅ **Accepted**: Implemented and in use
- ❌ **Deprecated**: No longer recommended, but might still be in use
- ⚠️ **Superseded**: Replaced by another ADR (reference it)

**Numbering:**
- Use 4-digit format: 0001, 0002, etc.
- Never reuse or skip numbers
- Number sequentially in order of creation (not priority)
