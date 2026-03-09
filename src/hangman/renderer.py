"""
UI renderer module for Hangman CLI.

Handles terminal output, ASCII art display, and user messages.
"""

from __future__ import annotations

import os
import sys
from enum import Enum
from typing import List, Optional

from .game import GameState


class MessageType(Enum):
    """Types of messages for display styling."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROMPT = "prompt"


class UIStyles:
    """ANSI color codes for terminal output."""

    # Colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


class UIRenderer:
    """
    Renders the game UI to the terminal.

    Handles display of game state, hangman ASCII art, and messages.
    """

    # ASCII art for hangman stages (0-6)
    HANGMAN_ART = [
        # Stage 0: Empty gallows
        """
    +---+
    |   |
        |
        |
        |
        |
  =========
""",
        # Stage 1: Head
        """
    +---+
    |   |
    O   |
        |
        |
        |
  =========
""",
        # Stage 2: Head + Body
        """
    +---+
    |   |
    O   |
    |   |
        |
        |
  =========
""",
        # Stage 3: Head + Body + Left Arm
        """
    +---+
    |   |
    O   |
   /|   |
        |
        |
  =========
""",
        # Stage 4: Head + Body + Both Arms
        """
    +---+
    |   |
    O   |
   /|\\  |
        |
        |
  =========
""",
        # Stage 5: Head + Body + Both Arms + Left Leg
        """
    +---+
    |   |
    O   |
   /|\\  |
   /    |
        |
  =========
""",
        # Stage 6: Complete hangman (game over)
        """
    +---+
    |   |
    O   |
   /|\\  |
   / \\  |
        |
  =========
""",
    ]

    def __init__(self, enable_colors: bool = True) -> None:
        """
        Initialize the UI renderer.

        Args:
            enable_colors: Whether to use ANSI colors in output.
        """
        self._enable_colors = enable_colors
        self._last_message_type: Optional[MessageType] = None

    @property
    def enable_colors(self) -> bool:
        """Check if colors are enabled."""
        return self._enable_colors

    @enable_colors.setter
    def enable_colors(self, value: bool) -> None:
        """Set whether colors are enabled."""
        self._enable_colors = value

    def _style(self, text: str, msg_type: MessageType) -> str:
        """
        Apply styling to text based on message type.

        Args:
            text: The text to style.
            msg_type: The type of message.

        Returns:
            Styled text string.
        """
        if not self._enable_colors:
            return text

        style_map = {
            MessageType.INFO: UIStyles.CYAN,
            MessageType.SUCCESS: UIStyles.BRIGHT_GREEN,
            MessageType.WARNING: UIStyles.BRIGHT_YELLOW,
            MessageType.ERROR: UIStyles.BRIGHT_RED,
            MessageType.PROMPT: UIStyles.BOLD + UIStyles.BLUE,
        }

        color = style_map.get(msg_type, "")
        return f"{color}{text}{UIStyles.RESET}"

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        # Use 'cls' for Windows, 'clear' for Unix-like systems
        os.system("cls" if os.name == "nt" else "clear")

    def display_welcome(self) -> None:
        """Display the welcome message and game rules."""
        welcome_text = """
