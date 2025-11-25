"""
Comprehensive unit tests for PluginAnalyzer.

Tests cover:
- Plugin recommendation logic (rule-based)
- AI-powered recommendations (mocked)
- Plugin filtering based on conditions
- Plugin metadata lookup
- Config dict generation for plugins.yaml
- Error handling and edge cases
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import json

from src.generator.plugin_analyzer import PluginAnalyzer, PluginRecommendation
from src.generator.analyzer import ProjectConfig


# ==================== Fixtures ====================

@pytest.fixture
def mock_templates_dir(tmp_path):
    """Create a mock templates directory with plugin configs."""
    templates = tmp_path / 'templates'
    templates.mkdir()

    # Create plugins directory with registry
    plugins_dir = templates / 'plugins'
    plugins_dir.mkdir()

    # Create plugin registry
    registry = {
        'plugins': [
            {
                'name': 'testing-plugin',
                'marketplace_id': 'test@marketplace',
                'install_command': '/plugin install testing-plugin',
                'category': 'development',
                'description': 'Testing utilities'
            },
            {
                'name': 'linting-plugin',
                'marketplace_id': 'lint@marketplace',
                'install_command': '/plugin install linting-plugin',
                'category': 'quality',
                'description': 'Code linting'
            },
            {
                'name': 'react-plugin',
                'marketplace_id': 'react@marketplace',
                'install_command': '/plugin install react-plugin',
                'category': 'frontend',
                'description': 'React development tools'
            },
            {
                'name': 'python-plugin',
                'marketplace_id': 'python@marketplace',
                'install_command': '/plugin install python-plugin',
                'category': 'backend',
                'description': 'Python development tools'
            }
        ]
    }

    (plugins_dir / 'registry.yaml').write_text(yaml.dump(registry))

    # Create project-types directory
    project_types_dir = templates / 'project-types'
    project_types_dir.mkdir()

    # Create saas-web-app project type config
    saas_config = {
        'name': 'saas-web-app',
        'recommended_plugins': [
            {
                'name': 'testing-plugin',
                'reason': 'Essential for SaaS testing',
                'priority': 'high'
            },
            {
                'name': 'linting-plugin',
                'reason': 'Code quality',
                'priority': 'medium'
            },
            {
                'name': 'react-plugin',
                'reason': 'React development',
                'priority': 'high',
                'conditions': {
                    'frontend': ['react', 'react-typescript']
                }
            },
            {
                'name': 'python-plugin',
                'reason': 'Python backend',
                'priority': 'medium',
                'conditions': {
                    'backend': ['python-fastapi', 'django', 'flask']
                }
            }
        ]
    }

    (project_types_dir / 'saas-web-app.yaml').write_text(yaml.dump(saas_config))

    # Create api-service project type config
    api_config = {
        'name': 'api-service',
        'recommended_plugins': [
            {
                'name': 'testing-plugin',
                'reason': 'API testing',
                'priority': 'high'
            },
            {
                'name': 'python-plugin',
                'reason': 'Python backend',
                'priority': 'high'
            }
        ]
    }

    (project_types_dir / 'api-service.yaml').write_text(yaml.dump(api_config))

    return templates


@pytest.fixture
def plugin_analyzer(mock_templates_dir):
    """Create a PluginAnalyzer instance without AI."""
    return PluginAnalyzer(api_key=None, templates_dir=mock_templates_dir)


@pytest.fixture
def plugin_analyzer_with_ai(mock_templates_dir):
    """Create a PluginAnalyzer instance with mocked AI."""
    return PluginAnalyzer(api_key='fake-api-key', templates_dir=mock_templates_dir)


@pytest.fixture
def sample_saas_config():
    """Create a sample SaaS project config."""
    return ProjectConfig(
        project_name="My SaaS App",
        project_slug="my-saas-app",
        description="A SaaS application",
        project_type="saas-web-app",
        backend_framework="python-fastapi",
        frontend_framework="react",
        database="postgresql",
        features=["authentication", "api"],
        deployment_platform="docker"
    )


@pytest.fixture
def sample_api_config():
    """Create a sample API service config."""
    return ProjectConfig(
        project_name="My API",
        project_slug="my-api",
        description="An API service",
        project_type="api-service",
        backend_framework="python-fastapi",
        features=["api", "database"]
    )


# ==================== Test PluginRecommendation ====================

class TestPluginRecommendation:
    """Test PluginRecommendation data class."""

    def test_create_recommendation(self):
        """Test creating a plugin recommendation."""
        rec = PluginRecommendation(
            name="test-plugin",
            reason="For testing",
            priority="high"
        )

        assert rec.name == "test-plugin"
        assert rec.reason == "For testing"
        assert rec.priority == "high"

    def test_default_values(self):
        """Test default values for optional fields."""
        rec = PluginRecommendation(
            name="test-plugin",
            reason="For testing",
            priority="medium"
        )

        # Defaults
        assert rec.marketplace_id == "test-plugin"
        assert rec.install_command == "/plugin install test-plugin"
        assert rec.category == "productivity"

    def test_custom_values(self):
        """Test custom values override defaults."""
        rec = PluginRecommendation(
            name="test-plugin",
            reason="For testing",
            priority="low",
            marketplace_id="custom@marketplace",
            install_command="/custom install",
            category="development"
        )

        assert rec.marketplace_id == "custom@marketplace"
        assert rec.install_command == "/custom install"
        assert rec.category == "development"

    def test_to_dict(self):
        """Test converting recommendation to dictionary."""
        rec = PluginRecommendation(
            name="test-plugin",
            reason="For testing",
            priority="high",
            category="dev"
        )

        result = rec.to_dict()

        assert result['name'] == "test-plugin"
        assert result['reason'] == "For testing"
        assert result['priority'] == "high"
        assert result['category'] == "dev"
        assert 'marketplace_id' in result
        assert 'install_command' in result


# ==================== Test Initialization ====================

class TestInitialization:
    """Test PluginAnalyzer initialization."""

    def test_init_without_api_key(self, mock_templates_dir):
        """Test initialization without API key."""
        analyzer = PluginAnalyzer(api_key=None, templates_dir=mock_templates_dir)

        assert analyzer.api_key is None
        assert analyzer.client is None
        assert analyzer.templates_dir == mock_templates_dir

    def test_init_with_api_key(self, mock_templates_dir):
        """Test initialization with API key."""
        analyzer = PluginAnalyzer(api_key='test-key', templates_dir=mock_templates_dir)

        assert analyzer.api_key == 'test-key'
        assert analyzer.client is not None

    def test_init_loads_plugin_registry(self, plugin_analyzer):
        """Test that initialization loads plugin registry."""
        assert 'plugins' in plugin_analyzer.plugin_registry
        assert len(plugin_analyzer.plugin_registry['plugins']) == 4

    def test_init_missing_registry_warns(self, tmp_path, caplog):
        """Test warning when registry is missing."""
        templates = tmp_path / 'templates'
        templates.mkdir()

        analyzer = PluginAnalyzer(api_key=None, templates_dir=templates)

        import logging
        caplog.set_level(logging.WARNING)
        assert any('not found' in record.message for record in caplog.records)
        assert analyzer.plugin_registry == {"plugins": []}


# ==================== Test recommend_plugins() ====================

class TestRecommendPlugins:
    """Test main plugin recommendation logic."""

    def test_recommend_plugins_basic(self, plugin_analyzer, sample_saas_config):
        """Test basic plugin recommendation without AI."""
        recommendations = plugin_analyzer.recommend_plugins(
            sample_saas_config,
            use_ai=False
        )

        # Should get recommendations from project type
        assert len(recommendations) > 0
        names = [r.name for r in recommendations]
        assert 'testing-plugin' in names

    def test_recommend_plugins_sorted_by_priority(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that recommendations are sorted by priority."""
        recommendations = plugin_analyzer.recommend_plugins(
            sample_saas_config,
            use_ai=False
        )

        # High priority should come first
        priorities = [r.priority for r in recommendations]
        # Check that high comes before medium, medium before low
        if 'high' in priorities and 'medium' in priorities:
            high_idx = priorities.index('high')
            medium_idx = priorities.index('medium')
            assert high_idx < medium_idx

    def test_recommend_plugins_filters_by_conditions(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that plugins are filtered based on conditions."""
        # SaaS with React should get react-plugin
        recommendations = plugin_analyzer.recommend_plugins(
            sample_saas_config,
            use_ai=False
        )

        names = [r.name for r in recommendations]
        assert 'react-plugin' in names  # React is in frontend_framework
        assert 'python-plugin' in names  # Python-fastapi matches

    def test_recommend_plugins_excludes_non_matching(self, plugin_analyzer):
        """Test that non-matching plugins are excluded."""
        # API service without React should not get react-plugin
        config = ProjectConfig(
            project_name="API",
            project_slug="api",
            description="API service without frontend",
            project_type="api-service",
            backend_framework="python-fastapi",
            features=[]
        )

        recommendations = plugin_analyzer.recommend_plugins(config, use_ai=False)

        names = [r.name for r in recommendations]
        assert 'react-plugin' not in names  # No React


# ==================== Test _get_project_type_recommendations() ====================

class TestGetProjectTypeRecommendations:
    """Test loading recommendations from project type config."""

    def test_get_project_type_recommendations(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test loading recommendations from project type."""
        recommendations = plugin_analyzer._get_project_type_recommendations(
            sample_saas_config
        )

        assert len(recommendations) > 0
        names = [r.name for r in recommendations]
        assert 'testing-plugin' in names
        assert 'linting-plugin' in names

    def test_recommendations_include_metadata(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that recommendations include registry metadata."""
        recommendations = plugin_analyzer._get_project_type_recommendations(
            sample_saas_config
        )

        testing_rec = next(r for r in recommendations if r.name == 'testing-plugin')
        assert testing_rec.marketplace_id == 'test@marketplace'
        assert testing_rec.category == 'development'
        assert testing_rec.install_command == '/plugin install testing-plugin'


# ==================== Test _get_plugin_metadata() ====================

class TestGetPluginMetadata:
    """Test plugin metadata lookup."""

    def test_get_plugin_metadata_found(self, plugin_analyzer):
        """Test getting metadata for plugin in registry."""
        metadata = plugin_analyzer._get_plugin_metadata('testing-plugin')

        assert metadata['marketplace_id'] == 'test@marketplace'
        assert metadata['category'] == 'development'
        assert metadata['description'] == 'Testing utilities'

    def test_get_plugin_metadata_not_found(self, plugin_analyzer):
        """Test getting metadata for plugin not in registry."""
        metadata = plugin_analyzer._get_plugin_metadata('unknown-plugin')

        # Should return defaults
        assert metadata['marketplace_id'] == 'unknown-plugin'
        assert metadata['install_command'] == '/plugin install unknown-plugin'
        assert metadata['category'] == 'productivity'


# ==================== Test _filter_recommendations() ====================

class TestFilterRecommendations:
    """Test recommendation filtering based on conditions."""

    def test_filter_no_conditions(self, plugin_analyzer, sample_saas_config):
        """Test that plugins without conditions are always included."""
        # testing-plugin has no conditions
        base_recs = plugin_analyzer._get_project_type_recommendations(sample_saas_config)
        filtered = plugin_analyzer._filter_recommendations(sample_saas_config, base_recs)

        names = [r.name for r in filtered]
        assert 'testing-plugin' in names
        assert 'linting-plugin' in names

    def test_filter_matching_condition(self, plugin_analyzer, sample_saas_config):
        """Test that plugins with matching conditions are included."""
        base_recs = plugin_analyzer._get_project_type_recommendations(sample_saas_config)
        filtered = plugin_analyzer._filter_recommendations(sample_saas_config, base_recs)

        names = [r.name for r in filtered]
        # React condition matches
        assert 'react-plugin' in names
        # Python-fastapi condition matches
        assert 'python-plugin' in names

    def test_filter_non_matching_condition(self, plugin_analyzer):
        """Test that plugins with non-matching conditions are excluded."""
        # Config with Vue instead of React
        config = ProjectConfig(
            project_name="Vue App",
            project_slug="vue-app",
            description="A Vue.js application",
            project_type="saas-web-app",
            frontend_framework="vue",
            backend_framework="node-express",
            features=[]
        )

        base_recs = plugin_analyzer._get_project_type_recommendations(config)
        filtered = plugin_analyzer._filter_recommendations(config, base_recs)

        names = [r.name for r in filtered]
        # React plugin should be excluded (Vue doesn't match React condition)
        assert 'react-plugin' not in names
        # Python plugin should be excluded (node-express doesn't match python condition)
        assert 'python-plugin' not in names


# ==================== Test _get_config_value() ====================

class TestGetConfigValue:
    """Test config value extraction."""

    def test_get_config_value_backend(self, plugin_analyzer, sample_saas_config):
        """Test getting backend framework value."""
        value = plugin_analyzer._get_config_value(sample_saas_config, 'backend')
        assert value == 'python-fastapi'

    def test_get_config_value_frontend(self, plugin_analyzer, sample_saas_config):
        """Test getting frontend framework value."""
        value = plugin_analyzer._get_config_value(sample_saas_config, 'frontend')
        assert value == 'react'

    def test_get_config_value_database(self, plugin_analyzer, sample_saas_config):
        """Test getting database value."""
        value = plugin_analyzer._get_config_value(sample_saas_config, 'database')
        assert value == 'postgresql'

    def test_get_config_value_features(self, plugin_analyzer, sample_saas_config):
        """Test getting features list."""
        value = plugin_analyzer._get_config_value(sample_saas_config, 'features')
        assert isinstance(value, list)
        assert 'authentication' in value

    def test_get_config_value_unknown_key(self, plugin_analyzer, sample_saas_config):
        """Test getting value for unknown key."""
        value = plugin_analyzer._get_config_value(sample_saas_config, 'unknown')
        assert value is None


# ==================== Test get_plugin_config_dict() ====================

class TestGetPluginConfigDict:
    """Test plugin config dictionary generation."""

    def test_get_plugin_config_dict_structure(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that config dict has correct structure."""
        config_dict = plugin_analyzer.get_plugin_config_dict(
            sample_saas_config,
            use_ai=False
        )

        # Verify top-level keys
        assert 'project_type' in config_dict
        assert 'project_name' in config_dict
        assert 'generated_by' in config_dict
        assert 'recommended_plugins' in config_dict
        assert 'installed_plugins' in config_dict
        assert 'notes' in config_dict

        # Verify project info
        assert config_dict['project_type'] == 'saas-web-app'
        assert config_dict['project_name'] == 'My SaaS App'
        assert config_dict['generated_by'] == 'claude-code-generator'

    def test_get_plugin_config_dict_priorities(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that plugins are grouped by priority."""
        config_dict = plugin_analyzer.get_plugin_config_dict(
            sample_saas_config,
            use_ai=False
        )

        rec_plugins = config_dict['recommended_plugins']
        assert 'high_priority' in rec_plugins
        assert 'medium_priority' in rec_plugins
        assert 'low_priority' in rec_plugins

        # Should have some high priority plugins
        assert len(rec_plugins['high_priority']) > 0

    def test_get_plugin_config_dict_plugin_details(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that each plugin includes all details."""
        config_dict = plugin_analyzer.get_plugin_config_dict(
            sample_saas_config,
            use_ai=False
        )

        # Get first plugin from any priority
        all_plugins = (
            config_dict['recommended_plugins']['high_priority'] +
            config_dict['recommended_plugins']['medium_priority'] +
            config_dict['recommended_plugins']['low_priority']
        )

        if all_plugins:
            plugin = all_plugins[0]
            assert 'name' in plugin
            assert 'reason' in plugin
            assert 'priority' in plugin
            assert 'marketplace_id' in plugin
            assert 'install_command' in plugin
            assert 'category' in plugin


# ==================== Test AI Recommendations (Mocked) ====================

class TestAIRecommendations:
    """Test AI-powered recommendations with mocked API."""

    def test_ai_recommendations_disabled_without_client(
        self, plugin_analyzer, sample_saas_config
    ):
        """Test that AI recommendations are skipped without API client."""
        # plugin_analyzer has no client
        recommendations = plugin_analyzer.recommend_plugins(
            sample_saas_config,
            use_ai=True  # Request AI but should skip
        )

        # Should still get base recommendations
        assert len(recommendations) > 0

    def test_ai_recommendations_with_mocked_api(
        self, plugin_analyzer_with_ai, sample_saas_config
    ):
        """Test AI recommendations with mocked API response."""
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "additional_plugins": [
                {
                    "name": "testing-plugin",
                    "reason": "Enhanced testing for SaaS",
                    "priority": "high"
                }
            ]
        }))]

        with patch.object(plugin_analyzer_with_ai.client.messages, 'create', return_value=mock_response):
            recommendations = plugin_analyzer_with_ai.recommend_plugins(
                sample_saas_config,
                use_ai=True
            )

            # Should get recommendations
            assert len(recommendations) > 0

    def test_ai_recommendations_error_handling(
        self, plugin_analyzer_with_ai, sample_saas_config, caplog
    ):
        """Test that AI errors are handled gracefully."""
        import logging
        caplog.set_level(logging.WARNING)

        # Mock the API to raise a JSON decode error (common failure mode)
        with patch.object(
            plugin_analyzer_with_ai.client.messages,
            'create',
            side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
        ):
            recommendations = plugin_analyzer_with_ai.recommend_plugins(
                sample_saas_config,
                use_ai=True
            )

            # Should still return base recommendations
            assert len(recommendations) > 0

            # Should log warning
            assert any('Failed to parse AI response' in record.message for record in caplog.records)


