"""Contract tests for error handling and malformed diff parsing (Milestone 6).

These tests validate the parser's ability to handle malformed hunks and
enforce size limits, per parser-contracts.md.
"""

import pytest

from racgoat.parser.diff_parser import DiffParser
from racgoat.parser.models import DiffHunk, DiffFile, DiffSummary
from racgoat.exceptions import DiffTooLargeError, MalformedHunkError
from textual.widgets import Static


# T008: Contract test - Invalid hunk header detection


def test_invalid_hunk_header():
    """Test that invalid hunk headers are detected and marked as malformed.

    When the goat encounters a rocky cliff it can't climb, it remembers
    the path for later!

    Contract: parser-contracts.md Scenario 1
    """
    diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +10 @@
 context line
"""

    parser = DiffParser()
    summary = parser.parse(diff_text)

    # Should parse file but hunk should be malformed
    assert len(summary.files) == 1
    file = summary.files[0]

    assert file.file_path == "test.py"
    assert file.has_malformed_hunks is True

    # Should have one malformed hunk
    assert len(file.hunks) == 1
    hunk = file.hunks[0]

    assert hunk.is_malformed is True
    assert hunk.raw_text is not None
    assert "10 @@" in hunk.raw_text  # Malformed header preserved
    assert hunk.parse_error == "Invalid header format"


# T009: Contract test - Mismatched line counts


def test_mismatched_line_counts():
    """Test that hunks with mismatched line counts are marked as malformed.

    The raccoon counts its treasures carefully - if the count is off,
    something's not right!

    Contract: parser-contracts.md Scenario 2
    """
    diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
-old line 1
+new line 1
-old line 2
"""

    parser = DiffParser()
    summary = parser.parse(diff_text)

    assert len(summary.files) == 1
    file = summary.files[0]

    assert file.has_malformed_hunks is True
    assert len(file.hunks) == 1

    hunk = file.hunks[0]
    assert hunk.is_malformed is True
    assert hunk.raw_text is not None
    assert hunk.parse_error == "Mismatched line count"


# T010: Contract test - Mixed valid and malformed hunks


def test_mixed_hunks():
    """Test that files can contain both valid and malformed hunks.

    Some cliffs are easy, some are treacherous - the goat maps them all!

    Contract: parser-contracts.md Scenario 3
    """
    diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,2 @@
-old
+new

@@ invalid @@
broken content

@@ -5,1 +5,1 @@
-last
+change
"""

    parser = DiffParser()
    summary = parser.parse(diff_text)

    assert len(summary.files) == 1
    file = summary.files[0]

    assert file.has_malformed_hunks is True
    assert len(file.hunks) == 3

    # First hunk should be valid
    assert file.hunks[0].is_malformed is False
    assert len(file.hunks[0].lines) > 0

    # Second hunk should be malformed
    assert file.hunks[1].is_malformed is True
    assert "invalid" in file.hunks[1].raw_text.lower()
    assert file.hunks[1].parse_error is not None

    # Third hunk should be valid
    assert file.hunks[2].is_malformed is False
    assert len(file.hunks[2].lines) > 0


# T011: Contract test - Size limit enforcement


def test_size_limit_enforcement():
    """Test that diffs exceeding 10,000 lines trigger DiffTooLargeError.

    The raccoon's treasure chest can only hold so much!

    Contract: parser-contracts.md Scenario 3 (Size Limit)
    """
    # Test under limit
    small_diff = _generate_diff_with_line_count(8000)
    parser = DiffParser()
    summary = parser.parse(small_diff)

    assert summary.total_line_count == 8000
    assert summary.exceeds_limit is False

    # Test exactly at limit
    exact_diff = _generate_diff_with_line_count(10000)
    summary = parser.parse(exact_diff)

    assert summary.total_line_count == 10000
    assert summary.exceeds_limit is False

    # Test over limit - should raise exception
    large_diff = _generate_diff_with_line_count(12500)

    with pytest.raises(DiffTooLargeError) as exc_info:
        parser.parse(large_diff)

    assert exc_info.value.actual_lines == 12500  # type: ignore[unresolved-attribute]
    assert exc_info.value.limit == 10000  # type: ignore[unresolved-attribute]
    assert "🦝" in exc_info.value.message  # type: ignore[unresolved-attribute]
    assert "🐐" in exc_info.value.message  # type: ignore[unresolved-attribute]


# T012: Contract test - Malformed hunk display in DiffPane


@pytest.mark.asyncio
async def test_malformed_hunk_display():
    """Test that malformed hunks display with visual indicator in DiffPane.

    The UI should show a warning marker for unparseable content!

    Contract: parser-contracts.md - Visual indicator requirement
    """
    from racgoat.main import RacGoatApp
    from racgoat.ui.widgets.diff_pane import DiffPane

    diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ invalid @@
broken content
"""

    # Parse diff first
    parser = DiffParser()
    summary = parser.parse(diff_text)

    # Verify malformed hunk was detected
    assert len(summary.files) == 1
    test_file = summary.files[0]
    assert len(test_file.hunks) == 1
    malformed_hunk = test_file.hunks[0]
    assert malformed_hunk.is_malformed is True

    # Create app with diff summary
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        # Wait for app to render
        await pilot.pause()

        # Get DiffPane
        diff_pane = app.query_one(DiffPane)

        # Verify that format_hunk produces the correct output
        formatted_hunk = diff_pane.format_hunk(malformed_hunk)
        rendered_text = formatted_hunk.plain

        # Should contain unparseable marker
        assert "[⚠ UNPARSEABLE]" in rendered_text
        # Should contain raw text from the malformed hunk
        assert "invalid" in rendered_text.lower() or "broken" in rendered_text.lower()


# Helper functions


def _generate_diff_with_line_count(total_lines: int) -> str:
    """Generate a diff with specified total line count.

    Args:
        total_lines: Total number of lines (sum of all hunks' new_count)

    Returns:
        Diff text with exact line count
    """
    # Create multiple files to reach target line count
    # Each hunk will have 100 lines for simplicity
    lines_per_hunk = 100
    num_hunks = total_lines // lines_per_hunk
    remainder = total_lines % lines_per_hunk

    diff_parts = []

    for i in range(num_hunks):
        diff_parts.append(f"""diff --git a/file{i}.py b/file{i}.py
index 1234567..abcdefg 100644
--- a/file{i}.py
+++ b/file{i}.py
@@ -1,{lines_per_hunk} +1,{lines_per_hunk} @@
""")
        # Add lines
        for j in range(lines_per_hunk):
            diff_parts.append(f"+line {j}\n")

    # Add remainder lines in final file if needed
    if remainder > 0:
        diff_parts.append(f"""diff --git a/final.py b/final.py
index 1234567..abcdefg 100644
--- a/final.py
+++ b/final.py
@@ -1,{remainder} +1,{remainder} @@
""")
        for j in range(remainder):
            diff_parts.append(f"+line {j}\n")

    return "".join(diff_parts)