╔═══════════════════════════════════════════════════════════╗
║                    WELCOME TO HANGMAN                     ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Guess the word before the hangman is complete!           ║
║                                                           ║
║  Rules:                                                   ║
║  • You have 6 incorrect guesses before game over          ║
║  • Enter one letter at a time (a-z)                       ║
║  • Type 'quit' to exit the game                           ║
║  • Correct letters are revealed in the word               ║
║  • Don't let the hangman be completed!                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        print(self._style(welcome_text, MessageType.INFO))

    def display_hangman(self, stage: int) -> None:
        """
        Display the hangman ASCII art for the current stage.

        Args:
            stage: The current hangman stage (0-6).
        """
        stage = max(0, min(stage, len(self.HANGMAN_ART) - 1))
        art = self.HANGMAN_ART[stage]

        if stage >= 5:
            print(self._style(art, MessageType.ERROR))
        elif stage >= 3:
            print(self._style(art, MessageType.WARNING))
        else:
            print(art)

    def display_game_state(
        self,
        state: GameState,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> None:
        """
        Display the current game state.

        Args:
            state: The current game state.
            category: Optional category name to display.
            difficulty: Optional difficulty name to display.
        """
        print()

        # Display category and difficulty if provided
        if category or difficulty:
            info_parts = []
            if category:
                info_parts.append(f"Category: {category}")
            if difficulty:
                info_parts.append(f"Difficulty: {difficulty.upper()}")
            print(self._style(" | ".join(info_parts), MessageType.INFO))
            print()

        # Display hangman
        self.display_hangman(state.incorrect_guesses)

        # Display word state
        word_display = self._format_word_display(state)
        print(f"\n  {word_display}\n")

        # Display lives remaining
        lives = state.max_incorrect_guesses - state.incorrect_guesses
        lives_text = f"Lives: {lives}/{state.max_incorrect_guesses}"
        if lives <= 2:
            print(self._style(lives_text, MessageType.ERROR))
        elif lives <= 4:
            print(self._style(lives_text, MessageType.WARNING))
        else:
            print(self._style(lives_text, MessageType.SUCCESS))

        # Display guessed letters
        if state.guessed_letters:
            sorted_letters = sorted(state.guessed_letters)
            letters_str = ", ".join(sorted_letters)
            print(f"\nGuessed: {letters_str}")

        print()

    def _format_word_display(self, state: GameState) -> str:
        """
        Format the word display with proper spacing.

        Args:
            state: The current game state.

        Returns:
            Formatted word display string.
        """
        display_chars = []
        for char in state.word:
            if char in state.guessed_letters:
                display_chars.append(self._style(char.upper(), MessageType.SUCCESS))
            else:
                display_chars.append("_")
        return " ".join(display_chars)

    def display_message(self, message: str, msg_type: MessageType = MessageType.INFO) -> None:
        """
        Display a message to the user.

        Args:
            message: The message to display.
            msg_type: The type of message for styling.
        """
        self._last_message_type = msg_type
        styled = self._style(message, msg_type)
        print(styled)

    def display_win(self, word: str, duration: float) -> None:
        """
        Display victory message.

        Args:
            word: The word that was guessed.
            duration: Game duration in seconds.
        """
        win_message = f"""
╔═══════════════════════════════════════════════════════════╗
║                      🎉 YOU WIN! 🎉                       ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  The word was: {word.upper():<42} ║
║  Time: {duration:.1f} seconds                                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        print(self._style(win_message, MessageType.SUCCESS))

    def display_loss(self, word: str) -> None:
        """
        Display game over message.

        Args:
            word: The correct word.
        """
        loss_message = f"""
╔═══════════════════════════════════════════════════════════╗
║                    💀 GAME OVER 💀                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  The word was: {word.upper():<42} ║
║                                                           ║
║  Better luck next time!                                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        print(self._style(loss_message, MessageType.ERROR))

    def display_invalid_input(self, error_message: str) -> None:
        """
        Display an invalid input error.

        Args:
            error_message: The error message to display.
        """
        print(self._style(f"  ⚠ {error_message}", MessageType.ERROR))

    def display_already_guessed(self, letter: str) -> None:
        """
        Display a message that a letter was already guessed.

        Args:
            letter: The letter that was already guessed.
        """
        print(self._style(f"  You already guessed '{letter.upper()}'", MessageType.WARNING))

    def display_correct_guess(self, letter: str) -> None:
        """
        Display a message for a correct guess.

        Args:
            letter: The letter that was guessed correctly.
        """
        print(self._style(f"  ✓ '{letter.upper()}' is in the word!", MessageType.SUCCESS))

    def display_incorrect_guess(self, letter: str) -> None:
        """
        Display a message for an incorrect guess.

        Args:
            letter: The letter that was guessed incorrectly.
        """
        print(self._style(f"  ✗ '{letter.upper()}' is not in the word.", MessageType.ERROR))

    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from the user.

        Args:
            prompt: The prompt to display.

        Returns:
            User input string.
        """
        try:
            if prompt:
                styled_prompt = self._style(prompt, MessageType.PROMPT)
                sys.stderr.write(styled_prompt)
                sys.stderr.flush()

            return sys.stdin.readline().rstrip("\n\r")

        except KeyboardInterrupt:
            print()
            return "quit"

    def display_replay_prompt(self) -> None:
        """Display the replay prompt."""
        print()
        print(self._style("Play again? (yes/no)", MessageType.PROMPT))

    def display_goodbye(self) -> None:
        """Display a goodbye message."""
        goodbye = """
╔═══════════════════════════════════════════════════════════╗
║                    Thanks for playing!                    ║
║                       Goodbye! 👋                         ║
╚═══════════════════════════════════════════════════════════╝
"""
        print(self._style(goodbye, MessageType.INFO))

    def display_stats(self, stats: dict) -> None:
        """
        Display session statistics.

        Args:
            stats: Dictionary of statistics to display.
        """
        stats_text = """
╔═══════════════════════════════════════════════════════════╗
║                    SESSION STATISTICS                     ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
"""
        for key, value in stats.items():
            formatted_key = key.replace("_", " ").title()
            stats_text += f"║  {formatted_key}: {value:<44} ║\n"

        stats_text += """║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        print(self._style(stats_text, MessageType.INFO))
