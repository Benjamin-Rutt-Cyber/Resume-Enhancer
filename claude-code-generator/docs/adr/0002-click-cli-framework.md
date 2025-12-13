---
adr: 0002
title: Choose Click over Typer for CLI
date: 2025-11-26
status: Accepted
---

# ADR-0002: Choose Click over Typer for CLI

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

The Claude Code Generator needs a command-line interface framework to:
- Support multiple commands (`init`, `list-types`, `validate`)
- Provide both interactive and non-interactive modes
- Handle command-line arguments and options
- Integrate with interactive prompting library (Questionary)
- Display formatted console output (Rich library)
- Provide good user experience with clear help messages
- Support future extensibility (plugins, additional commands)

The CLI framework must be:
- Well-maintained and widely used in the Python ecosystem
- Easy to learn for contributors
- Flexible enough to support both simple and complex interactions
- Compatible with other libraries (Questionary for prompts, Rich for output)

## Decision

We will use **Click** as the CLI framework, augmented with **Questionary** for interactive prompts and **Rich** for formatted console output.

Configuration:
- Click decorators for command structure (`@click.group()`, `@click.command()`)
- Questionary with custom styling for interactive prompts
- Rich Console for formatted output, panels, and tables
- Click's built-in options for non-interactive mode (`--name`, `--description`, `--project-type`)

## Consequences

**Positive:**
- **Industry standard**: Click powers Flask, pip, Docker Compose CLI, and many other major tools
- **Mature and stable**: 10+ years of development, battle-tested in production
- **Excellent documentation**: Comprehensive docs with many real-world examples
- **Decorator-based**: Clean, readable syntax using Python decorators
- **Flexible integration**: Works seamlessly with Questionary and Rich
- **Command groups**: Built-in support for sub-commands and nested command structures
- **Auto-generated help**: Automatic `--help` generation from docstrings and decorators
- **Testing support**: `click.testing.CliRunner` for easy CLI testing
- **Large ecosystem**: Many plugins and extensions available

**Negative:**
- **Not type-hint based**: Uses decorators instead of modern type hints (less "Pythonic" than Typer)
- **Decorator complexity**: Multiple decorators can make function signatures harder to read
- **No automatic validation**: Type validation is manual compared to Typer's Pydantic integration
- **Imperative style**: Less declarative than some modern alternatives

**Neutral:**
- **Questionary for prompts**: We chose Questionary instead of Click's built-in prompts for better UX
- **Rich for output**: Rich provides better formatting than Click's built-in echo

## Alternatives Considered

### Typer
- **Pros**:
  - Modern, type-hint based approach (more "Pythonic")
  - Built on top of Click (inherits Click's stability)
  - Automatic validation via Pydantic type hints
  - Cleaner function signatures (no decorator clutter)
  - Excellent IDE autocompletion
  - Created by FastAPI author (modern best practices)
- **Cons**:
  - Newer library (less battle-tested, smaller community)
  - Fewer real-world examples and Stack Overflow answers
  - Documentation less comprehensive than Click
  - Type hints required (can be verbose for simple cases)
  - Less flexible for complex customization scenarios
- **Why rejected**: While Typer is more modern, Click's maturity, larger community, and extensive real-world usage provide better long-term stability. The type-hint advantage doesn't outweigh Click's proven track record for this use case.

### argparse
- **Pros**:
  - Built into Python standard library (no dependency)
  - Well-documented and stable
  - Familiar to most Python developers
- **Cons**:
  - Verbose, boilerplate-heavy code
  - No built-in support for command groups or sub-commands
  - No auto-generated help text from docstrings
  - Imperative setup (lots of `add_argument()` calls)
  - Poor ergonomics compared to Click/Typer
- **Why rejected**: Too much boilerplate code for a CLI with multiple commands. Click provides significantly better developer experience with less code.

### docopt
- **Pros**:
  - Elegant approach: CLI defined in docstring
  - No decorators or setup code
  - Portable (concept works across languages)
- **Cons**:
  - No type safety or validation
  - Docstring parsing can be fragile
  - Harder to test and maintain
  - Less popular than Click (smaller community)
  - No built-in support for interactive prompts
- **Why rejected**: The docstring-parsing approach is clever but fragile. Changes to help text can break functionality. Click's explicit approach is more maintainable.

### python-fire (Google)
- **Pros**:
  - Zero boilerplate - automatically creates CLI from any Python object
  - Very fast to prototype
  - Good for simple utilities
- **Cons**:
  - Too magical - hard to understand what CLI will be generated
  - Limited control over help text and argument names
  - Not well-suited for complex CLIs with interactive flows
  - Smaller community than Click
- **Why rejected**: The "magic" approach makes it hard to create polished, professional CLIs with custom prompts and formatting. We need explicit control over the user experience.

## References

- **File(s)**:
  - `src/cli/main.py:1-200` - Main CLI implementation
  - `src/cli/main.py:37-94` - Interactive mode using Questionary
  - `src/cli/main.py:97-99` - Click group decorator
- **Related ADRs**: None
- **External Links**:
  - [Click Documentation](https://click.palletsprojects.com/)
  - [Questionary Documentation](https://questionary.readthedocs.io/)
  - [Rich Documentation](https://rich.readthedocs.io/)

## Notes

We consciously chose to use **Questionary** for interactive prompts instead of Click's built-in `click.prompt()` because:
- Better user experience with styled prompts and visual selection
- More powerful validation and answer types
- Consistent styling across all prompts

We use **Rich** for output formatting because:
- Beautiful panels, tables, and progress bars
- Markdown rendering support
- Better than Click's `echo()` for formatted output
