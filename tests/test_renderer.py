"""
Tests for renderer.py module.

Tests UI rendering, styling, and display functionality.
"""

from unittest.mock import patch

import pytest

from hangman.game import GameEngine
from hangman.renderer import MessageType, UIRenderer, UIStyles
from hangman.words import Difficulty, WordEntry


class TestUIStyles:
    """Tests for UIStyles class."""

    def test_ui_styles_color_codes_exist(self):
        """Test UIStyles has all expected color codes."""
        assert UIStyles.RESET == "\033[0m"
        assert UIStyles.BOLD == "\033[1m"
        assert UIStyles.RED == "\033[31m"
        assert UIStyles.GREEN == "\033[32m"
        assert UIStyles.YELLOW == "\033[33m"
        assert UIStyles.BLUE == "\033[34m"
        assert UIStyles.BRIGHT_RED == "\033[91m"
        assert UIStyles.BRIGHT_GREEN == "\033[92m"
        assert UIStyles.BRIGHT_CYAN == "\033[96m"


class TestUIRendererInitialization:
    """Tests for UIRenderer initialization."""

    def test_renderer_creation_with_defaults(self):
        """Test UIRenderer creation with default settings."""
        renderer = UIRenderer()
        assert renderer.enable_colors is True

    def test_renderer_creation_without_colors(self):
        """Test UIRenderer creation with colors disabled."""
        renderer = UIRenderer(enable_colors=False)
        assert renderer.enable_colors is False

    def test_enable_colors_setter(self):
        """Test enable_colors property setter."""
        renderer = UIRenderer(enable_colors=False)
        renderer.enable_colors = True
        assert renderer.enable_colors is True


class TestStyleMethod:
    """Tests for _style method."""

    def test_style_disabled_colors(self):
        """Test _style returns plain text when colors disabled."""
        renderer = UIRenderer(enable_colors=False)
        result = renderer._style("test", MessageType.INFO)
        assert result == "test"

    def test_style_info_message(self):
        """Test _style with INFO message type."""
        renderer = UIRenderer(enable_colors=True)
        result = renderer._style("test", MessageType.INFO)
        assert UIStyles.CYAN in result
        assert UIStyles.RESET in result

    def test_style_success_message(self):
        """Test _style with SUCCESS message type."""
        renderer = UIRenderer(enable_colors=True)
        result = renderer._style("test", MessageType.SUCCESS)
        assert UIStyles.BRIGHT_GREEN in result

    def test_style_warning_message(self):
        """Test _style with WARNING message type."""
        renderer = UIRenderer(enable_colors=True)
        result = renderer._style("test", MessageType.WARNING)
        assert UIStyles.BRIGHT_YELLOW in result

    def test_style_error_message(self):
        """Test _style with ERROR message type."""
        renderer = UIRenderer(enable_colors=True)
        result = renderer._style("test", MessageType.ERROR)
        assert UIStyles.BRIGHT_RED in result

    def test_style_prompt_message(self):
        """Test _style with PROMPT message type."""
        renderer = UIRenderer(enable_colors=True)
        result = renderer._style("test", MessageType.PROMPT)
        assert UIStyles.BOLD in result
        assert UIStyles.BLUE in result


class TestDisplayHangman:
    """Tests for display_hangman method."""

    @pytest.mark.parametrize("stage", range(7))
    def test_display_hangman_all_stages(self, stage, capsys):
        """Test display_hangman for all stages (0-6)."""
        renderer = UIRenderer(enable_colors=False)
        renderer.display_hangman(stage)
        captured = capsys.readouterr()
        assert "+---+" in captured.out
        assert "|   |" in captured.out
        assert "=========" in captured.out

    def test_display_hangman_stage_clamping_low(self, capsys):
        """Test display_hangman clamps negative stage to 0."""
        renderer = UIRenderer(enable_colors=False)
        renderer.display_hangman(-1)
        captured = capsys.readouterr()
        # Stage 0 has no body parts
        assert "O" not in captured.out

    def test_display_hangman_stage_clamping_high(self, capsys):
        """Test display_hangman clamps high stage to max."""
        renderer = UIRenderer(enable_colors=False)
        renderer.display_hangman(100)
        captured = capsys.readouterr()
        # Max stage has full body
        assert "O" in captured.out
        assert "/|\\" in captured.out

    def test_display_hangman_color_stages_error(self, capsys):
        """Test display_hangman uses ERROR color for stage 5-6."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_hangman(6)
        captured = capsys.readouterr()
        assert UIStyles.BRIGHT_RED in captured.out

    def test_display_hangman_color_stages_warning(self, capsys):
        """Test display_hangman uses WARNING color for stage 3-4."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_hangman(4)
        captured = capsys.readouterr()
        assert UIStyles.BRIGHT_YELLOW in captured.out


