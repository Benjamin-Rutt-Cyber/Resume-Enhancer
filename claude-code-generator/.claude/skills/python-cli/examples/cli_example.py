"""
Complete CLI application example using Click + Questionary + Rich
"""
import click
import questionary
from questionary import Style
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from pathlib import Path
import sys

console = Console()

# Custom Questionary style
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
])


@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, verbose):
    """Example CLI Application - Demonstrates Click + Questionary + Rich."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.option('--project', '-p', help='Project name')
@click.option('--type', '-t', 'project_type',
              type=click.Choice(['web', 'api', 'cli']),
              help='Project type')
@click.option('--interactive/--no-interactive', default=True)
@click.pass_context
def init(ctx, project, project_type, interactive):
    """Initialize a new project."""

    console.print("\n[bold green]🎯 Project Initializer[/bold green]\n")

    # Interactive mode
    if interactive and not (project and project_type):
        project = questionary.text(
            "What's your project name?",
            validate=lambda text: len(text) > 0 or "Name cannot be empty",
            style=custom_style
        ).ask()

        project_type = questionary.select(
            "What type of project?",
            choices=['Web Application', 'API Service', 'CLI Tool'],
            style=custom_style
        ).ask()

        features = questionary.checkbox(
            "Select features:",
            choices=[
                'Authentication',
                'Database',
                'API Documentation',
                'Testing'
            ],
            style=custom_style
        ).ask()

        confirmed = questionary.confirm(
            f"Create '{project}' project?",
            default=True,
            style=custom_style
        ).ask()

        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            return

    # Non-interactive mode validation
    elif not (project and project_type):
        raise click.UsageError(
            "In non-interactive mode, --project and --type are required"
        )
    else:
        features = []

    # Show configuration
    table = Table(title="Project Configuration", show_header=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Name", project)
    table.add_row("Type", project_type)
    table.add_row("Features", ', '.join(features) if features else 'None')

    console.print(table)

    # Simulate project creation with progress
    create_project(project, project_type, features, ctx.obj.get('verbose', False))


def create_project(name, project_type, features, verbose):
    """Create project with progress indication."""

    tasks_list = [
        "Creating directory structure",
        "Generating configuration files",
        "Setting up dependencies",
        "Initializing git repository",
        "Creating README"
    ]

    with Progress() as progress:
        task = progress.add_task("[cyan]Creating project...", total=len(tasks_list))

        for task_name in tasks_list:
            if verbose:
                console.print(f"[dim]→ {task_name}[/dim]")

            # Simulate work
            import time
            time.sleep(0.3)

            progress.update(task, advance=1)

    # Success message
    console.print("\n[bold green]✓ Project created successfully![/bold green]\n")

    # Show next steps
    panel = Panel(
        f"[bold]Next Steps:[/bold]\n\n"
        f"1. cd {name}\n"
        f"2. Install dependencies: pip install -r requirements.txt\n"
        f"3. Start development!\n\n"
        f"[dim]Run 'cli help' for more commands[/dim]",
        title="🎉 Success",
        border_style="green"
    )
    console.print(panel)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
def list(path, format):
    """List files in a directory."""

    path_obj = Path(path)

    if not path_obj.is_dir():
        console.print(f"[red]Error: {path} is not a directory[/red]")
        sys.exit(1)

    files = list(path_obj.iterdir())

    if format == 'table':
        table = Table(title=f"Contents of {path}", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Size", style="green")

        for file in sorted(files):
            file_type = "📁 Directory" if file.is_dir() else "📄 File"
            size = f"{file.stat().st_size:,} bytes" if file.is_file() else "-"
            table.add_row(file.name, file_type, size)

        console.print(table)

    else:  # JSON format
        import json
        data = [
            {
                "name": f.name,
                "type": "directory" if f.is_dir() else "file",
                "size": f.stat().st_size if f.is_file() else None
            }
            for f in sorted(files)
        ]
        console.print(json.dumps(data, indent=2))


@cli.command()
@click.option('--force', is_flag=True, help='Skip confirmation')
def cleanup(force):
    """Clean up temporary files."""

    if not force:
        confirmed = questionary.confirm(
            "⚠️  This will delete temporary files. Continue?",
            default=False,
            style=custom_style
        ).ask()

        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            return

    with console.status("[bold yellow]Cleaning up..."):
        import time
        time.sleep(1)  # Simulate cleanup

    console.print("[green]✓ Cleanup complete[/green]")


if __name__ == '__main__':
    cli()
