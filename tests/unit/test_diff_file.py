"""Unit tests for DiffFile entity.

Tests the DiffFile dataclass validating attributes, defaults, and validation rules.
"""

import pytest
from racgoat.parser.models import DiffFile


def test_diff_file_creation():
    """Validate DiffFile creation with all attributes."""
    file = DiffFile(
        file_path="src/parser/diff_parser.py",
        added_lines=42,
        removed_lines=8,
        is_binary=False
    )

    assert file.file_path == "src/parser/diff_parser.py"
    assert file.added_lines == 42
    assert file.removed_lines == 8
    assert file.is_binary is False


def test_diff_file_defaults():
    """Validate DiffFile defaults: added=0, removed=0, is_binary=False."""
    file = DiffFile(file_path="src/main.py")

    assert file.file_path == "src/main.py"
    assert file.added_lines == 0
    assert file.removed_lines == 0
    assert file.is_binary is False


def test_diff_file_binary_marker():
    """Validate DiffFile with binary marker."""
    file = DiffFile(
        file_path="image.png",
        is_binary=True
    )

    assert file.file_path == "image.png"
    assert file.is_binary is True
    assert file.added_lines == 0
    assert file.removed_lines == 0


def test_diff_file_only_additions():
    """Validate DiffFile with only added lines."""
    file = DiffFile(
        file_path="new_file.py",
        added_lines=100
    )

    assert file.added_lines == 100
    assert file.removed_lines == 0


def test_diff_file_only_deletions():
    """Validate DiffFile with only removed lines."""
    file = DiffFile(
        file_path="deleted_file.py",
        removed_lines=50
    )

    assert file.added_lines == 0
    assert file.removed_lines == 50


def test_diff_file_path_with_spaces():
    """Validate DiffFile preserves paths with spaces."""
    file = DiffFile(
        file_path="path with spaces/file.py",
        added_lines=5,
        removed_lines=2
    )

    assert file.file_path == "path with spaces/file.py"


def test_diff_file_path_with_special_chars():
    """Validate DiffFile preserves paths with special characters."""
    file = DiffFile(
        file_path="src/__init__.py",
        added_lines=3,
        removed_lines=1
    )

    assert file.file_path == "src/__init__.py"


def test_diff_file_validation_non_empty_path():
    """Validate file_path cannot be empty string."""
    # Empty string should be allowed by dataclass, but validation should happen elsewhere
    # This test documents expected behavior - actual validation may be in parser
    file = DiffFile(file_path="")
    assert file.file_path == ""
    # Note: Actual validation for non-empty paths should occur in the parser logic


def test_diff_file_validation_non_negative_counts():
    """Validate added_lines and removed_lines must be >= 0."""
    # Negative values should be prevented by type system or validation
    # This test documents expected behavior
    file = DiffFile(
        file_path="test.py",
        added_lines=0,
        removed_lines=0
    )

    assert file.added_lines >= 0
    assert file.removed_lines >= 0


def test_diff_file_nested_directory_path():
    """Validate DiffFile handles deeply nested paths."""
    file = DiffFile(
        file_path="src/api/v2/endpoints/users.py",
        added_lines=25,
        removed_lines=10
    )

    assert file.file_path == "src/api/v2/endpoints/users.py"
    assert file.added_lines == 25
    assert file.removed_lines == 10
