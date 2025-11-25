---
name: python-cli
description: Expert knowledge in building Python command-line interfaces using Click, Typer, Questionary, and Rich libraries. Use this skill when implementing CLI commands, handling user input, creating interactive prompts, formatting terminal output, parsing arguments, or working with CLI applications. This skill provides patterns, best practices, and code examples for robust, user-friendly command-line tools.
allowed-tools: [Read, Write, Bash]
---

# Python CLI Development Skill

Comprehensive knowledge for building professional Python CLI applications with Click, Typer, Questionary, and Rich.

## Core Libraries and Their Uses

### Click - Command-Line Interface Framework

**When to use:**
- Building complex CLI applications with multiple commands
- Need for command groups and subcommands
- Automatic help text generation
- Type conversion and validation
- Progress bars and prompts

**Basic Structure:**
```python
import click

@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, verbose):
    """My CLI Application."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

@cli.command()
@click.option('--name', '-n', required=True, help='Your name')
@click.option('--count', '-c', default=1, type=int, help='Repeat count')
@click.pass_context
def greet(ctx, name, count):
    """Greet someone."""
    for _ in range(count):
        message = f"Hello, {name}!"
        if ctx.obj.get('verbose'):
            click.echo(f"[VERBOSE] {message}")
        else:
            click.echo(message)

if __name__ == '__main__':
    cli()
```

**Key Patterns:**

1. **Command Groups:**
```python
@click.group()
def cli():
    """Main CLI entry point."""
    pass

@cli.group()
def db():
    """Database commands."""
    pass

@db.command()
def migrate():
    """Run migrations."""
    click.echo("Running migrations...")

@db.command()
def seed():
    """Seed database."""
    click.echo("Seeding database...")

# Usage: cli db migrate, cli db seed
```

2. **Context Passing:**
```python
@click.group()
@click.option('--config', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config) if config else {}

@cli.command()
@click.pass_context
def status(ctx):
    config = ctx.obj['config']
    click.echo(f"Config loaded: {config}")
```

3. **Custom Types:**
```python
class EmailType(click.ParamType):
    name = 'email'

    def convert(self, value, param, ctx):
        if '@' not in value:
            self.fail(f'{value} is not a valid email', param, ctx)
        return value

EMAIL = EmailType()

@click.command()
@click.option('--email', type=EMAIL, required=True)
def register(email):
    click.echo(f"Registering: {email}")
```

4. **Callbacks and Validation:**
```python
def validate_port(ctx, param, value):
    if not 1 <= value <= 65535:
        raise click.BadParameter('Port must be between 1 and 65535')
    return value

@click.command()
@click.option('--port', type=int, callback=validate_port, default=8000)
def serve(port):
    click.echo(f"Serving on port {port}")
```

5. **Multiple Values:**
```python
@click.command()
@click.option('--tag', '-t', multiple=True, help='Add tag (can be repeated)')
@click.option('--exclude', '-e', multiple=True, help='Exclude patterns')
def build(tag, exclude):
    click.echo(f"Tags: {', '.join(tag)}")
    click.echo(f"Excluding: {', '.join(exclude)}")

# Usage: cli build -t python -t web -e tests -e docs
```

6. **File Handling:**
```python
@click.command()
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
def process(input, output):
    """Process file (stdin/stdout by default)."""
    for line in input:
        output.write(line.upper())

# Usage: cli process < input.txt > output.txt
```

7. **Path Handling:**
```python
@click.command()
@click.option('--config', type=click.Path(exists=True, dir_okay=False))
@click.option('--output', type=click.Path(dir_okay=True, writable=True))
def export(config, output):
    config_path = Path(config) if config else Path.cwd() / 'config.yml'
    output_path = Path(output) if output else Path.cwd()
    click.echo(f"Exporting from {config_path} to {output_path}")
```

### Questionary - Interactive Prompts

**When to use:**
- Interactive configuration
- User-friendly prompts
- Multiple choice selections
- Form-like input collection

**Basic Patterns:**

