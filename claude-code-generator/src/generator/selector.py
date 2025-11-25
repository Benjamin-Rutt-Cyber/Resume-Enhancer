"""
Template Selector - Selects appropriate templates based on project configuration.
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import yaml
from .constants import PRIORITY_ORDER
from .analyzer import ProjectConfig

logger = logging.getLogger(__name__)


class TemplateSelector:
    """Select templates based on project configuration."""

    def __init__(self, templates_dir: Path):
        """
        Initialize selector with templates directory.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = Path(templates_dir)
        self.registry = self._load_registry()
        self.project_types = self._load_project_types()

    def _load_registry(self) -> Dict[str, Any]:
        """Load template registry with error handling."""
        registry_path = self.templates_dir / 'registry.yaml'
        default_registry = {'agents': [], 'skills': [], 'commands': [], 'docs': []}

        if not registry_path.exists():
            logger.warning(f"Registry not found at {registry_path}, using defaults")
            return default_registry

        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

                # Validate structure
                if not isinstance(config, dict):
                    logger.error(f"Registry must be a dictionary, got {type(config)}")
                    raise ValueError(f"Invalid registry format in {registry_path}")

                return config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in registry: {e}")
            raise ValueError(f"Failed to parse {registry_path}: {e}") from e
        except (IOError, OSError) as e:
            logger.error(f"Cannot read registry file: {e}")
            raise IOError(f"Failed to read {registry_path}: {e}") from e

    def _load_project_types(self) -> Dict[str, Any]:
        """Load all project type configurations with error handling."""
        project_types = {}
        project_types_dir = self.templates_dir / 'project-types'

        if not project_types_dir.exists():
            logger.warning(f"Project types directory not found at {project_types_dir}")
            return {}

        for yaml_file in project_types_dir.glob('*.yaml'):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                    # Validate structure
                    if not isinstance(config, dict):
                        logger.warning(f"Skipping {yaml_file}: not a dictionary")
                        continue

                    if 'name' not in config:
                        logger.warning(f"Skipping {yaml_file}: missing 'name' field")
                        continue

                    project_types[config['name']] = config

            except yaml.YAMLError as e:
                logger.error(f"Invalid YAML in {yaml_file}: {e}")
                continue  # Skip this file, continue with others
            except (IOError, OSError) as e:
                logger.error(f"Cannot read {yaml_file}: {e}")
                continue  # Skip this file, continue with others

        return project_types

    def select_templates(self, config: ProjectConfig) -> Dict[str, List[str]]:
        """
        Select templates for a project configuration.

        Args:
            config: Validated project configuration

        Returns:
            Dictionary with lists of template files for each category

        Example:
            {
                'agents': ['agents/api-development-agent.md.j2', ...],
                'skills': ['skills/python-fastapi/', ...],
                'commands': ['commands/setup-dev.md.j2', ...],
                'docs': ['docs/ARCHITECTURE.md.j2', ...]
            }
        """
        # Get project type configuration
        project_type_config = self.project_types.get(config.project_type)
        if not project_type_config:
            # Fallback to minimal set
            return self._get_minimal_templates()

        # Base templates from project type
        selected = {
            'agents': self._select_agents(config, project_type_config),
            'skills': self._select_skills(config, project_type_config),
            'commands': self._select_commands(config, project_type_config),
            'docs': self._select_docs(config, project_type_config)
        }

        # Add feature-specific templates
        selected = self._add_feature_templates(selected, config, project_type_config)

        return selected

    def _select_agents(
        self, config: ProjectConfig, project_type_config: Dict[str, Any]
    ) -> List[str]:
        """Select agent templates using smart selection algorithm."""
        # Use smart selection based on selection_conditions
        selected_agents = self._select_by_conditions(
            self.registry.get('agents', []),
            config
        )

        # Sort by priority (high > medium > low)
        selected_agents.sort(key=lambda a: PRIORITY_ORDER.get(a.get('priority', 'medium'), 1))

        # Return file paths
        return [agent['file'] for agent in selected_agents]

    def _select_skills(
        self, config: ProjectConfig, project_type_config: Dict[str, Any]
    ) -> List[str]:
        """Select skill templates using smart selection algorithm."""
        # Use smart selection based on selection_conditions
        selected_skills = self._select_by_conditions(
            self.registry.get('skills', []),
            config
        )

        # Sort by priority (high > medium > low)
        selected_skills.sort(key=lambda s: PRIORITY_ORDER.get(s.get('priority', 'medium'), 1))

        # Return file paths
        return [skill['file'] for skill in selected_skills]

    def _select_commands(
        self, config: ProjectConfig, project_type_config: Dict[str, Any]
    ) -> List[str]:
        """Select command templates."""
        command_names = project_type_config.get('commands', [])

        # Get template files from registry
        command_templates = []
        for command in self.registry.get('commands', []):
            if command['name'] in command_names:
                command_templates.append(command['file'])

        return command_templates

    def _select_docs(
        self, config: ProjectConfig, project_type_config: Dict[str, Any]
    ) -> List[str]:
        """Select documentation templates using smart selection."""
        docs = self.registry.get('docs', [])

        # Use smart selection for library docs with selection_conditions
        selected_docs = self._select_by_conditions(docs, config)

        # Get file paths and sort by priority
        doc_paths = [doc['file'] for doc in selected_docs]

        # Also add legacy docs from project_type_config (for .j2 templates)
        doc_names = project_type_config.get('docs', [])
        for doc in docs:
            if doc['name'] in doc_names and doc['file'] not in doc_paths:
                doc_paths.append(doc['file'])

        return doc_paths

    def _select_by_conditions(
        self, resources: List[Dict[str, Any]], config: ProjectConfig
    ) -> List[Dict[str, Any]]:
        """
        Select resources based on selection_conditions.

        Implements smart selection algorithm:
        1. Filter by project_type
        2. Filter by required_any (OR logic)
        3. Filter by required_all (AND logic)
        4. Fallback to always-applicable resources

        Args:
            resources: List of agent/skill dicts from registry
            config: Project configuration

        Returns:
            List of selected resource dicts
        """
        selected = []

        # Build tech stack dict from config attributes
        tech_stack = {
            'backend': getattr(config, 'backend_framework', '') or '',
            'frontend_framework': getattr(config, 'frontend_framework', '') or '',
            'database': getattr(config, 'database', '') or '',
            'deployment': getattr(config, 'deployment_platform', '') or '',
            'framework': getattr(config, 'framework', '') or '',  # For mobile (if exists)
        }

        for resource in resources:
            # Skip resources without selection_conditions (old format)
            if 'selection_conditions' not in resource:
                continue

            conditions = resource['selection_conditions']

            # 1. Filter by project_types
            project_types = conditions.get('project_types', [])
            if project_types and config.project_type not in project_types:
                continue

            # 2. Filter by required_any (OR logic)
            required_any = conditions.get('required_any', {})
            if required_any:
                match_found = False
                for field, values in required_any.items():
                    if tech_stack.get(field, '') in values:
                        match_found = True
                        break
                if not match_found:
                    continue  # Skip if no OR match

            # 3. Filter by required_all (AND logic)
            required_all = conditions.get('required_all', {})
            if required_all:
                all_matched = True
                for field, values in required_all.items():
                    if tech_stack.get(field, '') not in values:
                        all_matched = False
                        break
                if not all_matched:
                    continue  # Skip if not all AND conditions met

            # All conditions passed - include this resource
            selected.append(resource)

        return selected

    def _add_feature_templates(
        self,
        selected: Dict[str, List[str]],
        config: ProjectConfig,
        project_type_config: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Add templates for selected features."""
        features_config = project_type_config.get('features', [])

        for feature_config in features_config:
            feature_name = feature_config.get('name')

            if feature_name in config.features:
                # Add agents for this feature
                feature_agents = feature_config.get('adds_agents', [])
                for agent_name in feature_agents:
                    # Find template file
                    for agent in self.registry.get('agents', []):
                        if agent['name'] == agent_name:
                            if agent['file'] not in selected['agents']:
                                selected['agents'].append(agent['file'])

                # Add skills for this feature
                feature_skills = feature_config.get('adds_skills', [])
                for skill_name in feature_skills:
                    # Find template file
                    for skill in self.registry.get('skills', []):
                        if skill['name'] == skill_name:
                            if skill['file'] not in selected['skills']:
                                selected['skills'].append(skill['file'])

        return selected

    def _get_minimal_templates(self) -> Dict[str, List[str]]:
        """Return minimal template set as fallback."""
        return {
            'agents': ['agents/library/api-development-agent.md'],
            'skills': ['skills/library/python-fastapi/SKILL.md'],
            'commands': ['commands/setup-dev.md.j2', 'commands/run-server.md.j2'],
            'docs': ['docs/ARCHITECTURE.md.j2', 'docs/SETUP.md.j2']
        }

    def get_project_type_info(self, project_type: str) -> Dict[str, Any]:
        """
        Get information about a project type.

        Args:
            project_type: Project type name

        Returns:
            Project type configuration
        """
        return self.project_types.get(project_type, {})

    def list_available_project_types(self) -> List[Dict[str, str]]:
        """
        List all available project types.

        Returns:
            List of project type info dictionaries
        """
        types = []
        for name, config in self.project_types.items():
            types.append({
                'name': name,
                'display_name': config.get('display_name', name),
                'description': config.get('description', '')
            })
        return types
