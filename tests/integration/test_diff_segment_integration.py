"""Integration tests for diff segment feature (Feature 007).

End-to-end tests validating diff segments appear correctly in review.md output.

The raccoon's treasure map now shows the before and after treasures!
"""

import pytest
import tempfile
from pathlib import Path
from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
from racgoat.models.comments import ReviewSession, FileReview, LineComment, RangeComment, FileComment
from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary


class TestLineCommentDiffSegments:
    """Integration tests for line comments with diff segments."""

    def test_end_to_end_line_comment_with_diff_segment(self, tmp_path):
        """Create line comment, serialize, verify diff segment in output file."""
        # Setup: Create diff with simple change
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'def foo():'),
                ('-', '    old_implementation'),
                ('+', '    new_implementation'),
                (' ', ''),
            ]
        )

        diff_file = DiffFile(
            file_path="test.py",
            added_lines=1,
            removed_lines=1,
            hunks=[hunk]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create comment
        comment = LineComment(line_number=3, text="Why was this changed?", status="open")
        session = ReviewSession(
            file_reviews={
                "test.py": FileReview(file_path="test.py", comments=[comment])
            },
            branch_name="feature/update",
            commit_sha="abc123"
        )

        # Execute: Serialize and write to file
        output = serialize_review_session(session, diff_summary)
        output_file = tmp_path / "review.md"
        write_markdown_output(output, output_file)

        # Assert: File contains diff segment with markers
        content = output_file.read_text()
        assert "```diff" in content
        assert "-    old_implementation" in content
        assert "+    new_implementation" in content
        assert "Why was this changed?" in content


class TestRangeCommentDiffSegments:
    """Integration tests for range comments with diff segments."""

    def test_end_to_end_range_comment_with_diff_segment(self, tmp_path):
        """Create range comment, serialize, verify full range in output."""
        # Setup: Create diff with multiple changes
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'class Foo:'),
                ('+', '    def __init__(self):'),
                ('+', '        self.value = 0'),
                ('+', '        self.name = "foo"'),
                (' ', ''),
            ]
        )

        diff_file = DiffFile(
            file_path="foo.py",
            added_lines=3,
            removed_lines=0,
            hunks=[hunk]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create range comment spanning the additions
        comment = RangeComment(
            start_line=2,
            end_line=4,
            text="Constructor needs validation",
            status="open"
        )
        session = ReviewSession(
            file_reviews={
                "foo.py": FileReview(file_path="foo.py", comments=[comment])
            },
            branch_name="feature/class",
            commit_sha="def456"
        )

        # Execute
        output = serialize_review_session(session, diff_summary)
        output_file = tmp_path / "review.md"
        write_markdown_output(output, output_file)

        # Assert: Full range + context included
        content = output_file.read_text()
        assert "```diff" in content
        assert "+    def __init__(self):" in content
        assert "+        self.value = 0" in content
        assert "+        self.name = \"foo\"" in content


class TestFileCommentStatistics:
    """Integration tests for file-level comments with statistical summaries."""

    def test_end_to_end_file_comment_with_stats(self, tmp_path):
        """Create file comment, verify statistical summary in output."""
        # Setup: Create diff with multiple hunks
        diff_file = DiffFile(
            file_path="large.py",
            added_lines=120,
            removed_lines=45,
            hunks=[
                DiffHunk(old_start=1, new_start=1, lines=[(' ', 'x')]),
                DiffHunk(old_start=10, new_start=10, lines=[(' ', 'y')]),
                DiffHunk(old_start=20, new_start=20, lines=[(' ', 'z')]),
            ]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create file-level comment
        comment = FileComment(text="This file needs comprehensive testing", status="open")
        session = ReviewSession(
            file_reviews={
                "large.py": FileReview(file_path="large.py", comments=[comment])
            },
            branch_name="refactor",
            commit_sha="ghi789"
        )

        # Execute
        output = serialize_review_session(session, diff_summary)
        output_file = tmp_path / "review.md"
        write_markdown_output(output, output_file)

        # Assert: Statistical summary present
        content = output_file.read_text()
        assert "**File changes**:" in content
        assert "3 hunks, +120 -45 lines" in content
        assert "```diff" not in content  # No diff segment for file comments


class TestMultipleComments:
    """Integration tests for multiple comments in same file."""

    def test_multiple_comments_same_file(self, tmp_path):
        """Multiple comments should each have correct diff segments."""
        # Setup: Create diff with multiple changes
        hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=[
                (' ', 'def process(data):'),
                ('-', '    return data'),
                ('+', '    return validate(data)'),
                (' ', ''),
                (' ', 'def validate(data):'),
                ('+', '    if not data:'),
                ('+', '        raise ValueError("Empty")'),
                (' ', '    return True'),
            ]
        )

        diff_file = DiffFile(
            file_path="processor.py",
            added_lines=3,
            removed_lines=1,
            hunks=[hunk]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create three comments
        comments = [
            LineComment(line_number=3, text="Good improvement", status="open"),
            LineComment(line_number=6, text="Check for None vs empty", status="open"),
            LineComment(line_number=7, text="Consider custom exception", status="open"),
        ]
        session = ReviewSession(
            file_reviews={
                "processor.py": FileReview(file_path="processor.py", comments=comments)
            },
            branch_name="validation",
            commit_sha="jkl012"
        )

        # Execute
        output = serialize_review_session(session, diff_summary)
        output_file = tmp_path / "review.md"
        write_markdown_output(output, output_file)

        # Assert: All comments have correct segments
        content = output_file.read_text()
        assert content.count("```diff") == 3  # Three diff segments
        assert "Good improvement" in content
        assert "Check for None vs empty" in content
        assert "Consider custom exception" in content


class TestLargeHunks:
    """Integration tests for large hunks (100+ lines)."""

    def test_large_hunk_no_truncation(self, tmp_path):
        """Large hunks should not be truncated."""
        # Setup: Create large hunk with 150 lines
        large_lines = [(' ', f'line_{i}') for i in range(150)]
        large_lines[75] = ('+', 'modified_line_75')

        large_hunk = DiffHunk(
            old_start=1,
            new_start=1,
            lines=large_lines
        )

        diff_file = DiffFile(
            file_path="huge.py",
            added_lines=1,
            removed_lines=0,
            hunks=[large_hunk]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create comment near the modification
        comment = LineComment(line_number=76, text="This change needs review", status="open")
        session = ReviewSession(
            file_reviews={
                "huge.py": FileReview(file_path="huge.py", comments=[comment])
            },
            branch_name="large-change",
            commit_sha="mno345"
        )

        # Execute
        output = serialize_review_session(session, diff_summary)
        output_file = tmp_path / "review.md"
        write_markdown_output(output, output_file)

        # Assert: Context window shows ±2 lines (not truncated)
        content = output_file.read_text()
        assert "line_73" in content  # -2
        assert "line_74" in content  # -1
        assert "modified_line_75" in content  # target
        assert "line_76" in content  # +1
        assert "line_77" in content  # +2
        # Lines far from context should not appear
        assert "line_50" not in content
        assert "line_100" not in content
