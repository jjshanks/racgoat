"""Contract tests for Enhanced Markdown output format.

These tests validate the enhanced Markdown structure with YAML frontmatter,
HTML metadata, and code context snippets.

Tests verify:
- YAML frontmatter structure and fields
- HTML metadata per comment (id, status, line/lines)
- Code context extraction and formatting
- Sequential comment IDs (c1, c2, c3...)
- File-level comments (no line field in metadata)
- Horizontal rule separators between comments
- Backward compatibility (works without diff_summary)
"""

import pytest
import re
from racgoat.models.comments import (
    LineComment,
    RangeComment,
    FileComment,
    FileReview,
    ReviewSession,
)
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.services.markdown_writer import serialize_review_session


class TestYAMLFrontmatter:
    """Contract tests for YAML frontmatter structure."""

    def test_yaml_frontmatter_present(self):
        """YAML frontmatter must be present at start of output."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Fix this", line_number=10)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        output = serialize_review_session(session)

        # Check frontmatter delimiters
        assert output.startswith("---\n"), "Output must start with YAML frontmatter delimiter"
        assert "\n---\n" in output, "YAML frontmatter must be closed with delimiter"

    def test_yaml_frontmatter_fields(self):
        """YAML frontmatter must contain all required fields."""
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(text="Comment 1", line_number=10),
                LineComment(text="Comment 2", line_number=20)
            ]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="feature/auth",
            commit_sha="def456"
        )

        output = serialize_review_session(session)

        # Extract frontmatter
        frontmatter = output.split("---\n")[1]

        # Verify all fields
        assert 'review_id:' in frontmatter, "review_id field missing"
        assert 'branch: "feature/auth"' in frontmatter, "branch field incorrect"
        assert 'base_commit: "def456"' in frontmatter, "base_commit field incorrect"
        assert 'files_reviewed: 1' in frontmatter, "files_reviewed field incorrect"
        assert 'total_comments: 2' in frontmatter, "total_comments field incorrect"

    def test_review_id_format(self):
        """review_id must follow YYYYMMDD-HHMMSS format."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Test", line_number=1)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Extract review_id
        match = re.search(r'review_id: "(\d{8}-\d{6})"', output)
        assert match, "review_id not in expected format YYYYMMDD-HHMMSS"
        review_id = match.group(1)
        assert len(review_id) == 15, f"review_id length incorrect: {review_id}"


