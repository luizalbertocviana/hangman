"""
Core game engine module for Hangman CLI.

Handles game state management, guess evaluation, and win/loss detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set

from .words import Difficulty, WordEntry


class GameError(Exception):
    """Base exception for game-related errors."""

    pass


class InvalidGuess(GameError):
    """Exception raised for invalid guess attempts."""

    pass


class GameNotStarted(GameError):
    """Exception raised when game actions are attempted before starting."""

    pass


@dataclass
class GuessResult:
    """
    Result of a guess attempt.

    Attributes:
        letter: The letter that was guessed.
        is_correct: Whether the letter is in the word.
        is_duplicate: Whether the letter was already guessed.
        word_state: Current state of the word with revealed letters.
        incorrect_guesses: Current count of incorrect guesses.
        remaining_lives: Number of lives remaining.
    """

    letter: str
    is_correct: bool
    is_duplicate: bool
    word_state: str
    incorrect_guesses: int
    remaining_lives: int


@dataclass
class GameState:
    """
    Represents the current state of a game session.

    Attributes:
        word: Target word (lowercase).
        category: Word category.
        difficulty: Difficulty level.
        guessed_letters: Letters guessed by player.
        incorrect_guesses: Count of wrong guesses (0-6).
        max_incorrect_guesses: Maximum allowed incorrect guesses.
        is_game_over: True when win or loss.
        is_win: True if player won.
        start_time: Game start timestamp.
        end_time: Game end timestamp.
    """

    word: str = ""
    category: str = ""
    difficulty: Difficulty = Difficulty.EASY
    guessed_letters: Set[str] = field(default_factory=set)
    incorrect_guesses: int = 0
    max_incorrect_guesses: int = 6
    is_game_over: bool = False
    is_win: bool = False
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def reset(self) -> None:
        """Reset the game state to initial values."""
        self.word = ""
        self.category = ""
        self.guessed_letters = set()
        self.incorrect_guesses = 0
        self.is_game_over = False
        self.is_win = False
        self.start_time = datetime.now()
        self.end_time = None


class GameEngine:
    """
    Core game engine for Hangman.

    Manages game state, processes guesses, and determines win/loss conditions.
    """

    def __init__(self, max_incorrect_guesses: int = 6) -> None:
        """
        Initialize the game engine.

        Args:
            max_incorrect_guesses: Maximum incorrect guesses before game over.
        """
        self._state = GameState()
        self._max_incorrect_guesses = max_incorrect_guesses
        self._started = False

    @property
    def state(self) -> GameState:
        """Get the current game state."""
        return self._state

    @property
    def is_started(self) -> bool:
        """Check if game has been started."""
        return self._started

    def start_game(
        self, word_entry: WordEntry, max_incorrect_guesses: Optional[int] = None
    ) -> GameState:
        """
        Start a new game with the given word.

        Args:
            word_entry: The word entry to use for the game.
            max_incorrect_guesses: Optional override for max incorrect guesses.

        Returns:
            The initial game state.
        """
        self._state.reset()
        self._state.word = word_entry.word.lower()
        self._state.category = word_entry.category
        self._state.difficulty = word_entry.difficulty
        self._state.max_incorrect_guesses = (
            max_incorrect_guesses or self._max_incorrect_guesses
        )
        self._state.start_time = datetime.now()
        self._started = True

        return self._state

    def make_guess(self, letter: str) -> GuessResult:
        """
        Process a letter guess.

        Args:
            letter: The letter being guessed.

        Returns:
            GuessResult with the outcome of the guess.

        Raises:
            GameNotStarted: If game hasn't been started.
            InvalidGuess: If the guess is invalid.
        """
        if not self._started:
            raise GameNotStarted("Game has not been started")

        # Validate the guess (but not for duplicates - we handle that below)
        if not self._state.is_game_over:
            self._validate_guess_non_duplicate(letter)

        letter = letter.lower().strip()
        is_duplicate = letter in self._state.guessed_letters

        # Add to guessed letters
        self._state.guessed_letters.add(letter)

        # Check if correct
        is_correct = letter in self._state.word

        if not is_correct and not is_duplicate:
            self._state.incorrect_guesses += 1

        # Check win/loss conditions
        self._check_game_state()

        # Calculate remaining lives
        remaining_lives = (
            self._state.max_incorrect_guesses - self._state.incorrect_guesses
        )

        return GuessResult(
            letter=letter,
            is_correct=is_correct,
            is_duplicate=is_duplicate,
            word_state=self.get_display_word(),
            incorrect_guesses=self._state.incorrect_guesses,
            remaining_lives=remaining_lives,
        )

    def _validate_guess(self, letter: str) -> None:
        """
        Validate a guess attempt.

        Args:
            letter: The letter to validate.

        Raises:
            InvalidGuess: If the guess is invalid.
        """
        if len(letter) != 1:
            raise InvalidGuess("Please enter only one letter at a time")

        if not letter.isalpha():
            raise InvalidGuess("Please enter a single letter (a-z)")

        if letter.lower() in self._state.guessed_letters:
            raise InvalidGuess(f"You already guessed '{letter}'")

    def _validate_guess_non_duplicate(self, letter: str) -> None:
        """
        Validate a guess attempt, excluding duplicate check.

        This is used by make_guess() to validate input format while
        allowing duplicate guesses to be handled gracefully.

        Args:
            letter: The letter to validate.

        Raises:
            InvalidGuess: If the guess is invalid (not a duplicate).
        """
        if len(letter) != 1:
            raise InvalidGuess("Please enter only one letter at a time")

        if not letter.isalpha():
            raise InvalidGuess("Please enter a single letter (a-z)")

    def _check_game_state(self) -> None:
        """Check and update game over conditions."""
        # Check for win: all letters guessed
        word_letters = set(self._state.word)
        if self._state.guessed_letters >= word_letters:
            self._state.is_win = True
            self._state.is_game_over = True
            self._state.end_time = datetime.now()
            return

        # Check for loss: max incorrect guesses reached
        if self._state.incorrect_guesses >= self._state.max_incorrect_guesses:
            self._state.is_win = False
            self._state.is_game_over = True
            self._state.end_time = datetime.now()

    def get_display_word(self) -> str:
        """
        Get the word with unguessed letters hidden.

        Returns:
            String with guessed letters shown and others as underscores.

        Raises:
            GameNotStarted: If game hasn't been started.
        """
        if not self._started:
            raise GameNotStarted("Game has not been started")

        display = []
        for char in self._state.word:
            if char in self._state.guessed_letters:
                display.append(char)
            else:
                display.append("_")

        return " ".join(display)

    def get_hangman_stage(self) -> int:
        """
        Get the current hangman drawing stage.

        Returns:
            Integer from 0 to max_incorrect_guesses representing stage.

        Raises:
            GameNotStarted: If game hasn't been started.
        """
        if not self._started:
            raise GameNotStarted("Game has not been started")

        return self._state.incorrect_guesses

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            True if game is over (win or loss).
        """
        return self._state.is_game_over

    def is_win(self) -> bool:
        """
        Check if the player has won.

        Returns:
            True if player won.
        """
        return self._state.is_win

    def get_remaining_lives(self) -> int:
        """
        Get the number of remaining lives.

        Returns:
            Number of lives remaining.
        """
        return self._state.max_incorrect_guesses - self._state.incorrect_guesses

    def get_guessed_letters(self) -> Set[str]:
        """
        Get the set of guessed letters.

        Returns:
            Set of guessed letters.
        """
        return self._state.guessed_letters.copy()

    def get_game_duration(self) -> float:
        """
        Get the game duration in seconds.

        Returns:
            Duration in seconds, or 0 if game hasn't ended.
        """
        if self._state.end_time is None:
            return 0.0
        return (self._state.end_time - self._state.start_time).total_seconds()

    def reset(self) -> None:
        """Reset the game engine to initial state."""
        self._state.reset()
        self._started = False