class TestDisplayGameState:
    """Tests for display_game_state method."""

    def test_display_game_state_with_category_difficulty(self, capsys):
        """Test display_game_state shows category and difficulty."""
        renderer = UIRenderer(enable_colors=False)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="animals", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        renderer.display_game_state(game.state, category="Animals", difficulty="Easy")
        captured = capsys.readouterr()
        assert "Category: Animals" in captured.out
        assert "Difficulty: EASY" in captured.out

    def test_display_game_state_word_display(self, capsys):
        """Test display_game_state shows word with underscores."""
        renderer = UIRenderer(enable_colors=False)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        assert "_ _ _ _" in captured.out

    def test_display_game_state_lives_display(self, capsys):
        """Test display_game_state shows lives remaining."""
        renderer = UIRenderer(enable_colors=False)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        assert "Lives: 6/6" in captured.out

    def test_display_game_state_lives_low(self, capsys):
        """Test display_game_state uses ERROR color for low lives."""
        renderer = UIRenderer(enable_colors=True)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        # Make 4 incorrect guesses to have 2 lives left
        for letter in "xyzw":
            game.make_guess(letter)

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        assert UIStyles.BRIGHT_RED in captured.out

    def test_display_game_state_lives_medium(self, capsys):
        """Test display_game_state uses WARNING color for medium lives."""
        renderer = UIRenderer(enable_colors=True)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        # Make 2 incorrect guesses to have 4 lives left
        for letter in "xy":
            game.make_guess(letter)

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        assert UIStyles.BRIGHT_YELLOW in captured.out

    def test_display_game_state_guessed_letters(self, capsys):
        """Test display_game_state shows guessed letters."""
        renderer = UIRenderer(enable_colors=False)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        game.make_guess("t")
        game.make_guess("e")

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        assert "Guessed: e, t" in captured.out

    def test_display_game_state_revealed_letters(self, capsys):
        """Test display_game_state reveals correctly guessed letters."""
        renderer = UIRenderer(enable_colors=True)
        game = GameEngine()
        word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
        game.start_game(word_entry)

        game.make_guess("t")

        renderer.display_game_state(game.state)
        captured = capsys.readouterr()
        # T should be revealed with styling
        assert "T" in captured.out
        assert UIStyles.BRIGHT_GREEN in captured.out


