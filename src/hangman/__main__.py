#!/usr/bin/env python3
"""
Hangman CLI Game - Main Entry Point.

A command-line interface application for playing the classic Hangman word-guessing game.

Usage:
    python -m hangman
    hangman  # If installed via pip

Run with --help for more information.
"""

from __future__ import annotations

import sys


def parse_args(args: list[str] | None = None) -> bool:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        True if application should continue running.
    """
    if args is None:
        args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_help()
        return False

    if "--version" in args or "-v" in args:
        print_version()
        return False

    return True


def print_help() -> None:
    """Print help message."""
    help_text = """
Hangman CLI Game v1.0.0

Usage:
    hangman [OPTIONS]

Options:
    -h, --help      Show this help message and exit
    -v, --version   Show version information and exit

Description:
    A command-line interface application for playing the classic
    Hangman word-guessing game.

    The game will:
    - Display a welcome message with rules
    - Select a random word from a category
    - Accept single-letter guesses
    - Show ASCII art hangman visualization
    - Track wins, losses, and statistics

Controls:
    - Enter a letter (a-z) to guess
    - Type 'quit' to exit the game
    - Press Ctrl+C to exit at any time

Examples:
    hangman           # Start the game
    hangman --help    # Show this help
    hangman --version # Show version

For more information, see the README.md file.
"""
    print(help_text)


def print_version() -> None:
    """Print version information."""
    from . import __version__

    print(f"Hangman CLI Game v{__version__}")
    print("Python", sys.version.split()[0])


def main() -> int:
    """
    Main entry point for the Hangman CLI game.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Parse command-line arguments
    if not parse_args():
        return 0

    # Import and run the application
    try:
        from .app import ApplicationController

        app = ApplicationController()
        return app.run()

    except ImportError as e:
        print(f"Error: Failed to import application module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
