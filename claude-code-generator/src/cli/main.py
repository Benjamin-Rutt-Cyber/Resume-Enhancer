"""
Claude Code Generator CLI - Main entry point.
"""

import click
import sys
from pathlib import Path
import os
from typing import Optional, Dict, List
import questionary
from questionary import Style

from src.generator.analyzer import ProjectAnalyzer, ProjectConfig
from src.generator.selector import TemplateSelector
from src.generator.file_generator import FileGenerator
from src.generator.ai_generator import AIGenerationConfig
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint


def _create_console() -> Console:
    """Create console with Windows compatibility."""
    import platform

    if platform.system() == 'Windows':
        return Console(
            force_terminal=True,
            force_interactive=True,
            legacy_windows=False
        )
    return Console()


console = _create_console()

# Custom style for questionary prompts
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
])


def _safe_prompt(prompt_func, error_context: str):
    """
    Safely execute a questionary prompt with error handling.

    Args:
        prompt_func: Questionary prompt function to execute
        error_context: Context description for error messages

    Returns:
        Prompt result or None if error occurred
    """
    try:
        return prompt_func.ask()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except EOFError:
        console.print(
            f"\n[red]Error: {error_context} failed (terminal disconnected)[/red]"
        )
        console.print("[yellow]Try using command-line arguments instead:[/yellow]")
        console.print("  claude-gen init --project 'NAME' --description 'DESC'")
        sys.exit(1)
    except Exception as e:
        console.print(
            f"\n[red]Error: {error_context} failed[/red]"
        )
        console.print(f"[dim]Details: {e}[/dim]")
        console.print("\n[yellow]Your terminal may not support interactive mode.[/yellow]")
        console.print("[yellow]Use command-line arguments instead:[/yellow]")
        console.print("  claude-gen init --project 'NAME' --description 'DESC'")
        sys.exit(1)


def _check_terminal_compatibility() -> tuple[bool, str]:
    """
    Check if terminal supports interactive prompts.

    Returns:
        (is_compatible, reason) tuple
    """
    import sys
    import os

    # Check if stdin is a TTY
    if not sys.stdin.isatty():
        return False, "stdin is not a TTY (running in pipe/redirect)"

    # Check for CI/CD environment variables
    ci_vars = ['CI', 'JENKINS', 'TRAVIS', 'CIRCLECI', 'GITHUB_ACTIONS']
    if any(os.getenv(var) for var in ci_vars):
        return False, "running in CI/CD environment"

    # Check for dumb terminal
    if os.getenv('TERM') == 'dumb':
        return False, "TERM is set to 'dumb'"

    return True, ""


def _interactive_mode() -> tuple[str, str, Optional[str], bool]:
    """Run interactive project configuration."""
    # Check terminal compatibility first
    is_compatible, reason = _check_terminal_compatibility()
    if not is_compatible:
        console.print(f"\n[red]Cannot use interactive mode: {reason}[/red]")
        console.print("[yellow]Use command-line arguments instead:[/yellow]")
        console.print("  claude-gen init --project 'NAME' --description 'DESCRIPTION'")
        sys.exit(1)

    console.print("\n[bold green]Claude Code Project Generator[/bold green]")
    console.print("[dim]Answer a few questions to generate your project...[/dim]\n")

    # Project name
    project_name = _safe_prompt(
        questionary.text(
            "What's your project name?",
            validate=lambda text: len(text) >= 3 or "Project name must be at least 3 characters",
            style=custom_style
        ),
        "Project name input"
    )

    # Project description
    description = _safe_prompt(
        questionary.text(
            "Describe your project (be detailed):",
            validate=lambda text: len(text) >= 10 or "Please provide more detail (10+ characters)",
            style=custom_style
        ),
        "Project description input"
    )

    # Project type
    project_type_choice = _safe_prompt(
        questionary.select(
            "What type of project is this?",
            choices=[
                questionary.Choice("SaaS Web Application (Full-stack app with auth, payments, APIs)", value='saas-web-app'),
                questionary.Choice("API/Backend Service (RESTful API or microservice)", value='api-service'),
                questionary.Choice("Mobile Application (React Native, Flutter, or native)", value='mobile-app'),
                questionary.Choice("Hardware/IoT Device (Embedded systems, firmware, sensors)", value='hardware-iot'),
                questionary.Choice("Data Science Project (ML/AI, Jupyter notebooks, analysis)", value='data-science'),
                questionary.Choice("Auto-detect from description", value=None),
            ],
            style=custom_style
        ),
        "Project type selection"
    )

    # Auto-detect confirmation
    if project_type_choice is None:
        auto_detect_confirm = _safe_prompt(
            questionary.confirm(
                "Let AI analyze your description to determine the best project type?",
                default=True,
                style=custom_style
            ),
            "Auto-detect confirmation"
        )
        project_type = None if auto_detect_confirm else 'saas-web-app'
    else:
        project_type = project_type_choice

    # Generate boilerplate code?
    with_code = _safe_prompt(
        questionary.confirm(
            "Generate starter code/boilerplate for your tech stack?",
            default=False,
            style=custom_style
        ),
        "Boilerplate confirmation"
    )

    return project_name, description, project_type, with_code


