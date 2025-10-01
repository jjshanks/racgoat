"""Unit tests for DiffSummary entity.

Tests validate:
- is_empty property for no files
- files list management
- format_output() method
- duplicate file path handling
"""

import pytest
from racgoat.parser.models import DiffFile, DiffSummary


def test_diff_summary_empty():
    """Validate is_empty=True for no files."""
    summary = DiffSummary(files=[])
    assert summary.is_empty is True
    assert summary.total_files == 0


def test_diff_summary_not_empty():
    """Validate is_empty=False when files present."""
    file1 = DiffFile(file_path="src/main.py", added_lines=10, removed_lines=5)
    summary = DiffSummary(files=[file1])
    assert summary.is_empty is False
    assert summary.total_files == 1


def test_diff_summary_add_file():
    """Validate files list grows when adding files."""
    summary = DiffSummary(files=[])

    file1 = DiffFile(file_path="src/main.py", added_lines=10, removed_lines=5)
    summary.add_file(file1)

    assert len(summary.files) == 1
    assert summary.total_files == 1
    assert summary.is_empty is False

    file2 = DiffFile(file_path="tests/test_main.py", added_lines=20, removed_lines=0)
    summary.add_file(file2)

    assert len(summary.files) == 2
    assert summary.total_files == 2


def test_diff_summary_format_output():
    """Validate output format: 'path: +X -Y\\n'."""
    file1 = DiffFile(file_path="src/main.py", added_lines=15, removed_lines=3)
    file2 = DiffFile(file_path="tests/test_parser.py", added_lines=42, removed_lines=0)
    file3 = DiffFile(file_path="racgoat/utils.py", added_lines=8, removed_lines=12)

    summary = DiffSummary(files=[file1, file2, file3])
    output = summary.format_output()

    expected = """src/main.py: +15 -3
tests/test_parser.py: +42 -0
racgoat/utils.py: +8 -12
"""

    assert output == expected


def test_diff_summary_format_output_single_file():
    """Validate format for single file (includes trailing newline per contract)."""
    file1 = DiffFile(file_path="src/main.py", added_lines=10, removed_lines=5)
    summary = DiffSummary(files=[file1])

    output = summary.format_output()
    assert output == "src/main.py: +10 -5\n"
    assert output.endswith("\n") is True  # format_output includes trailing newline per contract


def test_diff_summary_format_output_empty():
    """Validate format_output for empty summary."""
    summary = DiffSummary(files=[])
    output = summary.format_output()
    assert output == ""


def test_diff_summary_format_output_special_chars():
    """Validate file paths with special characters preserved."""
    file1 = DiffFile(file_path="path with spaces/file.py", added_lines=5, removed_lines=2)
    file2 = DiffFile(file_path="src/__init__.py", added_lines=3, removed_lines=1)

    summary = DiffSummary(files=[file1, file2])
    output = summary.format_output()

    assert "path with spaces/file.py: +5 -2" in output
    assert "src/__init__.py: +3 -1" in output


def test_diff_summary_format_output_zero_counts():
    """Validate +0 -0 allowed in format (for new/deleted files)."""
    file1 = DiffFile(file_path="new_file.py", added_lines=10, removed_lines=0)
    file2 = DiffFile(file_path="deleted_file.py", added_lines=0, removed_lines=8)

    summary = DiffSummary(files=[file1, file2])
    output = summary.format_output()

    assert "new_file.py: +10 -0" in output
    assert "deleted_file.py: +0 -8" in output


def test_diff_summary_no_duplicates():
    """Validate same file path doesn't create duplicates."""
    # Note: This test validates the expected behavior - DiffSummary should
    # handle duplicate file paths by merging counts or preventing duplicates.
    # Implementation choice: we'll merge counts when same path appears.

    summary = DiffSummary(files=[])

    file1 = DiffFile(file_path="src/main.py", added_lines=10, removed_lines=5)
    summary.add_file(file1)

    # Same file appears again (e.g., multiple hunks in diff)
    file2 = DiffFile(file_path="src/main.py", added_lines=5, removed_lines=3)
    summary.add_file(file2)

    # Should have merged counts, not created duplicate entries
    assert summary.total_files == 1
    assert summary.files[0].file_path == "src/main.py"
    assert summary.files[0].added_lines == 15  # 10 + 5
    assert summary.files[0].removed_lines == 8  # 5 + 3


def test_diff_summary_order_preserved():
    """Validate files appear in order they were added."""
    summary = DiffSummary(files=[])

    file1 = DiffFile(file_path="zzz_last.py", added_lines=1, removed_lines=0)
    file2 = DiffFile(file_path="aaa_first.py", added_lines=2, removed_lines=0)
    file3 = DiffFile(file_path="mmm_middle.py", added_lines=3, removed_lines=0)

    summary.add_file(file1)
    summary.add_file(file2)
    summary.add_file(file3)

    # Should maintain insertion order, not alphabetical
    assert summary.files[0].file_path == "zzz_last.py"
    assert summary.files[1].file_path == "aaa_first.py"
    assert summary.files[2].file_path == "mmm_middle.py"
