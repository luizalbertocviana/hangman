"""
Configuration manager module for Hangman CLI.

Handles loading, validating, and providing application configuration settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""

    pass


@dataclass
class GameConfig:
    """Game-specific configuration settings."""

    max_incorrect_guesses: int = 6


@dataclass
class PathConfig:
    """Path configuration settings."""

    word_lists: str = "./data/words"
    stats_file: str = "~/.hangman/stats.json"


@dataclass
class DisplayConfig:
    """Display configuration settings."""

    enable_colors: bool = True
    min_terminal_width: int = 80
    min_terminal_height: int = 24


@dataclass
class Config:
    """
    Application configuration.

    Aggregates all configuration sections into a single object.
    """

    game: GameConfig = field(default_factory=GameConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    language: str = "en"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Create a Config instance from a dictionary."""
        config = cls()

        if "game" in data:
            game_data = data["game"]
            config.game = GameConfig(
                max_incorrect_guesses=game_data.get(
                    "max_incorrect_guesses", GameConfig.max_incorrect_guesses
                )
            )

        if "paths" in data:
            paths_data = data["paths"]
            config.paths = PathConfig(
                word_lists=paths_data.get("word_lists", PathConfig.word_lists),
                stats_file=paths_data.get("stats_file", PathConfig.stats_file),
            )

        if "display" in data:
            display_data = data["display"]
            config.display = DisplayConfig(
                enable_colors=display_data.get(
                    "enable_colors", DisplayConfig.enable_colors
                ),
                min_terminal_width=display_data.get(
                    "min_terminal_width", DisplayConfig.min_terminal_width
                ),
                min_terminal_height=display_data.get(
                    "min_terminal_height", DisplayConfig.min_terminal_height
                ),
            )

        if "language" in data:
            config.language = data["language"]

        return config


class ConfigurationManager:
    """
    Singleton manager for application configuration.

    Loads configuration from YAML files and provides validated settings.
    """

    _instance: ConfigurationManager | None = None
    _config: Config | None = None

    def __new__(cls) -> ConfigurationManager:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if not hasattr(self, "_initialized"):
            self._config = None
            self._initialized = True

    def load(self, config_path: str | None = None) -> Config:
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to the configuration file. If None, uses default.

        Returns:
            Config: The loaded configuration object.

        Raises:
            ConfigurationError: If the configuration file cannot be loaded or is invalid.
        """
        if config_path is None:
            config_path = self._get_default_config_path()

        try:
            path = Path(config_path).expanduser()
            if not path.exists():
                # Use defaults if config file doesn't exist
                self._config = Config()
                return self._config

            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            self._config = Config.from_dict(data)
            self._validate_config()
            return self._config

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}") from e
        except OSError as e:
            raise ConfigurationError(f"Cannot read config file: {e}") from e

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Check for config in project root
        project_root = Path(__file__).parent.parent.parent
        project_config = project_root / "config" / "default.yaml"

        if project_config.exists():
            return str(project_config)

        # Fallback to user config
        return "~/.hangman/config.yaml"

    def _validate_config(self) -> None:
        """
        Validate the loaded configuration.

        Raises:
            ConfigurationError: If configuration values are invalid.
        """
        if self._config is None:
            raise ConfigurationError("No configuration loaded")

        if self._config.game.max_incorrect_guesses < 1:
            raise ConfigurationError("max_incorrect_guesses must be at least 1")

        if self._config.display.min_terminal_width < 40:
            raise ConfigurationError("min_terminal_width must be at least 40")

        if self._config.display.min_terminal_height < 10:
            raise ConfigurationError("min_terminal_height must be at least 10")

    def get_config(self) -> Config:
        """
        Get the current configuration.

        Returns:
            Config: The current configuration object.

        Raises:
            ConfigurationError: If no configuration is loaded.
        """
        if self._config is None:
            self._config = Config()
        return self._config

    def get_word_lists_path(self) -> Path:
        """
        Get the resolved path to word lists directory.

        Returns:
            Path: Absolute path to word lists directory.
        """
        config = self.get_config()
        return Path(config.paths.word_lists).expanduser().resolve()

    def get_stats_file_path(self) -> Path:
        """
        Get the resolved path to stats file.

        Returns:
            Path: Absolute path to stats file.
        """
        config = self.get_config()
        return Path(config.paths.stats_file).expanduser().resolve()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = Config()

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._config = None
