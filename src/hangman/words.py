"""
Word list manager module for Hangman CLI.

Handles loading, filtering, and providing words from word list files.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class Difficulty(Enum):
    """Word difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class WordEntry:
    """
    Represents a word in the word list.

    Attributes:
        word: The word itself (lowercase, alphabetic only).
        category: Category the word belongs to.
        difficulty: Difficulty level of the word.
    """

    word: str
    category: str
    difficulty: Difficulty

    def __post_init__(self) -> None:
        """Normalize the word after initialization."""
        self.word = self.word.lower().strip()


class WordListError(Exception):
    """Base exception for word list errors."""

    pass


class WordListNotFound(WordListError):
    """Exception raised when word list file is not found."""

    pass


class EmptyWordList(WordListError):
    """Exception raised when word list is empty."""

    pass


class WordListManager:
    """
    Manages word lists for the Hangman game.

    Loads words from JSON files and provides filtered access
    by category and difficulty.
    """

    def __init__(self, word_lists_path: Optional[Path] = None) -> None:
        """
        Initialize the word list manager.

        Args:
            word_lists_path: Path to the directory containing word list files.
        """
        self._word_lists_path = word_lists_path
        self._words: Dict[str, List[WordEntry]] = {}
        self._categories: Set[str] = set()
        self._loaded = False

    def load_word_lists(self, path: Optional[Path] = None) -> Dict[str, List[WordEntry]]:
        """
        Load word lists from JSON files.

        Args:
            path: Optional path to word lists directory. Uses stored path if not provided.

        Returns:
            Dictionary mapping category names to lists of WordEntry objects.

        Raises:
            WordListNotFound: If the word lists directory or files are not found.
            WordListError: If word list files are invalid or empty.
        """
        if path is not None:
            self._word_lists_path = path

        if self._word_lists_path is None:
            self._word_lists_path = Path(__file__).parent.parent / "data" / "words"

        word_lists_dir = Path(self._word_lists_path)

        if not word_lists_dir.exists():
            raise WordListNotFound(f"Word lists directory not found: {word_lists_dir}")

        if not word_lists_dir.is_dir():
            raise WordListNotFound(f"Path is not a directory: {word_lists_dir}")

        self._words = {}
        self._categories = set()

        # Load all JSON files in the directory
        json_files = list(word_lists_dir.glob("*.json"))

        if not json_files:
            raise EmptyWordList("No word list files found in directory")

        for json_file in json_files:
            self._load_word_file(json_file)

        self._loaded = True
        return self._words

    def _load_word_file(self, file_path: Path) -> None:
        """
        Load a single word list file.

        Args:
            file_path: Path to the JSON file.

        Raises:
            WordListError: If the file cannot be parsed or is invalid.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise WordListError(f"Invalid JSON in {file_path}: {e}") from e
        except IOError as e:
            raise WordListError(f"Cannot read {file_path}: {e}") from e

        if not isinstance(data, dict) or "categories" not in data:
            raise WordListError(f"Invalid word list format in {file_path}")

        categories = data.get("categories", {})

        for category_name, difficulties in categories.items():
            if not isinstance(difficulties, dict):
                continue

            self._categories.add(category_name)

            if category_name not in self._words:
                self._words[category_name] = []

            for difficulty_name, words in difficulties.items():
                if not isinstance(words, list):
                    continue

                try:
                    difficulty = Difficulty(difficulty_name.lower())
                except ValueError:
                    continue

                for word in words:
                    if isinstance(word, str) and word.strip():
                        entry = WordEntry(
                            word=word.strip(),
                            category=category_name,
                            difficulty=difficulty,
                        )
                        # Avoid duplicates
                        if entry.word not in [w.word for w in self._words[category_name]]:
                            self._words[category_name].append(entry)

    def get_random_word(
        self,
        category: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
    ) -> WordEntry:
        """
        Get a random word, optionally filtered by category and difficulty.

        Args:
            category: Optional category to filter by.
            difficulty: Optional difficulty level to filter by.

        Returns:
            A randomly selected WordEntry.

        Raises:
            WordListError: If no words match the criteria or word lists not loaded.
        """
        if not self._loaded:
            self.load_word_lists()

        candidates = self._get_filtered_words(category, difficulty)

        if not candidates:
            filter_desc = []
            if category:
                filter_desc.append(f"category='{category}'")
            if difficulty:
                filter_desc.append(f"difficulty='{difficulty.value}'")
            raise EmptyWordList(
                f"No words available for filters: {', '.join(filter_desc)}"
            )

        return random.choice(candidates)

    def _get_filtered_words(
        self,
        category: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
    ) -> List[WordEntry]:
        """
        Get words filtered by category and difficulty.

        Args:
            category: Optional category filter.
            difficulty: Optional difficulty filter.

        Returns:
            List of matching WordEntry objects.
        """
        if category is None and difficulty is None:
            # Return all words
            all_words: List[WordEntry] = []
            for words in self._words.values():
                all_words.extend(words)
            return all_words

        candidates: List[WordEntry] = []

        # Determine which categories to search
        categories_to_search: List[str] = []
        if category is None:
            categories_to_search = list(self._words.keys())
        elif category in self._words:
            categories_to_search = [category]

        for cat in categories_to_search:
            for word_entry in self._words[cat]:
                if difficulty is None or word_entry.difficulty == difficulty:
                    candidates.append(word_entry)

        return candidates

    def get_categories(self) -> List[str]:
        """
        Get list of available categories.

        Returns:
            List of category names.
        """
        if not self._loaded:
            self.load_word_lists()
        return sorted(list(self._categories))

    def get_difficulties(self) -> List[Difficulty]:
        """
        Get list of available difficulty levels.

        Returns:
            List of Difficulty enum values.
        """
        return list(Difficulty)

    def get_word_count(
        self,
        category: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
    ) -> int:
        """
        Get count of words matching filters.

        Args:
            category: Optional category filter.
            difficulty: Optional difficulty filter.

        Returns:
            Number of matching words.
        """
        return len(self._get_filtered_words(category, difficulty))

    def reload(self) -> None:
        """Reload word lists from disk."""
        self._loaded = False
        self.load_word_lists()

    def reset(self) -> None:
        """Reset the manager state."""
        self._words = {}
        self._categories = set()
        self._loaded = False
