"""
Tests for CLI - Command Line Interface.

Tests cover:
- CLI group (version, help)
- init command (project generation)
- list-types command
- validate command
- Helper display functions
- Error handling
- Interactive prompts
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock, mock_open
import yaml

from src.cli.main import (
    cli,
    _display_config,
    _display_results,
    _display_plugin_recommendations,
    _display_next_steps,
)
from src.generator.analyzer import ProjectConfig


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_config():
    """Provide a sample ProjectConfig for testing."""
    return ProjectConfig(
        project_name="Test Project",
        project_slug="test-project",
        project_type="saas-web-app",
        description="A test project for CLI testing",
        backend_framework="python-fastapi",
        frontend_framework="react-typescript",
        database="postgresql",
        features=["authentication", "payments"],
        has_auth=True,
        has_api=True,
    )


@pytest.fixture
def created_files():
    """Provide sample created files dictionary."""
    return {
        "agents": ["api-dev.md", "frontend.md", "testing.md"],
        "skills": ["python-fastapi", "react-typescript"],
        "commands": ["setup-dev.md", "run-server.md"],
        "docs": ["README.md", "ARCHITECTURE.md"],
    }


# ============================================================================
# CLI Group Tests
# ============================================================================


class TestCLIGroup:
    """Test CLI group functionality."""

    def test_cli_help(self, runner):
        """Test CLI help message."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Claude Code Generator" in result.output
        assert "Create complete Claude Code environments" in result.output

    def test_cli_version(self, runner):
        """Test CLI version display."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_cli_no_command(self, runner):
        """Test CLI with no command shows usage."""
        result = runner.invoke(cli)

        # Click groups return exit code 2 when no command is provided
        assert result.exit_code == 2
        assert "Usage:" in result.output


# ============================================================================
# init Command Tests
# ============================================================================


class TestInitCommand:
    """Test init command for project generation."""

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_with_all_options(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command with all options specified."""
        # Setup mocks
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {
            "agents": ["test.md"],
            "skills": ["test-skill"],
        }
        mock_generator_class.return_value = mock_generator

        output_dir = tmp_path / "test-project"

        # Run command (non-interactive, no confirmation needed)
        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test Project",
                    "--description",
                    "A test project for testing the CLI",
                    "--type",
                    "saas-web-app",
                    "--output",
                    str(output_dir),
                    "--overwrite",
                    "--no-ai",
                    "--no-plugins",
                ],
            )

        assert result.exit_code == 0
        assert "Project analyzed successfully" in result.output
        assert "Project generated successfully" in result.output

        # Verify analyzer was called correctly
        mock_analyzer.analyze.assert_called_once()

        # Verify generator was called with correct params
        mock_generator.generate_project.assert_called_once()
        call_args = mock_generator.generate_project.call_args
        assert call_args.kwargs["recommend_plugins"] is False

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    @patch("src.cli.main._interactive_mode")
    def test_init_interactive_mode(
        self, mock_interactive, mock_analyzer_class, mock_generator_class, runner, sample_config
    ):
        """Test init command in interactive mode with prompts."""
        # Mock interactive mode to return test values
        mock_interactive.return_value = (
            "My Project",
            "A cool project description for testing",
            "saas-web-app",
            False,  # with_code
        )

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": ["test.md"]}
        mock_generator_class.return_value = mock_generator

        # Invoke with interactive flag
        result = runner.invoke(
            cli,
            ["init", "--interactive", "--no-ai", "--no-plugins"],
        )

        assert result.exit_code == 0
        # Verify interactive mode was called
        mock_interactive.assert_called_once()

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_init_with_api_key(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command with API key in environment."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": []}
        mock_generator_class.return_value = mock_generator

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for API key testing",
                    "--no-plugins",
                    "--output",
                    str(tmp_path / "test"),
                ],
            )

        assert result.exit_code == 0
        # Verify API key was passed to analyzer
        mock_analyzer_class.assert_called_with(api_key="test-key")

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_without_api_key_shows_warning(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command without API key shows warning."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": []}
        mock_generator_class.return_value = mock_generator

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for warning test",
                    "--no-plugins",
                    "--output",
                    str(tmp_path / "test"),
                ],
            )

        assert result.exit_code == 0
        assert "ANTHROPIC_API_KEY not found" in result.output
        assert "Using keyword-based detection" in result.output

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_project_type_override(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command with project type override."""
        # Analyzer detects saas-web-app, but we override to api-service
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": []}
        mock_generator_class.return_value = mock_generator

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for type override",
                    "--type",
                    "api-service",
                    "--no-ai",
                    "--no-plugins",
                    "--output",
                    str(tmp_path / "test"),
                ],
            )

        assert result.exit_code == 0
        # Verify project type was overridden
        assert sample_config.project_type == "api-service"

    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_user_cancels_generation(
        self, mock_analyzer_class, runner, sample_config
    ):
        """Test init command when user cancels at confirmation."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        # User declines confirmation
        with patch("click.confirm", return_value=False):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for cancellation test",
                    "--no-ai",
                ],
            )

        assert result.exit_code == 0
        assert "Generation cancelled" in result.output

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_file_exists_error(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command handles FileExistsError."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.side_effect = FileExistsError(
            "Project directory already exists"
        )
        mock_generator_class.return_value = mock_generator

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for error handling",
                    "--no-ai",
                    "--no-plugins",
                    "--output",
                    str(tmp_path / "test"),
                ],
            )

        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Use --overwrite" in result.output

    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_value_error(self, mock_analyzer_class, runner):
        """Test init command handles ValueError from analyzer."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = ValueError(
            "Description must be at least 10 characters"
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(
            cli,
            [
                "init",
                "--project",
                "Test",
                "--description",
                "Short",
                "--no-ai",
            ],
        )

        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "at least 10 characters" in result.output

    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_unexpected_error(self, mock_analyzer_class, runner):
        """Test init command handles unexpected errors."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = RuntimeError("Unexpected error occurred")
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(
            cli,
            [
                "init",
                "--project",
                "Test",
                "--description",
                "Test description for unexpected error",
                "--no-ai",
            ],
        )

        assert result.exit_code == 1
        assert "Unexpected error:" in result.output

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_default_output_directory(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config
    ):
        """Test init command uses project slug as default output directory."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": []}
        mock_generator_class.return_value = mock_generator

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test Project",
                    "--description",
                    "Test description for default output",
                    "--no-ai",
                    "--no-plugins",
                ],
            )

        assert result.exit_code == 0

        # Verify generator was called with slug-based path
        call_args = mock_generator.generate_project.call_args
        output_path = call_args.args[1]
        assert output_path.name == "test-project"

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_init_with_plugins_enabled(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test init command with plugin recommendations enabled."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {
            "agents": ["test.md"],
            "plugins": [".claude/plugins.yaml"],
        }
        mock_generator_class.return_value = mock_generator

        # Create mock plugins.yaml file
        output_dir = tmp_path / "test-project"
        output_dir.mkdir(parents=True)
        claude_dir = output_dir / ".claude"
        claude_dir.mkdir()
        plugins_file = claude_dir / "plugins.yaml"

        plugins_data = {
            "recommended_plugins": {
                "high_priority": [
                    {
                        "name": "black",
                        "reason": "Python code formatting",
                        "install_command": "/plugin install black",
                    }
                ],
                "medium_priority": [
                    {
                        "name": "prettier",
                        "reason": "JavaScript formatting",
                        "install_command": "/plugin install prettier",
                    }
                ],
            }
        }

        with open(plugins_file, "w") as f:
            yaml.dump(plugins_data, f)

        with patch("click.confirm", return_value=True):
            result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for plugins",
                    "--no-ai",
                    "--output",
                    str(output_dir),
                ],
            )

        assert result.exit_code == 0
        # Verify plugins section is displayed
        assert "PLUGINS" in result.output or "black" in result.output


# ============================================================================
# list-types Command Tests
# ============================================================================


class TestListTypesCommand:
    """Test list-types command."""

    @patch("src.cli.main.TemplateSelector")
    def test_list_types_default_templates_dir(self, mock_selector_class, runner):
        """Test list-types command with default templates directory."""
        mock_selector = Mock()
        mock_selector.list_available_project_types.return_value = [
            {
                "name": "saas-web-app",
                "display_name": "SaaS Web App",
                "description": "Full-stack web application",
            },
            {
                "name": "api-service",
                "display_name": "API Service",
                "description": "RESTful API backend",
            },
        ]
        mock_selector_class.return_value = mock_selector

        result = runner.invoke(cli, ["list-types"])

        assert result.exit_code == 0
        assert "Available Project Types" in result.output
        assert "saas-web-app" in result.output
        assert "api-service" in result.output
        assert "Full-stack web application" in result.output

    @patch("src.cli.main.TemplateSelector")
    def test_list_types_custom_templates_dir(
        self, mock_selector_class, runner, tmp_path
    ):
        """Test list-types command with custom templates directory."""
        mock_selector = Mock()
        mock_selector.list_available_project_types.return_value = [
            {
                "name": "custom-type",
                "display_name": "Custom Type",
                "description": "A custom project type",
            }
        ]
        mock_selector_class.return_value = mock_selector

        custom_templates = tmp_path / "custom-templates"
        custom_templates.mkdir()

        result = runner.invoke(
            cli, ["list-types", "--templates-dir", str(custom_templates)]
        )

        assert result.exit_code == 0
        assert "custom-type" in result.output

        # Verify selector was initialized with custom path
        mock_selector_class.assert_called_once()
        call_args = mock_selector_class.call_args
        assert call_args.args[0] == custom_templates


# ============================================================================
# validate Command Tests
# ============================================================================


class TestValidateCommand:
    """Test validate command."""

    def test_validate_valid_project(self, runner, tmp_path):
        """Test validate command on a valid project structure."""
        # Create valid project structure
        project_dir = tmp_path / "valid-project"
        project_dir.mkdir()
        (project_dir / ".claude").mkdir()
        (project_dir / ".claude" / "agents").mkdir()
        (project_dir / ".claude" / "skills").mkdir()
        (project_dir / ".claude" / "commands").mkdir()
        (project_dir / "README.md").write_text("# Test")
        (project_dir / "docs").mkdir()

        result = runner.invoke(cli, ["validate", str(project_dir)])

        assert result.exit_code == 0
        assert "PASS" in result.output
        assert "All checks passed" in result.output

    def test_validate_invalid_project_missing_claude(self, runner, tmp_path):
        """Test validate command on invalid project (missing .claude)."""
        # Create incomplete project
        project_dir = tmp_path / "invalid-project"
        project_dir.mkdir()

        result = runner.invoke(cli, ["validate", str(project_dir)])

        assert result.exit_code == 1
        assert "FAIL" in result.output
        assert "Some checks failed" in result.output

    def test_validate_partial_structure(self, runner, tmp_path):
        """Test validate command on partially complete project."""
        project_dir = tmp_path / "partial-project"
        project_dir.mkdir()
        (project_dir / ".claude").mkdir()
        (project_dir / ".claude" / "agents").mkdir()
        # Missing skills, commands, README, docs

        result = runner.invoke(cli, ["validate", str(project_dir)])

        assert result.exit_code == 1
        assert "FAIL" in result.output
        # Should have some passes and some fails
        assert "PASS" in result.output


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestHelperFunctions:
    """Test helper display functions."""

    def test_display_config_basic(self, sample_config):
        """Test _display_config with basic configuration."""
        # Should not raise any exceptions
        _display_config(sample_config)

    def test_display_config_minimal(self):
        """Test _display_config with minimal configuration."""
        config = ProjectConfig(
            project_name="Minimal",
            project_slug="minimal",
            project_type="api-service",
            description="Minimal project configuration for testing",
        )

        # Should not raise exceptions even with minimal fields
        _display_config(config)

    def test_display_config_with_all_fields(self, sample_config):
        """Test _display_config with all optional fields populated."""
        config = ProjectConfig(
            project_name="Full Config",
            project_slug="full-config",
            project_type="hardware-iot",
            description="Full configuration with all fields populated",
            backend_framework="micropython",
            frontend_framework=None,
            database=None,
            platform="pico-w",
            features=["sensors", "mqtt", "cloud"],
        )

        _display_config(config)

    def test_display_results(self, created_files, tmp_path):
        """Test _display_results displays file counts."""
        output_dir = tmp_path / "test-project"

        _display_results(output_dir, created_files)

    def test_display_results_empty(self, tmp_path):
        """Test _display_results with empty files dict."""
        output_dir = tmp_path / "empty-project"

        _display_results(output_dir, {})

    def test_display_plugin_recommendations_with_file(self, tmp_path):
        """Test _display_plugin_recommendations with existing plugins file."""
        output_dir = tmp_path / "project"
        output_dir.mkdir()
        claude_dir = output_dir / ".claude"
        claude_dir.mkdir()

        plugins_data = {
            "recommended_plugins": {
                "high_priority": [
                    {
                        "name": "black",
                        "reason": "Code formatting",
                        "install_command": "/plugin install black",
                    }
                ],
                "medium_priority": [
                    {
                        "name": "pytest-runner",
                        "reason": "Test runner",
                        "install_command": "/plugin install pytest-runner",
                    }
                ],
            }
        }

        plugins_file = claude_dir / "plugins.yaml"
        with open(plugins_file, "w") as f:
            yaml.dump(plugins_data, f)

        # Should not raise exceptions
        _display_plugin_recommendations(output_dir, no_ai=False)
        _display_plugin_recommendations(output_dir, no_ai=True)

    def test_display_plugin_recommendations_no_file(self, tmp_path):
        """Test _display_plugin_recommendations when file doesn't exist."""
        output_dir = tmp_path / "no-plugins"
        output_dir.mkdir()

        # Should not raise exceptions
        _display_plugin_recommendations(output_dir, no_ai=False)

    def test_display_plugin_recommendations_empty_plugins(self, tmp_path):
        """Test _display_plugin_recommendations with empty plugin lists."""
        output_dir = tmp_path / "empty-plugins"
        output_dir.mkdir()
        claude_dir = output_dir / ".claude"
        claude_dir.mkdir()

        plugins_data = {"recommended_plugins": {"high_priority": [], "medium_priority": []}}

        plugins_file = claude_dir / "plugins.yaml"
        with open(plugins_file, "w") as f:
            yaml.dump(plugins_data, f)

        _display_plugin_recommendations(output_dir, no_ai=False)

    def test_display_next_steps(self, tmp_path):
        """Test _display_next_steps displays instructions."""
        output_dir = tmp_path / "test-project"

        # Should not raise exceptions
        _display_next_steps(output_dir)


