"""
Unit tests for the word list manager module.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from hangman.words import (
    Difficulty,
    EmptyWordListError,
    WordEntry,
    WordListNotFoundError,
)


class TestWordEntry:
    """Tests for the WordEntry dataclass."""

    def test_word_entry_creation(self):
        """Test creating a WordEntry."""
        entry = WordEntry(
            word="Python",
            category="programming",
            difficulty=Difficulty.MEDIUM,
        )

        assert entry.word == "python"  # Normalized to lowercase
        assert entry.category == "programming"
        assert entry.difficulty == Difficulty.MEDIUM

    def test_word_entry_normalization(self):
        """Test that words are normalized."""
        entry = WordEntry(
            word="  PYTHON  ",
            category="programming",
            difficulty=Difficulty.MEDIUM,
        )

        assert entry.word == "python"


class TestWordListManager:
    """Tests for the WordListManager class."""

    def test_load_word_lists(self, word_list_manager):
        """Test loading word lists from the default directory."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        assert len(word_list_manager._words) > 0
        assert "animals" in word_list_manager._words

    def test_get_categories(self, word_list_manager):
        """Test getting available categories."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        categories = word_list_manager.get_categories()

        assert "animals" in categories
        assert "countries" in categories
        assert "fruits" in categories

    def test_get_difficulties(self, word_list_manager):
        """Test getting available difficulties."""
        difficulties = word_list_manager.get_difficulties()

        assert Difficulty.EASY in difficulties
        assert Difficulty.MEDIUM in difficulties
        assert Difficulty.HARD in difficulties

    def test_get_random_word(self, word_list_manager):
        """Test getting a random word."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        word = word_list_manager.get_random_word()

        assert isinstance(word, WordEntry)
        assert word.word.islower()
        assert word.word.isalpha()

    def test_get_random_word_filtered_category(self, word_list_manager):
        """Test getting a random word with category filter."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        word = word_list_manager.get_random_word(category="animals")

        assert word.category == "animals"

    def test_get_random_word_filtered_difficulty(self, word_list_manager):
        """Test getting a random word with difficulty filter."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        word = word_list_manager.get_random_word(difficulty=Difficulty.EASY)

        assert word.difficulty == Difficulty.EASY

    def test_get_random_word_filtered_both(self, word_list_manager):
        """Test getting a random word with both filters."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        word = word_list_manager.get_random_word(
            category="animals",
            difficulty=Difficulty.EASY,
        )

        assert word.category == "animals"
        assert word.difficulty == Difficulty.EASY

    def test_get_word_count(self, word_list_manager):
        """Test getting word count."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        total = word_list_manager.get_word_count()
        assert total > 0

        animals_count = word_list_manager.get_word_count(category="animals")
        assert animals_count > 0

        easy_count = word_list_manager.get_word_count(difficulty=Difficulty.EASY)
        assert easy_count > 0

    def test_load_nonexistent_directory(self, word_list_manager):
        """Test loading from a nonexistent directory."""
        with pytest.raises(WordListNotFoundError):
            word_list_manager.load_word_lists(Path("/nonexistent/path"))

    def test_empty_word_list(self, word_list_manager):
        """Test handling of empty word list directory.

        Note: BUG FIX (hangman-kgf) - Now raises EmptyWordList when JSON files
        have empty categories, not just when no JSON files exist.
        """
        with TemporaryDirectory() as tmpdir:
            # Create an empty JSON file
            empty_file = Path(tmpdir) / "empty.json"
            with open(empty_file, "w") as f:
                json.dump({"categories": {}}, f)

            # Should now raise EmptyWordList when files have empty categories
            with pytest.raises(EmptyWordListError):
                word_list_manager.load_word_lists(Path(tmpdir))

    def test_reload(self, word_list_manager):
        """Test reloading word lists."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        # Modify the internal state
        word_list_manager._words = {}

        # Reload should restore the words
        word_list_manager.reload()

        assert len(word_list_manager._words) > 0

    def test_reset(self, word_list_manager):
        """Test resetting the manager."""
        word_lists_path = Path(__file__).parent.parent / "data" / "words"
        word_list_manager.load_word_lists(word_lists_path)

        word_list_manager.reset()

        assert len(word_list_manager._words) == 0
        assert len(word_list_manager._categories) == 0


class TestDifficulty:
    """Tests for the Difficulty enum."""

    def test_difficulty_values(self):
        """Test difficulty enum values."""
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.MEDIUM.value == "medium"
        assert Difficulty.HARD.value == "hard"

    def test_difficulty_from_string(self):
        """Test creating Difficulty from string."""
        assert Difficulty("easy") == Difficulty.EASY
        assert Difficulty("medium") == Difficulty.MEDIUM
        assert Difficulty("hard") == Difficulty.HARD
