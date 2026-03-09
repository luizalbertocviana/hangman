"""
CLI input handler module for Hangman CLI.

Handles reading, validating, and sanitizing user input from stdin.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set


class InputType(Enum):
    """Types of valid input."""

    LETTER = "letter"
    QUIT = "quit"
    REPLAY_YES = "yes"
    REPLAY_NO = "no"
    INVALID = "invalid"


@dataclass
class ValidationResult:
    """
    Result of input validation.

    Attributes:
        input_type: The type of input detected.
        is_valid: Whether the input is valid.
        value: The sanitized value (if applicable).
        error_message: Error message for invalid input.
    """

    input_type: InputType
    is_valid: bool
    value: Optional[str] = None
    error_message: Optional[str] = None


class InputError(Exception):
    """Base exception for input-related errors."""

    pass


class QuitRequested(InputError):
    """Exception raised when user requests to quit."""

    pass


class InputHandler:
    """
    Handles user input processing for the Hangman game.

    Provides methods to read, validate, and sanitize user input.
    """

    # Quit commands
    QUIT_COMMANDS = {"quit", "exit", "q"}

    # Yes responses for replay
    YES_RESPONSES = {"yes", "y"}

    # No responses for replay
    NO_RESPONSES = {"no", "n"}

    def __init__(self) -> None:
        """Initialize the input handler."""
        self._guessed_letters: Set[str] = set()

    def set_guessed_letters(self, letters: Set[str]) -> None:
        """
        Set the set of already guessed letters.

        Args:
            letters: Set of letters that have been guessed.
        """
        self._guessed_letters = {c.lower() for c in letters}

    def read_input(self, prompt: str = "> ") -> str:
        """
        Read input from stdin.

        Args:
            prompt: Optional prompt to display.

        Returns:
            The raw input string.

        Raises:
            InputError: If there's an error reading input.
            QuitRequested: If user sends EOF (Ctrl+D/Ctrl+Z).
        """
        try:
            # Write prompt to stderr to keep output clean
            if prompt:
                sys.stderr.write(prompt)
                sys.stderr.flush()

            # Read from stdin
            line = sys.stdin.readline()

            # Check for EOF (Ctrl+D on Unix, Ctrl+Z on Windows)
            if not line:
                raise QuitRequested("User requested exit (EOF)")

            return line.rstrip("\n\r")

        except KeyboardInterrupt:
            raise QuitRequested("User requested exit (Ctrl+C)")

    def validate_letter(self, user_input: str) -> ValidationResult:
        """
        Validate a letter guess.

        Args:
            user_input: The raw user input.

        Returns:
            ValidationResult with validation outcome.
        """
        # Check for quit command first
        if self.is_quit_command(user_input):
            return ValidationResult(
                input_type=InputType.QUIT,
                is_valid=False,
                error_message="Quit command received",
            )

        # Strip whitespace
        sanitized = user_input.strip().lower()

        # Check for empty input
        if not sanitized:
            return ValidationResult(
                input_type=InputType.INVALID,
                is_valid=False,
                error_message="Please enter a letter",
            )

        # Check for multi-character input
        if len(sanitized) > 1:
            return ValidationResult(
                input_type=InputType.INVALID,
                is_valid=False,
                error_message="Please enter only one letter at a time",
            )

        # Check for non-alphabetic character
        if not sanitized.isalpha():
            return ValidationResult(
                input_type=InputType.INVALID,
                is_valid=False,
                error_message="Please enter a single letter (a-z)",
            )

        # Check for duplicate guess
        if sanitized in self._guessed_letters:
            return ValidationResult(
                input_type=InputType.INVALID,
                is_valid=False,
                error_message=f"You already guessed '{sanitized}'",
            )

        # Valid letter guess
        return ValidationResult(
            input_type=InputType.LETTER,
            is_valid=True,
            value=sanitized,
        )

    def validate_replay(self, user_input: str) -> ValidationResult:
        """
        Validate a replay response.

        Args:
            user_input: The raw user input.

        Returns:
            ValidationResult with validation outcome.
        """
        # Check for quit command
        if self.is_quit_command(user_input):
            return ValidationResult(
                input_type=InputType.QUIT,
                is_valid=False,
                error_message="Quit command received",
            )

        # Strip and lowercase
        sanitized = user_input.strip().lower()

        # Check for yes
        if sanitized in self.YES_RESPONSES:
            return ValidationResult(
                input_type=InputType.REPLAY_YES,
                is_valid=True,
                value="yes",
            )

        # Check for no
        if sanitized in self.NO_RESPONSES:
            return ValidationResult(
                input_type=InputType.REPLAY_NO,
                is_valid=True,
                value="no",
            )

        # Invalid response
        return ValidationResult(
            input_type=InputType.INVALID,
            is_valid=False,
            error_message="Please enter 'yes' or 'no'",
        )

    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input.

        Args:
            user_input: Raw user input.

        Returns:
            Sanitized input (lowercase, stripped).
        """
        return user_input.strip().lower()

    def is_quit_command(self, user_input: str) -> bool:
        """
        Check if input is a quit command.

        Args:
            user_input: The raw user input.

        Returns:
            True if input matches a quit command.
        """
        sanitized = user_input.strip().lower()
        return sanitized in self.QUIT_COMMANDS

    def reset(self) -> None:
        """Reset the input handler state."""
        self._guessed_letters = set()
