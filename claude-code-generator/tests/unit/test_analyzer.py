"""
Tests for ProjectAnalyzer - AI-powered project description analysis.

Tests cover:
- ProjectConfig validation and slug generation
- ProjectAnalyzer initialization with/without API
- Claude API analysis (mocked)
- Keyword-based fallback analysis
- Project type detection (5 types)
- Feature extraction
- Helper methods
- Edge cases
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from src.generator.analyzer import ProjectAnalyzer, ProjectConfig


# ============================================================================
# ProjectConfig Tests
# ============================================================================


class TestProjectConfig:
    """Test ProjectConfig validation and field generation."""

    def test_valid_config_with_all_fields(self):
        """Test creating a valid config with all fields."""
        config = ProjectConfig(
            project_name="My SaaS App",
            project_slug="my-saas-app",
            project_type="saas-web-app",
            description="A comprehensive SaaS application with authentication",
            backend_framework="python-fastapi",
            frontend_framework="react-typescript",
            database="postgresql",
            deployment_platform="docker",
            features=["authentication", "payments"],
            has_auth=True,
            has_api=True,
            has_payments=True,
        )

        assert config.project_name == "My SaaS App"
        assert config.project_slug == "my-saas-app"
        assert config.project_type == "saas-web-app"
        assert config.has_auth is True

    def test_slug_auto_generation_from_name(self):
        """Test automatic slug generation from project name."""
        config = ProjectConfig(
            project_name="My Cool Project",
            project_slug=None,  # Should be auto-generated
            project_type="saas-web-app",
            description="A cool project for testing slug generation",
        )

        assert config.project_slug == "my-cool-project"

    def test_slug_generation_with_special_characters(self):
        """Test slug generation handles special characters."""
        config = ProjectConfig(
            project_name="My Project! @#$ Test",
            project_slug=None,
            project_type="api-service",
            description="Testing special character handling in slugs",
        )

        # Special chars are removed, which can leave consecutive hyphens
        assert config.project_slug == "my-project--test"

    def test_slug_generation_with_underscores(self):
        """Test slug generation converts underscores to hyphens."""
        config = ProjectConfig(
            project_name="My_Cool_Project",
            project_slug=None,
            project_type="mobile-app",
            description="Testing underscore to hyphen conversion",
        )

        assert config.project_slug == "my-cool-project"

    def test_slug_generation_multiple_spaces(self):
        """Test slug generation handles multiple consecutive spaces."""
        config = ProjectConfig(
            project_name="My    Project   Name",
            project_slug=None,
            project_type="saas-web-app",
            description="Testing multiple space handling in names",
        )

        assert config.project_slug == "my-project-name"

    def test_project_name_min_length_validation(self):
        """Test project name must be at least 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                project_name="AB",  # Too short
                project_slug="ab",
                project_type="saas-web-app",
                description="Testing minimum name length validation",
            )

        assert "at least 3 characters" in str(exc_info.value)

    def test_project_name_max_length_validation(self):
        """Test project name must be at most 100 characters."""
        long_name = "A" * 101  # Too long

        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                project_name=long_name,
                project_slug="test",
                project_type="saas-web-app",
                description="Testing maximum name length validation",
            )

        assert "at most 100 characters" in str(exc_info.value)

    def test_description_min_length_validation(self):
        """Test description must be at least 10 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                project_name="Test Project",
                project_slug="test-project",
                project_type="saas-web-app",
                description="Short",  # Too short
            )

        assert "at least 10 characters" in str(exc_info.value)

    def test_project_slug_pattern_validation(self):
        """Test project slug must match lowercase-hyphen pattern."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                project_name="Test Project",
                project_slug="Invalid_Slug!",  # Invalid characters
                project_type="saas-web-app",
                description="Testing slug pattern validation",
            )

        assert "String should match pattern" in str(exc_info.value)

    def test_project_type_pattern_validation(self):
        """Test project type must match lowercase-hyphen pattern."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                project_name="Test Project",
                project_slug="test-project",
                project_type="InvalidType",  # Invalid format
                description="Testing type pattern validation",
            )

        assert "String should match pattern" in str(exc_info.value)

    def test_optional_fields_default_to_none(self):
        """Test optional fields default to None."""
        config = ProjectConfig(
            project_name="Minimal Project",
            project_slug="minimal",
            project_type="api-service",
            description="Testing minimal config with defaults",
        )

        assert config.backend_framework is None
        assert config.frontend_framework is None
        assert config.database is None
        assert config.deployment_platform is None
        assert config.connectivity is None
        assert config.firmware_language is None

    def test_features_default_to_empty_list(self):
        """Test features field defaults to empty list."""
        config = ProjectConfig(
            project_name="Test Project",
            project_slug="test",
            project_type="saas-web-app",
            description="Testing default features list",
        )

        assert config.features == []

    def test_boolean_fields_default_values(self):
        """Test boolean fields have correct defaults."""
        config = ProjectConfig(
            project_name="Test Project",
            project_slug="test",
            project_type="api-service",
            description="Testing boolean field defaults",
        )

        assert config.has_auth is False
        assert config.has_api is True  # Default is True
        assert config.has_websockets is False
        assert config.has_payments is False

    def test_year_default_value(self):
        """Test year field defaults to 2025."""
        config = ProjectConfig(
            project_name="Test Project",
            project_slug="test",
            project_type="saas-web-app",
            description="Testing year default value",
        )

        assert config.year == 2025

    def test_author_default_value(self):
        """Test author field defaults to 'Developer'."""
        config = ProjectConfig(
            project_name="Test Project",
            project_slug="test",
            project_type="saas-web-app",
            description="Testing author default value",
        )

        assert config.author == "Developer"


# ============================================================================
# ProjectAnalyzer Initialization Tests
# ============================================================================


class TestProjectAnalyzerInitialization:
    """Test ProjectAnalyzer initialization."""

    def test_init_with_api_key(self):
        """Test initializing analyzer with API key."""
        analyzer = ProjectAnalyzer(api_key="test-api-key")

        assert analyzer.api_key == "test-api-key"
        assert analyzer.client is not None

    def test_init_without_api_key(self):
        """Test initializing analyzer without API key."""
        with patch.dict(os.environ, {}, clear=True):
            analyzer = ProjectAnalyzer()

            assert analyzer.api_key is None
            assert analyzer.client is None

    def test_init_with_env_var(self):
        """Test initializing analyzer using ANTHROPIC_API_KEY env var."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-api-key"}):
            analyzer = ProjectAnalyzer()

            assert analyzer.api_key == "env-api-key"
            assert analyzer.client is not None

    def test_api_key_parameter_overrides_env(self):
        """Test that explicit API key parameter overrides env var."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            analyzer = ProjectAnalyzer(api_key="param-key")

            assert analyzer.api_key == "param-key"


# ============================================================================
# Analyze Method Tests
# ============================================================================


class TestAnalyzeMethod:
    """Test main analyze() method."""

    def test_analyze_validates_description_length(self):
        """Test analyze() raises error for too-short descriptions."""
        analyzer = ProjectAnalyzer(api_key=None)

        with pytest.raises(ValueError, match="at least 10 characters"):
            analyzer.analyze("Short")

    def test_analyze_validates_empty_description(self):
        """Test analyze() raises error for empty descriptions."""
        analyzer = ProjectAnalyzer(api_key=None)

        with pytest.raises(ValueError, match="at least 10 characters"):
            analyzer.analyze("")

    def test_analyze_validates_whitespace_description(self):
        """Test analyze() raises error for whitespace-only descriptions."""
        analyzer = ProjectAnalyzer(api_key=None)

        with pytest.raises(ValueError, match="at least 10 characters"):
            analyzer.analyze("   ")

    def test_analyze_with_claude_api(self):
        """Test analyze() uses Claude API when available."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        # Mock the Claude API call
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text=json.dumps(
                    {
                        "project_name": "Test SaaS",
                        "project_slug": None,  # Will be auto-generated
                        "project_type": "saas-web-app",
                        "description": "A comprehensive SaaS application",
                        "backend_framework": "python-fastapi",
                        "frontend_framework": "react-typescript",
                        "database": "postgresql",
                        "deployment_platform": "docker",
                        "features": ["authentication"],
                        "has_auth": True,
                        "has_api": True,
                        "has_websockets": False,
                        "has_payments": False,
                    }
                )
            )
        ]

        with patch.object(
            analyzer.client.messages, "create", return_value=mock_response
        ):
            config = analyzer.analyze("A comprehensive SaaS application")

            assert config.project_name == "Test SaaS"
            assert config.project_type == "saas-web-app"
            assert config.backend_framework == "python-fastapi"

    def test_analyze_without_claude_api_uses_keywords(self):
        """Test analyze() falls back to keywords without API."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "An IoT temperature monitoring system using Raspberry Pi Pico W",
            project_name="TempMonitor",
        )

        assert config.project_name == "TempMonitor"
        assert config.project_type == "hardware-iot"
        assert config.platform == "pico-w"

    def test_analyze_returns_project_config(self):
        """Test analyze() returns a ProjectConfig instance."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A REST API service for managing tasks", project_name="TaskAPI"
        )

        assert isinstance(config, ProjectConfig)
        assert config.project_name == "TaskAPI"


