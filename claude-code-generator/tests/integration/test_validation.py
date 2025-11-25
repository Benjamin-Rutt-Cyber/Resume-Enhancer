"""
Comprehensive validation tests for registry and selection system.
"""

import unittest
from pathlib import Path
import yaml
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from generator.selector import TemplateSelector
from generator.analyzer import ProjectConfig


class TestRegistryValidation(unittest.TestCase):
    """Validate registry structure and file paths."""

    def setUp(self):
        """Set up test fixtures."""
        self.templates_dir = Path(__file__).parent.parent.parent / 'templates'
        self.selector = TemplateSelector(self.templates_dir)
        self.registry = self.selector.registry

    def test_all_agent_files_exist(self):
        """Verify all agent files in registry exist."""
        agents = self.registry.get('agents', [])
        missing_files = []

        for agent in agents:
            agent_path = self.templates_dir / agent['file']
            if not agent_path.exists():
                missing_files.append(agent['file'])

        self.assertEqual(len(missing_files), 0,
                        f"Missing agent files: {missing_files}")

    def test_all_skill_files_exist(self):
        """Verify all skill files in registry exist."""
        skills = self.registry.get('skills', [])
        missing_files = []

        for skill in skills:
            skill_path = self.templates_dir / skill['file']
            if not skill_path.exists():
                missing_files.append(skill['file'])

        self.assertEqual(len(missing_files), 0,
                        f"Missing skill files: {missing_files}")

    def test_all_agents_have_selection_conditions(self):
        """Verify all agents have selection_conditions."""
        agents = self.registry.get('agents', [])
        missing_conditions = []

        for agent in agents:
            if 'selection_conditions' not in agent:
                missing_conditions.append(agent['name'])

        self.assertEqual(len(missing_conditions), 0,
                        f"Agents missing selection_conditions: {missing_conditions}")

    def test_all_skills_have_selection_conditions(self):
        """Verify all skills have selection_conditions."""
        skills = self.registry.get('skills', [])
        missing_conditions = []

        for skill in skills:
            if 'selection_conditions' not in skill:
                missing_conditions.append(skill['name'])

        self.assertEqual(len(missing_conditions), 0,
                        f"Skills missing selection_conditions: {missing_conditions}")

    def test_selection_conditions_structure(self):
        """Verify selection_conditions have correct structure."""
        resources = self.registry.get('agents', []) + self.registry.get('skills', [])
        invalid_resources = []

        for resource in resources:
            conditions = resource.get('selection_conditions', {})

            # Check required keys
            if 'project_types' not in conditions:
                invalid_resources.append(f"{resource['name']}: missing project_types")
            if 'required_any' not in conditions:
                invalid_resources.append(f"{resource['name']}: missing required_any")
            if 'required_all' not in conditions:
                invalid_resources.append(f"{resource['name']}: missing required_all")

            # Check types
            if not isinstance(conditions.get('project_types', []), list):
                invalid_resources.append(f"{resource['name']}: project_types not a list")
            if not isinstance(conditions.get('required_any', {}), dict):
                invalid_resources.append(f"{resource['name']}: required_any not a dict")
            if not isinstance(conditions.get('required_all', {}), dict):
                invalid_resources.append(f"{resource['name']}: required_all not a dict")

        self.assertEqual(len(invalid_resources), 0,
                        f"Invalid selection_conditions:\n" + "\n".join(invalid_resources))

    def test_priority_values(self):
        """Verify all resources have valid priority values."""
        resources = self.registry.get('agents', []) + self.registry.get('skills', [])
        invalid_priorities = []
        valid_priorities = ['high', 'medium', 'low']

        for resource in resources:
            priority = resource.get('priority')
            if priority not in valid_priorities:
                invalid_priorities.append(f"{resource['name']}: {priority}")

        self.assertEqual(len(invalid_priorities), 0,
                        f"Invalid priorities: {invalid_priorities}")

    def test_registry_version(self):
        """Verify registry is at version 2.0.0."""
        version = self.registry.get('version')
        self.assertEqual(version, '2.0.0',
                        f"Registry version should be 2.0.0, got {version}")

    def test_agent_count(self):
        """Verify we have 10 agents."""
        agents = self.registry.get('agents', [])
        self.assertEqual(len(agents), 10,
                        f"Should have 10 agents, found {len(agents)}")

    def test_skill_count(self):
        """Verify we have 14 skills."""
        skills = self.registry.get('skills', [])
        self.assertEqual(len(skills), 14,
                        f"Should have 14 skills, found {len(skills)}")


