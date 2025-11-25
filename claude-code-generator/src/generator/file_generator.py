"""
File Generator - Creates project files from templates.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil
import os
import logging
import yaml
from .constants import MAX_PATH_LENGTH, MAX_FILE_SIZE_BYTES
from .analyzer import ProjectConfig
from .selector import TemplateSelector
from .renderer import TemplateRenderer
from .plugin_analyzer import PluginAnalyzer
from .boilerplate_generator import BoilerplateGenerator

logger = logging.getLogger(__name__)


class FileGenerator:
    """Generate project files from templates."""

    def __init__(self, templates_dir: Path, api_key: Optional[str] = None):
        """
        Initialize file generator.

        Args:
            templates_dir: Path to templates directory
            api_key: Optional Anthropic API key for plugin recommendations
        """
        self.templates_dir = Path(templates_dir)
        self.selector = TemplateSelector(templates_dir)
        self.renderer = TemplateRenderer(templates_dir)
        self.plugin_analyzer = PluginAnalyzer(api_key=api_key, templates_dir=templates_dir)
        self.boilerplate_generator = BoilerplateGenerator(templates_dir)

    def _validate_output_path(self, output_dir: Path) -> Path:
        """
        Validate output directory path for security and compatibility.

        Args:
            output_dir: Directory path to validate

        Returns:
            Validated and resolved path

        Raises:
            ValueError: If path is invalid or too long
        """
        # Check for path traversal attempts BEFORE resolving
        original_path = Path(output_dir)
        for part in original_path.parts:
            if part == '..':
                raise ValueError(
                    f"Path traversal not allowed: {output_dir}. "
                    f"Paths containing '..' components are forbidden for security reasons."
                )

        # Now resolve to absolute path
        try:
            output_dir = original_path.resolve()
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid output path: {e}") from e

        # Check path length (Windows compatibility)
        path_str = str(output_dir)
        if len(path_str) > MAX_PATH_LENGTH:
            raise ValueError(
                f"Output path too long ({len(path_str)} chars). "
                f"Maximum is {MAX_PATH_LENGTH} to allow for nested files."
            )

        return output_dir

    def _validate_file_size(self, file_path: Path, max_size: int = MAX_FILE_SIZE_BYTES) -> None:
        """
        Validate file size before reading.

        Args:
            file_path: Path to file
            max_size: Maximum allowed file size in bytes

        Raises:
            ValueError: If file is too large
        """
        try:
            file_size = file_path.stat().st_size
            if file_size > max_size:
                raise ValueError(
                    f"File too large: {file_path} ({file_size} bytes). "
                    f"Maximum is {max_size} bytes."
                )
        except OSError as e:
            raise IOError(f"Cannot stat file {file_path}: {e}") from e

    def generate_project(
        self,
        config: ProjectConfig,
        output_dir: Path,
        overwrite: bool = False,
        recommend_plugins: bool = True,
        use_ai_plugins: bool = True,
        generate_boilerplate: bool = False,
        keep_partial_on_error: bool = False,
    ) -> Dict[str, List[Path]]:
        """
        Generate complete project structure with automatic rollback on failure.

        Args:
            config: Project configuration
            output_dir: Output directory path
            overwrite: Whether to overwrite existing files
            recommend_plugins: Whether to generate plugin recommendations
            use_ai_plugins: Whether to use AI for smart plugin recommendations
            generate_boilerplate: Whether to generate starter code/boilerplate
            keep_partial_on_error: If True, keep partial generation for debugging on error

        Returns:
            Dictionary mapping categories to lists of created files

        Raises:
            FileExistsError: If output directory exists and overwrite=False
            ValueError: If output path is invalid or too long
        """
        # Validate output path
        output_dir = self._validate_output_path(output_dir)

        # Track if we created the directory (for rollback)
        created_output_dir = False

        # Check if directory exists
        if output_dir.exists() and not overwrite:
            if any(output_dir.iterdir()):
                raise FileExistsError(
                    f"Directory {output_dir} already exists. "
                    f"Use overwrite=True to overwrite."
                )

        # Create output directory
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            created_output_dir = True

        try:
            # Convert config to dict for templating
            config_dict = config.model_dump()
            context = self.renderer.prepare_context(config_dict)

            # Select templates
            templates = self.selector.select_templates(config)

            # Generate files
            created_files = {
                'agents': [],
                'skills': [],
                'commands': [],
                'docs': [],
                'other': []
            }

            # Generate agents
            for agent_template in templates['agents']:
                file_path = self._generate_agent(agent_template, context, output_dir)
                created_files['agents'].append(file_path)

            # Generate skills
            for skill_template in templates['skills']:
                file_path = self._generate_skill(skill_template, context, output_dir)
                created_files['skills'].append(file_path)

            # Generate commands
            for command_template in templates['commands']:
                file_path = self._generate_command(command_template, context, output_dir)
                created_files['commands'].append(file_path)

            # Generate documentation
            for doc_template in templates['docs']:
                file_path = self._generate_doc(doc_template, context, output_dir)
                created_files['docs'].append(file_path)

            # Generate README
            readme_path = self._generate_readme(context, output_dir)
            created_files['other'].append(readme_path)

            # Generate .gitignore
            gitignore_path = self._generate_gitignore(context, output_dir)
            created_files['other'].append(gitignore_path)

            # Generate plugin recommendations
            if recommend_plugins:
                plugin_config_path = self._generate_plugin_config(
                    config, output_dir, use_ai=use_ai_plugins
                )
                created_files['other'].append(plugin_config_path)

            # Generate boilerplate code
            if generate_boilerplate:
                boilerplate_files = self.boilerplate_generator.generate_boilerplate(
                    config, output_dir
                )
                # Add generated boilerplate files to created_files dict
                for category, files in boilerplate_files.items():
                    if category in created_files:
                        created_files[category].extend(files)
                    else:
                        created_files[category] = files

            # Create directory structure
            self._create_directory_structure(config, output_dir)

            return created_files

        except Exception as e:
            # Rollback: Clean up partially generated project
            logger.error(f"Project generation failed: {e}")

            if not keep_partial_on_error and created_output_dir and output_dir.exists():
                logger.info(f"Rolling back: deleting {output_dir}")
                try:
                    shutil.rmtree(output_dir)
                    logger.info("Rollback successful")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up {output_dir}: {cleanup_error}")
            elif keep_partial_on_error:
                logger.info(f"Keeping partial generation at {output_dir} for debugging")

            # Re-raise the original exception
            raise

    def _generate_agent(
        self, template_path: str, context: Dict[str, Any], output_dir: Path
    ) -> Path:
        """Generate agent file - either copy reusable or render template."""
        template_file = self.templates_dir / template_path

        # Create output directory
        output_dir_path = output_dir / '.claude' / 'agents'
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Check if this is a reusable agent (no .j2 extension) or template (.j2)
        if template_path.endswith('.j2'):
            # GENERATED AGENT: Render Jinja2 template with project context
            content = self.renderer.render_template(template_path, context)
            filename = Path(template_path).name.replace('.j2', '')
            output_path = output_dir_path / filename
            output_path.write_text(content, encoding='utf-8')
        else:
            # REUSABLE AGENT: Copy as-is (no templating needed)
            filename = Path(template_path).name
            output_path = output_dir_path / filename
            shutil.copy2(template_file, output_path)

        return output_path

    def _generate_skill(
        self, template_path: str, context: Dict[str, Any], output_dir: Path
    ) -> Path:
        """
        Generate skill directory.

        Handles both:
        - Library skills: skills/library/python-fastapi/SKILL.md (copy as-is)
        - Template skills: skills/python-fastapi/ (render SKILL.md.j2)

        Args:
            template_path: Path to skill template
            context: Template context
            output_dir: Output directory

        Returns:
            Path to generated skill directory
        """
        is_library_skill = self._is_library_skill(template_path)

        if is_library_skill:
            content, skill_name = self._process_library_skill(template_path)
        else:
            content, skill_name = self._process_template_skill(template_path, context)

        output_path = self._write_skill_file(output_dir, skill_name, content)
        self._copy_additional_skill_files(template_path, output_path, is_library_skill)

        return output_path

    def _is_library_skill(self, template_path: str) -> bool:
        """
        Check if skill is a library skill (copy as-is) or template skill.

        Args:
            template_path: Path to skill template

        Returns:
            True if library skill, False if template skill
        """
        return template_path.endswith('SKILL.md') and not template_path.endswith('.j2')

    def _process_library_skill(self, template_path: str) -> tuple[str, str]:
        """
        Process library skill by reading the SKILL.md file.

        Args:
            template_path: Path to library skill

        Returns:
            Tuple of (content, skill_name)
        """
        template_path_obj = Path(template_path)
        skill_dir = template_path_obj.parent
        skill_name = skill_dir.name
        skill_file_path = self.templates_dir / template_path

        # Validate file size before reading
        self._validate_file_size(skill_file_path)

        # Read the library skill file
        content = skill_file_path.read_text(encoding='utf-8')

        return content, skill_name

    def _process_template_skill(self, template_path: str, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Process template skill by rendering SKILL.md.j2 with context.

        Args:
            template_path: Path to template skill directory
            context: Template rendering context

        Returns:
            Tuple of (content, skill_name)
        """
        template_path_obj = Path(template_path)
        skill_name = template_path_obj.name
        skill_template_path = template_path + 'SKILL.md.j2'

        # Render template
        content = self.renderer.render_template(skill_template_path, context)

        return content, skill_name

    def _write_skill_file(self, output_dir: Path, skill_name: str, content: str) -> Path:
        """
        Write SKILL.md file to output directory.

        Args:
            output_dir: Base output directory
            skill_name: Name of the skill
            content: Content to write

        Returns:
            Path to skill directory
        """
        output_path = output_dir / '.claude' / 'skills' / skill_name
        output_path.mkdir(parents=True, exist_ok=True)

        skill_file = output_path / 'SKILL.md'
        skill_file.write_text(content, encoding='utf-8')

        return output_path

    def _copy_additional_skill_files(
        self, template_path: str, output_path: Path, is_library_skill: bool
    ) -> None:
        """
        Copy additional files from skill directory (excluding SKILL.md templates).

        Args:
            template_path: Path to skill template
            output_path: Output skill directory
            is_library_skill: Whether this is a library skill
        """
        template_path_obj = Path(template_path)

        if is_library_skill:
            # Library skill - check for additional files in the skill directory
            skill_dir_path = self.templates_dir / template_path_obj.parent
        else:
            # Template skill - use the template directory
            skill_dir_path = self.templates_dir / template_path

        if skill_dir_path.exists() and skill_dir_path.is_dir():
            for item in skill_dir_path.iterdir():
                # Skip SKILL.md templates and hidden files
                if item.name not in ['SKILL.md', 'SKILL.md.j2'] and not item.name.startswith('.'):
                    dest = output_path / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)

    def _generate_command(
        self, template_path: str, context: Dict[str, Any], output_dir: Path
    ) -> Path:
        """Generate command file."""
        # Render template
        content = self.renderer.render_template(template_path, context)

        # Determine output filename (remove .j2 extension)
        filename = Path(template_path).name.replace('.j2', '')

        # Create output path
        output_path = output_dir / '.claude' / 'commands' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def _generate_doc(
        self, template_path: str, context: Dict[str, Any], output_dir: Path
    ) -> Path:
        """
        Generate documentation file.

        Handles both:
        - Library docs: docs/library/*.md (copy as-is, skip READMEs)
        - Template docs: docs/*.md.j2 (render with Jinja2)
        """
        template_path_obj = Path(template_path)

        # Skip library READMEs - they're handled by _generate_readme()
        if 'library/README-' in template_path:
            # Return a dummy path - the README is handled elsewhere
            return output_dir / 'README.md'

        # Check if this is a library doc (in docs/library/, no .j2)
        if '/library/' in template_path and not template_path.endswith('.j2'):
            # Library doc - copy as-is
            doc_file_path = self.templates_dir / template_path

            if not doc_file_path.exists():
                # Doc doesn't exist, skip gracefully
                logger.warning(f"Library doc not found: {template_path}")
                return output_dir / 'docs' / template_path_obj.name

            # Validate file size before reading
            self._validate_file_size(doc_file_path)

            content = doc_file_path.read_text(encoding='utf-8')
            filename = template_path_obj.name
        else:
            # Template doc - render with Jinja2
            if not (self.templates_dir / template_path).exists():
                # Template doesn't exist, skip gracefully
                logger.warning(f"Doc template not found: {template_path}")
                return output_dir / 'docs' / template_path_obj.name.replace('.j2', '')

            content = self.renderer.render_template(template_path, context)
            filename = template_path_obj.name.replace('.j2', '')

        # Create output path
        output_path = output_dir / 'docs' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def _generate_readme(self, context: Dict[str, Any], output_dir: Path) -> Path:
        """
        Generate README.md file using project-type-specific library templates.

        Uses comprehensive README templates from templates/docs/library/
        based on the project type. Falls back to basic template if library
        file doesn't exist.
        """
        project_type = context['project_type']
        readme_filename = f"README-{project_type}.md"
        library_readme = self.templates_dir / 'docs' / 'library' / readme_filename

        readme_path = output_dir / 'README.md'

        # Try to use library README (Week 4 comprehensive templates)
        if library_readme.exists():
            # Copy the comprehensive project-type-specific README
            shutil.copy2(library_readme, readme_path)
            logger.info(f"Using comprehensive README for {project_type}")
        else:
            # Fallback to basic template if library file missing
            logger.warning(f"Library README not found for {project_type}, using basic template")
            readme_content = self._generate_basic_readme(context)
            readme_path.write_text(readme_content, encoding='utf-8')

        return readme_path

    def _generate_basic_readme(self, context: Dict[str, Any]) -> str:
        """Generate basic README as fallback."""
        readme_content = f"""# {context['project_name']}

{context['description']}

## Project Type

{context['project_type']}

## Tech Stack

"""
        if context.get('backend_framework'):
            readme_content += f"- **Backend:** {context['backend_framework']}\n"
        if context.get('frontend_framework'):
            readme_content += f"- **Frontend:** {context['frontend_framework']}\n"
        if context.get('database'):
            readme_content += f"- **Database:** {context['database']}\n"
        if context.get('platform'):
            readme_content += f"- **Platform:** {context['platform']}\n"

        readme_content += """
## Getting Started

See documentation for detailed setup instructions.

Quick start:

```bash
# Setup development environment
/setup-dev

# Run tests
/run-tests
"""

        if context.get('backend_framework'):
            readme_content += """
# Start server
/run-server
"""

        readme_content += """```

## Features

"""
        for feature in context.get('features', []):
            readme_content += f"- {feature.replace('_', ' ').title()}\n"

        readme_content += f"""
## Generated

This project was generated with Claude Code Generator.
"""
        return readme_content

    def _generate_gitignore(self, context: Dict[str, Any], output_dir: Path) -> Path:
        """Generate .gitignore file."""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