# ============================================================================
# Claude API Analysis Tests
# ============================================================================


class TestClaudeAPIAnalysis:
    """Test _analyze_with_claude() method."""

    def test_claude_analysis_calls_api_correctly(self):
        """Test Claude API is called with correct parameters."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        mock_response = Mock()
        mock_response.content = [
            Mock(
                text=json.dumps(
                    {
                        "project_name": "API Service",
                        "project_slug": None,  # Will be auto-generated
                        "project_type": "api-service",
                        "description": "A RESTful API service",
                        "backend_framework": "python-fastapi",
                        "has_api": True,
                    }
                )
            )
        ]

        with patch.object(
            analyzer.client.messages, "create", return_value=mock_response
        ) as mock_create:
            analyzer.analyze("A RESTful API service")

            # Verify API was called
            mock_create.assert_called_once()
            call_args = mock_create.call_args

            # Check model
            assert call_args.kwargs["model"] == "claude-sonnet-4-5-20250929"
            # Check max_tokens
            assert call_args.kwargs["max_tokens"] == 2000
            # Check messages structure
            assert len(call_args.kwargs["messages"]) == 1
            assert call_args.kwargs["messages"][0]["role"] == "user"

    def test_claude_analysis_extracts_json_from_response(self):
        """Test JSON extraction from Claude's response."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        # Response with JSON embedded in text
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text='Here is the analysis:\n{"project_name": "Test", "project_slug": null, "project_type": "saas-web-app", "description": "Test project description"}'
            )
        ]

        with patch.object(
            analyzer.client.messages, "create", return_value=mock_response
        ):
            config = analyzer.analyze("Test project description")

            assert config.project_name == "Test"

    def test_claude_analysis_handles_malformed_json(self):
        """Test error handling for malformed JSON responses."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        mock_response = Mock()
        mock_response.content = [Mock(text="No JSON here!")]

        with patch.object(
            analyzer.client.messages, "create", return_value=mock_response
        ):
            with pytest.raises(ValueError, match="Could not extract JSON"):
                analyzer.analyze("Test project")


# ============================================================================
# Keyword Analysis Tests
# ============================================================================


class TestKeywordAnalysis:
    """Test _analyze_with_keywords() fallback method."""

    def test_keyword_detects_hardware_iot_type(self):
        """Test keyword detection for hardware/IoT projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "An IoT sensor system using ESP32 and MQTT for data transmission"
        )

        assert config.project_type == "hardware-iot"
        assert config.connectivity == "mqtt"
        assert config.platform == "esp32"

    def test_keyword_detects_mobile_app_type(self):
        """Test keyword detection for mobile app projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A mobile application for iOS and Android using React Native"
        )

        assert config.project_type == "mobile-app"
        assert config.frontend_framework == "react-native"

    def test_keyword_detects_data_science_type(self):
        """Test keyword detection for data science projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A machine learning model for predicting customer churn"
        )

        assert config.project_type == "data-science"
        assert config.backend_framework == "python"

    def test_keyword_detects_api_service_type(self):
        """Test keyword detection for API service projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A REST API backend service for managing user data"
        )

        assert config.project_type == "api-service"
        assert config.backend_framework == "python-fastapi"
        assert config.frontend_framework is None

    def test_keyword_defaults_to_saas_web_app(self):
        """Test default project type is saas-web-app."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A web application for team collaboration")

        assert config.project_type == "saas-web-app"
        assert config.backend_framework == "python-fastapi"
        assert config.frontend_framework == "react-typescript"

    def test_keyword_extracts_authentication_feature(self):
        """Test keyword detection for authentication feature."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A web app with user authentication and login system"
        )

        assert "authentication" in config.features
        assert config.has_auth is True

    def test_keyword_extracts_payment_feature(self):
        """Test keyword detection for payment feature."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "An e-commerce platform with subscription payments"
        )

        assert "payments" in config.features
        assert config.has_payments is True

    def test_keyword_extracts_email_feature(self):
        """Test keyword detection for email feature."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A notification system with email alerts")

        assert "email" in config.features

    def test_keyword_extracts_websocket_feature(self):
        """Test keyword detection for real-time/websocket feature."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A real-time chat application with websockets")

        assert "websockets" in config.features
        assert config.has_websockets is True

    def test_keyword_extracts_multiple_features(self):
        """Test extraction of multiple features."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A SaaS platform with authentication, payment processing, and email notifications"
        )

        assert "authentication" in config.features
        assert "payments" in config.features
        assert "email" in config.features

    def test_keyword_uses_provided_project_name(self):
        """Test keyword analysis uses provided project name."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze(
            "A task management application", project_name="TaskMaster"
        )

        assert config.project_name == "TaskMaster"

    def test_keyword_generates_name_if_not_provided(self):
        """Test keyword analysis generates name from description."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("Build A Cool Project with features")

        # Should use first 3 words
        assert "Build A Cool" in config.project_name


# ============================================================================
# Helper Method Tests
# ============================================================================


class TestHelperMethods:
    """Test helper methods."""

    def test_detect_platform_pico(self):
        """Test platform detection for Raspberry Pi Pico."""
        analyzer = ProjectAnalyzer(api_key=None)

        platform = analyzer._detect_platform("using raspberry pi pico w")

        assert platform == "pico-w"

    def test_detect_platform_esp32(self):
        """Test platform detection for ESP32."""
        analyzer = ProjectAnalyzer(api_key=None)

        platform = analyzer._detect_platform("esp32 microcontroller")

        assert platform == "esp32"

    def test_detect_platform_arduino(self):
        """Test platform detection for Arduino."""
        analyzer = ProjectAnalyzer(api_key=None)

        platform = analyzer._detect_platform("arduino uno board")

        assert platform == "arduino"

    def test_detect_platform_raspberry_pi(self):
        """Test platform detection for Raspberry Pi (not Pico)."""
        analyzer = ProjectAnalyzer(api_key=None)

        platform = analyzer._detect_platform("raspberry pi 4 model b")

        assert platform == "raspberry-pi"

    def test_detect_platform_defaults_to_pico(self):
        """Test platform detection defaults to pico-w."""
        analyzer = ProjectAnalyzer(api_key=None)

        platform = analyzer._detect_platform("some unknown hardware")

        assert platform == "pico-w"

    def test_extract_name_from_description(self):
        """Test name extraction from description."""
        analyzer = ProjectAnalyzer(api_key=None)

        name = analyzer._extract_name("Build a task management system")

        assert name == "Build A Task"

    def test_extract_name_limits_length(self):
        """Test name extraction limits to 50 characters."""
        analyzer = ProjectAnalyzer(api_key=None)

        long_desc = "A" * 100

        name = analyzer._extract_name(long_desc)

        assert len(name) <= 50

    def test_build_analysis_prompt_with_name(self):
        """Test prompt building with project name."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        prompt = analyzer._build_analysis_prompt(
            "Test description", project_name="TestProject"
        )

        assert "Test description" in prompt
        assert "TestProject" in prompt
        assert "Project name: TestProject" in prompt

    def test_build_analysis_prompt_without_name(self):
        """Test prompt building without project name."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        prompt = analyzer._build_analysis_prompt("Test description")

        assert "Test description" in prompt
        assert "Project name:" not in prompt

    def test_extract_json_from_text(self):
        """Test JSON extraction from text."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        text = 'Here is the JSON: {"key": "value"}'

        json_str = analyzer._extract_json(text)

        assert json_str == '{"key": "value"}'

    def test_extract_json_multiline(self):
        """Test JSON extraction from multiline text."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        text = """Here is the analysis:
        {
            "project_name": "Test",
            "project_type": "saas-web-app"
        }
        Done!"""

        json_str = analyzer._extract_json(text)

        parsed = json.loads(json_str)
        assert parsed["project_name"] == "Test"

    def test_extract_json_raises_on_no_json(self):
        """Test JSON extraction raises error when no JSON found."""
        analyzer = ProjectAnalyzer(api_key="test-key")

        with pytest.raises(ValueError, match="Could not extract JSON"):
            analyzer._extract_json("No JSON in this text!")


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_unicode_in_project_name(self):
        """Test handling of Unicode characters in project name."""
        config = ProjectConfig(
            project_name="My Project 你好",
            project_slug=None,
            project_type="saas-web-app",
            description="Testing Unicode character handling",
        )

        # Unicode characters should be removed from slug
        assert "你好" not in config.project_slug

    def test_unicode_in_description(self):
        """Test handling of Unicode in description."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A project with Unicode: 你好世界")

        assert config.description == "A project with Unicode: 你好世界"

    def test_very_long_description(self):
        """Test handling of very long descriptions."""
        analyzer = ProjectAnalyzer(api_key=None)

        long_description = "A " * 1000 + "project"

        config = analyzer.analyze(long_description)

        assert config.description == long_description

    def test_case_insensitive_keyword_detection(self):
        """Test keyword detection is case-insensitive."""
        analyzer = ProjectAnalyzer(api_key=None)

        config1 = analyzer.analyze("An IOT sensor system")
        config2 = analyzer.analyze("An iot sensor system")
        config3 = analyzer.analyze("An IoT sensor system")

        assert config1.project_type == "hardware-iot"
        assert config2.project_type == "hardware-iot"
        assert config3.project_type == "hardware-iot"

    def test_multiple_project_type_keywords(self):
        """Test detection when multiple type keywords present."""
        analyzer = ProjectAnalyzer(api_key=None)

        # "IoT" takes precedence as it's checked first
        config = analyzer.analyze("An IoT mobile app for sensor monitoring")

        assert config.project_type == "hardware-iot"

    def test_deployment_platform_always_docker(self):
        """Test deployment platform defaults to docker in keyword mode."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A web application for users")

        assert config.deployment_platform == "docker"

    def test_has_api_always_true_in_keyword_mode(self):
        """Test has_api is always True in keyword mode."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A simple web app without API")

        assert config.has_api is True

    def test_micropython_detection(self):
        """Test MicroPython firmware language detection."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("An IoT device using MicroPython")

        assert config.project_type == "hardware-iot"
        assert config.firmware_language == "micropython"

    def test_circuitpython_default_for_iot(self):
        """Test CircuitPython is default for IoT without MicroPython."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("An IoT sensor system")

        assert config.project_type == "hardware-iot"
        assert config.firmware_language == "circuitpython"

    def test_http_connectivity_default_for_iot(self):
        """Test HTTP connectivity is default for IoT without MQTT."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("An IoT temperature monitor")

        assert config.project_type == "hardware-iot"
        assert config.connectivity == "http"

    def test_state_management_redux_for_frontend(self):
        """Test state management defaults to redux for frontend projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A web application with user interface")

        assert config.frontend_framework == "react-typescript"
        assert config.state_management == "redux"

    def test_no_state_management_for_backend_only(self):
        """Test no state management for backend-only projects."""
        analyzer = ProjectAnalyzer(api_key=None)

        config = analyzer.analyze("A REST API service")

        assert config.frontend_framework is None
        assert config.state_management is None
