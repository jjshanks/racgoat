"""Unit tests for comment data models (Milestone 4).

These tests verify validation rules and constraints for comment models.
"""

import pytest
from racgoat.models.comments import (
    SerializableComment,
    LineComment,
    RangeComment,
    FileComment,
    FileReview,
    ReviewSession,
)


class TestCommentModelValidations:
    """Test validation rules for comment models."""

    def test_empty_text_rejection(self):
        """Raccoon refuses to stash empty thoughts."""
        # Empty string
        with pytest.raises(ValueError, match="must not be empty"):
            LineComment(text="", line_number=1)

        # Whitespace only (should be caught if we trim)
        # Note: Current implementation checks len(text) < 1, so whitespace passes
        # This is acceptable per spec (min 1 char)

    def test_max_comment_length(self):
        """Goat bleats when comment is too long."""
        # Exactly 10,000 chars - should pass
        long_text = "x" * 10_000
        comment = LineComment(text=long_text, line_number=1)
        assert len(comment.text) == 10_000

        # 10,001 chars - should fail
        too_long_text = "x" * 10_001
        with pytest.raises(ValueError, match="exceeds maximum length"):
            LineComment(text=too_long_text, line_number=1)

    def test_invalid_line_numbers(self):
        """Raccoon won't stash treasure at negative lines."""
        # Zero line number
        with pytest.raises(ValueError, match="must be positive"):
            LineComment(text="Comment", line_number=0)

        # Negative line number
        with pytest.raises(ValueError, match="must be positive"):
            LineComment(text="Comment", line_number=-1)

    def test_invalid_range_end_before_start(self):
        """Goat refuses backwards ranges."""
        # End < Start
        with pytest.raises(ValueError, match="End line.*must be >= start line"):
            RangeComment(text="Comment", start_line=10, end_line=5)

    def test_invalid_range_start_zero(self):
        """Raccoon won't start range at line zero."""
        with pytest.raises(ValueError, match="Start line must be positive"):
            RangeComment(text="Comment", start_line=0, end_line=5)


class TestFileReviewValidations:
    """Test validation rules for FileReview."""

    def test_empty_file_path_rejection(self):
        """Goat bleats when file path is missing."""
        with pytest.raises(ValueError, match="File path must not be empty"):
            FileReview(file_path="", comments=[])

    def test_max_comments_per_file(self):
        """Raccoon's cache has limits - 100 comments max."""
        # Exactly 100 comments - should pass
        comments = [LineComment(text=f"Comment {i}", line_number=i) for i in range(1, 101)]
        review = FileReview(file_path="test.py", comments=comments)
        assert len(review.comments) == 100

        # 101 comments - should fail
        too_many_comments = [LineComment(text=f"Comment {i}", line_number=i) for i in range(1, 102)]
        with pytest.raises(ValueError, match="maximum is 100"):
            FileReview(file_path="test.py", comments=too_many_comments)

    def test_comments_list_ordering_preserved(self):
        """Raccoon remembers the order of stashed treasures."""
        comments = [
            LineComment(text="First", line_number=10),
            LineComment(text="Second", line_number=5),
            LineComment(text="Third", line_number=15),
        ]
        review = FileReview(file_path="test.py", comments=comments)

        # Order should match insertion order
        assert review.comments[0].text == "First"
        assert review.comments[1].text == "Second"
        assert review.comments[2].text == "Third"


class TestReviewSessionValidations:
    """Test validation rules for ReviewSession."""

    def test_max_total_comments(self):
        """Goat enforces 100 comment limit across all files."""
        # Create 100 comments across multiple files
        file_reviews = {}
        for i in range(10):
            comments = [LineComment(text=f"C{j}", line_number=j) for j in range(1, 11)]
            file_reviews[f"file{i}.py"] = FileReview(
                file_path=f"file{i}.py",
                comments=comments
            )

        # Exactly 100 comments - should pass
        session = ReviewSession(file_reviews=file_reviews)
        assert session.total_comment_count == 100

        # Add one more comment to exceed limit
        file_reviews["extra.py"] = FileReview(
            file_path="extra.py",
            comments=[LineComment(text="Extra", line_number=1)]
        )

        # 101 comments - should fail
        with pytest.raises(ValueError, match="maximum is 100"):
            ReviewSession(file_reviews=file_reviews)

    def test_has_comments_property_empty(self):
        """Raccoon knows when cache is empty."""
        session = ReviewSession(file_reviews={})
        assert not session.has_comments
        assert session.total_comment_count == 0

    def test_has_comments_property_with_comments(self):
        """Raccoon knows when cache has treasures."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=1)]
        )
        session = ReviewSession(file_reviews={"test.py": review})
        assert session.has_comments
        assert session.total_comment_count == 1

    def test_total_comment_count_calculation(self):
        """Goat counts all comments accurately."""
        file_reviews = {
            "file1.py": FileReview(
                file_path="file1.py",
                comments=[
                    LineComment(text="C1", line_number=1),
                    LineComment(text="C2", line_number=2),
                ]
            ),
            "file2.py": FileReview(
                file_path="file2.py",
                comments=[
                    RangeComment(text="C3", start_line=5, end_line=10),
                ]
            ),
            "file3.py": FileReview(
                file_path="file3.py",
                comments=[
                    FileComment(text="C4"),
                    LineComment(text="C5", line_number=20),
                ]
            ),
        }

        session = ReviewSession(file_reviews=file_reviews)
        assert session.total_comment_count == 5
