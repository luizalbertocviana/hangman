"""
Pytest fixtures for Hangman CLI tests.
"""

import pytest

from hangman.config import Config, ConfigurationManager
from hangman.game import GameEngine, GameState
from hangman.input_handler import InputHandler
from hangman.renderer import UIRenderer
from hangman.stats import SessionStats, StatsManager
from hangman.words import Difficulty, WordEntry, WordListManager


@pytest.fixture
def game_engine():
    """Create a fresh GameEngine instance."""
    engine = GameEngine(max_incorrect_guesses=6)
    yield engine
    engine.reset()


@pytest.fixture
def game_state():
    """Create a fresh GameState instance."""
    return GameState()


@pytest.fixture
def word_entry():
    """Create a sample WordEntry for testing."""
    return WordEntry(word="python", category="programming", difficulty=Difficulty.MEDIUM)


@pytest.fixture
def word_list_manager():
    """Create a WordListManager instance."""
    manager = WordListManager()
    yield manager
    manager.reset()


@pytest.fixture
def input_handler():
    """Create a fresh InputHandler instance."""
    handler = InputHandler()
    yield handler
    handler.reset()


@pytest.fixture
def renderer():
    """Create a UIRenderer instance with colors disabled."""
    return UIRenderer(enable_colors=False)


@pytest.fixture
def session_stats():
    """Create a fresh SessionStats instance."""
    return SessionStats()


@pytest.fixture
def config():
    """Create a sample Config instance."""
    return Config()


@pytest.fixture
def config_manager():
    """Create a ConfigurationManager instance."""
    manager = ConfigurationManager()
    yield manager
    ConfigurationManager.reset_instance()


@pytest.fixture
def stats_manager():
    """Create a StatsManager instance."""
    manager = StatsManager()
    yield manager
    StatsManager.reset_instance()
