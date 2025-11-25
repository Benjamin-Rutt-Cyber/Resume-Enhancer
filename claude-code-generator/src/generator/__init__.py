"""
Claude Code Generator - Core generation modules.

This package provides the core functionality for generating Claude Code project structures.
"""

from .analyzer import ProjectAnalyzer, ProjectConfig
from .selector import TemplateSelector
from .renderer import TemplateRenderer
from .file_generator import FileGenerator
from .plugin_analyzer import PluginAnalyzer, PluginRecommendation
from .boilerplate_generator import BoilerplateGenerator
from .constants import (
    CLAUDE_MODEL,
    MAX_API_TOKENS,
    PLUGIN_RECOMMENDATION_MAX_TOKENS,
    API_TEMPERATURE,
    MIN_PROJECT_NAME_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
    MIN_DESCRIPTION_LENGTH,
    MAX_PROJECT_SLUG_LENGTH,
    MAX_PATH_LENGTH,
    MAX_FILE_SIZE_BYTES,
    DEFAULT_API_PORT,
    DEFAULT_FRONTEND_PORT,
    DEFAULT_YEAR,
    DEFAULT_AUTHOR,
    PRIORITY_ORDER,
)

__all__ = [
    # Main classes
    'ProjectAnalyzer',
    'ProjectConfig',
    'TemplateSelector',
    'TemplateRenderer',
    'FileGenerator',
    'PluginAnalyzer',
    'PluginRecommendation',
    'BoilerplateGenerator',
    # Constants
    'CLAUDE_MODEL',
    'MAX_API_TOKENS',
    'PLUGIN_RECOMMENDATION_MAX_TOKENS',
    'API_TEMPERATURE',
    'MIN_PROJECT_NAME_LENGTH',
    'MAX_PROJECT_NAME_LENGTH',
    'MIN_DESCRIPTION_LENGTH',
    'MAX_PROJECT_SLUG_LENGTH',
    'MAX_PATH_LENGTH',
    'MAX_FILE_SIZE_BYTES',
    'DEFAULT_API_PORT',
    'DEFAULT_FRONTEND_PORT',
    'DEFAULT_YEAR',
    'DEFAULT_AUTHOR',
    'PRIORITY_ORDER',
]

__version__ = '0.2.0'
