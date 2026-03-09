"""
Integration tests for Hangman CLI.

Tests full game sessions and component interactions.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from hangman.game import GameEngine
from hangman.input_handler import InputHandler, InputType
from hangman.renderer import UIRenderer
from hangman.stats import SessionStats, StatsManager
from hangman.words import Difficulty, WordEntry, WordListManager
from hangman.config import Config, ConfigurationManager


class TestFullGameSession:
    """Integration tests for complete game sessions."""

    def test_complete_winning_game(self, word_entry):
        """Test a complete game session that results in a win."""
        # Setup components
        game_engine = GameEngine(max_incorrect_guesses=6)
        input_handler = InputHandler()
        renderer = UIRenderer(enable_colors=False)
        stats = SessionStats()

        # Start game
        game_engine.start_game(word_entry)
        input_handler.set_guessed_letters(game_engine.get_guessed_letters())

        # Make correct guesses to win
        for letter in "python":
            if letter not in game_engine.get_guessed_letters():
                result = input_handler.validate_letter(letter)
                if result.is_valid:
                    game_engine.make_guess(result.value)

        # Verify win condition
        assert game_engine.is_game_over() is True
        assert game_engine.is_win() is True

        # Record stats
        stats.record_game(is_win=True, guesses_made=len(game_engine.get_guessed_letters()))
        assert stats.games_won == 1

    def test_complete_losing_game(self, word_entry):
        """Test a complete game session that results in a loss."""
        game_engine = GameEngine(max_incorrect_guesses=6)
        input_handler = InputHandler()
        stats = SessionStats()

        # Start game
        game_engine.start_game(word_entry)

        # Make 6 incorrect guesses
        incorrect_letters = "xyzwvq"
        for letter in incorrect_letters:
            result = input_handler.validate_letter(letter)
            if result.is_valid:
                game_engine.make_guess(result.value)

        # Verify loss condition
        assert game_engine.is_game_over() is True
        assert game_engine.is_win() is False

        # Record stats
        stats.record_game(is_win=False, guesses_made=len(incorrect_letters))
        assert stats.games_lost == 1

    def test_game_with_mixed_guesses(self, word_entry):
        """Test a game with both correct and incorrect guesses."""
        game_engine = GameEngine(max_incorrect_guesses=6)
        input_handler = InputHandler()

        # Start game
        game_engine.start_game(word_entry)

        # Mix of correct and incorrect guesses
        guesses = ["p", "x", "y", "z", "t", "w", "h", "o", "n"]
        for letter in guesses:
            result = input_handler.validate_letter(letter)
            if result.is_valid:
                game_engine.make_guess(result.value)

        # Should win (all letters guessed)
        assert game_engine.is_game_over() is True
        assert game_engine.is_win() is True
        assert game_engine.state.incorrect_guesses == 3  # x, z, w

    def test_renderer_displays_game_state(self, renderer, game_engine, word_entry):
        """Test that renderer correctly displays game state."""
        game_engine.start_game(word_entry)

        # Capture output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            renderer.display_game_state(
                game_engine.state,
                category="Programming",
                difficulty="Medium"
            )
            output = mock_stdout.getvalue()

        # Verify output contains expected elements
        assert "Category: Programming" in output
        assert "Difficulty: MEDIUM" in output
        assert "Lives:" in output

    def test_renderer_displays_win_message(self, renderer):
        """Test that renderer displays win message correctly."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            renderer.display_win("python", 45.5)
            output = mock_stdout.getvalue()

        assert "YOU WIN" in output
        assert "PYTHON" in output

    def test_renderer_displays_loss_message(self, renderer):
        """Test that renderer displays loss message correctly."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            renderer.display_loss("python")
            output = mock_stdout.getvalue()

        assert "GAME OVER" in output
        assert "PYTHON" in output

    def test_input_handler_replay_flow(self, input_handler):
        """Test the replay prompt flow."""
        # Test yes responses
        for response in ["yes", "y", "Yes", "Y"]:
            result = input_handler.validate_replay(response)
            assert result.input_type == InputType.REPLAY_YES
            assert result.is_valid is True

        # Test no responses
        for response in ["no", "n", "No", "N"]:
            result = input_handler.validate_replay(response)
            assert result.input_type == InputType.REPLAY_NO
            assert result.is_valid is True

    def test_stats_persistence_across_games(self):
        """Test that stats persist across multiple games."""
        stats = SessionStats()

        # Play multiple games
        stats.record_game(is_win=True, guesses_made=5)
        stats.record_game(is_win=True, guesses_made=4)
        stats.record_game(is_win=False, guesses_made=6)
        stats.record_game(is_win=True, guesses_made=3)

        # Verify cumulative stats
        assert stats.games_played == 4
        assert stats.games_won == 3
        assert stats.games_lost == 1
        assert stats.current_streak == 1
        assert stats.best_streak == 2
        assert stats.get_win_rate() == 75.0


class TestWordListManagerIntegration:
    """Integration tests for word list management."""

    def test_load_and_get_random_word(self, word_list_manager):
        """Test loading word lists and getting random words."""
        from pathlib import Path
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        # Get multiple random words
        words = set()
        for _ in range(10):
            word = word_list_manager.get_random_word()
            words.add(word.word)

        # Should get varied words
        assert len(words) >= 1

    def test_word_list_filtering(self, word_list_manager):
        """Test filtering words by category and difficulty."""
        from pathlib import Path
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        # Filter by category
        animals = word_list_manager.get_random_word(category="animals")
        assert animals.category == "animals"

        # Filter by difficulty
        easy_word = word_list_manager.get_random_word(difficulty=Difficulty.EASY)
        assert easy_word.difficulty == Difficulty.EASY

        # Filter by both
        easy_animal = word_list_manager.get_random_word(
            category="animals",
            difficulty=Difficulty.EASY
        )
        assert easy_animal.category == "animals"
        assert easy_animal.difficulty == Difficulty.EASY

    def test_word_normalization(self, word_list_manager):
        """Test that words are properly normalized."""
        from pathlib import Path
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        # Get many random words and verify normalization
        for _ in range(20):
            word = word_list_manager.get_random_word()
            assert word.word == word.word.lower()
            assert word.word.isalpha()


class TestConfigurationIntegration:
    """Integration tests for configuration management."""

    def test_config_manager_singleton(self):
        """Test that ConfigurationManager is a proper singleton."""
        manager1 = ConfigurationManager()
        manager2 = ConfigurationManager()

        assert manager1 is manager2

        # Load config on one instance
        config1 = manager1.load()

        # Should be same config on other instance
        config2 = manager2.get_config()

        assert config1 is config2

        ConfigurationManager.reset_instance()

    def test_config_affects_game_engine(self):
        """Test that configuration affects game engine behavior."""
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""
game:
  max_incorrect_guesses: 4
""")

            manager = ConfigurationManager()
            config = manager.load(str(config_file))

            # Create game engine with config value
            game_engine = GameEngine(max_incorrect_guesses=config.game.max_incorrect_guesses)
            word_entry = WordEntry(word="test", category="test", difficulty=Difficulty.EASY)
            game_engine.start_game(word_entry)

            # Make 4 incorrect guesses - should lose
            for letter in "xyzw":
                game_engine.make_guess(letter)

            assert game_engine.is_game_over() is True
            assert game_engine.is_win() is False

            ConfigurationManager.reset_instance()