1. **Text Input:**
```python
import questionary

name = questionary.text(
    "What's your name?",
    validate=lambda text: len(text) > 0 or "Name cannot be empty"
).ask()

email = questionary.text(
    "Your email:",
    validate=lambda text: '@' in text or "Invalid email"
).ask()
```

2. **Select (Single Choice):**
```python
framework = questionary.select(
    "Choose your backend framework:",
    choices=[
        'Python / FastAPI',
        'Python / Django',
        'Node.js / Express',
        'Go / Gin',
        'Ruby / Rails'
    ]
).ask()
```

3. **Checkbox (Multiple Choice):**
```python
features = questionary.checkbox(
    "Select features to include:",
    choices=[
        questionary.Choice('Authentication', checked=True),
        questionary.Choice('Payment Processing'),
        questionary.Choice('Real-time Features'),
        questionary.Choice('Background Jobs'),
        questionary.Choice('API Documentation', checked=True),
    ]
).ask()
```

4. **Confirm:**
```python
confirmed = questionary.confirm(
    "Generate project structure?",
    default=True
).ask()

if not confirmed:
    click.echo("Cancelled")
    sys.exit(0)
```

5. **Password:**
```python
password = questionary.password(
    "Enter password:",
    validate=lambda pwd: len(pwd) >= 8 or "Password must be at least 8 characters"
).ask()
```

6. **Path:**
```python
directory = questionary.path(
    "Choose output directory:",
    only_directories=True,
    default=str(Path.cwd())
).ask()
```

7. **Custom Styling:**
```python
from questionary import Style

custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),        # Question mark color
    ('question', 'bold'),                 # Question text
    ('answer', 'fg:#f44336 bold'),       # User's answer
    ('pointer', 'fg:#673ab7 bold'),      # Selection pointer
    ('highlighted', 'fg:#673ab7 bold'),  # Highlighted choice
    ('selected', 'fg:#cc5454'),          # Selected choice
    ('separator', 'fg:#cc5454'),         # Separator
    ('instruction', ''),                  # Instruction text
    ('text', ''),                         # Plain text
])

result = questionary.select(
    "Choose option:",
    choices=['Option 1', 'Option 2'],
    style=custom_style
).ask()
```

8. **Conditional Prompts:**
```python
project_type = questionary.select(
    "Project type:",
    choices=['Web App', 'API Service', 'CLI Tool']
).ask()

if project_type == 'Web App':
    frontend = questionary.select(
        "Frontend framework:",
        choices=['React', 'Vue', 'Svelte']
    ).ask()
```

### Rich - Terminal Formatting

**When to use:**
- Beautiful terminal output
- Progress bars and spinners
- Tables and panels
- Syntax highlighting
- Tree views

**Basic Patterns:**

1. **Console Output:**
```python
from rich.console import Console

console = Console()

# Styled text
console.print("[bold green]Success![/bold green]")
console.print("[red]Error:[/red] Something went wrong")
console.print("[yellow]⚠ Warning[/yellow]")

# Emoji support
console.print("✨ [bold cyan]Generating project...[/bold cyan]")

# Multiple styles
console.print("[bold underline]Important Message[/bold underline]")
```

2. **Progress Bars:**
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:

    task1 = progress.add_task("[cyan]Downloading...", total=100)
    task2 = progress.add_task("[green]Processing...", total=100)

    while not progress.finished:
        progress.update(task1, advance=0.5)
        progress.update(task2, advance=0.3)
        time.sleep(0.02)
```

3. **Spinners (Indeterminate Progress):**
```python
from rich.console import Console
from rich.spinner import Spinner

console = Console()

with console.status("[bold green]Analyzing project...") as status:
    # Do work here
    time.sleep(2)
    status.update("[bold blue]Selecting templates...")
    time.sleep(2)
    status.update("[bold yellow]Rendering files...")
    time.sleep(2)

console.print("[bold green]✓ Complete!")
```

4. **Tables:**
```python
from rich.table import Table

