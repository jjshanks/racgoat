"""Contract tests for Markdown output format (Milestone 4).

These tests define the expected Markdown structure for review output files.
They MUST fail before implementation (TDD approach per constitution).

Tests verify:
- Markdown structure (headings, metadata format)
- Comment serialization (line, range, file-level)
- Special character preservation (no escaping)
- Git metadata placeholders
- File ordering (alphabetical)
- Empty session handling (no file creation)
"""

import pytest
from pathlib import Path
from racgoat.models.comments import (
    LineComment,
    RangeComment,
    FileComment,
    FileReview,
    ReviewSession,
)


class TestMarkdownOutputContract:
    """Contract tests for Markdown serialization format."""

    def test_minimal_valid_output(self):
        """Raccoon stashes a single treasure (line comment)."""
        # Arrange: Create ReviewSession with one line comment
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Fix this", line_number=10)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Serialize to Markdown (not implemented yet - should fail)
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)

        # Assert: Exact match to expected format
        expected = """# Code Review

**Branch**: main
**Commit**: abc123

## File: test.py

### Line 10
Fix this
"""
        assert output == expected, f"Expected:\n{expected}\nGot:\n{output}"

    def test_multiple_comment_types(self):
        """Goat climbs through all comment terrains."""
        # Arrange: LineComment + RangeComment + FileComment in one file
        review = FileReview(
            file_path="app.py",
            comments=[
                LineComment(text="Add validation", line_number=5),
                RangeComment(text="Refactor loop", start_line=10, end_line=15),
                FileComment(text="Good structure"),
            ]
        )
        session = ReviewSession(
            file_reviews={"app.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Serialize
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)

        # Assert: All three comment types with correct H3 headings
        assert "### Line 5" in output
        assert "Add validation" in output
        assert "### Lines 10-15" in output
        assert "Refactor loop" in output
        assert "### File-level comment" in output
        assert "Good structure" in output

    def test_special_markdown_chars_preserved(self):
        """Raccoon respects shiny Markdown symbols."""
        # Arrange: Comment with Markdown special chars
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(
                    text="Use `*args` and `**kwargs` instead of #TODO",
                    line_number=20
                )
            ]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Serialize
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)

        # Assert: No escaping - chars preserved exactly
        assert "Use `*args` and `**kwargs` instead of #TODO" in output
        assert "\\*" not in output  # No escaped asterisks
        assert "\\#" not in output  # No escaped hashes
        assert "\\`" not in output  # No escaped backticks

    def test_git_metadata_placeholders(self):
        """Goat shrugs when git repo vanishes."""
        # Arrange: ReviewSession with placeholder metadata (git failed)
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="Unknown Branch",
            commit_sha="Unknown SHA"
        )

        # Act: Serialize
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)

        # Assert: Placeholders appear in output
        assert "**Branch**: Unknown Branch" in output
        assert "**Commit**: Unknown SHA" in output

    def test_alphabetical_file_order(self):
        """Raccoon alphabetizes the trash pile."""
        # Arrange: Files out of alphabetical order
        session = ReviewSession(
            file_reviews={
                "zebra.py": FileReview(
                    file_path="zebra.py",
                    comments=[LineComment(text="Z", line_number=1)]
                ),
                "alpha.py": FileReview(
                    file_path="alpha.py",
                    comments=[LineComment(text="A", line_number=1)]
                ),
                "beta.py": FileReview(
                    file_path="beta.py",
                    comments=[LineComment(text="B", line_number=1)]
                ),
            },
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Serialize
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)

        # Assert: Files appear in alphabetical order
        alpha_pos = output.find("## File: alpha.py")
        beta_pos = output.find("## File: beta.py")
        zebra_pos = output.find("## File: zebra.py")

        assert alpha_pos < beta_pos < zebra_pos, \
            f"Files not in alphabetical order: alpha={alpha_pos}, beta={beta_pos}, zebra={zebra_pos}"

    def test_no_output_when_empty(self, tmp_path):
        """Goat refuses to leave droppings without reason."""
        # Arrange: Empty ReviewSession (no comments)
        session = ReviewSession(
            file_reviews={},
            branch_name="main",
            commit_sha="abc123"
        )
        output_file = tmp_path / "review.md"

        # Act: Attempt to write output
        from racgoat.services.markdown_writer import write_markdown_output
        from racgoat.services.markdown_writer import serialize_review_session

        # Should not create file when session has no comments
        if session.has_comments:
            content = serialize_review_session(session)
            write_markdown_output(content, output_file)

        # Assert: No file created
        assert not output_file.exists(), \
            "File should not be created for empty session"