ENV/
env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Build
dist/
build/
*.egg-info/

# Testing
.coverage
htmlcov/
.pytest_cache/

# OS
.DS_Store
Thumbs.db
"""
        gitignore_path = output_dir / '.gitignore'
        gitignore_path.write_text(gitignore_content, encoding='utf-8')

        return gitignore_path

    def _generate_plugin_config(
        self, config: ProjectConfig, output_dir: Path, use_ai: bool = True
    ) -> Path:
        """
        Generate .claude/plugins.yaml with recommended plugins.

        Args:
            config: Project configuration
            output_dir: Output directory
            use_ai: Whether to use AI for smart recommendations

        Returns:
            Path to generated plugins.yaml file
        """
        # Get plugin recommendations
        plugin_config_dict = self.plugin_analyzer.get_plugin_config_dict(
            config, use_ai=use_ai
        )

        # Create .claude directory if it doesn't exist
        claude_dir = output_dir / '.claude'
        claude_dir.mkdir(parents=True, exist_ok=True)

        # Write plugins.yaml
        plugins_path = claude_dir / 'plugins.yaml'
        with open(plugins_path, 'w', encoding='utf-8') as f:
            yaml.dump(plugin_config_dict, f, sort_keys=False, allow_unicode=True, indent=2)

        return plugins_path

    def _create_directory_structure(self, config: ProjectConfig, output_dir: Path):
        """Create project directory structure."""
        # Get directory structure from project type
        project_type_config = self.selector.get_project_type_info(config.project_type)
        directories = project_type_config.get('directory_structure', [])

        for directory in directories:
            dir_path = output_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create __init__.py for Python packages
            if (config.backend_framework and 'python' in config.backend_framework) or 'python' in str(config.project_type):
                if any(parent in str(dir_path) for parent in ['app', 'src', 'backend']):
                    init_file = dir_path / '__init__.py'
                    if not init_file.exists():
                        init_file.write_text('"""Package module."""\n', encoding='utf-8')
