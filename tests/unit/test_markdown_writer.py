"""Unit tests for markdown_writer service (Feature 007).

Tests individual functions in isolation: extract_diff_segment() and format_file_stats().

The raccoon's treasure transformation spells, tested one at a time!
"""

import pytest
from racgoat.services.markdown_writer import extract_diff_segment, format_file_stats
from racgoat.parser.models import DiffFile, DiffHunk


class TestExtractDiffSegment:
    """Unit tests for extract_diff_segment() function."""

    def test_extract_diff_segment_line_comment(self):
        """Extract diff segment for line comment with ±2 context."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'def foo():'),
                ('-', '    return 1'),
                ('+', '    return 2'),
                (' ', ''),
            ]
        )

        diff_file = DiffFile(file_path="test.py", hunks=[hunk])

        # Target line 3 (the + line)
        result = extract_diff_segment(diff_file, line_number=3)

        # Assert: Diff segment with context
        assert result is not None
        assert ' def foo():' in result
        assert '-    return 1' in result
        assert '+    return 2' in result
        assert ' ' in result  # empty context line

    def test_extract_diff_segment_range_comment(self):
        """Extract diff segment for range comment spanning multiple lines."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'line1'),  # context
                ('+', 'line2'),  # range start
                ('+', 'line3'),  # range middle
                ('+', 'line4'),  # range end
                (' ', 'line5'),  # context
            ]
        )

        diff_file = DiffFile(file_path="test.py", added_lines=3, removed_lines=0, hunks=[hunk])

        # Target range 2-4
        result = extract_diff_segment(diff_file, line_range=(2, 4))

        # Assert: Full range included
        assert result is not None
        assert ' line1' in result
        assert '+line2' in result
        assert '+line3' in result
        assert '+line4' in result
        assert ' line5' in result

    def test_extract_diff_segment_file_comment_returns_none(self):
        """File-level comment (no line/range) returns None."""
        diff_file = DiffFile(file_path="test.py", hunks=[])

        result = extract_diff_segment(diff_file, line_number=None, line_range=None)

        assert result is None

    def test_extract_diff_segment_boundary_start(self):
        """Context window respects hunk start boundary."""
        hunk = DiffHunk(
            old_start=10,
            new_start=10,
            lines=[
                (' ', 'line10'),  # only 1 context line before target
                ('+', 'line11'),  # target
                (' ', 'line12'),
                (' ', 'line13'),
            ]
        )

        diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=0, hunks=[hunk])

        # Target line 11 (would need 2 lines before for full context, but only 1 available)
        result = extract_diff_segment(diff_file, line_number=11)

        # Assert: Context starts at hunk boundary (line 10)
        assert result is not None
        assert ' line10' in result
        assert '+line11' in result
        # Should not try to show line 9 or 8

    def test_extract_diff_segment_boundary_end(self):
        """Context window respects hunk end boundary."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'line1'),
                (' ', 'line2'),
                ('+', 'line3'),  # target
                (' ', 'line4'),  # only 1 context line after target
            ]
        )

        diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=0, hunks=[hunk])

        # Target line 3 (would need 2 lines after for full context, but only 1 available)
        result = extract_diff_segment(diff_file, line_number=3)

        # Assert: Context ends at hunk boundary (line 4)
        assert result is not None
        assert '+line3' in result
        assert ' line4' in result
        # Should not try to show line 5 or 6

    def test_extract_diff_segment_malformed_hunk(self):
        """Malformed hunk returns None gracefully (no exception)."""
        malformed = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[],
            is_malformed=True,
            raw_text="@@ invalid @@",
            parse_error="Bad format"
        )

        diff_file = DiffFile(file_path="test.py", hunks=[malformed])

        result = extract_diff_segment(diff_file, line_number=5)

        assert result is None

    def test_extract_diff_segment_target_not_found(self):
        """Target line not in any hunk returns None."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'line1'),
                (' ', 'line2'),
            ]
        )

        diff_file = DiffFile(file_path="test.py", hunks=[hunk])

        # Target line 100 (does not exist in hunk)
        result = extract_diff_segment(diff_file, line_number=100)

        assert result is None

    def test_extract_diff_segment_removed_lines_included(self):
        """Removed lines (-) are included in the diff segment."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'context'),
                ('-', 'removed_line'),
                ('+', 'added_line'),
                (' ', 'context2'),
            ]
        )

        diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=1, hunks=[hunk])

        # Target line 2 (the added line)
        result = extract_diff_segment(diff_file, line_number=2)

        # Assert: Removed line is included
        assert result is not None
        assert '-removed_line' in result
        assert '+added_line' in result

    def test_extract_diff_segment_context_zero(self):
        """Context lines = 0 returns only target line(s)."""
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'line1'),
                ('+', 'line2'),  # target
                (' ', 'line3'),
            ]
        )

        diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=0, hunks=[hunk])

        # Target line 2 with context_lines=0
        result = extract_diff_segment(diff_file, line_number=2, context_lines=0)

        # Assert: Only target line (no context)
        assert result is not None
        assert '+line2' in result
        assert 'line1' not in result
        assert 'line3' not in result


class TestFormatFileStats:
    """Unit tests for format_file_stats() function."""

    def test_format_file_stats_normal_file(self):
        """Format file stats for normal file with changes."""
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=120,
            removed_lines=45,
            hunks=[DiffHunk(old_start=1, new_start=1, lines=[(' ', 'x')])] * 5
        )

        result = format_file_stats(diff_file)

        assert result == "5 hunks, +120 -45 lines"

    def test_format_file_stats_new_file(self):
        """Format file stats for new file (only additions)."""
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=50,
            removed_lines=0,
            hunks=[
                DiffHunk(old_start=0, new_start=1, lines=[('+', 'new line')])
            ]
        )

        result = format_file_stats(diff_file)

        assert result == "1 hunks, +50 -0 lines"

    def test_format_file_stats_empty_file(self):
        """Format file stats for empty file (no changes)."""
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=0,
            removed_lines=0,
            hunks=[]
        )

        result = format_file_stats(diff_file)

        assert result == "0 hunks, +0 -0 lines"