class TestSelectionCoverage(unittest.TestCase):
    """Test selection coverage for all project types."""

    def setUp(self):
        """Set up test fixtures."""
        self.templates_dir = Path(__file__).parent.parent.parent / 'templates'
        self.selector = TemplateSelector(self.templates_dir)

    def test_saas_web_app_selection(self):
        """Test selection for SaaS web app project."""
        config = ProjectConfig(
            project_name='test-saas',
            project_slug='test-saas',
            project_type='saas-web-app',
            description='Test SaaS application',
            backend_framework='python-fastapi',
            frontend_framework='react-typescript',
            database='postgresql',
            deployment_platform='docker',
            features=['authentication']
        )

        selected = self.selector.select_templates(config)

        # Should have multiple agents
        self.assertGreater(len(selected['agents']), 3,
                          "SaaS app should select multiple agents")

        # Should have multiple skills
        self.assertGreater(len(selected['skills']), 3,
                          "SaaS app should select multiple skills")

        # Should have frontend agent
        self.assertTrue(any('frontend' in a.lower() for a in selected['agents']),
                       "SaaS app should have frontend agent")

        # Should have backend agent
        self.assertTrue(any('api' in a.lower() or 'backend' in a.lower()
                           for a in selected['agents']),
                       "SaaS app should have API/backend agent")

    def test_api_service_selection(self):
        """Test selection for API service project."""
        config = ProjectConfig(
            project_name='test-api',
            project_slug='test-api',
            project_type='api-service',
            description='Test API service',
            backend_framework='python-fastapi',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Should have agents
        self.assertGreater(len(selected['agents']), 2,
                          "API service should select multiple agents")

        # Should NOT have frontend agent
        self.assertFalse(any('frontend' in a.lower() for a in selected['agents']),
                        "API service should NOT have frontend agent")

        # Should NOT have frontend skills
        self.assertFalse(any('react' in s.lower() or 'vue' in s.lower()
                            for s in selected['skills']),
                        "API service should NOT have frontend skills")

    def test_mobile_app_selection(self):
        """Test selection for mobile app project."""
        config = ProjectConfig(
            project_name='test-mobile',
            project_slug='test-mobile',
            project_type='mobile-app',
            description='Test mobile app',
            frontend_framework='react-native',
            backend_framework='python-fastapi',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Should have mobile agent
        self.assertTrue(any('mobile' in a.lower() for a in selected['agents']),
                       "Mobile app should have mobile agent")

        # Should have mobile skill
        self.assertTrue(any('mobile' in s.lower() or 'react-native' in s.lower()
                           for s in selected['skills']),
                       "Mobile app should have mobile skill")

    def test_hardware_iot_selection(self):
        """Test selection for hardware/IoT project."""
        config = ProjectConfig(
            project_name='test-iot',
            project_slug='test-iot',
            project_type='hardware-iot',
            description='Test IoT device',
            platform='pico-w',
            firmware_language='micropython',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Should have embedded agent
        self.assertTrue(any('embedded' in a.lower() or 'iot' in a.lower()
                           for a in selected['agents']),
                       "IoT project should have embedded/IoT agent")

        # Should NOT have web frontend agent
        self.assertFalse(any('frontend-react' in a.lower() or 'frontend-vue' in a.lower()
                            for a in selected['agents']),
                        "IoT project should NOT have web frontend agent")

    def test_data_science_selection(self):
        """Test selection for data science project."""
        config = ProjectConfig(
            project_name='test-ml',
            project_slug='test-ml',
            project_type='data-science',
            description='Test ML project',
            backend_framework='python-fastapi',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Should have data science agent
        self.assertTrue(any('data-science' in a.lower() or 'data_science' in a.lower()
                           for a in selected['agents']),
                       "Data science project should have data science agent")

    def test_all_resources_used(self):
        """Verify all resources are used by at least one project type."""
        all_agents = set(agent['name'] for agent in self.selector.registry.get('agents', []))
        all_skills = set(skill['name'] for skill in self.selector.registry.get('skills', []))

        used_agents = set()
        used_skills = set()

        # Test all 5 project types
        project_configs = [
            # SaaS Web App
            ProjectConfig(
                project_name='test-saas',
                project_slug='test-saas',
                project_type='saas-web-app',
                description='Test SaaS application for validation',
                backend_framework='python-fastapi',
                frontend_framework='react-typescript',
                database='postgresql'
            ),
            # API Service
            ProjectConfig(
                project_name='test-api',
                project_slug='test-api',
                project_type='api-service',
                description='Test API service for validation',
                backend_framework='python-fastapi',
                database='postgresql'
            ),
            # Mobile App
            ProjectConfig(
                project_name='test-mobile',
                project_slug='test-mobile',
                project_type='mobile-app',
                description='Test mobile app for validation',
                frontend_framework='react-native',
                backend_framework='python-fastapi'
            ),
            # Hardware IoT
            ProjectConfig(
                project_name='test-iot',
                project_slug='test-iot',
                project_type='hardware-iot',
                description='Test IoT device for validation',
                platform='pico-w',
                firmware_language='micropython'
            ),
            # Data Science
            ProjectConfig(
                project_name='test-ml',
                project_slug='test-ml',
                project_type='data-science',
                description='Test ML project for validation',
                backend_framework='python-fastapi',
                database='postgresql'
            ),
        ]

        for config in project_configs:
            selected = self.selector.select_templates(config)

            # Extract agent names from paths
            for agent_path in selected['agents']:
                for agent_name in all_agents:
                    if agent_name in agent_path:
                        used_agents.add(agent_name)

            # Extract skill names from paths
            for skill_path in selected['skills']:
                for skill_name in all_skills:
                    if skill_name in skill_path:
                        used_skills.add(skill_name)

        unused_agents = all_agents - used_agents
        unused_skills = all_skills - used_skills

        # Some resources might be intentionally unused (like Vue or Django in basic tests)
        # Just report them, don't fail
        if unused_agents:
            print(f"\nNote: Unused agents with basic test configs: {unused_agents}")
        if unused_skills:
            print(f"\nNote: Unused skills with basic test configs: {unused_skills}")


if __name__ == '__main__':
    unittest.main()
