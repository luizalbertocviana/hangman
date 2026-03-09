"""
Unit tests for the input handler module.
"""


from hangman.input_handler import (
    InputType,
    ValidationResult,
)


class TestInputHandler:
    """Tests for the InputHandler class."""

    def test_validate_letter_valid(self, input_handler):
        """Test validating a valid letter guess."""
        result = input_handler.validate_letter("a")

        assert result.input_type == InputType.LETTER
        assert result.is_valid is True
        assert result.value == "a"

    def test_validate_letter_uppercase(self, input_handler):
        """Test that uppercase letters are normalized."""
        result = input_handler.validate_letter("A")

        assert result.is_valid is True
        assert result.value == "a"

    def test_validate_letter_whitespace(self, input_handler):
        """Test that whitespace is stripped."""
        result = input_handler.validate_letter("  a  ")

        assert result.is_valid is True
        assert result.value == "a"

    def test_validate_letter_empty(self, input_handler):
        """Test validating empty input."""
        result = input_handler.validate_letter("")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID

    def test_validate_letter_multiple_chars(self, input_handler):
        """Test validating multiple characters."""
        result = input_handler.validate_letter("ab")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID
        assert "one letter" in result.error_message.lower()

    def test_validate_letter_non_alpha(self, input_handler):
        """Test validating non-alphabetic input."""
        result = input_handler.validate_letter("1")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID

    def test_validate_letter_special_chars(self, input_handler):
        """Test validating special characters."""
        result = input_handler.validate_letter("@")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID

    def test_validate_letter_duplicate(self, input_handler):
        """Test validating a duplicate guess."""
        input_handler.set_guessed_letters({"a", "b"})

        result = input_handler.validate_letter("a")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID
        assert "already guessed" in result.error_message.lower()

    def test_validate_letter_quit_command(self, input_handler):
        """Test that quit commands are detected."""
        result = input_handler.validate_letter("quit")

        assert result.input_type == InputType.QUIT
        assert result.is_valid is False

    def test_validate_letter_exit_command(self, input_handler):
        """Test that exit commands are detected."""
        result = input_handler.validate_letter("exit")

        assert result.input_type == InputType.QUIT

    def test_validate_letter_short_quit(self, input_handler):
        """Test that single letter 'q' is treated as a valid letter guess.

        Note: Previously 'q' was a quit command, but this conflicted with
        valid letter guesses. Now only full words 'quit' and 'exit' are
        recognized as quit commands (BUG FIX: hangman-hxk).
        """
        result = input_handler.validate_letter("q")

        # 'q' is now a valid letter guess, not a quit command
        assert result.input_type == InputType.LETTER
        assert result.is_valid is True
        assert result.value == "q"

    def test_validate_replay_yes(self, input_handler):
        """Test validating yes responses."""
        for yes in ["yes", "Yes", "YES", "y", "Y"]:
            result = input_handler.validate_replay(yes)
            assert result.input_type == InputType.REPLAY_YES
            assert result.is_valid is True

    def test_validate_replay_no(self, input_handler):
        """Test validating no responses."""
        for no in ["no", "No", "NO", "n", "N"]:
            result = input_handler.validate_replay(no)
            assert result.input_type == InputType.REPLAY_NO
            assert result.is_valid is True

    def test_validate_replay_invalid(self, input_handler):
        """Test validating invalid replay responses."""
        result = input_handler.validate_replay("maybe")

        assert result.is_valid is False
        assert result.input_type == InputType.INVALID

    def test_sanitize_input(self, input_handler):
        """Test input sanitization."""
        assert input_handler.sanitize_input("  A  ") == "a"
        assert input_handler.sanitize_input("Hello") == "hello"
        assert input_handler.sanitize_input("  TEST  ") == "test"

    def test_is_quit_command(self, input_handler):
        """Test quit command detection."""
        assert input_handler.is_quit_command("quit") is True
        assert input_handler.is_quit_command("QUIT") is True
        assert input_handler.is_quit_command("  quit  ") is True
        assert input_handler.is_quit_command("exit") is True
        # Single letter 'q' is NOT a quit command (it's a valid guess)
        assert input_handler.is_quit_command("q") is False
        assert input_handler.is_quit_command("play") is False
        assert input_handler.is_quit_command("a") is False

    def test_set_guessed_letters(self, input_handler):
        """Test setting guessed letters."""
        input_handler.set_guessed_letters({"A", "b", "C"})

        result = input_handler.validate_letter("a")
        assert result.is_valid is False

        result = input_handler.validate_letter("b")
        assert result.is_valid is False

        result = input_handler.validate_letter("d")
        assert result.is_valid is True

    def test_reset(self, input_handler):
        """Test resetting the input handler."""
        input_handler.set_guessed_letters({"a", "b"})
        input_handler.reset()

        result = input_handler.validate_letter("a")
        assert result.is_valid is True


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_validation_result_valid(self):
        """Test creating a valid validation result."""
        result = ValidationResult(
            input_type=InputType.LETTER,
            is_valid=True,
            value="a",
        )

        assert result.input_type == InputType.LETTER
        assert result.is_valid is True
        assert result.value == "a"
        assert result.error_message is None

    def test_validation_result_invalid(self):
        """Test creating an invalid validation result."""
        result = ValidationResult(
            input_type=InputType.INVALID,
            is_valid=False,
            error_message="Invalid input",
        )

        assert result.is_valid is False
        assert result.error_message == "Invalid input"
