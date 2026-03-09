"""
Unit tests for the configuration manager module.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from hangman.config import (
    Config,
    GameConfig,
    PathConfig,
    DisplayConfig,
    ConfigurationManager,
    ConfigurationError,
)


class TestConfigDataclasses:
    """Tests for configuration dataclasses."""

    def test_game_config_defaults(self):
        """Test GameConfig default values."""
        config = GameConfig()
        assert config.max_incorrect_guesses == 6

    def test_path_config_defaults(self):
        """Test PathConfig default values."""
        config = PathConfig()
        assert config.word_lists == "./data/words"
        assert config.stats_file == "~/.hangman/stats.json"

    def test_display_config_defaults(self):
        """Test DisplayConfig default values."""
        config = DisplayConfig()
        assert config.enable_colors is True
        assert config.min_terminal_width == 80
        assert config.min_terminal_height == 24

    def test_config_defaults(self):
        """Test Config default values."""
        config = Config()
        assert config.game.max_incorrect_guesses == 6
        assert config.language == "en"

    def test_config_from_dict_full(self):
        """Test creating Config from full dictionary."""
        data = {
            "game": {"max_incorrect_guesses": 8},
            "paths": {
                "word_lists": "/custom/words",
                "stats_file": "/custom/stats.json",
            },
            "display": {
                "enable_colors": False,
                "min_terminal_width": 100,
                "min_terminal_height": 30,
            },
            "language": "es",
        }

        config = Config.from_dict(data)

        assert config.game.max_incorrect_guesses == 8
        assert config.paths.word_lists == "/custom/words"
        assert config.display.enable_colors is False
        assert config.language == "es"

    def test_config_from_dict_partial(self):
        """Test creating Config from partial dictionary."""
        data = {
            "game": {"max_incorrect_guesses": 10},
        }

        config = Config.from_dict(data)

        assert config.game.max_incorrect_guesses == 10
        # Other values should be defaults
        assert config.language == "en"
        assert config.display.enable_colors is True

    def test_config_from_dict_empty(self):
        """Test creating Config from empty dictionary."""
        config = Config.from_dict({})

        assert config.game.max_incorrect_guesses == 6
        assert config.language == "en"


class TestConfigurationManager:
    """Tests for the ConfigurationManager class."""

    def test_singleton_instance(self):
        """Test that ConfigurationManager is a singleton."""
        manager1 = ConfigurationManager()
        manager2 = ConfigurationManager()

        assert manager1 is manager2

        ConfigurationManager.reset_instance()

    def test_load_default_config(self):
        """Test loading default configuration."""
        manager = ConfigurationManager()
        config = manager.load()

        assert isinstance(config, Config)
        assert config.game.max_incorrect_guesses == 6

        ConfigurationManager.reset_instance()

    def test_load_from_file(self):
        """Test loading configuration from a YAML file."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""
game:
  max_incorrect_guesses: 8

paths:
  word_lists: "/test/words"

display:
  enable_colors: false

language: "fr"
""")

            manager = ConfigurationManager()
            config = manager.load(str(config_file))

            assert config.game.max_incorrect_guesses == 8
            assert config.paths.word_lists == "/test/words"
            assert config.display.enable_colors is False
            assert config.language == "fr"

            ConfigurationManager.reset_instance()

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file uses defaults."""
        manager = ConfigurationManager()
        config = manager.load("/nonexistent/config.yaml")

        assert config.game.max_incorrect_guesses == 6

        ConfigurationManager.reset_instance()

    def test_get_word_lists_path(self):
        """Test getting resolved word lists path."""
        manager = ConfigurationManager()
        manager.load()

        path = manager.get_word_lists_path()
        assert isinstance(path, Path)

        ConfigurationManager.reset_instance()

    def test_get_stats_file_path(self):
        """Test getting resolved stats file path."""
        manager = ConfigurationManager()
        manager.load()

        path = manager.get_stats_file_path()
        assert isinstance(path, Path)

        ConfigurationManager.reset_instance()

    def test_reset(self):
        """Test resetting configuration."""
        manager = ConfigurationManager()
        manager.load()

        manager._config = Config.from_dict({"game": {"max_incorrect_guesses": 10}})

        manager.reset()

        assert manager.get_config().game.max_incorrect_guesses == 6

        ConfigurationManager.reset_instance()

    def test_validate_invalid_max_guesses(self):
        """Test validation of invalid max_incorrect_guesses."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("""
game:
  max_incorrect_guesses: 0
""")

            manager = ConfigurationManager()

            with pytest.raises(ConfigurationError):
                manager.load(str(config_file))

            ConfigurationManager.reset_instance()


class TestConfigurationValidation:
    """Tests for configuration validation."""

    def test_valid_config(self):
        """Test that valid config passes validation."""
        config = Config()
        manager = ConfigurationManager()
        manager._config = config

        # Should not raise
        manager._validate_config()

        ConfigurationManager.reset_instance()

    def test_min_terminal_width_validation(self):
        """Test validation of min_terminal_width."""
        config = Config.from_dict({"display": {"min_terminal_width": 30}})
        manager = ConfigurationManager()
        manager._config = config

        with pytest.raises(ConfigurationError):
            manager._validate_config()

        ConfigurationManager.reset_instance()

    def test_min_terminal_height_validation(self):
        """Test validation of min_terminal_height."""
        config = Config.from_dict({"display": {"min_terminal_height": 5}})
        manager = ConfigurationManager()
        manager._config = config

        with pytest.raises(ConfigurationError):
            manager._validate_config()

        ConfigurationManager.reset_instance()
