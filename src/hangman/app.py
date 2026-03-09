"""
Application controller module for Hangman CLI.

Orchestrates game sessions and component interactions.
"""

from __future__ import annotations

import signal
import sys

from .config import Config, ConfigurationManager
from .game import GameEngine
from .input_handler import InputHandler, InputType, QuitRequestedError
from .renderer import MessageType, UIRenderer
from .stats import StatsManager
from .words import WordListError, WordListManager


class ApplicationController:
    """
    Main application controller for Hangman CLI.

    Orchestrates all components and manages the game loop.
    """

    def __init__(self) -> None:
        """Initialize the application controller."""
        self._config: Config | None = None
        self._config_manager = ConfigurationManager()
        self._word_manager: WordListManager | None = None
        self._game_engine: GameEngine | None = None
        self._input_handler: InputHandler | None = None
        self._renderer: UIRenderer | None = None
        self._stats_manager: StatsManager | None = None
        self._running = False

    def initialize(self) -> bool:
        """
        Initialize all application components.

        Returns:
            True if initialization was successful.
        """
        try:
            # Load configuration
            self._config = self._config_manager.load()

            # Initialize components with configuration
            self._renderer = UIRenderer(
                enable_colors=self._config.display.enable_colors
            )

            self._word_manager = WordListManager(
                self._config_manager.get_word_lists_path()
            )

            self._game_engine = GameEngine(
                max_incorrect_guesses=self._config.game.max_incorrect_guesses
            )

            self._input_handler = InputHandler()

            self._stats_manager = StatsManager()
            self._stats_manager.initialize(self._config_manager.get_stats_file_path())

            # Set up signal handlers for graceful exit
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)

            return True

        except Exception as e:
            print(f"Failed to initialize application: {e}", file=sys.stderr)
            return False

    def _handle_signal(self, signum: int, frame: object) -> None:
        """Handle termination signals gracefully."""
        self._running = False

    def run(self) -> int:
        """
        Run the main application loop.

        Returns:
            Exit code (0 for success, 1 for error).
        """
        if not self.initialize():
            return 1

        # Type narrowing: components are guaranteed to be initialized after initialize()
        assert self._renderer is not None
        assert self._word_manager is not None
        assert self._game_engine is not None
        assert self._input_handler is not None
        assert self._stats_manager is not None

        try:
            self._running = True

            # Display welcome screen
            self._renderer.clear_screen()
            self._renderer.display_welcome()

            # Load word lists
            try:
                self._word_manager.load_word_lists()
            except WordListError as e:
                self._renderer.display_message(
                    f"Error loading word lists: {e}", MessageType.ERROR
                )
                return 1

            # Show session stats on startup
            self._display_startup_stats()

            # Main game loop
            while self._running:
                self._play_game()

                # Ask to play again
                if not self._ask_replay():
                    break

            # Goodbye
            self._renderer.display_goodbye()

            # Save stats before exit
            self._stats_manager.save()

            return 0

        except QuitRequestedError:
            self._renderer.display_goodbye()
            self._stats_manager.save()
            return 0

        except Exception as e:
            self._renderer.display_message(f"Unexpected error: {e}", MessageType.ERROR)
            return 1

    def _display_startup_stats(self) -> None:
        """Display statistics from previous sessions."""
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._stats_manager is not None
        assert self._renderer is not None

        stats = self._stats_manager.get_stats()
        if stats.games_played > 0:
            self._renderer.display_message(
                f"Previous sessions: {stats.games_played} games, "
                f"{stats.games_won} wins ({stats.get_win_rate():.1f}%)",
                MessageType.INFO,
            )
            print()

    def _play_game(self) -> None:
        """Play a single game session."""
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._game_engine is not None
        assert self._word_manager is not None
        assert self._input_handler is not None
        assert self._renderer is not None

        # Select a random word
        try:
            word_entry = self._word_manager.get_random_word()
        except WordListError as e:
            self._renderer.display_message(
                f"Error selecting word: {e}", MessageType.ERROR
            )
            return

        # Start the game
        self._game_engine.start_game(word_entry)

        # Update input handler with game state
        self._input_handler.set_guessed_letters(self._game_engine.get_guessed_letters())

        # Game loop
        while self._running and not self._game_engine.is_game_over():
            self._render_game()
            self._handle_guess()

        # Game over
        self._handle_game_over()

    def _render_game(self) -> None:
        """Render the current game state."""
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._game_engine is not None
        assert self._renderer is not None

        state = self._game_engine.state
        self._renderer.clear_screen()
        self._renderer.display_game_state(
            state,
            category=state.category.title(),
            difficulty=state.difficulty.value.title(),
        )

    def _handle_guess(self) -> None:
        """Handle a single guess from the player."""
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._game_engine is not None
        assert self._input_handler is not None
        assert self._renderer is not None

        try:
            # Get input
            user_input = self._input_handler.read_input("Enter a letter (or 'quit'): ")

            # Validate
            result = self._input_handler.validate_letter(user_input)

            if result.input_type == InputType.QUIT:
                raise QuitRequestedError("User requested exit")

            if not result.is_valid:
                self._renderer.display_invalid_input(result.error_message or "")
                return

            # Make the guess
            if result.value:
                guess_result = self._game_engine.make_guess(result.value)

                if guess_result.is_duplicate:
                    self._renderer.display_already_guessed(result.value)
                elif guess_result.is_correct:
                    self._renderer.display_correct_guess(result.value)
                else:
                    self._renderer.display_incorrect_guess(result.value)

        except QuitRequestedError:
            raise

    def _handle_game_over(self) -> None:
        """Handle game end conditions."""
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._game_engine is not None
        assert self._renderer is not None
        assert self._stats_manager is not None

        state = self._game_engine.state

        # Record the game
        guesses_made = len(state.guessed_letters)
        self._stats_manager.record_game(state.is_win, guesses_made)

        if state.is_win:
            duration = self._game_engine.get_game_duration()
            self._renderer.display_win(state.word, duration)
        else:
            self._renderer.display_loss(state.word)

        # Save stats after each game
        self._stats_manager.save()

    def _ask_replay(self) -> bool:
        """
        Ask the player if they want to play again.

        Returns:
            True if player wants to play again.
        """
        # Type narrowing: components guaranteed non-None after initialize()
        assert self._renderer is not None
        assert self._input_handler is not None

        self._renderer.display_replay_prompt()

        try:
            while True:
                user_input = self._input_handler.read_input("> ")
                result = self._input_handler.validate_replay(user_input)

                if result.input_type == InputType.QUIT:
                    return False

                if result.input_type == InputType.REPLAY_YES:
                    return True

                if result.input_type == InputType.REPLAY_NO:
                    return False

                # Invalid input
                if result.error_message:
                    self._renderer.display_invalid_input(result.error_message)

        except QuitRequestedError:
            return False

        return False


def create_app() -> ApplicationController:
    """
    Create and configure the application.

    Returns:
        Configured ApplicationController instance.
    """
    return ApplicationController()
