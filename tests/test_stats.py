"""
Unit tests for the statistics module.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from hangman.stats import SessionStats, StatsManager


class TestSessionStats:
    """Tests for the SessionStats dataclass."""

    def test_initial_stats(self, session_stats):
        """Test initial statistics values."""
        assert session_stats.games_played == 0
        assert session_stats.games_won == 0
        assert session_stats.games_lost == 0
        assert session_stats.current_streak == 0
        assert session_stats.best_streak == 0
        assert session_stats.total_guesses == 0

    def test_record_game_win(self, session_stats):
        """Test recording a win."""
        session_stats.record_game(is_win=True, guesses_made=5)

        assert session_stats.games_played == 1
        assert session_stats.games_won == 1
        assert session_stats.current_streak == 1
        assert session_stats.best_streak == 1
        assert session_stats.total_guesses == 5

    def test_record_game_loss(self, session_stats):
        """Test recording a loss."""
        session_stats.record_game(is_win=False, guesses_made=6)

        assert session_stats.games_played == 1
        assert session_stats.games_lost == 1
        assert session_stats.current_streak == 0
        assert session_stats.total_guesses == 6

    def test_win_streak(self, session_stats):
        """Test win streak tracking."""
        session_stats.record_game(is_win=True, guesses_made=5)
        session_stats.record_game(is_win=True, guesses_made=4)
        session_stats.record_game(is_win=True, guesses_made=6)

        assert session_stats.current_streak == 3
        assert session_stats.best_streak == 3

    def test_streak_reset_on_loss(self, session_stats):
        """Test that streak resets on loss."""
        session_stats.record_game(is_win=True, guesses_made=5)
        session_stats.record_game(is_win=True, guesses_made=4)
        session_stats.record_game(is_win=False, guesses_made=6)

        assert session_stats.current_streak == 0
        assert session_stats.best_streak == 2  # Best streak preserved

    def test_best_streak_preserved(self, session_stats):
        """Test that best streak is preserved across sessions."""
        session_stats.record_game(is_win=True, guesses_made=5)
        session_stats.record_game(is_win=True, guesses_made=4)
        session_stats.record_game(is_win=True, guesses_made=3)
        session_stats.record_game(is_win=False, guesses_made=6)
        session_stats.record_game(is_win=True, guesses_made=5)

        assert session_stats.current_streak == 1
        assert session_stats.best_streak == 3

    def test_get_win_rate(self, session_stats):
        """Test win rate calculation."""
        assert session_stats.get_win_rate() == 0.0

        session_stats.record_game(is_win=True, guesses_made=5)
        assert session_stats.get_win_rate() == 100.0

        session_stats.record_game(is_win=False, guesses_made=6)
        assert session_stats.get_win_rate() == 50.0

        session_stats.record_game(is_win=False, guesses_made=6)
        assert session_stats.get_win_rate() == pytest.approx(33.33, rel=0.1)

    def test_to_dict(self, session_stats):
        """Test converting stats to dictionary."""
        session_stats.record_game(is_win=True, guesses_made=5)

        data = session_stats.to_dict()

        assert data["games_played"] == 1
        assert data["games_won"] == 1
        assert "start_time" in data
        assert "last_updated" in data

    def test_from_dict(self):
        """Test creating stats from dictionary."""
        data = {
            "games_played": 10,
            "games_won": 7,
            "games_lost": 3,
            "current_streak": 2,
            "best_streak": 5,
            "total_guesses": 50,
        }

        stats = SessionStats.from_dict(data)

        assert stats.games_played == 10
        assert stats.games_won == 7
        assert stats.best_streak == 5

    def test_from_dict_with_timestamps(self):
        """Test creating stats with timestamps."""
        now = datetime.now().isoformat()
        data = {
            "games_played": 5,
            "start_time": now,
            "last_updated": now,
        }

        stats = SessionStats.from_dict(data)

        assert stats.games_played == 5
        assert isinstance(stats.start_time, datetime)

    def test_from_dict_invalid_timestamp(self):
        """Test handling of invalid timestamps."""
        data = {
            "games_played": 5,
            "start_time": "invalid-date",
        }

        stats = SessionStats.from_dict(data)

        assert stats.games_played == 5
        assert isinstance(stats.start_time, datetime)

    def test_reset(self, session_stats):
        """Test resetting statistics."""
        session_stats.record_game(is_win=True, guesses_made=5)
        session_stats.record_game(is_win=True, guesses_made=4)

        session_stats.reset()

        assert session_stats.games_played == 0
        assert session_stats.current_streak == 0


class TestStatsManager:
    """Tests for the StatsManager class."""

    def test_singleton_instance(self):
        """Test that StatsManager is a singleton."""
        manager1 = StatsManager()
        manager2 = StatsManager()

        assert manager1 is manager2

        StatsManager.reset_instance()

    def test_initialize_new_manager(self):
        """Test initializing a new manager."""
        manager = StatsManager()
        stats = manager.initialize()

        assert isinstance(stats, SessionStats)

        StatsManager.reset_instance()

    def test_save_and_load(self):
        """Test saving and loading stats."""
        with TemporaryDirectory() as tmpdir:
            stats_file = Path(tmpdir) / "stats.json"

            manager = StatsManager()
            manager.initialize(stats_file)

            # Record some games
            manager.record_game(is_win=True, guesses_made=5)
            manager.record_game(is_win=False, guesses_made=6)

            # Save
            assert manager.save() is True

            # Create new manager instance
            StatsManager.reset_instance()
            manager2 = StatsManager()
            manager2.initialize(stats_file)

            stats = manager2.get_stats()

            assert stats.games_played == 2
            assert stats.games_won == 1

            StatsManager.reset_instance()

    def test_get_display_stats(self):
        """Test getting formatted display stats."""
        with TemporaryDirectory() as tmpdir:
            stats_file = Path(tmpdir) / "stats.json"

            manager = StatsManager()
            manager.initialize(stats_file)

            manager.record_game(is_win=True, guesses_made=5)
            manager.record_game(is_win=True, guesses_made=4)

            display = manager.get_display_stats()

            assert "Games Played" in display
            assert display["Games Played"] == 2
            assert "Win Rate" in display

            StatsManager.reset_instance()

    def test_reset_session(self):
        """Test resetting session stats."""
        manager = StatsManager()
        manager.initialize()

        manager.record_game(is_win=True, guesses_made=5)

        manager.reset_session()

        stats = manager.get_stats()
        assert stats.games_played == 0

        StatsManager.reset_instance()

    def test_corrupted_stats_file(self):
        """Test handling of corrupted stats file."""
        with TemporaryDirectory() as tmpdir:
            stats_file = Path(tmpdir) / "stats.json"

            # Write corrupted data
            with open(stats_file, "w") as f:
                f.write("not valid json {{{")

            manager = StatsManager()
            stats = manager.initialize(stats_file)

            # Should return new stats, not crash
            assert isinstance(stats, SessionStats)
            assert stats.games_played == 0

            StatsManager.reset_instance()