# ============================================================================
# Integration Tests
# ============================================================================


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    @patch("src.cli.main.FileGenerator")
    @patch("src.cli.main.ProjectAnalyzer")
    def test_full_workflow_no_ai_no_plugins(
        self, mock_analyzer_class, mock_generator_class, runner, sample_config, tmp_path
    ):
        """Test complete workflow: init + validate."""
        # Setup mocks
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = sample_config
        mock_analyzer_class.return_value = mock_analyzer

        mock_generator = Mock()
        mock_generator.generate_project.return_value = {"agents": ["test.md"]}
        mock_generator_class.return_value = mock_generator

        output_dir = tmp_path / "test-project"

        # Step 1: Init project
        with patch("click.confirm", return_value=True):
            init_result = runner.invoke(
                cli,
                [
                    "init",
                    "--project",
                    "Test",
                    "--description",
                    "Test description for integration test",
                    "--no-ai",
                    "--no-plugins",
                    "--output",
                    str(output_dir),
                ],
            )

        assert init_result.exit_code == 0

        # Step 2: Create minimal structure for validation
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / ".claude").mkdir()
        (output_dir / ".claude" / "agents").mkdir()
        (output_dir / ".claude" / "skills").mkdir()
        (output_dir / ".claude" / "commands").mkdir()
        (output_dir / "README.md").write_text("# Test")
        (output_dir / "docs").mkdir()

        # Step 3: Validate project
        validate_result = runner.invoke(cli, ["validate", str(output_dir)])

        assert validate_result.exit_code == 0
        assert "All checks passed" in validate_result.output