table = Table(title="Project Configuration", show_header=True, header_style="bold magenta")

table.add_column("Property", style="cyan", no_wrap=True)
table.add_column("Value", style="green")

table.add_row("Project Name", "My SaaS App")
table.add_row("Type", "saas-web-app")
table.add_row("Backend", "Python / FastAPI")
table.add_row("Frontend", "React / TypeScript")
table.add_row("Database", "PostgreSQL")

console.print(table)
```

5. **Panels:**
```python
from rich.panel import Panel

console.print(Panel(
    "[bold]Next Steps:[/bold]\n\n"
    "1. cd your-project-name\n"
    "2. Run: /setup-dev\n"
    "3. Start coding!",
    title="🎉 Success",
    border_style="green"
))
```

6. **Trees:**
```python
from rich.tree import Tree

tree = Tree("📁 [bold]my-project/[/bold]")

claude = tree.add("📁 .claude/")
claude.add("📄 agents/api-agent.md")
claude.add("📄 agents/frontend-agent.md")
claude.add("📁 skills/")

src = tree.add("📁 src/")
src.add("📁 backend/")
src.add("📁 frontend/")

tree.add("📄 README.md")
tree.add("📄 docker-compose.yml")

console.print(tree)
```

7. **Syntax Highlighting:**
```python
from rich.syntax import Syntax

code = '''
def hello(name: str) -> None:
    print(f"Hello, {name}!")
'''

syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)
```

8. **Live Display (Real-time Updates):**
```python
from rich.live import Live
from rich.table import Table
import time

def generate_table():
    table = Table()
    table.add_column("Status")
    table.add_column("Count")
    return table

with Live(generate_table(), refresh_per_second=4) as live:
    for i in range(20):
        time.sleep(0.4)
        table = generate_table()
        table.add_row("Processing", str(i))
        live.update(table)
```

9. **Markdown Rendering:**
```python
from rich.markdown import Markdown

markdown_text = """
# Project Generated Successfully

## Next Steps
1. Review the generated files
2. Run tests
3. Start development

> **Note:** Make sure to review the security settings
"""

console.print(Markdown(markdown_text))
```

## Common CLI Patterns

### 1. Interactive vs Non-Interactive Mode

```python
@click.command()
@click.option('--project', help='Project name')
@click.option('--type', 'project_type', help='Project type')
@click.option('--interactive/--no-interactive', default=True)
def init(project, project_type, interactive):
    """Initialize project."""

    if interactive and not (project and project_type):
        # Launch interactive mode
        project = questionary.text("Project name:").ask()
        project_type = questionary.select(
            "Project type:",
            choices=['saas', 'api', 'mobile']
        ).ask()
    elif not (project and project_type):
        # Required in non-interactive mode
        raise click.UsageError(
            "In non-interactive mode, --project and --type are required"
        )

    # Proceed with generation
    console.print(f"[green]Creating {project_type} project: {project}[/green]")
```

### 2. Configuration Loading

```python
import os
from pathlib import Path
import yaml

def load_config(config_path=None):
    """Load configuration from file or environment."""

    # Priority: CLI arg > env var > default location
    if config_path:
        config_file = Path(config_path)
    elif os.getenv('MY_CLI_CONFIG'):
        config_file = Path(os.getenv('MY_CLI_CONFIG'))
    else:
        config_file = Path.home() / '.my-cli' / 'config.yml'

    if config_file.exists():
        return yaml.safe_load(config_file.read_text())

    return {}

