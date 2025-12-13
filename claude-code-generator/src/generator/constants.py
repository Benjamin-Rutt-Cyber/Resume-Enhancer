"""
Constants for the Claude Code Generator.

This module contains all configuration constants used throughout the codebase
to avoid magic numbers and improve maintainability.
"""

# ==================== API Configuration ====================

# Claude API settings
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
MAX_API_TOKENS = 2000
PLUGIN_RECOMMENDATION_MAX_TOKENS = 1500
API_TEMPERATURE = 0.3

# ==================== Project Configuration ====================

# Project name validation
MIN_PROJECT_NAME_LENGTH = 3
MAX_PROJECT_NAME_LENGTH = 100
MAX_PROJECT_NAME_DISPLAY = 100

# Project slug validation
MAX_PROJECT_SLUG_LENGTH = 50

# Description validation
MIN_DESCRIPTION_LENGTH = 10

# ==================== File System ====================

# Path validation (Windows MAX_PATH is 260, leave room for nested files)
MAX_PATH_LENGTH = 200

# File size limits
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# ==================== Default Values ====================

# Default ports for boilerplate generation
DEFAULT_API_PORT = 8000
DEFAULT_FRONTEND_PORT = 3000

# Default year for templates
DEFAULT_YEAR = 2025

# Default author
DEFAULT_AUTHOR = "Developer"

# ==================== Priority Ordering ====================

# Priority levels for agents, skills, and plugins
PRIORITY_ORDER = {
    'high': 0,
    'medium': 1,
    'low': 2
}

# ==================== AI Generation Configuration ====================

# Domain uniqueness thresholds
UNIQUENESS_THRESHOLD_LOW = 30  # Below this: Use library only
UNIQUENESS_THRESHOLD_MEDIUM = 70  # Above this: Always generate custom

# Token budgets for AI generation
DEFAULT_TOKEN_BUDGET = 5000  # Hard cap per generation session
AGENT_GENERATION_TOKENS = 2000  # Max tokens per agent
SKILL_GENERATION_TOKENS = 1500  # Max tokens per skill

# Cache settings
CACHE_EXPIRY_DAYS = 30  # Days before cache entries expire
CACHE_DIR_NAME = '.claude-generator-cache'  # Cache directory name
