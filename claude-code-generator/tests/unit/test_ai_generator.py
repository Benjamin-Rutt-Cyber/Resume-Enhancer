"""
Unit tests for AI Agent Generator.

Tests cover:
- Domain uniqueness scoring
- Library match calculation
- Decision logic (when to use AI vs library)
- Token budget management
- AI generation with mocked API
- Cache integration
- Error handling and fallbacks
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.generator.ai_generator import (
    AIGenerationConfig,
    AIAgentGenerator,
    HIGH_UNIQUENESS_KEYWORDS,
    LOW_UNIQUENESS_KEYWORDS,
    UNIQUENESS_THRESHOLD_LOW,
    DEFAULT_TOKEN_BUDGET,
)


class TestAIGenerationConfig:
    """Test AIGenerationConfig initialization."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AIGenerationConfig()

        assert config.enabled is False
        assert config.threshold == UNIQUENESS_THRESHOLD_LOW
        assert config.token_budget == DEFAULT_TOKEN_BUDGET
        assert config.use_cache is True
        assert config.show_stats is False
        assert config.tokens_used == 0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = AIGenerationConfig(
            enabled=True,
            threshold=50,
            token_budget=10000,
            use_cache=False,
            show_stats=True,
            api_key="test-key"
        )

        assert config.enabled is True
        assert config.threshold == 50
        assert config.token_budget == 10000
        assert config.use_cache is False
        assert config.show_stats is True
        assert config.api_key == "test-key"

    def test_api_key_from_env(self, monkeypatch):
        """Test API key read from environment."""
        monkeypatch.setenv('ANTHROPIC_API_KEY', 'env-key')
        config = AIGenerationConfig(enabled=True)

        assert config.api_key == 'env-key'


class TestDomainUniquenessScoring:
    """Test domain uniqueness calculation."""

    def test_generic_crud_app_low_score(self):
        """Test that generic CRUD apps get low uniqueness scores."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'description': 'A simple CRUD REST API for managing todo items',
            'project_type': 'api-service',
            'backend_framework': 'python-fastapi',
            'database': 'postgresql',
        }

        score = generator._calculate_domain_uniqueness(project_context)

        # Should be low due to 'crud', 'rest-api', 'todo' keywords
        assert score < 40

    def test_healthcare_app_high_score(self):
        """Test that healthcare apps get high uniqueness scores."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'description': 'A medical records system with HIPAA compliance and clinical workflows',
            'project_type': 'saas-web-app',
            'backend_framework': 'python-fastapi',
            'database': 'postgresql',
        }

        score = generator._calculate_domain_uniqueness(project_context)

        # Should be high due to 'medical', 'hipaa', 'clinical' keywords
        assert score >= 70

    def test_fintech_app_high_score(self):
        """Test that fintech apps get high uniqueness scores."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'description': 'Cryptocurrency trading platform with PCI-DSS compliance',
            'project_type': 'saas-web-app',
            'backend_framework': 'python-fastapi',
            'database': 'postgresql',
        }

        score = generator._calculate_domain_uniqueness(project_context)

        # Should be high due to 'cryptocurrency', 'trading', 'pci-dss'
        assert score >= 70

    def test_iot_embedded_bonus(self):
        """Test that IoT + embedded combinations get bonus points."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'description': 'IoT sensor network with edge computing and real-time data processing',
            'project_type': 'hardware-iot',
            'backend_framework': 'micropython',
            'platform': 'esp32',
        }

        score = generator._calculate_domain_uniqueness(project_context)

        # Should get bonus for IoT + embedded combo
        assert score >= 60

    def test_multiple_specialized_domains_combo_bonus(self):
        """Test that multiple specialized domains get combo bonus."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'description': 'Aerospace defense system for satellite monitoring with regulatory compliance',
            'project_type': 'saas-web-app',
        }

        score = generator._calculate_domain_uniqueness(project_context)

        # Should get combo bonus for aerospace + defense + satellite + regulatory
        assert score >= 100  # Will be clamped to 100


class TestLibraryMatchCalculation:
    """Test library match scoring."""

    def test_exact_name_match_high_score(self):
        """Test that exact agent name match gives high score."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        library_templates = [
            {'name': 'api-development-agent', 'selection_conditions': {'project_types': ['api-service']}}
        ]

        score = generator._calculate_library_match(
            'api-development-agent',
            {'project_type': 'api-service'},
            library_templates
        )

        assert score >= 90

    def test_project_type_match_medium_score(self):
        """Test that project type match gives medium score."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        library_templates = [
            {'name': 'testing-agent', 'selection_conditions': {'project_types': ['api-service', 'saas-web-app']}}
        ]

        score = generator._calculate_library_match(
            'different-agent',
            {'project_type': 'api-service'},
            library_templates
        )

        assert 60 <= score <= 80

    def test_no_match_zero_score(self):
        """Test that no match gives zero score."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        library_templates = [
            {'name': 'other-agent', 'selection_conditions': {'project_types': ['mobile-app']}}
        ]

        score = generator._calculate_library_match(
            'api-development-agent',
            {'project_type': 'api-service'},
            library_templates
        )

        assert score == 0


