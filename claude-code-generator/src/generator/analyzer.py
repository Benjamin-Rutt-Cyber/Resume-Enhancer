"""
Project Analyzer - Analyzes project descriptions using Claude API.
"""

import json
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from pydantic import BaseModel, Field, field_validator, ValidationInfo
import re

from .constants import (
    MIN_PROJECT_NAME_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
    MIN_DESCRIPTION_LENGTH,
    MAX_PROJECT_SLUG_LENGTH,
    CLAUDE_MODEL,
    MAX_API_TOKENS,
    MAX_PROJECT_NAME_DISPLAY,
    DEFAULT_YEAR,
    DEFAULT_AUTHOR,
)


class ProjectConfig(BaseModel):
    """Validated project configuration."""

    project_name: str = Field(..., min_length=MIN_PROJECT_NAME_LENGTH, max_length=MAX_PROJECT_NAME_LENGTH)
    project_slug: str = Field(..., pattern=r'^[a-z0-9-]+$')
    project_type: str = Field(..., pattern=r'^[a-z-]+$')
    description: str = Field(..., min_length=MIN_DESCRIPTION_LENGTH)
    backend_framework: Optional[str] = None
    frontend_framework: Optional[str] = None
    database: Optional[str] = None
    deployment_platform: Optional[str] = None
    connectivity: Optional[str] = None  # For IoT
    firmware_language: Optional[str] = None  # For IoT
    platform: Optional[str] = None  # For IoT
    state_management: Optional[str] = None  # For frontend
    features: list[str] = Field(default_factory=list)
    has_auth: bool = False
    has_api: bool = True
    has_websockets: bool = False
    has_payments: bool = False
    author: str = DEFAULT_AUTHOR
    year: int = DEFAULT_YEAR

    @field_validator('project_slug', mode='before')
    @classmethod
    def generate_slug(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Generate slug from project name if not provided."""
        if v is None and 'project_name' in info.data:
            name = info.data['project_name']
            slug = name.lower()
            slug = re.sub(r'[\s_]+', '-', slug)
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            return slug.strip('-')
        return v


class ProjectAnalyzer:
    """Analyze project descriptions and extract configuration."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize analyzer with Claude API.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def analyze(self, description: str, project_name: Optional[str] = None) -> ProjectConfig:
        """
        Analyze project description and extract configuration.

        Args:
            description: Natural language project description
            project_name: Optional project name override

        Returns:
            ProjectConfig with extracted information

        Raises:
            ValueError: If description is empty or invalid
        """
        if not description or len(description.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")

        if self.client:
            # Use Claude API for intelligent analysis
            config_dict = self._analyze_with_claude(description, project_name)
        else:
            # Fallback to keyword-based analysis
            config_dict = self._analyze_with_keywords(description, project_name)

        # Validate and return
        return ProjectConfig(**config_dict)

    def _analyze_with_claude(
        self, description: str, project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze using Claude API."""
        prompt = self._build_analysis_prompt(description, project_name)

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_API_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract JSON from response
        response_text = response.content[0].text
        config_json = self._extract_json(response_text)

        return json.loads(config_json)

    def _analyze_with_keywords(
        self, description: str, project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback keyword-based analysis."""
        desc_lower = description.lower()

        # Determine project type
        if any(word in desc_lower for word in ['iot', 'pico', 'esp32', 'sensor', 'embedded', 'hardware']):
            project_type = 'hardware-iot'
            backend_framework = None
            frontend_framework = None
            database = None
            platform = self._detect_platform(desc_lower)
            firmware_language = 'micropython' if 'micropython' in desc_lower else 'circuitpython'
            connectivity = 'mqtt' if 'mqtt' in desc_lower else 'http'
        elif any(word in desc_lower for word in ['mobile', 'ios', 'android', 'react native', 'flutter']):
            project_type = 'mobile-app'
            backend_framework = 'python-fastapi'
            frontend_framework = 'react-native'
            database = 'postgresql'
            platform = None
            firmware_language = None
            connectivity = None
        elif any(word in desc_lower for word in ['machine learning', 'ml', 'data science', 'model', 'prediction']):
            project_type = 'data-science'
            backend_framework = 'python'
            frontend_framework = None
            database = 'postgresql'
            platform = None
            firmware_language = None
            connectivity = None
        elif any(word in desc_lower for word in ['api', 'rest', 'backend', 'service', 'microservice']):
            project_type = 'api-service'
            backend_framework = 'python-fastapi'
            frontend_framework = None
            database = 'postgresql'
            platform = None
            firmware_language = None
            connectivity = None
        else:
            # Default to SaaS web app
            project_type = 'saas-web-app'
            backend_framework = 'python-fastapi'
            frontend_framework = 'react-typescript'
            database = 'postgresql'
            platform = None
            firmware_language = None
            connectivity = None

        # Extract features
        features = []
        if 'auth' in desc_lower or 'login' in desc_lower:
            features.append('authentication')
        if 'payment' in desc_lower or 'subscription' in desc_lower:
            features.append('payments')
        if 'email' in desc_lower:
            features.append('email')
        if 'real-time' in desc_lower or 'websocket' in desc_lower:
            features.append('websockets')

        return {
            'project_name': project_name or self._extract_name(description),
            'project_slug': None,  # Will be auto-generated
            'project_type': project_type,
            'description': description,
            'backend_framework': backend_framework,
            'frontend_framework': frontend_framework,
            'database': database,
            'deployment_platform': 'docker',
            'platform': platform,
            'firmware_language': firmware_language,
            'connectivity': connectivity,
            'state_management': 'redux' if frontend_framework else None,
            'features': features,
            'has_auth': 'authentication' in features,
            'has_api': True,
            'has_websockets': 'websockets' in features,
            'has_payments': 'payments' in features,
        }

    def _detect_platform(self, desc_lower: str) -> str:
        """Detect hardware platform from description."""
        if 'pico' in desc_lower:
            return 'pico-w'
        elif 'esp32' in desc_lower:
            return 'esp32'
        elif 'arduino' in desc_lower:
            return 'arduino'
        elif 'raspberry pi' in desc_lower and 'pico' not in desc_lower:
            return 'raspberry-pi'
        return 'pico-w'  # Default

    def _extract_name(self, description: str) -> str:
        """Extract a reasonable project name from description."""
        # Take first few words
        words = description.split()[:3]
        name = ' '.join(words)
        if len(name) > MAX_PROJECT_SLUG_LENGTH:
            name = name[:MAX_PROJECT_SLUG_LENGTH]
        return name.title()

    def _build_analysis_prompt(
        self, description: str, project_name: Optional[str] = None
    ) -> str:
        """Build prompt for Claude API."""
        return f"""Analyze this project description and extract configuration as JSON.

Project description: {description}
{f"Project name: {project_name}" if project_name else ""}

Determine:
1. Project type (saas-web-app, api-service, mobile-app, hardware-iot, data-science)
2. Appropriate tech stack
3. Required features
4. Project name (if not provided)

Return ONLY valid JSON with this structure:
{{
  "project_name": "string",
  "project_type": "saas-web-app|api-service|mobile-app|hardware-iot|data-science",
  "description": "string",
  "backend_framework": "python-fastapi|node-express|go-gin|null",
  "frontend_framework": "react-typescript|vue-typescript|null",
  "database": "postgresql|mysql|mongodb|null",
  "deployment_platform": "docker|kubernetes|aws",
  "platform": "pico-w|esp32|null (for IoT only)",
  "firmware_language": "micropython|circuitpython|null (for IoT only)",
  "connectivity": "mqtt|http|bluetooth|null (for IoT only)",
  "state_management": "redux|mobx|null (for frontend)",
  "features": ["authentication", "payments", "email", etc],
  "has_auth": boolean,
  "has_api": boolean,
  "has_websockets": boolean,
  "has_payments": boolean
}}

JSON:"""

    def _extract_json(self, text: str) -> str:
        """Extract JSON from Claude's response."""
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # If no JSON found, raise error
        raise ValueError(f"Could not extract JSON from response: {text}")