class TestHTMLMetadata:
    """Contract tests for HTML metadata per comment."""

    def test_html_metadata_present(self):
        """Each comment must have HTML metadata block."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=10)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Check HTML comment syntax
        assert "<!--comment" in output, "HTML metadata opening tag missing"
        assert "-->" in output, "HTML metadata closing tag missing"

    def test_sequential_comment_ids(self):
        """Comment IDs must be sequential (c1, c2, c3...)."""
        review1 = FileReview(
            file_path="alpha.py",
            comments=[
                LineComment(text="A1", line_number=1),
                LineComment(text="A2", line_number=2)
            ]
        )
        review2 = FileReview(
            file_path="beta.py",
            comments=[LineComment(text="B1", line_number=1)]
        )
        session = ReviewSession(
            file_reviews={"alpha.py": review1, "beta.py": review2}
        )

        output = serialize_review_session(session)

        # Extract comment IDs
        ids = re.findall(r'id: (c\d+)', output)
        assert ids == ['c1', 'c2', 'c3'], f"Comment IDs not sequential: {ids}"

    def test_line_comment_metadata(self):
        """Line comments must have 'line:' field in metadata."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Fix", line_number=42)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Check metadata structure
        assert "id: c1" in output
        assert "status: open" in output
        assert "line: 42" in output
        assert "lines:" not in output  # Should not have range field

    def test_range_comment_metadata(self):
        """Range comments must have 'lines:' field in metadata."""
        review = FileReview(
            file_path="test.py",
            comments=[RangeComment(text="Refactor", start_line=10, end_line=15)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Check metadata structure
        assert "id: c1" in output
        assert "status: open" in output
        assert "lines: 10-15" in output
        assert "line: " not in output or "lines: " in output  # Should not have single line field

    def test_file_comment_no_line_field(self):
        """File comments must NOT have line/lines field in metadata."""
        review = FileReview(
            file_path="test.py",
            comments=[FileComment(text="Good structure")]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Extract metadata block
        metadata_match = re.search(r'<!--comment\n(.*?)-->', output, re.DOTALL)
        assert metadata_match, "HTML metadata block not found"
        metadata = metadata_match.group(1)

        # Verify no line field
        assert "line:" not in metadata, "File comment should not have 'line:' field"
        assert "lines:" not in metadata, "File comment should not have 'lines:' field"


class TestCodeContext:
    """Contract tests for code context extraction."""

    def test_code_context_with_diff_summary(self):
        """Code context must be included when diff_summary provided."""
        # Create diff with hunks
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=5,
            removed_lines=0,
            hunks=[
                DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def login(user):'),
                        ('+', '    # No validation'),
                        ('+', '    db.query(user.email)'),
                        ('+', '    return user'),
                    ]
                )
            ]
        )
        diff_summary = DiffSummary(files=[diff_file])

        # Create comment on line 3
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Add validation", line_number=3)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session, diff_summary=diff_summary)

        # Verify context block (diff format, not line numbers)
        assert "**Context**:" in output, "Context header missing"
        assert "```diff" in output, "Diff code block markers missing"
        assert "+    db.query(user.email)" in output, "Code content with diff marker missing"

    def test_no_code_context_without_diff_summary(self):
        """Code context must be omitted when diff_summary not provided."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=10)]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)  # No diff_summary

        # Verify no context
        assert "**Context**:" not in output, "Context should not be present without diff_summary"
        assert output.count("```") == 0, "Code blocks should not be present without diff_summary"

    def test_file_comment_has_stats_not_context(self):
        """File comments must have statistical summary, NOT code context."""
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=2,
            removed_lines=0,
            hunks=[
                DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'line1'), ('+', 'line2')]
                )
            ]
        )
        diff_summary = DiffSummary(files=[diff_file])

        review = FileReview(
            file_path="test.py",
            comments=[FileComment(text="Good file")]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session, diff_summary=diff_summary)

        # File comment should have statistical summary
        assert "**File changes**:" in output, "File comment should have statistical summary"
        assert "1 hunks, +2 -0 lines" in output, "Statistical summary incorrect"
        # File comment should not have diff context
        context_count = output.count("**Context**:")
        assert context_count == 0, "File comment should not have code context"
        assert "```diff" not in output, "File comment should not have diff block"


class TestHorizontalRules:
    """Contract tests for horizontal rule separators."""

    def test_horizontal_rules_between_comments(self):
        """Horizontal rules must separate comments within same file."""
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(text="Comment 1", line_number=1),
                LineComment(text="Comment 2", line_number=2),
                LineComment(text="Comment 3", line_number=3)
            ]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Count horizontal rules (should be n-1 for n comments)
        # Note: Count only standalone "---" on their own line
        hr_count = len([line for line in output.split('\n') if line.strip() == '---'])
        # Subtract 2 for YAML frontmatter delimiters
        hr_between_comments = hr_count - 2
        assert hr_between_comments == 2, f"Expected 2 horizontal rules, got {hr_between_comments}"

    def test_no_trailing_horizontal_rule(self):
        """No horizontal rule after last comment in file."""
        review = FileReview(
            file_path="test.py",
            comments=[
                LineComment(text="Comment 1", line_number=1),
                LineComment(text="Comment 2", line_number=2)
            ]
        )
        session = ReviewSession(file_reviews={"test.py": review})

        output = serialize_review_session(session)

        # Extract section after Comment 2
        lines = output.split('\n')
        comment2_idx = next(i for i, line in enumerate(lines) if 'Comment 2' in line)

        # Check remaining lines after Comment 2 - should not have ---
        remaining = '\n'.join(lines[comment2_idx:])
        # Count --- after Comment 2 (excluding YAML frontmatter)
        trailing_hr = remaining.count('\n---\n')
        assert trailing_hr == 0, "Should not have horizontal rule after last comment"


class TestBackwardCompatibility:
    """Contract tests for backward compatibility."""

    def test_works_without_diff_summary(self):
        """Serialization must work without diff_summary (backward compatible)."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Comment", line_number=10)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        # Should not raise exception
        output = serialize_review_session(session)

        # Verify basic structure
        assert "# Code Review" in output
        assert "## File: `test.py`" in output
        assert "### Line 10" in output
        assert "Comment" in output

    def test_old_tests_still_pass_with_new_format(self):
        """Existing test expectations should still be met (with additions)."""
        review = FileReview(
            file_path="test.py",
            comments=[LineComment(text="Fix this", line_number=10)]
        )
        session = ReviewSession(
            file_reviews={"test.py": review},
            branch_name="main",
            commit_sha="abc123"
        )

        output = serialize_review_session(session)

        # Old format expectations (from test_markdown_output.py)
        assert "# Code Review" in output
        assert "## File: `test.py`" in output  # Note: backticks added
        assert "### Line 10" in output
        assert "Fix this" in output

        # New format additions
        assert "---\n" in output  # YAML frontmatter
        assert "review_id:" in output
        assert "<!--comment" in output  # HTML metadata