class TestDecisionLogic:
    """Test decision logic for when to use AI vs library."""

    def test_ai_disabled_use_library(self):
        """Test that AI disabled always uses library."""
        config = AIGenerationConfig(enabled=False)
        generator = AIAgentGenerator(config)

        should_generate, reason, score = generator.should_generate_custom_agent(
            'test-agent',
            {'description': 'healthcare system with HIPAA', 'project_type': 'saas-web-app'},
            50.0
        )

        assert should_generate is False
        assert "not enabled" in reason

    def test_no_api_key_use_library(self):
        """Test that missing API key uses library."""
        config = AIGenerationConfig(enabled=True, api_key=None)
        generator = AIAgentGenerator(config)

        should_generate, reason, score = generator.should_generate_custom_agent(
            'test-agent',
            {'description': 'healthcare system', 'project_type': 'saas-web-app'},
            50.0
        )

        assert should_generate is False
        assert "No API key" in reason

    def test_token_budget_exhausted_use_library(self):
        """Test that exhausted token budget uses library."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", token_budget=100)
        config.tokens_used = 100  # Exhausted
        generator = AIAgentGenerator(config)

        should_generate, reason, score = generator.should_generate_custom_agent(
            'test-agent',
            {'description': 'healthcare system', 'project_type': 'saas-web-app'},
            50.0
        )

        assert should_generate is False
        assert "budget exhausted" in reason

    def test_low_uniqueness_use_library(self):
        """Test that low uniqueness score uses library."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", threshold=50)
        generator = AIAgentGenerator(config)

        should_generate, reason, score = generator.should_generate_custom_agent(
            'test-agent',
            {'description': 'simple CRUD app', 'project_type': 'api-service'},
            50.0
        )

        assert should_generate is False
        assert "too generic" in reason or "score:" in reason

    def test_excellent_library_match_use_library(self):
        """Test that excellent library match (>90) uses library even if unique."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", threshold=30)
        generator = AIAgentGenerator(config)

        should_generate, reason, score = generator.should_generate_custom_agent(
            'test-agent',
            {'description': 'healthcare system with HIPAA', 'project_type': 'saas-web-app'},
            95.0  # Excellent library match
        )

        assert should_generate is False
        assert "Library match excellent" in reason

    def test_high_uniqueness_generate_ai(self):
        """Test that high uniqueness with no perfect library match generates AI."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", threshold=50)
        # Mock client
        with patch('src.generator.ai_generator.Anthropic'):
            generator = AIAgentGenerator(config)

            should_generate, reason, score = generator.should_generate_custom_agent(
                'test-agent',
                {'description': 'aerospace defense satellite system', 'project_type': 'saas-web-app'},
                60.0  # Good but not perfect library match
            )

            assert should_generate is True
            assert "Novel domain" in reason or "warrants custom" in reason


class TestAIGeneration:
    """Test AI generation with mocked API calls."""

    @patch('src.generator.ai_generator.Anthropic')
    def test_generate_agent_success(self, mock_anthropic_class):
        """Test successful agent generation."""
        # Setup mock
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="# Test Agent\n\nThis is a test agent.")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=500)
        mock_client.messages.create.return_value = mock_response

        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'project_name': 'Test Project',
            'project_type': 'saas-web-app',
            'description': 'Test description',
            'backend_framework': 'python-fastapi',
            'frontend_framework': 'react-typescript',
            'database': 'postgresql',
            'features': ['auth', 'api']
        }

        content, metadata = generator.generate_agent(
            'testing',
            'Testing guidance',
            project_context
        )

        # Verify API was called
        assert mock_client.messages.create.called

        # Verify content has frontmatter
        assert 'generation:' in content
        assert 'type: ai-generated' in content

        # Verify metadata
        assert metadata['type'] == 'ai-generated'
        assert metadata['tokens_used'] == 600  # 100 + 500

        # Verify token tracking
        assert generator.config.tokens_used == 600

    @patch('src.generator.ai_generator.Anthropic')
    def test_generate_skill_success(self, mock_anthropic_class):
        """Test successful skill generation."""
        # Setup mock
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="# Test Skill\n\nThis is a test skill.")]
        mock_response.usage = Mock(input_tokens=80, output_tokens=400)
        mock_client.messages.create.return_value = mock_response

        config = AIGenerationConfig(enabled=True, api_key="test-key")
        generator = AIAgentGenerator(config)

        project_context = {
            'project_name': 'Test Project',
            'project_type': 'api-service',
            'description': 'Test description',
        }

        content, metadata = generator.generate_skill(
            'custom-skill',
            'Custom skill guidance',
            project_context
        )

        # Verify content
        assert 'generation:' in content
        assert metadata['tokens_used'] == 480

    @patch('src.generator.ai_generator.Anthropic')
    def test_generate_agent_no_api_key_raises_error(self, mock_anthropic_class):
        """Test that generation without API key raises error."""
        config = AIGenerationConfig(enabled=True, api_key=None)
        generator = AIAgentGenerator(config)

        with pytest.raises(ValueError, match="No API key available"):
            generator.generate_agent('test', 'test purpose', {})


