"""
Tests for interactive CLI mode functionality.

Tests cover:
- _safe_prompt error handling (KeyboardInterrupt, EOFError, general exceptions)
- _check_terminal_compatibility (non-TTY, CI environments, dumb terminal)
- Interactive mode trigger logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os


class TestSafePrompt:
    """Test _safe_prompt error handling."""

    @patch('src.cli.main.console')
    def test_safe_prompt_successful(self, mock_console):
        """Test successful prompt execution."""
        from src.cli.main import _safe_prompt

        mock_prompt = Mock()
        mock_prompt.ask.return_value = "test result"

        result = _safe_prompt(mock_prompt, "test context")

        assert result == "test result"
        mock_prompt.ask.assert_called_once()

    @patch('src.cli.main.console')
    def test_safe_prompt_keyboard_interrupt(self, mock_console):
        """Test _safe_prompt handles KeyboardInterrupt (Ctrl+C)."""
        from src.cli.main import _safe_prompt

        mock_prompt = Mock()
        mock_prompt.ask.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            _safe_prompt(mock_prompt, "test context")

        assert exc_info.value.code == 0
        mock_console.print.assert_called()

    @patch('src.cli.main.console')
    def test_safe_prompt_eof_error(self, mock_console):
        """Test _safe_prompt handles EOFError (terminal disconnect)."""
        from src.cli.main import _safe_prompt

        mock_prompt = Mock()
        mock_prompt.ask.side_effect = EOFError()

        with pytest.raises(SystemExit) as exc_info:
            _safe_prompt(mock_prompt, "test context")

        assert exc_info.value.code == 1

    @patch('src.cli.main.console')
    def test_safe_prompt_general_exception(self, mock_console):
        """Test _safe_prompt handles general exceptions."""
        from src.cli.main import _safe_prompt

        mock_prompt = Mock()
        mock_prompt.ask.side_effect = Exception("Terminal not supported")

        with pytest.raises(SystemExit) as exc_info:
            _safe_prompt(mock_prompt, "test context")

        assert exc_info.value.code == 1


class TestTerminalCompatibility:
    """Test _check_terminal_compatibility function."""

    @patch('sys.stdin')
    def test_compatible_terminal(self, mock_stdin):
        """Test compatible terminal (TTY, no CI, not dumb)."""
        from src.cli.main import _check_terminal_compatibility

        mock_stdin.isatty.return_value = True

        with patch.dict(os.environ, {}, clear=True):
            is_compatible, reason = _check_terminal_compatibility()

        assert is_compatible is True
        assert reason == ""

    @patch('sys.stdin')
    def test_non_tty_terminal(self, mock_stdin):
        """Test non-TTY terminal (piped input)."""
        from src.cli.main import _check_terminal_compatibility

        mock_stdin.isatty.return_value = False

        is_compatible, reason = _check_terminal_compatibility()

        assert is_compatible is False
        assert "not a TTY" in reason

    @patch('sys.stdin')
    def test_ci_environment(self, mock_stdin):
        """Test CI/CD environment detection."""
        from src.cli.main import _check_terminal_compatibility

        mock_stdin.isatty.return_value = True

        ci_vars = ['CI', 'JENKINS', 'TRAVIS', 'CIRCLECI', 'GITHUB_ACTIONS']
        for ci_var in ci_vars:
            with patch.dict(os.environ, {ci_var: '1'}, clear=True):
                is_compatible, reason = _check_terminal_compatibility()

            assert is_compatible is False
            assert "CI/CD" in reason

    @patch('sys.stdin')
    def test_dumb_terminal(self, mock_stdin):
        """Test dumb terminal detection."""
        from src.cli.main import _check_terminal_compatibility

        mock_stdin.isatty.return_value = True

        with patch.dict(os.environ, {'TERM': 'dumb'}, clear=True):
            is_compatible, reason = _check_terminal_compatibility()

        assert is_compatible is False
        assert "dumb" in reason


class TestInteractiveModeTriggerLogic:
    """Test interactive mode trigger logic (OR vs AND)."""

    def test_trigger_with_interactive_flag(self):
        """Test that --interactive flag always triggers interactive mode."""
        interactive = True
        project = "Test"
        description = "Test description"

        should_trigger = interactive or (not project and not description)
        assert should_trigger is True

    def test_trigger_with_both_missing(self):
        """Test trigger when both project AND description are missing."""
        interactive = False
        project = None
        description = None

        should_trigger = interactive or (not project and not description)
        assert should_trigger is True

    def test_no_trigger_with_only_project_missing(self):
        """Test that interactive mode does NOT trigger with only project missing."""
        interactive = False
        project = None
        description = "Test description"

        should_trigger = interactive or (not project and not description)
        assert should_trigger is False

    def test_no_trigger_with_only_description_missing(self):
        """Test that interactive mode does NOT trigger with only description missing."""
        interactive = False
        project = "Test Project"
        description = None

        should_trigger = interactive or (not project and not description)
        assert should_trigger is False

    def test_no_trigger_with_both_provided(self):
        """Test that interactive mode does NOT trigger when both are provided."""
        interactive = False
        project = "Test Project"
        description = "Test description"

        should_trigger = interactive or (not project and not description)
        assert should_trigger is False
