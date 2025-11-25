"""
Plugin Analyzer - Intelligently recommends Claude Code marketplace plugins.

This module analyzes project configuration and uses both:
1. Project type-based recommendations (from project-types/*.yaml)
2. Smart AI analysis (Claude API) to recommend contextually appropriate plugins
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from anthropic import Anthropic, APIError, APIConnectionError, APITimeoutError
import yaml

from .constants import CLAUDE_MODEL, PLUGIN_RECOMMENDATION_MAX_TOKENS, API_TEMPERATURE
from .analyzer import ProjectConfig

logger = logging.getLogger(__name__)


class PluginRecommendation:
    """A recommended plugin with metadata."""

    def __init__(
        self,
        name: str,
        reason: str,
        priority: str,
        marketplace_id: Optional[str] = None,
        install_command: Optional[str] = None,
        category: Optional[str] = None,
    ):
        self.name = name
        self.reason = reason
        self.priority = priority  # high, medium, low
        self.marketplace_id = marketplace_id or name
        self.install_command = install_command or f"/plugin install {name}"
        self.category = category or "productivity"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "reason": self.reason,
            "priority": self.priority,
            "marketplace_id": self.marketplace_id,
            "install_command": self.install_command,
            "category": self.category,
        }


class PluginAnalyzer:
    """Analyze projects and recommend appropriate marketplace plugins."""

    def __init__(self, api_key: Optional[str] = None, templates_dir: Optional[Path] = None):
        """
        Initialize plugin analyzer.

        Args:
            api_key: Anthropic API key for smart analysis. If None, reads from env.
            templates_dir: Path to templates directory. If None, auto-detects.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

        # Find templates directory
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Auto-detect: should be in project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            self.templates_dir = project_root / 'templates'

        # Load plugin registry
        self.plugin_registry = self._load_plugin_registry()

    def _load_plugin_registry(self) -> Dict[str, Any]:
        """Load the plugin registry from templates/plugins/registry.yaml with error handling."""
        registry_path = self.templates_dir / 'plugins' / 'registry.yaml'
        default_registry = {"plugins": []}

        if not registry_path.exists():
            logger.warning(f"Plugin registry not found at {registry_path}")
            return default_registry

        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

                # Validate structure
                if not isinstance(config, dict):
                    logger.error(f"Plugin registry must be a dictionary, got {type(config)}")
                    return default_registry

                return config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in plugin registry: {e}")
            return default_registry
        except (IOError, OSError) as e:
            logger.error(f"Cannot read plugin registry file: {e}")
            return default_registry

    def _load_project_type_config(self, project_type: str) -> Dict[str, Any]:
        """Load project type configuration with error handling."""
        config_path = self.templates_dir / 'project-types' / f'{project_type}.yaml'

        if not config_path.exists():
            logger.warning(f"Project type config not found: {config_path}")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

                # Validate structure
                if not isinstance(config, dict):
                    logger.error(f"Project type config must be a dictionary, got {type(config)}")
                    return {}

                return config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in project type config {config_path}: {e}")
            return {}
        except (IOError, OSError) as e:
            logger.error(f"Cannot read project type config file {config_path}: {e}")
            return {}

    def recommend_plugins(
        self, config: ProjectConfig, use_ai: bool = True
    ) -> List[PluginRecommendation]:
        """
        Recommend plugins for a project.

        Args:
            config: Project configuration
            use_ai: Whether to use AI analysis for smart recommendations

        Returns:
            List of recommended plugins, sorted by priority
        """
        # Get base recommendations from project type
        base_recommendations = self._get_project_type_recommendations(config)

        # Filter based on conditions (tech stack, features, etc.)
        filtered_recommendations = self._filter_recommendations(config, base_recommendations)

        # Enhance with AI if available
        if use_ai and self.client:
            ai_recommendations = self._get_ai_recommendations(config, filtered_recommendations)
            # Merge AI recommendations (avoiding duplicates)
            existing_names = {r.name for r in filtered_recommendations}
            for ai_rec in ai_recommendations:
                if ai_rec.name not in existing_names:
                    filtered_recommendations.append(ai_rec)

        # Sort by priority: high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        filtered_recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        return filtered_recommendations

    def _get_project_type_recommendations(
        self, config: ProjectConfig
    ) -> List[PluginRecommendation]:
        """Get base plugin recommendations from project type config."""
        project_type_config = self._load_project_type_config(config.project_type)
        recommended_plugins = project_type_config.get('recommended_plugins', [])

        recommendations = []
        for plugin_def in recommended_plugins:
            name = plugin_def.get('name')
            reason = plugin_def.get('reason', f'Useful for {config.project_type} projects')
            priority = plugin_def.get('priority', 'medium')

            # Get additional metadata from plugin registry
            plugin_meta = self._get_plugin_metadata(name)

            recommendations.append(
                PluginRecommendation(
                    name=name,
                    reason=reason,
                    priority=priority,
                    marketplace_id=plugin_meta.get('marketplace_id'),
                    install_command=plugin_meta.get('install_command'),
                    category=plugin_meta.get('category'),
                )
            )

        return recommendations

    def _get_plugin_metadata(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin metadata from the registry."""
        plugins = self.plugin_registry.get('plugins', [])

        for plugin in plugins:
            if plugin.get('name') == plugin_name:
                return plugin

        # Not found in registry, return defaults
        return {
            'marketplace_id': plugin_name,
            'install_command': f'/plugin install {plugin_name}',
            'category': 'productivity',
        }

    def _filter_recommendations(
        self, config: ProjectConfig, recommendations: List[PluginRecommendation]
    ) -> List[PluginRecommendation]:
        """
        Filter recommendations based on project configuration.

        Removes plugins that don't match conditions (e.g., React plugins for Vue projects).
        """
        # Load project type config to get plugin conditions
        project_type_config = self._load_project_type_config(config.project_type)
        recommended_plugins_config = project_type_config.get('recommended_plugins', [])

        # Build a map of plugin name -> conditions
        conditions_map = {}
        for plugin_def in recommended_plugins_config:
            name = plugin_def.get('name')
            conditions = plugin_def.get('conditions', {})
            conditions_map[name] = conditions

        filtered = []
        for rec in recommendations:
            conditions = conditions_map.get(rec.name, {})

            # If no conditions, always include
            if not conditions:
                filtered.append(rec)
                continue

            # Check if conditions match
            matches = True
            for condition_key, condition_values in conditions.items():
                # Map config attributes to project_type_config keys
                config_value = self._get_config_value(config, condition_key)

                # Check if config value matches any of the condition values
                if config_value and config_value not in condition_values:
                    matches = False
                    break

            if matches:
                filtered.append(rec)

        return filtered

    def _get_config_value(self, config: ProjectConfig, key: str) -> Optional[str]:
        """Get configuration value for a given key."""
        # Map common keys to ProjectConfig attributes
        key_mapping = {
            'backend': 'backend_framework',
            'frontend': 'frontend_framework',
            'database': 'database',
            'deployment': 'deployment_platform',
            'platform': 'platform',
            'framework': 'frontend_framework',  # For mobile apps
            'language': 'firmware_language',  # For IoT
            'connectivity': 'connectivity',  # For IoT
            'features': 'features',
        }

        config_attr = key_mapping.get(key)
        if not config_attr:
            return None

        value = getattr(config, config_attr, None)

        # Handle features specially (it's a list)
        if key == 'features' and isinstance(value, list):
            # Check if any required feature is in the list
            # This is handled differently in the filtering logic
            return value

        return value

    def _get_ai_recommendations(
        self, config: ProjectConfig, existing_recommendations: List[PluginRecommendation]
    ) -> List[PluginRecommendation]:
        """Use Claude API to get smart plugin recommendations."""
        if not self.client:
            return []

        prompt = self._build_ai_recommendation_prompt(config, existing_recommendations)

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=PLUGIN_RECOMMENDATION_MAX_TOKENS,
                temperature=API_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Parse response
            content = response.content[0].text
            # Look for JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)

                recommendations = []
                for plugin_def in result.get('additional_plugins', []):
                    # Verify plugin exists in registry
                    plugin_meta = self._get_plugin_metadata(plugin_def['name'])

                    recommendations.append(
                        PluginRecommendation(
                            name=plugin_def['name'],
                            reason=plugin_def.get('reason', ''),
                            priority=plugin_def.get('priority', 'medium'),
                            marketplace_id=plugin_meta.get('marketplace_id'),
                            install_command=plugin_meta.get('install_command'),
                            category=plugin_meta.get('category'),
                        )
                    )

                return recommendations

        except (APIError, APIConnectionError, APITimeoutError) as e:
            logger.warning(f"AI API error during plugin recommendation: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response for plugin recommendations: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.warning(f"Invalid AI response format for plugin recommendations: {e}")
            return []

        return []

    def _build_ai_recommendation_prompt(
        self, config: ProjectConfig, existing_recommendations: List[PluginRecommendation]
    ) -> str:
        """Build prompt for AI-based plugin recommendations."""
        existing_plugin_names = [r.name for r in existing_recommendations]

        # Get available plugins from registry
        available_plugins = []
        for plugin in self.plugin_registry.get('plugins', []):
            if plugin['name'] not in existing_plugin_names:
                available_plugins.append(
                    {
                        'name': plugin['name'],
                        'category': plugin.get('category'),
                        'description': plugin.get('description'),
                    }
                )

        prompt = f"""You are an expert at recommending Claude Code marketplace plugins for software projects.

Project Information:
- Name: {config.project_name}
- Type: {config.project_type}
- Description: {config.description}
- Backend: {config.backend_framework or 'N/A'}
- Frontend: {config.frontend_framework or 'N/A'}
- Database: {config.database or 'N/A'}
- Features: {', '.join(config.features) if config.features else 'None'}

Already Recommended Plugins:
{', '.join(existing_plugin_names)}

Available Additional Plugins:
{json.dumps(available_plugins[:30], indent=2)}

Task: Analyze this project and recommend 0-5 additional plugins that would be highly valuable but aren't already recommended. Focus on plugins that match the specific tech stack and features.

Return your response as JSON in this exact format:
{{
  "additional_plugins": [
    {{
      "name": "plugin-name",
      "reason": "Why this plugin is valuable for this specific project",
      "priority": "high|medium|low"
    }}
  ]
}}

Only recommend plugins that are truly valuable for this specific project. If no additional plugins are needed, return an empty array."""

        return prompt

    def get_plugin_config_dict(
        self, config: ProjectConfig, use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Get plugin configuration as a dictionary for .claude/plugins.yaml.

        Args:
            config: Project configuration
            use_ai: Whether to use AI recommendations

        Returns:
            Dictionary ready to be written as YAML
        """
        recommendations = self.recommend_plugins(config, use_ai=use_ai)

        # Group by priority
        high_priority = [r for r in recommendations if r.priority == 'high']
        medium_priority = [r for r in recommendations if r.priority == 'medium']
        low_priority = [r for r in recommendations if r.priority == 'low']

        plugin_config = {
            'project_type': config.project_type,
            'project_name': config.project_name,
            'generated_by': 'claude-code-generator',
            'recommended_plugins': {
                'high_priority': [r.to_dict() for r in high_priority],
                'medium_priority': [r.to_dict() for r in medium_priority],
                'low_priority': [r.to_dict() for r in low_priority],
            },
            'installed_plugins': [],
            'notes': 'Install recommended plugins using the install_command for each plugin.',
        }

        return plugin_config
