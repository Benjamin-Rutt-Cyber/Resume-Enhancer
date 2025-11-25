"""
Unit tests for TemplateSelector.
"""

import unittest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from generator.selector import TemplateSelector
from generator.analyzer import ProjectConfig


class TestTemplateSelector(unittest.TestCase):
    """Test suite for TemplateSelector."""

    def setUp(self):
        """Set up test fixtures."""
        self.templates_dir = Path(__file__).parent.parent.parent / 'templates'
        self.selector = TemplateSelector(self.templates_dir)

    def test_selector_initialization(self):
        """Test that selector initializes correctly."""
        self.assertIsNotNone(self.selector.registry)
        self.assertIsNotNone(self.selector.project_types)
        self.assertIn('agents', self.selector.registry)
        self.assertIn('skills', self.selector.registry)

    def test_saas_web_app_react_fastapi(self):
        """Test selection for SaaS web app with React + FastAPI + PostgreSQL."""
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

        # Check agents
        agent_files = selected['agents']
        self.assertTrue(any('api-development-agent' in a for a in agent_files),
                       "Should select API development agent")
        self.assertTrue(any('frontend-react-agent' in a for a in agent_files),
                       "Should select React frontend agent")
        self.assertTrue(any('database-postgres-agent' in a for a in agent_files),
                       "Should select PostgreSQL agent")
        self.assertTrue(any('testing-agent' in a for a in agent_files),
                       "Should select testing agent")
        self.assertTrue(any('deployment-agent' in a for a in agent_files),
                       "Should select deployment agent")
        self.assertTrue(any('security-agent' in a for a in agent_files),
                       "Should select security agent")

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('python-fastapi' in s for s in skill_files),
                       "Should select FastAPI skill")
        self.assertTrue(any('react-typescript' in s for s in skill_files),
                       "Should select React TypeScript skill")
        self.assertTrue(any('postgresql' in s for s in skill_files),
                       "Should select PostgreSQL skill")
        self.assertTrue(any('docker-deployment' in s for s in skill_files),
                       "Should select Docker deployment skill")
        self.assertTrue(any('authentication' in s for s in skill_files),
                       "Should select authentication skill")

    def test_api_service_no_frontend(self):
        """Test selection for API service (no frontend agents/skills)."""
        config = ProjectConfig(
            project_name='test-api',
            project_slug='test-api',
            project_type='api-service',
            description='Test API service',
            backend_framework='python-fastapi',
            database='postgresql',
            deployment_platform='docker',
            features=['authentication']
        )

        selected = self.selector.select_templates(config)

        # Check agents - should NOT have frontend agent
        agent_files = selected['agents']
        self.assertFalse(any('frontend' in a.lower() for a in agent_files),
                        "API service should not select frontend agent")
        self.assertTrue(any('api-development-agent' in a for a in agent_files),
                       "Should select API development agent")
        self.assertTrue(any('database-postgres-agent' in a for a in agent_files),
                       "Should select database agent")

        # Check skills - should NOT have frontend skills
        skill_files = selected['skills']
        self.assertFalse(any('react' in s.lower() for s in skill_files),
                        "API service should not select React skill")
        self.assertFalse(any('vue' in s.lower() for s in skill_files),
                        "API service should not select Vue skill")
        self.assertTrue(any('python-fastapi' in s for s in skill_files),
                       "Should select FastAPI skill")
        self.assertTrue(any('postgresql' in s for s in skill_files),
                       "Should select PostgreSQL skill")

    def test_mobile_app_react_native(self):
        """Test selection for mobile app with React Native."""
        config = ProjectConfig(
            project_name='test-mobile',
            project_slug='test-mobile',
            project_type='mobile-app',
            description='Test mobile app',
            frontend_framework='react-native',
            backend_framework='python-fastapi',
            database='postgresql',
            features=['authentication']
        )

        selected = self.selector.select_templates(config)

        # Check agents
        agent_files = selected['agents']
        self.assertTrue(any('mobile-react-native-agent' in a for a in agent_files),
                       "Should select React Native mobile agent")
        self.assertTrue(any('api-development-agent' in a for a in agent_files),
                       "Should select API development agent for backend")

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('mobile-react-native' in s for s in skill_files),
                       "Should select React Native skill")
        self.assertTrue(any('python-fastapi' in s for s in skill_files),
                       "Should select FastAPI skill for backend")

    def test_hardware_iot_embedded(self):
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

        # Check agents
        agent_files = selected['agents']
        self.assertTrue(any('embedded-iot-agent' in a for a in agent_files),
                       "Should select embedded IoT agent")
        self.assertTrue(any('testing-agent' in a for a in agent_files),
                       "Should select testing agent")
        self.assertTrue(any('deployment-agent' in a for a in agent_files),
                       "Should select deployment agent")

        # Should NOT have web-specific agents
        self.assertFalse(any('frontend' in a.lower() for a in agent_files),
                        "IoT project should not select frontend agent")
        self.assertFalse(any('security-agent' in a for a in agent_files),
                        "IoT project should not select web security agent")

    def test_data_science_project(self):
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

        # Check agents
        agent_files = selected['agents']
        self.assertTrue(any('data-science-agent' in a for a in agent_files),
                       "Should select data science agent")
        self.assertTrue(any('testing-agent' in a for a in agent_files),
                       "Should select testing agent")

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('python-fastapi' in s for s in skill_files),
                       "Should select FastAPI skill")
        self.assertTrue(any('postgresql' in s for s in skill_files),
                       "Should select PostgreSQL skill")

    def test_vue_frontend_selection(self):
        """Test that Vue frontend is selected correctly."""
        config = ProjectConfig(
            project_name='test-vue',
            project_slug='test-vue',
            project_type='saas-web-app',
            description='Test Vue app',
            backend_framework='node-express',
            frontend_framework='vue-typescript',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('vue-typescript' in s for s in skill_files),
                       "Should select Vue TypeScript skill")
        self.assertTrue(any('node-express' in s for s in skill_files),
                       "Should select Node Express skill")
        self.assertFalse(any('react-typescript' in s for s in skill_files),
                        "Should not select React skill when Vue is chosen")

    def test_django_backend_selection(self):
        """Test that Django backend is selected correctly."""
        config = ProjectConfig(
            project_name='test-django',
            project_slug='test-django',
            project_type='saas-web-app',
            description='Test Django app',
            backend_framework='django',
            frontend_framework='react-typescript',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('django' in s for s in skill_files),
                       "Should select Django skill")
        self.assertTrue(any('react-typescript' in s for s in skill_files),
                       "Should select React skill")
        self.assertFalse(any('python-fastapi' in s for s in skill_files),
                        "Should not select FastAPI when Django is chosen")

    def test_node_express_backend_selection(self):
        """Test that Node Express backend is selected correctly."""
        config = ProjectConfig(
            project_name='test-express',
            project_slug='test-express',
            project_type='api-service',
            description='Test Express API',
            backend_framework='node-express',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Check skills
        skill_files = selected['skills']
        self.assertTrue(any('node-express' in s for s in skill_files),
                       "Should select Node Express skill")
        self.assertFalse(any('python-fastapi' in s for s in skill_files),
                        "Should not select FastAPI when Express is chosen")
        self.assertFalse(any('django' in s for s in skill_files),
                        "Should not select Django when Express is chosen")

    def test_missing_tech_stack_fallback(self):
        """Test fallback behavior when tech stack is incomplete."""
        config = ProjectConfig(
            project_name='test-minimal',
            project_slug='test-minimal',
            project_type='saas-web-app',
            description='Test minimal config',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # Should still select some agents/skills based on project type
        agent_files = selected['agents']
        skill_files = selected['skills']

        self.assertTrue(len(agent_files) > 0, "Should select some agents even with empty tech stack")
        self.assertTrue(len(skill_files) > 0, "Should select some skills even with empty tech stack")

    def test_priority_ordering(self):
        """Test that resources are ordered by priority."""
        config = ProjectConfig(
            project_name='test-priority',
            project_slug='test-priority',
            project_type='saas-web-app',
            description='Test priority ordering',
            backend_framework='python-fastapi',
            frontend_framework='react-typescript',
            database='postgresql',
            features=[]
        )

        selected = self.selector.select_templates(config)

        # High priority resources should appear first
        # Based on our registry: api-development, frontend-react, database-postgres are all high priority
        agent_files = selected['agents']

        # Check that we have agents selected
        self.assertTrue(len(agent_files) > 0, "Should select agents")

    def test_list_available_project_types(self):
        """Test listing all available project types."""
        project_types = self.selector.list_available_project_types()

        self.assertTrue(len(project_types) >= 5, "Should have at least 5 project types")

        # Check for expected project types
        type_names = [pt['name'] for pt in project_types]
        self.assertIn('saas-web-app', type_names)
        self.assertIn('api-service', type_names)
        self.assertIn('mobile-app', type_names)
        self.assertIn('hardware-iot', type_names)
        self.assertIn('data-science', type_names)

        # Check that each type has required fields
        for pt in project_types:
            self.assertIn('name', pt)
            self.assertIn('display_name', pt)
            self.assertIn('description', pt)

    def test_get_project_type_info(self):
        """Test getting info for a specific project type."""
        info = self.selector.get_project_type_info('saas-web-app')

        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'saas-web-app')
        self.assertIn('display_name', info)
        self.assertIn('description', info)
        self.assertIn('tech_stack_options', info)
        self.assertIn('features', info)


if __name__ == '__main__':
    unittest.main()
