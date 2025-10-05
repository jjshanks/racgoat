"""
RacGoat Utility Functions

Helper functions that combine raccoon cleverness with goat determination!
"""

from typing import List, Optional


def goat_climb(height: int) -> str:
    """
    Simulate a goat climbing to new heights.

    This function is 'goat' to be great!

    Args:
        height: The number of levels to climb (must be positive, goats don't go backwards!)

    Returns:
        A motivational message about the climb

    Examples:
        >>> goat_climb(5)
        "Goat climbed 5 levels – baa-dass! 🐐"
    """
    if height < 0:
        return "Goats don't climb backwards! They're stubborn like that. 🐐"
    elif height == 0:
        return "Even goats need to rest sometimes. 😴"
    elif height > 100:
        return f"Goat climbed {height} levels – absolute GOAT status achieved! 🏔️🐐"
    else:
        return f"Goat climbed {height} levels – baa-dass! 🐐"


def raccoon_cache(item: str, trash_bin: Optional[List[str]] = None) -> List[str]:
    """
    Add items to the raccoon's cache (aka trash bin).

    Raccoons are nature's hoarders - they cache everything!

    Args:
        item: The item to cache
        trash_bin: The existing cache (defaults to empty list)

    Returns:
        Updated cache with the new item

    Note:
        This is basically a glorified list append, but with more raccoon energy! 🦝
    """
    if trash_bin is None:
        trash_bin = []

    # Raccoons are clever - they check for duplicates!
    if item not in trash_bin:
        trash_bin.append(item)

    return trash_bin


def generate_ascii_art() -> str:
    """
    Generate RacGoat ASCII art.

    Because every good CLI tool needs ASCII art! 🎨

    Returns:
        A string containing beautiful RacGoat ASCII art
    """
    art = r"""
    🦝 RacGoat 🐐

       ___
      /   \     Raccoon eyes
     | O O |    watching your code!
      \___/
       |||
      / | \

        /\        Goat horns
       /  \       ready to debug!
      |    |
     /|    |\
    (_|____|_)

    "Where trash pandas meet mountain climbers!"
    """
    return art


def goat_path(base_path: str, *segments: str) -> str:
    """
    Build a file path the goat way - one step at a time, up the mountain!

    This is like os.path.join but with more attitude. 🐐

    Args:
        base_path: The starting point (base of the mountain)
        *segments: Path segments to climb through

    Returns:
        A properly formatted path

    Example:
        >>> goat_path("/home", "user", "racgoat")
        "/home/user/racgoat"
    """
    import os

    # Goats take it one step at a time!
    full_path = base_path
    for segment in segments:
        full_path = os.path.join(full_path, segment)

    return full_path


def trash_panda_search(haystack: str, needle: str) -> bool:
    """
    Search for something like a raccoon searching through trash.

    Very thorough. Very persistent. Just like a real trash panda! 🦝

    Args:
        haystack: The text to search through
        needle: What to find

    Returns:
        True if found, False otherwise

    Note:
        This is literally just 'in' but raccoons make everything better!
    """
    # Raccoons are case-insensitive - they don't care about your conventions!
    return needle.lower() in haystack.lower()


def generate_goat_ascii_art() -> str:
    """
    Generate Mountain Goat ASCII art for GOAT mode.

    Because the GREATEST OF ALL TIME deserves epic ASCII! 🐐

    Returns:
        A string containing majestic mountain goat ASCII art
    """
    art = r"""
    🐐 GOAT MODE 🐐

         /\
        /  \
       /    \      The summit
      /______\     awaits!

        (\/)
       (o o)       Mountain goat
      /|   |\      climbing to
     (_|   |_)     greatness!
       || ||
       || ||
      _|| ||_

    "Baa-lieve in yourself! You're the GOAT! 🏔️"
    """
    return art
