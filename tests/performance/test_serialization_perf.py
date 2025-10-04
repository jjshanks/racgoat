"""Performance tests for Markdown serialization (Milestone 4).

These tests verify that serialization and file write operations meet
performance requirements (NFR-002: <5 seconds for 100 comments).
"""

import time
import pytest
from pathlib import Path
from racgoat.models.comments import (
    LineComment,
    RangeComment,
    FileComment,
    FileReview,
    ReviewSession,
)
from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output


class TestSerializationPerformance:
    """Performance tests for serialization operations."""

    def test_100_comments_serialization_under_5_seconds(self):
        """Raccoon serializes 100 treasures quickly (<5s per NFR-002)."""
        # Create ReviewSession with 100 comments across 10 files
        file_reviews = {}
        for file_idx in range(10):
            comments = []
            for comment_idx in range(10):
                # Mix of comment types
                if comment_idx % 3 == 0:
                    comments.append(LineComment(
                        text=f"Line comment {comment_idx} in file {file_idx}",
                        line_number=comment_idx + 1
                    ))
                elif comment_idx % 3 == 1:
                    comments.append(RangeComment(
                        text=f"Range comment {comment_idx} in file {file_idx}",
                        start_line=comment_idx + 1,
                        end_line=comment_idx + 5
                    ))
                else:
                    comments.append(FileComment(
                        text=f"File comment {comment_idx} in file {file_idx}"
                    ))

            file_reviews[f"file{file_idx}.py"] = FileReview(
                file_path=f"file{file_idx}.py",
                comments=comments
            )

        session = ReviewSession(
            file_reviews=file_reviews,
            branch_name="main",
            commit_sha="abc123def456"
        )

        # Verify we have 100 comments
        assert session.total_comment_count == 100

        # Measure serialization time
        start_time = time.time()
        content = serialize_review_session(session)
        serialization_time = time.time() - start_time

        # Assert: Serialization completes in <5 seconds (per NFR-002)
        assert serialization_time < 5.0, \
            f"Serialization took {serialization_time:.2f}s, expected <5s"

        # Verify content is not empty
        assert len(content) > 0
        assert "# Code Review" in content

    def test_file_write_under_1_second(self, tmp_path):
        """Goat writes file quickly (<1s for normal-sized review)."""
        # Create session with 50 comments
        comments = [
            LineComment(text=f"Comment {i}", line_number=i)
            for i in range(1, 51)
        ]
        review = FileReview(file_path="test.py", comments=comments)
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Serialize
        content = serialize_review_session(session)

        # Measure file write time
        output_file = tmp_path / "review.md"
        start_time = time.time()
        write_markdown_output(content, output_file)
        write_time = time.time() - start_time

        # Assert: File write completes in <1 second
        assert write_time < 1.0, \
            f"File write took {write_time:.2f}s, expected <1s"

        # Verify file was created
        assert output_file.exists()
        assert len(output_file.read_text()) > 0
