"""Contract tests for diff segment extraction (Feature 007).

Validates functional requirements FR-001 through FR-013 for including actual
diff segments (with +/- markers) in review output instead of post-change code context.

The raccoon now shows you what was in the trash before you cleaned it!
"""

import pytest
from racgoat.services.markdown_writer import serialize_review_session
from racgoat.models.comments import ReviewSession, FileReview, LineComment, RangeComment, FileComment
from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary


@pytest.fixture
def sample_diff_file():
    """Create a DiffFile with sample hunk for testing."""
    return DiffFile(
        file_path="example.py",
        added_lines=1,
        removed_lines=1,
        hunks=[
            DiffHunk(
                old_start=1,
                new_start=1,
                lines=[
                    (' ', 'def calculate_total(items):'),
                    ('-', '    return sum(items)'),
                    ('+', '    return sum(item.price for item in items)'),
                    (' ', ''),
                ]
            )
        ]
    )


@pytest.fixture
def sample_review_session():
    """Create an empty ReviewSession for testing."""
    return ReviewSession(
        file_reviews={},
        branch_name="feature-branch",
        commit_sha="abc123"
    )


def test_diff_segment_included_for_line_comment(sample_diff_file, sample_review_session):
    """FR-001: Verify diff segment is included for line comments."""
    # Setup: Add line comment
    comment = LineComment(line_number=3, text="Optimize this", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute: Serialize with diff_summary
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Diff segment present
    assert "**Context**:" in output
    assert "```diff" in output
    assert "+    return sum(item.price for item in items)" in output


def test_before_after_states_shown(sample_diff_file, sample_review_session):
    """FR-002: Verify both - and + lines are shown."""
    # Setup
    comment = LineComment(line_number=3, text="Check this", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Both markers present
    assert "-    return sum(items)" in output
    assert "+    return sum(item.price for item in items)" in output


def test_context_lines_included(sample_diff_file, sample_review_session):
    """FR-003: Verify context lines are shown with space prefix."""
    # Setup
    comment = LineComment(line_number=3, text="Comment", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Context lines with space prefix
    assert " def calculate_total(items):" in output


def test_line_comment_has_two_context_lines(sample_review_session):
    """FR-004: Verify line comments have ±2 context lines."""
    # Setup: Create hunk with 7 lines (2 before + 1 target + 2 after + 2 extra for boundaries)
    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=[
            (' ', 'line1'),  # context
            (' ', 'line2'),  # context
            ('+', 'line3'),  # target line
            (' ', 'line4'),  # context
            (' ', 'line5'),  # context
            (' ', 'line6'),  # extra (should not appear)
        ]
    )

    diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=0, hunks=[hunk])
    sample_review_session.file_reviews["test.py"] = FileReview(
        file_path="test.py",
        comments=[LineComment(line_number=3, text="Target", status="open")]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: ±2 context lines included
    assert " line1" in output  # -2
    assert " line2" in output  # -1
    assert "+line3" in output  # target
    assert " line4" in output  # +1
    assert " line5" in output  # +2
    assert "line6" not in output  # beyond context window


def test_range_comment_includes_full_range_plus_context(sample_review_session):
    """FR-005: Verify range comments include full range + ±2 context."""
    # Setup: Create hunk with range spanning lines 3-5 (3 lines)
    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=[
            (' ', 'line1'),  # -2 context
            (' ', 'line2'),  # -1 context
            ('+', 'line3'),  # range start
            ('+', 'line4'),  # range middle
            ('+', 'line5'),  # range end
            (' ', 'line6'),  # +1 context
            (' ', 'line7'),  # +2 context
            (' ', 'line8'),  # beyond context (should not appear)
        ]
    )

    diff_file = DiffFile(file_path="test.py", added_lines=3, removed_lines=0, hunks=[hunk])
    sample_review_session.file_reviews["test.py"] = FileReview(
        file_path="test.py",
        comments=[RangeComment(start_line=3, end_line=5, text="Range comment", status="open")]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Full range + ±2 context
    assert " line1" in output  # -2
    assert " line2" in output  # -1
    assert "+line3" in output  # range start
    assert "+line4" in output  # range middle
    assert "+line5" in output  # range end
    assert " line6" in output  # +1
    assert " line7" in output  # +2
    assert "line8" not in output  # beyond context


def test_file_comment_shows_statistical_summary(sample_diff_file, sample_review_session):
    """FR-006: Verify file comments show 'N hunks, +X -Y lines'."""
    # Setup
    comment = FileComment(text="Needs more tests", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Statistical summary present
    assert "**File changes**:" in output
    assert "1 hunks, +1 -1 lines" in output


def test_boundary_respect(sample_review_session):
    """FR-007: Verify context window respects hunk boundaries."""
    # Setup: Hunk starting at line 10, comment at line 11 (only 1 line before)
    hunk = DiffHunk(
        old_start=10,
        new_start=10,
        lines=[
            (' ', 'line10'),  # only 1 context line available before
            ('+', 'line11'),  # target
            (' ', 'line12'),
            (' ', 'line13'),
        ]
    )

    diff_file = DiffFile(file_path="test.py", added_lines=1, removed_lines=0, hunks=[hunk])
    sample_review_session.file_reviews["test.py"] = FileReview(
        file_path="test.py",
        comments=[LineComment(line_number=11, text="Comment", status="open")]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Context starts at hunk boundary (line 10), not before
    assert " line10" in output
    assert "+line11" in output
    # Should not try to show line 9 or line 8 (before hunk start)


def test_malformed_hunk_graceful_handling(sample_review_session):
    """FR-008: Verify malformed hunks don't crash, return no context."""
    # Setup: Malformed hunk
    malformed_hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=[],
        is_malformed=True,
        raw_text="@@ invalid hunk @@",
        parse_error="Invalid header format"
    )

    diff_file = DiffFile(
        file_path="example.py",
        added_lines=0,
        removed_lines=0,
        hunks=[malformed_hunk]
    )

    comment = LineComment(line_number=3, text="Comment", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: No context (graceful fallback)
    assert "**Context**:" not in output
    # Comment text should still be present
    assert "Comment" in output


def test_fenced_code_block_with_diff_syntax(sample_diff_file, sample_review_session):
    """FR-009: Verify fenced code blocks use ```diff for syntax highlighting."""
    # Setup
    comment = LineComment(line_number=3, text="Comment", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Uses ```diff (not just ```)
    assert "```diff" in output


def test_backward_compatibility_no_diff_summary(sample_review_session):
    """FR-010: Verify no context when diff_summary is None."""
    # Setup
    comment = LineComment(line_number=3, text="Comment", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute: Serialize WITHOUT diff_summary
    output = serialize_review_session(sample_review_session, diff_summary=None)

    # Assert: No context section
    assert "**Context**:" not in output
    assert "```diff" not in output
    # Comment should still be present
    assert "Comment" in output


def test_unified_diff_format(sample_diff_file, sample_review_session):
    """FR-011: Verify standard unified diff format (no line numbers in diff segment)."""
    # Setup
    comment = LineComment(line_number=3, text="Comment", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: No line numbers in diff segment (standard unified diff format)
    # Old format would have "3 | return sum(...)"
    # New format should have "+    return sum(...)" with no line number prefix
    assert "3 |" not in output
    assert "2 |" not in output
    # Should have markers without line numbers
    assert "+    return sum(item.price for item in items)" in output
    assert "-    return sum(items)" in output


def test_edge_cases(sample_review_session):
    """FR-012: Verify edge cases (removed-only, added-only, boundary)."""
    # Test 1: Removed-only lines
    removed_only_hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=[
            (' ', 'context_before'),
            ('-', 'removed_line'),
            (' ', 'context_after'),
        ]
    )

    # Test 2: Added-only lines
    added_only_hunk = DiffHunk(
        old_start=1,
        new_start=5,
        lines=[
            (' ', 'context_before2'),
            ('+', 'added_line'),
            (' ', 'context_after2'),
        ]
    )

    diff_file = DiffFile(
        file_path="test.py",
        added_lines=1,
        removed_lines=1,
        hunks=[removed_only_hunk, added_only_hunk]
    )

    sample_review_session.file_reviews["test.py"] = FileReview(
        file_path="test.py",
        comments=[
            LineComment(line_number=2, text="Comment on context after removed", status="open"),
            LineComment(line_number=6, text="Comment on added", status="open"),
        ]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Removed lines included in context
    assert "-removed_line" in output
    # Assert: Added lines included
    assert "+added_line" in output


def test_no_truncation_for_large_hunks(sample_review_session):
    """FR-013: Verify large hunks (100+ lines) are not truncated."""
    # Setup: Create hunk with 120 lines
    large_lines = [(' ', f'line {i}') for i in range(120)]
    large_lines[60] = ('+', 'modified line 60')

    large_hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=large_lines
    )

    diff_file = DiffFile(
        file_path="large.py",
        added_lines=1,
        removed_lines=0,
        hunks=[large_hunk]
    )

    comment = LineComment(line_number=61, text="Check this", status="open")
    sample_review_session.file_reviews["large.py"] = FileReview(
        file_path="large.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Context includes ±2 lines around target line 61
    # Post-change line 61 = index 60 (modified), so context is lines 59-63 (post-change)
    # Which maps to indices 58-62 in the array
    assert "line 58" in output  # post-change line 59
    assert "line 59" in output  # post-change line 60
    assert "modified line 60" in output  # post-change line 61 (target)
    assert "line 61" in output  # post-change line 62
    assert "line 62" in output  # post-change line 63
    # Lines outside context window should not appear
    assert "line 50" not in output
    assert "line 63" not in output  # This is post-change line 64, outside ±2 window
    assert "line 70" not in output