# ==================== Test Edge Cases ====================

class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_missing_project_type_config(
        self, plugin_analyzer, capsys
    ):
        """Test handling of missing project type config."""
        config = ProjectConfig(
            project_name="Test",
            project_slug="test",
            description="Test project for missing type",
            project_type="nonexistent-type",
            features=[]
        )

        recommendations = plugin_analyzer.recommend_plugins(config, use_ai=False)

        # Should handle gracefully
        assert isinstance(recommendations, list)

        # Should print warning
    def test_empty_recommended_plugins(self, plugin_analyzer, mock_templates_dir):
        """Test project type with no recommended plugins."""
        # Create project type with no plugins
        empty_config = {
            'name': 'empty-type',
            'recommended_plugins': []
        }
        (mock_templates_dir / 'project-types' / 'empty-type.yaml').write_text(
            yaml.dump(empty_config)
        )

        config = ProjectConfig(
            project_name="Empty",
            project_slug="empty",
            description="Empty project with no plugins",
            project_type="empty-type",
            features=[]
        )

        recommendations = plugin_analyzer.recommend_plugins(config, use_ai=False)

        # Should return empty list
        assert recommendations == []

    def test_concurrent_recommendations(self, plugin_analyzer, sample_saas_config):
        """Test that analyzer can handle multiple recommendation calls."""
        # Call multiple times
        results = []
        for i in range(3):
            recs = plugin_analyzer.recommend_plugins(sample_saas_config, use_ai=False)
            results.append(recs)

        # All should return same results
        assert len(results[0]) == len(results[1])
        assert len(results[1]) == len(results[2])