@click.group()
@click.option('--config', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
```

### 3. Error Handling with Rich

```python
from rich.panel import Panel
import sys

def handle_error(error: Exception, verbose: bool = False):
    """Display user-friendly error message."""

    console.print(Panel(
        f"[bold red]Error:[/bold red] {str(error)}\n\n"
        f"[yellow]Suggestion:[/yellow] Check your input and try again.",
        title="❌ Error",
        border_style="red"
    ))

    if verbose:
        console.print_exception()

    sys.exit(1)

try:
    # Some operation
    pass
except ValueError as e:
    handle_error(e, verbose=ctx.obj.get('verbose', False))
```

### 4. Confirmation for Destructive Actions

```python
@click.command()
@click.option('--force', is_flag=True, help='Skip confirmation')
def delete(force):
    """Delete all data."""

    if not force:
        confirmed = questionary.confirm(
            "⚠️  This will delete all data. Continue?",
            default=False
        ).ask()

        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            return

    console.print("[red]Deleting all data...[/red]")
```

### 5. Progress Reporting

```python
def process_files(files):
    """Process multiple files with progress bar."""

    with Progress() as progress:
        task = progress.add_task("[cyan]Processing files...", total=len(files))

        for file in files:
            # Process file
            process_file(file)
            progress.update(task, advance=1)

    console.print("[green]✓ All files processed[/green]")
```

## Testing CLI Applications

```python
from click.testing import CliRunner

def test_cli_command():
    """Test CLI command."""
    runner = CliRunner()

    # Test with arguments
    result = runner.invoke(cli, ['init', '--project', 'test', '--type', 'saas', '--no-interactive'])

    assert result.exit_code == 0
    assert 'Creating' in result.output

def test_interactive_mode():
    """Test interactive mode."""
    runner = CliRunner()

    # Simulate user input
    result = runner.invoke(cli, ['init'], input='My Project\n1\n')

    assert result.exit_code == 0

def test_error_handling():
    """Test error message."""
    runner = CliRunner()

    result = runner.invoke(cli, ['init', '--type', 'invalid'])

    assert result.exit_code != 0
    assert 'Error' in result.output
```

## Best Practices

1. **Always provide help text**
```python
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def command(verbose):
    """Clear command description here."""
    pass
```

2. **Use sensible defaults**
```python
@click.option('--port', default=8000, help='Server port (default: 8000)')
@click.option('--workers', default=4, help='Number of workers')
```

3. **Validate input early**
```python
@click.option('--email', callback=validate_email, required=True)
```

4. **Provide clear error messages**
```python
if not api_key:
    console.print(Panel(
        "[red]API key not found[/red]\n\n"
        "Set via:\n"
        "• Environment variable: export API_KEY=...\n"
        "• Config file: ~/.config/myapp/config.yml\n"
        "• Command flag: --api-key=...",
        border_style="red"
    ))
    sys.exit(1)
```

5. **Support both interactive and non-interactive modes**
```python
# Allow automation: cli init --project test --type saas --no-interactive
# Also allow exploration: cli init (launches interactive prompts)
```

6. **Use progress indicators for long operations**
```python
with console.status("[bold green]Processing...") as status:
    # Long operation
    pass
```

7. **Consistent styling**
```python
# Define color scheme once
SUCCESS = "green"
ERROR = "red"
WARNING = "yellow"
INFO = "cyan"

console.print(f"[{SUCCESS}]✓ Success[/{SUCCESS}]")
console.print(f"[{ERROR}]✗ Error[/{ERROR}]")
```

## Available Resources

- `examples/cli_example.py` - Full CLI application example
- `examples/interactive_example.py` - Interactive prompts example
- `examples/rich_output_example.py` - Rich formatting examples

## Quick Reference

**Click decorators:**
- `@click.command()` - Define command
- `@click.group()` - Define command group
- `@click.option()` - Add option
- `@click.argument()` - Add argument
- `@click.pass_context` - Pass context object

**Questionary prompts:**
- `questionary.text()` - Text input
- `questionary.select()` - Single choice
- `questionary.checkbox()` - Multiple choice
- `questionary.confirm()` - Yes/No
- `questionary.password()` - Password input
- `questionary.path()` - File/directory path

**Rich components:**
- `console.print()` - Styled output
- `Progress()` - Progress bars
- `Table()` - Tables
- `Panel()` - Bordered panels
- `Tree()` - Tree views
- `Syntax()` - Code highlighting
- `Markdown()` - Markdown rendering
