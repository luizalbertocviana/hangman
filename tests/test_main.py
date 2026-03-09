"""
Tests for __main__.py entry point.

Tests argument parsing, flags, and main entry point functionality.
"""

import sys
from unittest.mock import MagicMock, patch

from hangman.__main__ import main, parse_args, print_help, print_version


class TestParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_empty(self):
        """Test parse_args with no arguments returns True."""
        result = parse_args([])
        assert result is True

    def test_parse_args_none(self):
        """Test parse_args with None uses sys.argv."""
        with patch("hangman.__main__.sys.argv", ["hangman"]):
            result = parse_args(None)
            assert result is True

    def test_parse_args_help_long(self):
        """Test parse_args with --help flag returns False."""
        with patch("hangman.__main__.print_help") as mock_help:
            result = parse_args(["--help"])
            assert result is False
            assert mock_help.called

    def test_parse_args_help_short(self):
        """Test parse_args with -h flag returns False."""
        with patch("hangman.__main__.print_help") as mock_help:
            result = parse_args(["-h"])
            assert result is False
            assert mock_help.called

    def test_parse_args_version_long(self):
        """Test parse_args with --version flag returns False."""
        with patch("hangman.__main__.print_version") as mock_version:
            result = parse_args(["--version"])
            assert result is False
            assert mock_version.called

    def test_parse_args_version_short(self):
        """Test parse_args with -v flag returns False."""
        with patch("hangman.__main__.print_version") as mock_version:
            result = parse_args(["-v"])
            assert result is False
            assert mock_version.called

    def test_parse_args_unknown_argument(self):
        """Test parse_args with unknown argument returns True."""
        result = parse_args(["--unknown"])
        assert result is True

    def test_parse_args_help_takes_precedence(self):
        """Test parse_args with multiple flags processes help first."""
        with patch("hangman.__main__.print_help") as mock_help:
            with patch("hangman.__main__.print_version") as mock_version:
                result = parse_args(["--help", "--version"])
                assert result is False
                assert mock_help.called
                assert not mock_version.called


class TestPrintHelp:
    """Tests for print_help function."""

    def test_print_help_outputs_help_text(self, capsys):
        """Test print_help outputs the help message."""
        print_help()
        captured = capsys.readouterr()
        assert "Hangman CLI Game v1.0.0" in captured.out
        assert "Usage:" in captured.out
        assert "hangman [OPTIONS]" in captured.out
        assert "-h, --help" in captured.out
        assert "-v, --version" in captured.out
        assert "Description:" in captured.out
        assert "Controls:" in captured.out
        assert "Examples:" in captured.out

    def test_print_help_includes_controls(self, capsys):
        """Test print_help includes control instructions."""
        print_help()
        captured = capsys.readouterr()
        assert "Enter a letter (a-z) to guess" in captured.out
        assert "Type 'quit' to exit" in captured.out
        assert "Ctrl+C" in captured.out

    def test_print_help_includes_examples(self, capsys):
        """Test print_help includes usage examples."""
        print_help()
        captured = capsys.readouterr()
        assert "hangman           # Start the game" in captured.out
        assert "hangman --help    # Show this help" in captured.out
        assert "hangman --version # Show version" in captured.out


class TestPrintVersion:
    """Tests for print_version function."""

    def test_print_version_outputs_version(self, capsys):
        """Test print_version outputs version information."""
        with patch("hangman.__version__", "1.0.0"):
            print_version()
            captured = capsys.readouterr()
            assert "Hangman CLI Game v1.0.0" in captured.out

    def test_print_version_outputs_python_version(self, capsys):
        """Test print_version outputs Python version."""
        with patch("hangman.__version__", "1.0.0"):
            print_version()
            captured = capsys.readouterr()
            assert "Python" in captured.out

    def test_print_version_python_version_format(self, capsys):
        """Test print_version outputs Python version in correct format."""
        with patch("hangman.__version__", "1.0.0"):
            print_version()
            captured = capsys.readouterr()
            # Should be first part of sys.version (e.g., "3.9.7")
            expected_python = sys.version.split()[0]
            assert expected_python in captured.out


class TestMain:
    """Tests for main entry point function."""

    def test_main_returns_zero_on_success(self):
        """Test main returns 0 on successful execution."""
        with patch("hangman.__main__.parse_args", return_value=True):
            with patch("hangman.app.ApplicationController") as mock_app_class:
                mock_app = MagicMock()
                mock_app.run.return_value = 0
                mock_app_class.return_value = mock_app

                result = main()

                assert result == 0
                assert mock_app_class.called
                assert mock_app.run.called

    def test_main_returns_zero_when_parse_args_false(self):
        """Test main returns 0 when parse_args returns False."""
        with patch("hangman.__main__.parse_args", return_value=False):
            result = main()
            assert result == 0

    def test_main_handles_import_error(self, capsys):
        """Test main handles ImportError gracefully."""
        with patch("hangman.__main__.parse_args", return_value=True):
            with patch("hangman.app.ApplicationController", side_effect=ImportError("Test error")):
                result = main()
                assert result == 1
                captured = capsys.readouterr()
                assert "Error: Failed to import application module" in captured.err

    def test_main_handles_general_exception(self, capsys):
        """Test main handles general exceptions gracefully."""
        with patch("hangman.__main__.parse_args", return_value=True):
            with patch("hangman.app.ApplicationController", side_effect=Exception("Test error")):
                result = main()
                assert result == 1
                captured = capsys.readouterr()
                assert "Error: Test error" in captured.err

    def test_main_creates_application_controller(self):
        """Test main creates ApplicationController instance."""
        with patch("hangman.__main__.parse_args", return_value=True):
            with patch("hangman.app.ApplicationController") as mock_app_class:
                mock_app = MagicMock()
                mock_app.run.return_value = 0
                mock_app_class.return_value = mock_app

                main()

                assert mock_app_class.called
                assert mock_app.run.called

    def test_main_returns_app_run_exit_code(self):
        """Test main returns the exit code from app.run()."""
        with patch("hangman.__main__.parse_args", return_value=True):
            with patch("hangman.app.ApplicationController") as mock_app_class:
                mock_app = MagicMock()
                mock_app.run.return_value = 42
                mock_app_class.return_value = mock_app

                result = main()

                assert result == 42


class TestMainWithRealArguments:
    """Tests for main with real sys.argv manipulation."""

    def test_main_with_help_flag(self, capsys):
        """Test main with --help flag displays help and exits."""
        with patch.object(sys, "argv", ["hangman", "--help"]):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Hangman CLI Game v1.0.0" in captured.out

    def test_main_with_version_flag(self, capsys):
        """Test main with --version flag displays version and exits."""
        with patch.object(sys, "argv", ["hangman", "--version"]):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Hangman CLI Game v" in captured.out
            assert "Python" in captured.out

    def test_main_with_short_help_flag(self, capsys):
        """Test main with -h flag displays help and exits."""
        with patch.object(sys, "argv", ["hangman", "-h"]):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Hangman CLI Game v1.0.0" in captured.out

    def test_main_with_short_version_flag(self, capsys):
        """Test main with -v flag displays version and exits."""
        with patch.object(sys, "argv", ["hangman", "-v"]):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Hangman CLI Game v" in captured.out
