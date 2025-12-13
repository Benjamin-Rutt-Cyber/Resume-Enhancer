---
adr: 0001
title: Use Jinja2 for Template Rendering
date: 2025-11-26
status: Accepted
---

# ADR-0001: Use Jinja2 for Template Rendering

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

The Claude Code Generator needs a template engine to:
- Generate agent files with project-specific context (`.md.j2` templates)
- Generate skill documentation with variable substitution
- Create boilerplate code for different tech stacks (Python, Node, React, etc.)
- Render README files and other documentation
- Transform project names into different case formats (slug, PascalCase, snake_case, camelCase)

The template engine must support:
- Variable interpolation and context injection
- Custom filters for text transformations
- Conditional logic and loops
- File-based and string-based template rendering
- Clear error messages for debugging template issues
- Good performance for generating 40+ files per project

## Decision

We will use **Jinja2** as the template rendering engine for all code and documentation generation.

Jinja2 is configured with:
- `trim_blocks=True` and `lstrip_blocks=True` for clean output without extra whitespace
- `keep_trailing_newline=True` to preserve file formatting
- Custom filters: `slugify`, `pascal_case`, `snake_case`, `camel_case` for name transformations
- Comprehensive error handling for TemplateNotFound, TemplateSyntaxError, and UndefinedError

## Consequences

**Positive:**
- **Mature and battle-tested**: Jinja2 is the de facto standard for Python templating, used by Flask, Ansible, Salt, and many others
- **Powerful features**: Supports template inheritance, macros, filters, tests, and control structures
- **Python-native**: No additional language to learn, seamless integration with Python ecosystem
- **Excellent error messages**: Clear stack traces and line numbers when templates fail
- **Rich filter system**: Built-in filters + easy to add custom filters for domain-specific transformations
- **Active community**: Large ecosystem, extensive documentation, and active maintenance
- **Performance**: Compiled templates with good caching support

**Negative:**
- **Syntax can be verbose**: `{{ variable }}` and `{% control %}` syntax is more verbose than some alternatives
- **Learning curve**: New contributors need to learn Jinja2 syntax in addition to Python
- **Template escaping**: Need to be careful with auto-escaping in non-HTML contexts
- **Dependency**: Adds jinja2 as a required dependency (~200KB)

**Neutral:**
- **Template files use `.j2` extension**: Clear distinction between static and template files

## Alternatives Considered

### Mustache (via pystache)
- **Pros**:
  - Logic-less templates are simpler and more portable across languages
  - Minimal syntax: just `{{variable}}` and `{{#section}}...{{/section}}`
  - No way to put complex logic in templates (forces logic into code)
- **Cons**:
  - Too simple for our needs - no custom filters or transformations
  - Would require extensive pre-processing of context data
  - Poor error messages
  - Less popular in Python ecosystem
- **Why rejected**: Cannot express case transformations (PascalCase, snake_case) without extensive pre-computation. Too restrictive for code generation use case.

### Mako
- **Pros**:
  - More powerful than Jinja2 - allows embedded Python code
  - Slightly faster performance
  - Used by Pyramid framework
- **Cons**:
  - Less popular than Jinja2 (smaller community, fewer resources)
  - Allowing Python code in templates can lead to poor separation of concerns
  - Different syntax from Jinja2 (less transferable knowledge)
  - Smaller ecosystem of filters and extensions
- **Why rejected**: The extra power isn't needed and could encourage bad practices (logic in templates). Jinja2's popularity and ecosystem outweigh minor performance benefits.

### String Formatting (f-strings, .format(), Template)
- **Pros**:
  - No dependencies - built into Python
  - Maximum performance
  - Simple for basic variable substitution
- **Cons**:
  - No template inheritance or includes
  - No filters or transformations
  - No control structures (loops, conditionals)
  - Would require building our own mini-framework
  - Poor readability for multi-line templates
- **Why rejected**: Not suitable for complex multi-line templates with conditional logic. Would end up reinventing Jinja2 poorly.

### Genshi (XML-based)
- **Pros**:
  - XML-based approach good for HTML generation
  - Template validation via XML schema
- **Cons**:
  - XML syntax is verbose and awkward for non-HTML content
  - Not well-suited for code generation or markdown
  - Less actively maintained
  - Steep learning curve
- **Why rejected**: Optimized for HTML/XML generation, not general-purpose text/code templates. Would be awkward for Python code, markdown, and YAML generation.

## References

- **File(s)**: `src/generator/renderer.py:1-170`
- **Usage**: `src/generator/file_generator.py:241-254` (agent rendering), `src/generator/boilerplate_generator.py` (code generation)
- **External Links**:
  - [Jinja2 Documentation](https://jinja.palletsprojects.com/)
  - [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