@click.group()
@click.version_option(version="0.2.0")
def cli() -> None:
    """
    Claude Code Generator - Create complete Claude Code environments.

    Generate project structures with agents, skills, commands, and documentation
    tailored to your project type.
    """
    pass


@cli.command()
@click.option(
    '--project',
    '-p',
    help='Name of your project'
)
@click.option(
    '--description',
    '-d',
    help='Describe your project in a few sentences'
)
@click.option(
    '--type',
    '-t',
    'project_type',
    type=click.Choice([
        'saas-web-app',
        'api-service',
        'mobile-app',
        'hardware-iot',
        'data-science'
    ]),
    help='Project type (will auto-detect if not specified)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output directory (defaults to project slug)'
)
@click.option(
    '--overwrite',
    is_flag=True,
    help='Overwrite existing files'
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    help='Skip confirmation prompts (auto-accept all)'
)
@click.option(
    '--interactive',
    is_flag=True,
    help='Use interactive mode with guided prompts'
)
@click.option(
    '--no-ai',
    is_flag=True,
    help='Skip AI analysis, use keyword detection only'
)
@click.option(
    '--no-plugins',
    is_flag=True,
    help='Skip plugin recommendations'
)
@click.option(
    '--no-ai-plugins',
    is_flag=True,
    help='Skip AI-based plugin analysis (keep project-type recommendations)'
)
@click.option(
    '--with-code',
    is_flag=True,
    help='Generate starter code/boilerplate for the project'
)
@click.option(
    '--with-ai-agents',
    is_flag=True,
    help='Enable AI-generated custom agents/skills for novel domains (requires API key)'
)
@click.option(
    '--ai-threshold',
    type=int,
    default=30,
    help='Minimum uniqueness score (0-100) to trigger AI generation (default: 30)'
)
@click.option(
    '--no-cache',
    'no_ai_cache',
    is_flag=True,
    help='Bypass cache and force fresh AI generation'
)
@click.option(
    '--show-ai-stats',
    is_flag=True,
    help='Display detailed AI generation statistics'
)
def init(
    project: Optional[str],
    description: Optional[str],
    project_type: Optional[str],
    output: Optional[str],
    overwrite: bool,
    yes: bool,
    interactive: bool,
    no_ai: bool,
    no_plugins: bool,
    no_ai_plugins: bool,
    with_code: bool,
    with_ai_agents: bool,
    ai_threshold: int,
    no_ai_cache: bool,
    show_ai_stats: bool
) -> None:
    """
    Initialize a new Claude Code project.

    Analyzes your project description and generates a complete Claude Code
    environment with appropriate agents, skills, commands, and documentation.

    Examples:

        \b
        # Interactive mode
        claude-gen init

        \b
        # With all options
        claude-gen init --project "My SaaS App" \
                       --description "A project management SaaS platform" \
                       --type saas-web-app \
                       --output ./my-saas-app

        \b
        # Generate with starter code/boilerplate
        claude-gen init --project "FastAPI Backend" \
                       --description "REST API with FastAPI and PostgreSQL" \
                       --with-code

        \b
        # Let AI detect project type
        claude-gen init --project "IoT Sensor" \
                       --description "Temperature monitoring with Pico W"
    """
    # Interactive mode
    if interactive or (not project and not description):
        project, description, project_type, with_code = _interactive_mode()
        # In interactive mode, always assume user wants to proceed
        yes = True

    # Validate required fields
    if not project or not description:
        missing = []
        if not project:
            missing.append("--project")
        if not description:
            missing.append("--description")

        console.print(f"[bold red]Error:[/bold red] Missing required arguments: {', '.join(missing)}")
        console.print("\n[bold]Options:[/bold]")
        console.print("  1. Provide both arguments:")
        console.print("     [cyan]claude-gen init --project 'NAME' --description 'DESCRIPTION'[/cyan]")
        console.print("  2. Use interactive mode:")
        console.print("     [cyan]claude-gen init --interactive[/cyan]")
        sys.exit(1)

    console.print(Panel.fit(
        "[bold blue]Claude Code Generator[/bold blue]\n"
        "Creating your project environment...",
        border_style="blue"
    ))

    try:
        # Get templates directory
        templates_dir = Path(__file__).parent.parent.parent / 'templates'

        # Initialize analyzer
        api_key = None if no_ai else os.getenv('ANTHROPIC_API_KEY')
        if not api_key and not no_ai:
            console.print(
                "[yellow]Warning: ANTHROPIC_API_KEY not found. "
                "Using keyword-based detection.[/yellow]"
            )

        analyzer = ProjectAnalyzer(api_key=api_key)

        # Analyze project
        with console.status("[bold green]Analyzing project..."):
            config = analyzer.analyze(description, project_name=project)

            # Override project type if specified
            if project_type:
                config.project_type = project_type

        # Display analysis results
        console.print("\n[bold green][OK][/bold green] Project analyzed successfully!")
        _display_config(config)

        # Confirm generation (skip if --yes flag is set)
        if not yes:
            if not click.confirm('\nGenerate project with this configuration?', default=True):
                console.print("[yellow]Generation cancelled.[/yellow]")
                return

        # Determine output directory
        if not output:
            output = Path.cwd() / config.project_slug
        else:
            output = Path(output)

        # Initialize AI generation config if enabled
        ai_config = None
        if with_ai_agents:
            # Check for API key
            if not api_key:
                console.print(
                    "[yellow]Warning: AI agent generation requires ANTHROPIC_API_KEY. "
                    "Falling back to library templates.[/yellow]"
                )
            ai_config = AIGenerationConfig(
                enabled=with_ai_agents,
                threshold=ai_threshold,
                use_cache=not no_ai_cache,
                show_stats=show_ai_stats,
                api_key=api_key
            )

        # Initialize file generator
        generator = FileGenerator(templates_dir, api_key=api_key, ai_config=ai_config)

        # Generate project
        with console.status(f"[bold green]Generating project at {output}..."):
            created_files = generator.generate_project(
                config,
                output,
                overwrite=overwrite,
                recommend_plugins=not no_plugins,
                use_ai_plugins=not no_ai_plugins,
                generate_boilerplate=with_code,
            )

        # Display results
        _display_results(output, created_files)

        # Display plugin recommendations
        if not no_plugins:
            _display_plugin_recommendations(output, no_ai_plugins)

        # Display AI generation statistics
        if with_ai_agents and (show_ai_stats or generator.ai_generator):
            _display_ai_stats(generator, show_ai_stats)

        # Next steps
        _display_next_steps(output, with_boilerplate=with_code)

    except FileExistsError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("Use --overwrite to overwrite existing files.")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    '--templates-dir',
    type=click.Path(exists=True),
    help='Path to templates directory'
)
def list_types(templates_dir: Optional[str]) -> None:
    """List available project types."""
    if not templates_dir:
        templates_dir = Path(__file__).parent.parent.parent / 'templates'
    else:
        templates_dir = Path(templates_dir)

    selector = TemplateSelector(templates_dir)
    types = selector.list_available_project_types()

    table = Table(title="Available Project Types", show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Description")

    for ptype in types:
        table.add_row(
            ptype['name'],
            ptype['display_name'],
            ptype['description']
        )

    console.print(table)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def validate(path: str) -> None:
    """Validate a generated project structure."""
    path = Path(path)

    console.print(f"Validating project at: {path}")

    checks = {
        '.claude directory': (path / '.claude').exists(),
        '.claude/agents': (path / '.claude' / 'agents').exists(),
        '.claude/skills': (path / '.claude' / 'skills').exists(),
        '.claude/commands': (path / '.claude' / 'commands').exists(),
        'README.md': (path / 'README.md').exists(),
        'docs directory': (path / 'docs').exists(),
    }

    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status")

    all_passed = True
    for check_name, passed in checks.items():
        status = "[green][PASS][/green]" if passed else "[red][FAIL][/red]"
        table.add_row(check_name, status)
        if not passed:
            all_passed = False

    console.print(table)

    if all_passed:
        console.print("\n[bold green][OK] All checks passed![/bold green]")
    else:
        console.print("\n[bold red][FAIL] Some checks failed[/bold red]")
        sys.exit(1)


def _display_config(config: ProjectConfig) -> None:
    """Display project configuration."""
    table = Table(title="Project Configuration", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Project Name", config.project_name)
    table.add_row("Project Slug", config.project_slug)
    table.add_row("Project Type", config.project_type)

    if config.backend_framework:
        table.add_row("Backend", config.backend_framework)
    if config.frontend_framework:
        table.add_row("Frontend", config.frontend_framework)
    if config.database:
        table.add_row("Database", config.database)
    if config.platform:
        table.add_row("Platform", config.platform)

    if config.features:
        table.add_row("Features", ", ".join(config.features))

    console.print(table)


def _display_results(output_dir: Path, created_files: Dict[str, List[Path]]) -> None:
    """Display generation results."""
    console.print(f"\n[bold green][SUCCESS][/bold green] Project generated successfully at: {output_dir}\n")

    table = Table(title="Generated Files", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green", justify="right")

    total = 0
    for category, files in created_files.items():
        count = len(files)
        total += count
        table.add_row(category.title(), str(count))

    table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")

    console.print(table)


def _display_plugin_recommendations(output_dir: Path, no_ai: bool) -> None:
    """Display recommended plugins."""
    import yaml

    plugins_file = output_dir / '.claude' / 'plugins.yaml'
    if not plugins_file.exists():
        return

    try:
        with open(plugins_file, 'r', encoding='utf-8') as f:
            plugins_config = yaml.safe_load(f)

        # Validate structure
        if not isinstance(plugins_config, dict):
            console.print("[yellow]Warning: Invalid plugins configuration format[/yellow]")
            return

        recommended = plugins_config.get('recommended_plugins', {})
        high_priority = recommended.get('high_priority', [])
        medium_priority = recommended.get('medium_priority', [])

    except yaml.YAMLError as e:
        console.print(f"[yellow]Warning: Could not parse plugins file: {e}[/yellow]")
        return
    except (IOError, OSError) as e:
        console.print(f"[yellow]Warning: Could not read plugins file: {e}[/yellow]")
        return

    if not high_priority and not medium_priority:
        return

    console.print("\n[bold blue][PLUGINS] Recommended Plugins:[/bold blue]")
    if no_ai:
        console.print("[dim](Based on project type)[/dim]\n")
    else:
        console.print("[dim](AI-enhanced recommendations)[/dim]\n")

    # Display high priority plugins
    if high_priority:
        console.print("[bold yellow]High Priority:[/bold yellow]")
        for plugin in high_priority[:5]:  # Show top 5
            console.print(f"  - [cyan]{plugin['name']}[/cyan] - {plugin['reason']}")
            console.print(f"    Install: [dim]{plugin['install_command']}[/dim]")
        console.print()

    # Display medium priority plugins (top 3)
    if medium_priority:
        console.print("[bold]Medium Priority:[/bold]")
        for plugin in medium_priority[:3]:
            console.print(f"  - [cyan]{plugin['name']}[/cyan] - {plugin['reason']}")
        console.print()

    console.print(f"[dim]View all recommendations: {plugins_file.relative_to(output_dir.parent)}[/dim]")


def _display_ai_stats(generator: FileGenerator, show_detailed: bool) -> None:
    """Display AI generation statistics."""
    if not generator.ai_generator:
        return

    stats = generator.ai_generator.get_generation_stats()

    # Always show summary if AI was enabled
    if stats['enabled']:
        console.print("\n[bold blue]AI Generation Summary:[/bold blue]\n")

        if stats['tokens_used'] > 0:
            console.print(f"  [green]✓[/green] Generated custom agents/skills")
            console.print(f"    Tokens used: {stats['tokens_used']:,} / {stats['token_budget']:,} ({stats['percentage_used']}%)")
            console.print(f"    Tokens remaining: {stats['tokens_remaining']:,}")

            # Estimate cost (approximate rates)
            estimated_cost = (stats['tokens_used'] / 1000) * 0.015  # $0.015 per 1K tokens (Sonnet input+output avg)
            console.print(f"    Estimated cost: ${estimated_cost:.3f}")
        else:
            console.print(f"  [yellow]○[/yellow] No AI generation needed (library templates sufficient)")

    # Show detailed stats if requested
    if show_detailed and generator.ai_cache:
        cache_stats = generator.ai_cache.get_statistics()

        console.print("\n[bold blue]Cache Statistics:[/bold blue]\n")
        console.print(f"  Cache directory: {cache_stats['cache_directory']}")
        console.print(f"  Total agents cached: {cache_stats['total_agents_cached']}")
        console.print(f"  Total skills cached: {cache_stats['total_skills_cached']}")

        if cache_stats['cache_hits'] > 0 or cache_stats['cache_misses'] > 0:
            console.print(f"  Cache hit rate: {cache_stats['hit_rate_percentage']}%")
            console.print(f"  Tokens saved by cache: {cache_stats['total_tokens_saved']:,}")

            # Estimate savings
            estimated_savings = (cache_stats['total_tokens_saved'] / 1000) * 0.015
            console.print(f"  Estimated cost savings: ${estimated_savings:.3f}")


def _display_next_steps(output_dir: Path, with_boilerplate: bool = False) -> None:
    """Display next steps."""
    console.print("\n[bold blue]Next Steps:[/bold blue]\n")

    console.print(f"1. Navigate to project:")
    console.print(f"   [cyan]cd {output_dir}[/cyan]\n")

    console.print("2. Review generated files:")
    console.print("   [cyan]cat README.md[/cyan]\n")

    if with_boilerplate:
        console.print("3. Review starter code:")
        console.print("   [cyan]# Check backend code in app/ or src/[/cyan]")
        console.print("   [cyan]# Check frontend code if applicable[/cyan]\n")

        console.print("4. Install dependencies:")
        console.print("   [cyan]# Python: pip install -r requirements.txt[/cyan]")
        console.print("   [cyan]# Node.js: npm install[/cyan]\n")

        console.print("5. Set up environment:")
        console.print("   [cyan]cp .env.example .env[/cyan]")
        console.print("   [cyan]# Edit .env with your configuration[/cyan]\n")

        console.print("6. Run the application:")
        console.print("   [cyan]/run-server[/cyan]\n")

        console.print("7. Explore with Claude Code:")
        console.print("   [cyan]claude[/cyan]\n")
    else:
        console.print("3. Set up development environment:")
        console.print("   [cyan]/setup-dev[/cyan]\n")

        console.print("4. Explore with Claude Code:")
        console.print("   [cyan]claude[/cyan]\n")

    console.print("[dim]Tip: All slash commands are available in .claude/commands/[/dim]")


if __name__ == '__main__':
    cli()
