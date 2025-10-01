"""
RacGoat Test Suite

Testing code like a goat climbs mountains - one step at a time! 🐐
"""

import pytest
from racgoat.utils import (
    goat_climb,
    raccoon_cache,
    goat_path,
    trash_panda_search,
    generate_ascii_art,
)


def test_racgoat_pun():
    """
    Test the fundamental truth of RacGoat.

    Trash panda meets cliff climber! 🦝🐐
    """
    assert "rac" + "goat" == "racgoat"  # The most important test!


def test_goat_climb_positive():
    """Test that goats can climb upward like the champions they are."""
    result = goat_climb(5)
    assert "5 levels" in result
    assert "baa-dass" in result


def test_goat_climb_negative():
    """Goats don't go backwards - they're too stubborn!"""
    result = goat_climb(-1)
    assert "backwards" in result.lower()


def test_goat_climb_zero():
    """Even goats need rest days."""
    result = goat_climb(0)
    assert "rest" in result.lower()


def test_goat_climb_epic():
    """Test for GOAT-level climbing achievements."""
    result = goat_climb(150)
    assert "GOAT" in result


def test_raccoon_cache_empty():
    """Test raccoon caching with an empty bin - so sad! 🦝"""
    result = raccoon_cache("shiny_object")
    assert "shiny_object" in result
    assert len(result) == 1


def test_raccoon_cache_existing():
    """Raccoons add to their hoard!"""
    trash_bin = ["pizza", "old_code"]
    result = raccoon_cache("new_bug", trash_bin)
    assert len(result) == 3
    assert "new_bug" in result


def test_raccoon_cache_duplicates():
    """Raccoons are clever - no duplicate hoarding!"""
    trash_bin = ["pizza"]
    result = raccoon_cache("pizza", trash_bin)
    assert len(result) == 1  # No duplicate!


def test_goat_path_single():
    """Test goat path with single segment."""
    result = goat_path("/home", "user")
    assert "/home" in result
    assert "user" in result


def test_goat_path_multiple():
    """Goats can climb multiple path segments!"""
    result = goat_path("/home", "user", "racgoat", "data")
    assert "user" in result
    assert "racgoat" in result
    assert "data" in result


def test_trash_panda_search_found():
    """Raccoons always find what they're looking for! 🦝"""
    assert trash_panda_search("Hello RacGoat World", "racgoat") is True


def test_trash_panda_search_not_found():
    """Even raccoons come up empty sometimes."""
    assert trash_panda_search("Hello World", "raccoon") is False


def test_trash_panda_search_case_insensitive():
    """Raccoons don't care about your capitalization!"""
    assert trash_panda_search("RACGOAT", "racgoat") is True
    assert trash_panda_search("racgoat", "RACGOAT") is True


def test_ascii_art_exists():
    """Make sure we have our beautiful ASCII art!"""
    art = generate_ascii_art()
    assert "RacGoat" in art
    assert "🦝" in art or "raccoon" in art.lower()
    assert "🐐" in art or "goat" in art.lower()


# Easter egg test - only true fans will find this! 🥚
def test_secret_truth():
    """
    The secret truth about RacGoat.

    If you're reading this, you're either:
    1. A dedicated code reviewer (bless you!)
    2. A curious raccoon digging through the codebase
    3. A goat who learned to read

    Either way, you're awesome! 🦝🐐
    """
    assert True  # The real treasure was the tests we wrote along the way


if __name__ == "__main__":
    # Run tests the goat way! 🐐
    pytest.main([__file__, "-v"])
