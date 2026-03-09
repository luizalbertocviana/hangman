# Hangman CLI Game

## Overview
A command-line interface (CLI) application for playing the classic Hangman word-guessing game.

## Core Requirements

### Functional
- Display welcome message and game rules on startup
- Select random words from configurable word lists
- Accept single-letter guesses via stdin
- Display word state (underscores for unguessed letters)
- Track and display guessed letters
- Show ASCII art hangman visualization (6 stages)
- Detect win (all letters guessed) and loss (6 incorrect guesses) conditions
- Offer replay option after game ends
- Support graceful exit (quit command, Ctrl+C)

### Non-Functional
- Cross-platform (Linux, macOS, Windows)
- Responsive input handling (<100ms)
- Clear error messages for invalid input
- Minimum terminal size: 80x24
- Memory footprint: <50MB

### Security
- Input sanitization for all user input
- Graceful error handling without crashes
- Validated file paths for word lists

### Word Management
- External word list files (configurable)
- Support for word categories
- Normalized words (lowercase, alphabetic only)

## Game Rules
1. Player has 6 incorrect guesses before game over
2. Each incorrect guess advances the hangman drawing
3. Correct guesses reveal all instances of that letter
4. Re-guessing letters is not allowed
5. Game ends when word is complete (win) or 6 wrong guesses (loss)

## See Also
- See `REQUIREMENTS.md` for detailed requirements analysis
- See `AGENTS.md` for development workflow instructions
