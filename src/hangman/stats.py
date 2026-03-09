"""
Session statistics module for Hangman CLI.

Tracks and persists game statistics across sessions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionStats:
    """
    Tracks statistics across multiple game sessions.

    Attributes:
        games_played: Total games played in session.
        games_won: Number of games won.
        games_lost: Number of games lost.
        current_streak: Current win streak.
        best_streak: Best win streak achieved.
        total_guesses: Total guesses made.
        start_time: Session start timestamp.
        last_updated: Last update timestamp.
    """

    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    current_streak: int = 0
    best_streak: int = 0
    total_guesses: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def record_game(self, is_win: bool, guesses_made: int) -> None:
        """
        Record a completed game.

        Args:
            is_win: Whether the game was won.
            guesses_made: Number of guesses made in the game.
        """
        self.games_played += 1
        self.total_guesses += guesses_made
        self.last_updated = datetime.now()

        if is_win:
            self.games_won += 1
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.games_lost += 1
            self.current_streak = 0

    def get_win_rate(self) -> float:
        """
        Calculate the win rate percentage.

        Returns:
            Win rate as a percentage (0-100), or 0 if no games played.
        """
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    def to_dict(self) -> dict[str, Any]:
        """
        Convert stats to a dictionary for serialization.

        Returns:
            Dictionary representation of stats.
        """
        return {
            "games_played": self.games_played,
            "games_won": self.games_won,
            "games_lost": self.games_lost,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "total_guesses": self.total_guesses,
            "start_time": self.start_time.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionStats:
        """
        Create SessionStats from a dictionary.

        Args:
            data: Dictionary with stats data.

        Returns:
            SessionStats instance.
        """
        stats = cls()

        stats.games_played = data.get("games_played", 0)
        stats.games_won = data.get("games_won", 0)
        stats.games_lost = data.get("games_lost", 0)
        stats.current_streak = data.get("current_streak", 0)
        stats.best_streak = data.get("best_streak", 0)
        stats.total_guesses = data.get("total_guesses", 0)

        # Parse timestamps
        if "start_time" in data:
            try:
                stats.start_time = datetime.fromisoformat(data["start_time"])
            except (ValueError, TypeError):
                stats.start_time = datetime.now()

        if "last_updated" in data:
            try:
                stats.last_updated = datetime.fromisoformat(data["last_updated"])
            except (ValueError, TypeError):
                stats.last_updated = datetime.now()

        return stats

    def reset(self) -> None:
        """Reset all statistics to initial values."""
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.current_streak = 0
        self.best_streak = 0
        self.total_guesses = 0
        self.start_time = datetime.now()
        self.last_updated = datetime.now()


class StatsManager:
    """
    Manages persistence of session statistics.

    Loads and saves statistics to a JSON file.
    """

    _instance: StatsManager | None = None
    _stats: SessionStats | None = None
    _stats_file: Path | None = None

    def __new__(cls) -> StatsManager:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the stats manager."""
        if not hasattr(self, "_initialized"):
            self._stats = None
            self._stats_file = None
            self._initialized = True

    def initialize(self, stats_file_path: Path | None = None) -> SessionStats:
        """
        Initialize the stats manager and load existing stats.

        Args:
            stats_file_path: Path to the stats file.

        Returns:
            Loaded or new SessionStats instance.
        """
        if stats_file_path is not None:
            self._stats_file = stats_file_path

        if self._stats_file is None:
            # Default to user's home directory
            home = Path.home()
            hangman_dir = home / ".hangman"
            hangman_dir.mkdir(parents=True, exist_ok=True)
            self._stats_file = hangman_dir / "stats.json"

        self._stats = self._load_stats()
        return self._stats

    def _load_stats(self) -> SessionStats:
        """
        Load statistics from file.

        Returns:
            Loaded SessionStats or new instance if file doesn't exist.
        """
        if self._stats_file is None:
            return SessionStats()

        if not self._stats_file.exists():
            return SessionStats()

        try:
            with open(self._stats_file, encoding="utf-8") as f:
                data = json.load(f)

            # Handle versioned stats files
            if isinstance(data, dict):
                if "stats" in data:
                    # New format with version
                    return SessionStats.from_dict(data["stats"])
                else:
                    # Old format (direct stats)
                    return SessionStats.from_dict(data)

        except (json.JSONDecodeError, OSError):
            # Return new stats if file is corrupted
            pass

        return SessionStats()

    def save(self) -> bool:
        """
        Save current statistics to file.

        Returns:
            True if save was successful, False otherwise.
        """
        if self._stats is None or self._stats_file is None:
            return False

        try:
            # Ensure directory exists
            self._stats_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "stats": self._stats.to_dict(),
            }

            with open(self._stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return True

        except OSError:
            return False

    def get_stats(self) -> SessionStats:
        """
        Get current session statistics.

        Returns:
            Current SessionStats instance.
        """
        if self._stats is None:
            self._stats = SessionStats()
        return self._stats

    def record_game(self, is_win: bool, guesses_made: int) -> None:
        """
        Record a completed game.

        Args:
            is_win: Whether the game was won.
            guesses_made: Number of guesses made.
        """
        if self._stats is None:
            self._stats = SessionStats()
        self._stats.record_game(is_win, guesses_made)

    def get_display_stats(self) -> dict[str, Any]:
        """
        Get statistics formatted for display.

        Returns:
            Dictionary of formatted statistics.
        """
        stats = self.get_stats()
        return {
            "Games Played": stats.games_played,
            "Games Won": stats.games_won,
            "Games Lost": stats.games_lost,
            "Win Rate": f"{stats.get_win_rate():.1f}%",
            "Current Streak": stats.current_streak,
            "Best Streak": stats.best_streak,
            "Total Guesses": stats.total_guesses,
        }

    def reset_session(self) -> None:
        """Reset the current session statistics."""
        if self._stats is not None:
            self._stats.reset()

    def reset_all(self) -> bool:
        """
        Reset all statistics and clear the file.

        Returns:
            True if reset was successful.
        """
        self._stats = SessionStats()
        return self.save()

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._stats = None
        cls._stats_file = None
