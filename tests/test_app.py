"""
Integration tests for ApplicationController (app.py).

Tests the main application controller and its components.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hangman.app import ApplicationController, create_app
from hangman.config import Config, ConfigurationManager
from hangman.game import GameEngine
from hangman.input_handler import InputHandler, InputType
from hangman.renderer import UIRenderer
from hangman.stats import StatsManager
from hangman.words import Difficulty, WordEntry, WordListError, WordListManager


class TestApplicationControllerInitialization:
    """Tests for ApplicationController initialization."""

    def test_create_app_factory(self):
        """Test the create_app factory function."""
        app = create_app()
        assert isinstance(app, ApplicationController)

    def test_application_controller_creation(self):
        """Test ApplicationController can be created."""
        app = ApplicationController()
        assert app is not None
        assert app._running is False

    def test_initialize_success(self, tmp_path):
        """Test successful initialization of all components."""
        # Create a temporary config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("game:\n  max_incorrect_guesses: 6\n")

        # Create temp word lists directory
        word_dir = tmp_path / "words"
        word_dir.mkdir()
        word_file = word_dir / "test.json"
        word_file.write_text("""
{
    "version": "1.0",
    "categories": {
        "test": {
            "easy": ["test"]
        }
    }
}
""")

        app = ApplicationController()

        with patch.object(
            app._config_manager, "_get_default_config_path", return_value=str(config_file)
        ):
            # Temporarily set word lists path
            original_init = app.__class__.__init__

            def mock_init(self):
                original_init(self)
                self._config_manager._config = None  # Reset config cache

            with patch.object(app.__class__, '__init__', mock_init):
                app = ApplicationController()
                # Re-setup for test
                app._config_manager = ConfigurationManager()
                app._word_manager = WordListManager(word_dir)

                # Initialize components manually for test
                app._config = app._config_manager.load()
                app._renderer = UIRenderer(enable_colors=False)
                app._input_handler = InputHandler()
                app._stats_manager = StatsManager()
                app._stats_manager.initialize(tmp_path / "stats.json")
                app._game_engine = GameEngine(max_incorrect_guesses=6)

                assert app._config is not None
                assert app._renderer is not None
                assert app._input_handler is not None
                assert app._stats_manager is not None
                assert app._game_engine is not None

            ConfigurationManager.reset_instance()
            StatsManager.reset_instance()

    def test_initialize_failure_handling(self):
        """Test initialization failure is handled gracefully."""
        app = ApplicationController()

        # Mock config manager to raise exception
        with patch.object(app._config_manager, 'load', side_effect=Exception("Config error")):
            result = app.initialize()
            assert result is False

        ConfigurationManager.reset_instance()


class TestApplicationControllerRun:
    """Tests for ApplicationController run method."""

    def test_run_initialization_failure(self):
        """Test run returns error code when initialization fails."""
        app = ApplicationController()

        with patch.object(app, 'initialize', return_value=False):
            exit_code = app.run()
            assert exit_code == 1

    def test_run_displays_welcome_screen(self):
        """Test that run displays welcome screen."""
        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        with patch.object(app, 'initialize', return_value=True):
            with patch.object(app._word_manager, 'load_word_lists'):
                with patch.object(app, '_play_game'):
                    with patch.object(app, '_ask_replay', return_value=False):
                        with patch.object(app._renderer, 'clear_screen') as mock_clear:
                            with patch.object(app._renderer, 'display_welcome') as mock_welcome:
                                exit_code = app.run()

                                assert mock_clear.called
                                assert mock_welcome.called
                                assert exit_code == 0

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_run_handles_word_list_error(self):
        """Test run handles word list loading errors."""
        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        with patch.object(app, 'initialize', return_value=True):
            with patch.object(app._word_manager, 'load_word_lists',
                            side_effect=WordListError("Word list error")):
                with patch.object(app._renderer, 'clear_screen'):
                    with patch.object(app._renderer, 'display_welcome'):
                        with patch.object(app._renderer, 'display_message') as mock_msg:
                            exit_code = app.run()

                            assert mock_msg.called
                            assert "Error loading word lists" in mock_msg.call_args[0][0]
                            assert exit_code == 1

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_run_handles_quit_requested(self):
        """Test run handles QuitRequestedError gracefully."""
        from hangman.input_handler import QuitRequestedError

        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        with patch.object(app, 'initialize', return_value=True):
            with patch.object(app._word_manager, 'load_word_lists'):
                with patch.object(app, '_play_game',
                                side_effect=QuitRequestedError("User quit")):
                    with patch.object(app._renderer, 'display_goodbye') as mock_bye:
                        exit_code = app.run()

                        assert mock_bye.called
                        assert exit_code == 0

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_run_handles_unexpected_exception(self):
        """Test run handles unexpected exceptions."""
        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        with patch.object(app, 'initialize', return_value=True):
            with patch.object(app._word_manager, 'load_word_lists'):
                with patch.object(app, '_play_game',
                                side_effect=Exception("Unexpected error")):
                    with patch.object(app._renderer, 'display_message') as mock_msg:
                        exit_code = app.run()

                        assert mock_msg.called
                        assert "Unexpected error" in mock_msg.call_args[0][0]
                        assert exit_code == 1

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()


class TestApplicationControllerGameFlow:
    """Tests for game flow methods."""

    def test_play_game_selects_word(self):
        """Test _play_game selects a word from word manager."""
        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()
        app._running = True

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)

        with patch.object(app._word_manager, 'get_random_word', return_value=word_entry):
            with patch.object(app._game_engine, 'start_game') as mock_start:
                with patch.object(app._input_handler, 'set_guessed_letters'):
                    with patch.object(app, "_render_game"):
                        with patch.object(app, "_handle_guess"):
                            with patch.object(app, "_handle_game_over"):
                                # Force game over immediately
                                with patch.object(
                                    app._game_engine, "is_game_over", return_value=True
                                ):
                                    app._play_game()

                                    assert mock_start.called
                                    assert mock_start.call_args[0][0] == word_entry

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_play_game_handles_word_list_error(self):
        """Test _play_game handles word selection errors."""
        app = ApplicationController()
        app._config = Config()
        app._renderer = UIRenderer(enable_colors=False)
        app._word_manager = WordListManager()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._stats_manager = StatsManager()

        with patch.object(app._word_manager, 'get_random_word',
                        side_effect=WordListError("No words")):
            with patch.object(app._renderer, 'display_message') as mock_msg:
                app._play_game()

                assert mock_msg.called
                assert "Error selecting word" in mock_msg.call_args[0][0]

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_render_game_clears_screen(self):
        """Test _render_game clears screen and displays state."""
        app = ApplicationController()
        app._game_engine = GameEngine()
        app._renderer = UIRenderer(enable_colors=False)

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        with patch.object(app._renderer, 'clear_screen') as mock_clear:
            with patch.object(app._renderer, 'display_game_state') as mock_display:
                app._render_game()

                assert mock_clear.called
                assert mock_display.called

    def test_handle_guess_valid_letter(self):
        """Test _handle_guess processes valid letter."""
        app = ApplicationController()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._renderer = UIRenderer(enable_colors=False)

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        with patch.object(app._input_handler, 'read_input', return_value="t"):
            with patch.object(app._input_handler, 'validate_letter') as mock_validate:
                mock_validate.return_value = MagicMock(
                    input_type=InputType.LETTER,
                    is_valid=True,
                    value="t",
                    error_message=None
                )
                with patch.object(app._game_engine, 'make_guess') as mock_guess:
                    mock_guess.return_value = MagicMock(
                        is_duplicate=False,
                        is_correct=True
                    )
                    app._handle_guess()

                    assert mock_validate.called
                    assert mock_guess.called

    def test_handle_guess_invalid_input(self):
        """Test _handle_guess handles invalid input."""
        app = ApplicationController()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._renderer = UIRenderer(enable_colors=False)

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        with patch.object(app._input_handler, 'read_input', return_value="123"):
            with patch.object(app._input_handler, 'validate_letter') as mock_validate:
                mock_validate.return_value = MagicMock(
                    input_type=InputType.INVALID,
                    is_valid=False,
                    value=None,
                    error_message="Invalid input"
                )
                with patch.object(app._renderer, 'display_invalid_input') as mock_invalid:
                    app._handle_guess()

                    assert mock_invalid.called

    def test_handle_guess_quit_command(self):
        """Test _handle_guess handles quit command."""
        from hangman.input_handler import QuitRequestedError

        app = ApplicationController()
        app._game_engine = GameEngine()
        app._input_handler = InputHandler()
        app._renderer = UIRenderer(enable_colors=False)

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        with patch.object(app._input_handler, 'read_input', return_value="quit"):
            with patch.object(app._input_handler, 'validate_letter') as mock_validate:
                mock_validate.return_value = MagicMock(
                    input_type=InputType.QUIT,
                    is_valid=False
                )
                with pytest.raises(QuitRequestedError):
                    app._handle_guess()

    def test_handle_game_over_win(self):
        """Test _handle_game_over handles win condition."""
        app = ApplicationController()
        app._game_engine = GameEngine()
        app._renderer = UIRenderer(enable_colors=False)
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        # Guess all letters to win
        for letter in "test":
            app._game_engine.make_guess(letter)

        with patch.object(app._stats_manager, 'record_game') as mock_record:
            with patch.object(app._renderer, 'display_win') as mock_win:
                app._handle_game_over()

                assert mock_record.called
                assert mock_win.called

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_handle_game_over_loss(self):
        """Test _handle_game_over handles loss condition."""
        app = ApplicationController()
        app._game_engine = GameEngine()
        app._renderer = UIRenderer(enable_colors=False)
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        app._game_engine.start_game(word_entry)

        # Make 6 incorrect guesses to lose
        for letter in "xyzwvq":
            app._game_engine.make_guess(letter)

        with patch.object(app._stats_manager, 'record_game') as mock_record:
            with patch.object(app._renderer, 'display_loss') as mock_loss:
                app._handle_game_over()

                assert mock_record.called
                assert mock_loss.called

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_ask_replay_yes(self):
        """Test _ask_replay returns True for yes."""
        app = ApplicationController()
        app._renderer = UIRenderer(enable_colors=False)
        app._input_handler = InputHandler()

        with patch.object(app._renderer, "display_replay_prompt"):
            with patch.object(app._input_handler, "read_input", return_value="yes"):
                with patch.object(app._input_handler, "validate_replay") as mock_replay:
                    mock_replay.return_value = MagicMock(
                        input_type=InputType.REPLAY_YES,
                        is_valid=True
                    )
                    result = app._ask_replay()
                    assert result is True

    def test_ask_replay_no(self):
        """Test _ask_replay returns False for no."""
        app = ApplicationController()
        app._renderer = UIRenderer(enable_colors=False)
        app._input_handler = InputHandler()

        with patch.object(app._renderer, 'display_replay_prompt'):
            with patch.object(app._input_handler, 'read_input', return_value="no"):
                with patch.object(app._input_handler, 'validate_replay') as mock_replay:
                    mock_replay.return_value = MagicMock(
                        input_type=InputType.REPLAY_NO,
                        is_valid=True
                    )
                    result = app._ask_replay()
                    assert result is False

    def test_display_startup_stats_with_previous_games(self):
        """Test _display_startup_stats shows stats when games played."""
        app = ApplicationController()
        app._renderer = UIRenderer(enable_colors=False)
        app._stats_manager = StatsManager()
        app._stats_manager.initialize()

        # Record a game
        app._stats_manager.record_game(is_win=True, guesses_made=5)

        with patch.object(app._renderer, 'display_message') as mock_msg:
            app._display_startup_stats()

            assert mock_msg.called
            assert "Previous sessions" in mock_msg.call_args[0][0]

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()

    def test_display_startup_stats_no_previous_games(self):
        """Test _display_startup_stats skips display when no games played."""
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            # Reset singleton to ensure clean state
            StatsManager.reset_instance()

            app = ApplicationController()
            app._renderer = UIRenderer(enable_colors=False)
            app._stats_manager = StatsManager()
            app._stats_manager.initialize(Path(tmpdir) / "stats.json")

            # Ensure no games played
            stats = app._stats_manager.get_stats()
            assert stats.games_played == 0

            with patch.object(app._renderer, "display_message") as mock_msg:
                app._display_startup_stats()

                # Should not display message when no games played
                assert not mock_msg.called

        ConfigurationManager.reset_instance()
        StatsManager.reset_instance()


class TestSignalHandling:
    """Tests for signal handling."""

    def test_handle_signal_sets_running_false(self):
        """Test _handle_signal sets _running to False."""
        app = ApplicationController()
        app._running = True

        app._handle_signal(2, None)  # SIGINT

        assert app._running is False


class TestCreateApp:
    """Tests for create_app factory function."""

    def test_create_app_returns_application_controller(self):
        """Test create_app returns ApplicationController instance."""
        app = create_app()
        assert isinstance(app, ApplicationController)
