"""
Template Renderer - Renders Jinja2 templates with project configuration.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import (
    Environment,
    FileSystemLoader,
    Template,
    TemplateError,
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError,
)
import re

from .constants import DEFAULT_YEAR


class TemplateRenderer:
    """Render Jinja2 templates with project configuration."""

    def __init__(self, templates_dir: Path):
        """
        Initialize renderer with templates directory.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Add custom filters
        self.env.filters['slugify'] = self._slugify
        self.env.filters['pascal_case'] = self._pascal_case
        self.env.filters['snake_case'] = self._snake_case
        self.env.filters['camel_case'] = self._camel_case

    def render_template(
        self, template_path: str, context: Dict[str, Any]
    ) -> str:
        """
        Render a template file with context.

        Args:
            template_path: Relative path to template file
            context: Dictionary of template variables

        Returns:
            Rendered template content

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If template has syntax errors or rendering fails
        """
        try:
            template = self.env.get_template(template_path)
            return template.render(**context)
        except TemplateNotFound as e:
            raise FileNotFoundError(f"Template not found: {template_path}") from e
        except TemplateSyntaxError as e:
            raise ValueError(
                f"Template syntax error in {template_path} at line {e.lineno}: {e.message}"
            ) from e
        except UndefinedError as e:
            raise ValueError(
                f"Undefined variable in template {template_path}: {e}"
            ) from e
        except TemplateError as e:
            raise ValueError(f"Error rendering template {template_path}: {e}") from e

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with context.

        Args:
            template_string: Template content as string
            context: Dictionary of template variables

        Returns:
            Rendered content
        """
        template = Template(template_string)
        return template.render(**context)

    def prepare_context(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare template context from configuration.

        Args:
            config_dict: Project configuration dictionary

        Returns:
            Enhanced context with computed values
        """
        context = config_dict.copy()

        # Add computed values
        context['project_slug_upper'] = context['project_slug'].upper().replace('-', '_')
        context['project_slug_pascal'] = self._pascal_case(context['project_slug'])

        # Add helper functions
        context['year'] = context.get('year', DEFAULT_YEAR)

        return context

    def _slugify(self, text: str) -> str:
        """Convert text to slug format."""
        slug = text.lower()
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug.strip('-')

    def _pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        words = re.split(r'[-_\s]+', text)
        return ''.join(word.capitalize() for word in words)

    def _snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        # Handle PascalCase
        text = re.sub(r'([A-Z])', r'_\1', text)
        text = text.lower()
        # Handle other separators
        text = re.sub(r'[-\s]+', '_', text)
        # Clean up
        text = re.sub(r'_+', '_', text)
        return text.strip('_')

    def _camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        pascal = self._pascal_case(text)
        if pascal:
            return pascal[0].lower() + pascal[1:]
        return pascal

    def validate_template(self, template_path: str) -> bool:
        """
        Validate that a template exists and can be compiled.

        Args:
            template_path: Relative path to template

        Returns:
            True if template is valid

        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If template has syntax errors
        """
        try:
            template = self.env.get_template(template_path)
            # Try to compile
            template.module
            return True
        except TemplateNotFound as e:
            raise FileNotFoundError(f"Template not found: {template_path}") from e
        except TemplateSyntaxError as e:
            raise ValueError(
                f"Template syntax error in {template_path} at line {e.lineno}: {e.message}"
            ) from e
        except TemplateError as e:
            raise ValueError(f"Template validation failed for {template_path}: {e}") from e
