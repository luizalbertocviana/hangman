"""
Unit tests for the core game engine module.
"""

import pytest
from datetime import datetime

from hangman.game import (
    GameEngine,
    GameState,
    GuessResult,
    GameError,
    InvalidGuess,
    GameNotStarted,
)
from hangman.words import Difficulty, WordEntry


class TestGameState:
    """Tests for the GameState dataclass."""

    def test_initial_state(self):
        """Test that initial state has correct default values."""
        state = GameState()
        assert state.word == ""
        assert state.category == ""
        assert state.difficulty == Difficulty.EASY
        assert len(state.guessed_letters) == 0
        assert state.incorrect_guesses == 0
        assert state.max_incorrect_guesses == 6
        assert state.is_game_over is False
        assert state.is_win is False

    def test_reset(self):
        """Test that reset clears the game state."""
        state = GameState()
        state.word = "test"
        state.category = "programming"
        state.guessed_letters = {"t", "e"}
        state.incorrect_guesses = 2
        state.is_game_over = True

        state.reset()

        assert state.word == ""
        assert state.guessed_letters == set()
        assert state.incorrect_guesses == 0
        assert state.is_game_over is False


class TestGameEngine:
    """Tests for the GameEngine class."""

    def test_start_game(self, game_engine, word_entry):
        """Test starting a new game."""
        state = game_engine.start_game(word_entry)

        assert game_engine.is_started is True
        assert state.word == "python"
        assert state.category == "programming"
        assert state.difficulty == Difficulty.MEDIUM
        assert state.incorrect_guesses == 0
        assert state.is_game_over is False

    def test_start_game_custom_max_guesses(self, word_entry):
        """Test starting a game with custom max incorrect guesses."""
        engine = GameEngine(max_incorrect_guesses=10)
        state = engine.start_game(word_entry, max_incorrect_guesses=8)

        assert state.max_incorrect_guesses == 8

    def test_make_guess_correct(self, game_engine, word_entry):
        """Test making a correct guess."""
        game_engine.start_game(word_entry)
        result = game_engine.make_guess("p")

        assert result.is_correct is True
        assert result.is_duplicate is False
        assert "p" in result.word_state

    def test_make_guess_incorrect(self, game_engine, word_entry):
        """Test making an incorrect guess."""
        game_engine.start_game(word_entry)
        result = game_engine.make_guess("z")

        assert result.is_correct is False
        assert result.incorrect_guesses == 1
        assert result.remaining_lives == 5

    def test_make_guess_duplicate(self, game_engine, word_entry):
        """Test making a duplicate guess."""
        game_engine.start_game(word_entry)
        game_engine.make_guess("p")
        result = game_engine.make_guess("p")

        assert result.is_duplicate is True

    def test_make_guess_before_start(self, game_engine):
        """Test that guessing before start raises error."""
        with pytest.raises(GameNotStarted):
            game_engine.make_guess("a")

    def test_make_guess_invalid_letter(self, game_engine, word_entry):
        """Test that invalid guesses raise errors."""
        game_engine.start_game(word_entry)

        with pytest.raises(InvalidGuess):
            game_engine.make_guess("ab")  # Multiple letters

        with pytest.raises(InvalidGuess):
            game_engine.make_guess("1")  # Non-alpha

    def test_get_display_word(self, game_engine, word_entry):
        """Test word display with guessed letters."""
        game_engine.start_game(word_entry)

        # Initial state - all hidden
        display = game_engine.get_display_word()
        assert display == "_ _ _ _ _ _"

        # Guess some letters
        game_engine.make_guess("p")
        game_engine.make_guess("y")

        display = game_engine.get_display_word()
        assert "P" in display or "p" in display.lower()

    def test_get_hangman_stage(self, game_engine, word_entry):
        """Test hangman stage progression."""
        game_engine.start_game(word_entry)

        assert game_engine.get_hangman_stage() == 0

        game_engine.make_guess("1")
        assert game_engine.get_hangman_stage() == 1

        game_engine.make_guess("2")
        assert game_engine.get_hangman_stage() == 2

    def test_win_condition(self, game_engine):
        """Test that game detects win condition."""
        # Use a short word for easier testing
        word = WordEntry(word="cat", category="animals", difficulty=Difficulty.EASY)
        game_engine.start_game(word)

        game_engine.make_guess("c")
        game_engine.make_guess("a")
        game_engine.make_guess("t")

        assert game_engine.is_game_over() is True
        assert game_engine.is_win() is True

    def test_loss_condition(self, game_engine, word_entry):
        """Test that game detects loss condition."""
        game_engine.start_game(word_entry)

        # Make 6 incorrect guesses
        for letter in "xyzwvq":
            game_engine.make_guess(letter)

        assert game_engine.is_game_over() is True
        assert game_engine.is_win() is False

    def test_get_remaining_lives(self, game_engine, word_entry):
        """Test remaining lives calculation."""
        game_engine.start_game(word_entry)

        assert game_engine.get_remaining_lives() == 6

        game_engine.make_guess("1")
        game_engine.make_guess("2")

        assert game_engine.get_remaining_lives() == 4

    def test_get_guessed_letters(self, game_engine, word_entry):
        """Test getting guessed letters."""
        game_engine.start_game(word_entry)

        game_engine.make_guess("p")
        game_engine.make_guess("y")
        game_engine.make_guess("t")

        guessed = game_engine.get_guessed_letters()
        assert "p" in guessed
        assert "y" in guessed
        assert "t" in guessed

    def test_game_duration(self, game_engine, word_entry):
        """Test game duration calculation."""
        game_engine.start_game(word_entry)

        # Game hasn't ended yet
        assert game_engine.get_game_duration() == 0.0

        # Complete the game
        game_engine.make_guess("p")
        game_engine.make_guess("y")
        game_engine.make_guess("t")
        game_engine.make_guess("h")
        game_engine.make_guess("o")
        game_engine.make_guess("n")

        duration = game_engine.get_game_duration()
        assert duration >= 0.0

    def test_reset(self, game_engine, word_entry):
        """Test resetting the game engine."""
        game_engine.start_game(word_entry)
        game_engine.make_guess("p")

        game_engine.reset()

        assert game_engine.is_started is False
        with pytest.raises(GameNotStarted):
            game_engine.get_display_word()


class TestGuessResult:
    """Tests for the GuessResult dataclass."""

    def test_guess_result_creation(self):
        """Test creating a GuessResult."""
        result = GuessResult(
            letter="a",
            is_correct=True,
            is_duplicate=False,
            word_state="a _ _ _ _",
            incorrect_guesses=0,
            remaining_lives=6,
        )

        assert result.letter == "a"
        assert result.is_correct is True
        assert result.remaining_lives == 6