class TestTokenBudgetManagement:
    """Test token budget tracking."""

    @patch('src.generator.ai_generator.Anthropic')
    def test_token_usage_tracked(self, mock_anthropic_class):
        """Test that token usage is tracked across multiple generations."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="# Agent")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=400)
        mock_client.messages.create.return_value = mock_response

        config = AIGenerationConfig(enabled=True, api_key="test-key", token_budget=1000)
        generator = AIAgentGenerator(config)

        # Generate first agent
        generator.generate_agent('agent1', 'purpose', {'project_name': 'Test', 'project_type': 'api', 'description': 'test'})
        assert generator.config.tokens_used == 500

        # Generate second agent
        generator.generate_agent('agent2', 'purpose', {'project_name': 'Test', 'project_type': 'api', 'description': 'test'})
        assert generator.config.tokens_used == 1000

    def test_get_generation_stats(self):
        """Test getting generation statistics."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", token_budget=5000)
        config.tokens_used = 1200

        with patch('src.generator.ai_generator.Anthropic'):
            generator = AIAgentGenerator(config)

            stats = generator.get_generation_stats()

            assert stats['enabled'] is True
            assert stats['tokens_used'] == 1200
            assert stats['token_budget'] == 5000
            assert stats['tokens_remaining'] == 3800
            assert stats['percentage_used'] == 24.0
            assert stats['api_key_available'] is True


class TestCacheIntegration:
    """Test integration with cache manager."""

    def test_generator_with_cache_manager(self):
        """Test that generator properly integrates with cache manager."""
        config = AIGenerationConfig(enabled=True, api_key="test-key", use_cache=True)
        mock_cache = Mock()

        with patch('src.generator.ai_generator.Anthropic'):
            generator = AIAgentGenerator(config, cache_manager=mock_cache)

            assert generator.cache_manager is mock_cache


class TestPromptConstruction:
    """Test prompt building for agent/skill generation."""

    def test_agent_prompt_includes_context(self):
        """Test that agent generation prompt includes project context."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        with patch('src.generator.ai_generator.Anthropic'):
            generator = AIAgentGenerator(config)

            project_context = {
                'project_name': 'Healthcare App',
                'project_type': 'saas-web-app',
                'description': 'HIPAA compliant medical records',
                'backend_framework': 'python-fastapi',
                'frontend_framework': 'react-typescript',
                'database': 'postgresql',
                'features': ['auth', 'encryption']
            }

            prompt = generator._build_agent_generation_prompt(
                'api-development',
                'API development for healthcare',
                project_context
            )

            # Verify key elements in prompt
            assert 'Healthcare App' in prompt
            assert 'saas-web-app' in prompt
            assert 'HIPAA compliant' in prompt
            assert 'python-fastapi' in prompt
            assert 'react-typescript' in prompt
            assert 'postgresql' in prompt

    def test_skill_prompt_includes_purpose(self):
        """Test that skill generation prompt includes purpose."""
        config = AIGenerationConfig(enabled=True, api_key="test-key")
        with patch('src.generator.ai_generator.Anthropic'):
            generator = AIAgentGenerator(config)

            project_context = {
                'project_name': 'Fintech Platform',
                'project_type': 'saas-web-app',
                'description': 'Trading platform'
            }

            prompt = generator._build_skill_generation_prompt(
                'compliance-check',
                'Financial compliance verification',
                project_context
            )

            assert 'compliance-check' in prompt
            assert 'Fintech Platform' in prompt
            assert 'Trading platform' in prompt
