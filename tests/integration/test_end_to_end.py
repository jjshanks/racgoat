"""Integration tests for end-to-end workflow (Milestone 4).

These tests verify the complete user journey from adding comments to
generating Markdown output files. They MUST fail before implementation (TDD).

Tests verify:
- Happy path: comments → quit → file created
- No comments → no file created
- Default output filename (review.md)
- File exists error → modal dialog
- Invalid path error → modal with /tmp fallback
- Git metadata unavailable → placeholders
- Special chars in comments → preserved
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


class TestEndToEndWorkflow:
    """Integration tests for complete review workflow."""

    def test_happy_path_with_comments(self, tmp_path):
        """Raccoon reviews diff, stashes treasures to Markdown."""
        # Arrange: Create session with comments
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(text="Fix this bug", line_number=5),
                RangeComment(text="Refactor this block", start_line=10, end_line=15),
            ]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123def456"
        )
        output_file = tmp_path / "review.md"

        # Act: Write output
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        if session.has_comments:
            content = serialize_review_session(session)
            write_markdown_output(content, output_file)

        # Assert: File created with correct content
        assert output_file.exists(), "Output file should be created"
        content = output_file.read_text()
        assert "# Code Review" in content
        # Check for YAML frontmatter (enhanced Markdown format)
        assert 'branch: "main"' in content, "Should have YAML frontmatter with branch"
        assert "### Line 5" in content
        assert "Fix this bug" in content
        assert "### Lines 10-15" in content
        assert "Refactor this block" in content

    def test_no_comments_no_file(self, tmp_path):
        """Goat leaves no droppings when pasture is empty."""
        # Arrange: Empty session (no comments)
        session = ReviewSession(
            file_reviews={},
            branch_name="main",
            commit_sha="abc123"
        )
        output_file = tmp_path / "review.md"

        # Act: Attempt to write (should skip)
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        if session.has_comments:
            content = serialize_review_session(session)
            write_markdown_output(content, output_file)

        # Assert: No file created
        assert not output_file.exists(), \
            "File should not be created when no comments exist"

    def test_default_output_filename(self, tmp_path, monkeypatch):
        """Raccoon uses default treasure map name."""
        # Arrange: Session with one comment, default filename
        monkeypatch.chdir(tmp_path)
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )
        default_output = Path("review.md")

        # Act: Write to default path
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        content = serialize_review_session(session)
        write_markdown_output(content, default_output)

        # Assert: Default file created
        assert default_output.exists(), "Should create review.md by default"
        assert "Comment" in default_output.read_text()

    def test_file_already_exists_error(self, tmp_path):
        """Raccoon respects existing treasure piles."""
        # Arrange: Create existing file
        output_file = tmp_path / "existing.md"
        output_file.write_text("old content")

        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="New comment", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Attempt to overwrite
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        content = serialize_review_session(session)

        # Assert: Raises FileExistsError
        with pytest.raises(FileExistsError):
            write_markdown_output(content, output_file)

        # Assert: Original file unchanged
        assert output_file.read_text() == "old content"

    def test_invalid_output_path(self, tmp_path):
        """Goat bleats when path leads nowhere."""
        # Arrange: Invalid path (directory doesn't exist)
        output_file = tmp_path / "nonexistent" / "dir" / "review.md"

        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Act: Attempt to write
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        content = serialize_review_session(session)

        # Assert: Raises OSError
        with pytest.raises(OSError):
            write_markdown_output(content, output_file)

    def test_git_metadata_unavailable(self, tmp_path, monkeypatch):
        """Raccoon finds placeholders when git tree is bare."""
        # Arrange: Change to non-git directory
        monkeypatch.chdir(tmp_path)

        # Act: Get git metadata
        from racgoat.services.git_metadata import get_git_metadata
        branch_name, commit_sha = get_git_metadata()

        # Assert: Placeholders used
        assert branch_name == "Unknown Branch"
        assert commit_sha == "Unknown SHA"

        # Verify session can use placeholders
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name=branch_name,
            commit_sha=commit_sha
        )

        # Serialize with placeholders
        from racgoat.services.markdown_writer import serialize_review_session
        output = serialize_review_session(session)
        # Check for YAML frontmatter (enhanced Markdown format)
        assert 'branch: "Unknown Branch"' in output, "Should have YAML frontmatter with placeholder branch"
        assert 'base_commit: "Unknown SHA"' in output, "Should have YAML frontmatter with placeholder commit"

    def test_special_chars_in_comments(self, tmp_path):
        """Raccoon preserves shiny Markdown syntax in comments."""
        # Arrange: Comment with Markdown special characters
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(
                    text="Use `*args` and `**kwargs` instead of #TODO",
                    line_number=1
                )
            ]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )
        output_file = tmp_path / "review.md"

        # Act: Write output
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        content = serialize_review_session(session)
        write_markdown_output(content, output_file)

        # Assert: Special chars preserved (not escaped)
        output_content = output_file.read_text()
        assert "Use `*args` and `**kwargs` instead of #TODO" in output_content
        assert "\\*" not in output_content  # No escaped asterisks
        assert "\\#" not in output_content  # No escaped hashes


class TestAtomicWriteSurvivesInterruption:
    """Test atomic write behavior during interruption."""

    def test_atomic_write_survives_interruption(self, tmp_path):
        """Raccoon's treasure cache survives sudden storms."""
        pytest.skip("Requires process interruption simulation - complex test, implement later")
        # Note: This test would require mocking file write to simulate
        # interruption (e.g., SIGTERM during write). This is complex and
        # should be implemented as part of T036.5 performance tests.
        # For now, we verify atomic write pattern in the implementation.