class TestDisplayMessages:
    """Tests for various display message methods."""

    def test_display_welcome(self, capsys):
        """Test display_welcome shows welcome message."""
        renderer = UIRenderer(enable_colors=False)
        renderer.display_welcome()
        captured = capsys.readouterr()
        assert "WELCOME TO HANGMAN" in captured.out
        assert "Rules:" in captured.out
        assert "6 incorrect guesses" in captured.out

    def test_display_message(self, capsys):
        """Test display_message shows styled message."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_message("Test message", MessageType.INFO)
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert UIStyles.CYAN in captured.out

    def test_display_invalid_input(self, capsys):
        """Test display_invalid_input shows error."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_invalid_input("Invalid letter")
        captured = capsys.readouterr()
        assert "Invalid letter" in captured.out
        assert "⚠" in captured.out
        assert UIStyles.BRIGHT_RED in captured.out

    def test_display_already_guessed(self, capsys):
        """Test display_already_guessed shows warning."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_already_guessed("a")
        captured = capsys.readouterr()
        assert "already guessed" in captured.out
        assert "A" in captured.out
        assert UIStyles.BRIGHT_YELLOW in captured.out

    def test_display_correct_guess(self, capsys):
        """Test display_correct_guess shows success."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_correct_guess("t")
        captured = capsys.readouterr()
        assert "is in the word" in captured.out
        assert "T" in captured.out
        assert UIStyles.BRIGHT_GREEN in captured.out

    def test_display_incorrect_guess(self, capsys):
        """Test display_incorrect_guess shows error."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_incorrect_guess("z")
        captured = capsys.readouterr()
        assert "is not in the word" in captured.out
        assert "Z" in captured.out
        assert UIStyles.BRIGHT_RED in captured.out


class TestWinLossDisplay:
    """Tests for win/loss display methods."""

    def test_display_win(self, capsys):
        """Test display_win shows victory message."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_win("test", 45.5)
        captured = capsys.readouterr()
        assert "YOU WIN" in captured.out
        assert "TEST" in captured.out
        assert "45.5" in captured.out
        assert UIStyles.BRIGHT_GREEN in captured.out

    def test_display_loss(self, capsys):
        """Test display_loss shows game over message."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_loss("test")
        captured = capsys.readouterr()
        assert "GAME OVER" in captured.out
        assert "TEST" in captured.out
        assert "Better luck" in captured.out
        assert UIStyles.BRIGHT_RED in captured.out


class TestInputMethods:
    """Tests for input-related methods."""

    def test_get_input_with_prompt(self):
        """Test get_input displays prompt and reads input."""
        renderer = UIRenderer(enable_colors=True)

        with patch("sys.stdin.readline", return_value="test\n"):
            result = renderer.get_input("> ")
            assert result == "test"

    def test_get_input_without_prompt(self):
        """Test get_input works without prompt."""
        renderer = UIRenderer(enable_colors=True)

        with patch("sys.stdin.readline", return_value="test\n"):
            result = renderer.get_input("")
            assert result == "test"

    def test_get_input_keyboard_interrupt(self, capsys):
        """Test get_input handles KeyboardInterrupt."""
        renderer = UIRenderer(enable_colors=False)

        with patch("sys.stdin.readline", side_effect=KeyboardInterrupt):
            result = renderer.get_input("> ")
            assert result == "quit"

    def test_display_replay_prompt(self, capsys):
        """Test display_replay_prompt shows prompt."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_replay_prompt()
        captured = capsys.readouterr()
        assert "Play again?" in captured.out
        assert "yes/no" in captured.out
        assert UIStyles.BOLD in captured.out

    def test_display_goodbye(self, capsys):
        """Test display_goodbye shows goodbye message."""
        renderer = UIRenderer(enable_colors=True)
        renderer.display_goodbye()
        captured = capsys.readouterr()
        assert "Thanks for playing" in captured.out
        assert "Goodbye" in captured.out
        assert UIStyles.CYAN in captured.out


class TestDisplayStats:
    """Tests for display_stats method."""

    def test_display_stats(self, capsys):
        """Test display_stats shows statistics."""
        renderer = UIRenderer(enable_colors=True)
        stats = {
            "games_played": 10,
            "games_won": 7,
            "win_rate": 70.0,
            "current_streak": 3,
        }
        renderer.display_stats(stats)
        captured = capsys.readouterr()
        assert "SESSION STATISTICS" in captured.out
        assert "Games Played: 10" in captured.out
        assert "Games Won: 7" in captured.out
        assert "Win Rate: 70.0" in captured.out
        assert "Current Streak: 3" in captured.out
        assert UIStyles.CYAN in captured.out

    def test_display_stats_empty(self, capsys):
        """Test display_stats with empty dict."""
        renderer = UIRenderer(enable_colors=False)
        renderer.display_stats({})
        captured = capsys.readouterr()
        assert "SESSION STATISTICS" in captured.out


class TestClearScreen:
    """Tests for clear_screen method."""

    def test_clear_screen_unix(self):
        """Test clear_screen uses 'clear' on Unix."""
        renderer = UIRenderer()
        with patch("os.system") as mock_system:
            with patch("os.name", "posix"):
                renderer.clear_screen()
                mock_system.assert_called_with("clear")

    def test_clear_screen_windows(self):
        """Test clear_screen uses 'cls' on Windows."""
        renderer = UIRenderer()
        with patch("os.system") as mock_system:
            with patch("os.name", "nt"):
                renderer.clear_screen()
                mock_system.assert_called_with("cls")