class TestEndToEndGameFlow:
    """End-to-end tests simulating real user interactions."""

    def test_typical_game_session(self, word_entry):
        """Simulate a typical game session with user input."""
        # Initialize all components
        game_engine = GameEngine(max_incorrect_guesses=6)
        input_handler = InputHandler()
        renderer = UIRenderer(enable_colors=False)
        stats = SessionStats()

        # Start game
        game_engine.start_game(word_entry)

        # Simulate user guesses
        user_guesses = ["p", "x", "y", "z", "t", "h", "o", "n"]
        for guess in user_guesses:
            if game_engine.is_game_over():
                break

            result = input_handler.validate_letter(guess)
            if result.is_valid and result.input_type == InputType.LETTER:
                guess_result = game_engine.make_guess(result.value)

        # Verify game ended
        assert game_engine.is_game_over() is True

        # Record final stats
        stats.record_game(is_win=game_engine.is_win(), guesses_made=len(user_guesses))

        # Verify stats
        assert stats.games_played == 1
        if game_engine.is_win():
            assert stats.games_won == 1

    def test_replay_session_flow(self, word_entry):
        """Test multiple games in a session (replay flow)."""
        game_engine = GameEngine(max_incorrect_guesses=6)
        stats = SessionStats()

        # Play first game - win
        game_engine.start_game(word_entry)
        for letter in "python":
            if letter not in game_engine.get_guessed_letters():
                game_engine.make_guess(letter)

        assert game_engine.is_win() is True
        stats.record_game(is_win=True, guesses_made=6)

        # Reset for replay
        game_engine.reset()

        # Play second game - loss
        game_engine.start_game(word_entry)
        for letter in "xyzwvq":
            game_engine.make_guess(letter)

        assert game_engine.is_win() is False
        stats.record_game(is_win=False, guesses_made=6)

        # Verify session stats
        assert stats.games_played == 2
        assert stats.games_won == 1
        assert stats.games_lost == 1
