# Test Requirements: Diff Segment Extraction

**Feature**: Include Diff Segments in Review Output
**Date**: 2025-10-10

This document maps functional requirements (FR-001 to FR-013) to specific test cases.

## Test Coverage Matrix

| Requirement | Test File | Test Function | Priority |
|-------------|-----------|---------------|----------|
| FR-001: Diff segments included for line/range comments | test_diff_segments.py | test_diff_segment_included_for_line_comment | P0 |
| FR-002: Before/after states with +/- markers | test_diff_segments.py | test_before_after_states_shown | P0 |
| FR-003: Context lines with space prefix | test_diff_segments.py | test_context_lines_included | P0 |
| FR-004: Line comments have ±2 context | test_diff_segments.py | test_line_comment_has_two_context_lines | P0 |
| FR-005: Range comments include full range + ±2 context | test_diff_segments.py | test_range_comment_includes_full_range_plus_context | P0 |
| FR-006: File comments show statistical summary | test_diff_segments.py | test_file_comment_shows_statistical_summary | P0 |
| FR-007: Boundary respect | test_diff_segments.py | test_boundary_respect | P1 |
| FR-008: Malformed hunk handling | test_diff_segments.py | test_malformed_hunk_graceful_handling | P1 |
| FR-009: Fenced code blocks with ```diff | test_diff_segments.py | test_fenced_code_block_with_diff_syntax | P0 |
| FR-010: Backward compatibility (no diff_summary) | test_diff_segments.py | test_backward_compatibility_no_diff_summary | P0 |
| FR-011: Unified diff format (no line numbers) | test_diff_segments.py | test_unified_diff_format | P0 |
| FR-012: Edge cases (boundary, removed-only, added-only) | test_diff_segments.py | test_edge_cases | P1 |
| FR-013: No truncation for large hunks | test_diff_segments.py | test_no_truncation_for_large_hunks | P1 |

## Test File Structure

### tests/contract/test_diff_segments.py

**Purpose**: Validate all functional requirements end-to-end

**Test count**: Minimum 13 (one per FR)

**Setup**:
```python
import pytest
from racgoat.services.markdown_writer import serialize_review_session
from racgoat.models.comments import ReviewSession, FileReview, LineComment, RangeComment, FileComment
from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary

@pytest.fixture
def sample_diff_file():
    """Create a DiffFile with multiple hunks for testing."""
    return DiffFile(
        file_path="example.py",
        added_lines=10,
        removed_lines=5,
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
            ),
            # More hunks...
        ]
    )

@pytest.fixture
def sample_review_session():
    """Create a ReviewSession for testing."""
    return ReviewSession(
        review_id="test-review",
        branch_name="feature-branch",
        commit_sha="abc123",
        file_reviews={}
    )
```

**Test Examples**:

```python
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
    comment = LineComment(line_number=3, text="Check this", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Both markers present
    assert "-    return sum(items)" in output
    assert "+    return sum(item.price for item in items)" in output

def test_file_comment_shows_statistical_summary(sample_diff_file, sample_review_session):
    """FR-006: Verify file comments show 'N hunks, +X -Y lines'."""
    comment = FileComment(text="Needs more tests", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: Statistical summary present
    assert "**File changes**:" in output
    assert "1 hunks, +10 -5 lines" in output  # Based on sample_diff_file

def test_backward_compatibility_no_diff_summary(sample_review_session):
    """FR-010: Verify no context when diff_summary is None."""
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

def test_malformed_hunk_graceful_handling(sample_review_session):
    """FR-008: Verify malformed hunks don't crash, return no context."""
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

    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert: No context (graceful fallback)
    assert "**Context**:" not in output

def test_no_truncation_for_large_hunks():
    """FR-013: Verify large hunks (100+ lines) are not truncated."""
    # Create hunk with 100+ lines
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
    session = ReviewSession(
        review_id="test",
        branch_name="branch",
        commit_sha="sha",
        file_reviews={
            "large.py": FileReview(file_path="large.py", comments=[comment])
        }
    )

    diff_summary = DiffSummary(files=[diff_file])
    output = serialize_review_session(session, diff_summary)

    # Assert: Context includes ±2 lines (lines 59-63 visible)
    assert "line 59" in output
    assert "line 60" in output or "modified line 60" in output
    assert "line 61" in output
    assert "line 63" in output
```

### tests/unit/test_markdown_writer.py

**Purpose**: Unit test individual functions in isolation

**Test count**: Minimum 12 new tests

**Examples**:

```python
from racgoat.services.markdown_writer import extract_diff_segment, format_file_stats
from racgoat.parser.models import DiffFile, DiffHunk

def test_extract_diff_segment_line_comment():
    """Unit test: Extract diff segment for line comment."""
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

def test_extract_diff_segment_file_comment_returns_none():
    """Unit test: File-level comment returns None."""
    diff_file = DiffFile(file_path="test.py", hunks=[])

    result = extract_diff_segment(diff_file, line_number=None, line_range=None)

    assert result is None

def test_extract_diff_segment_malformed_hunk():
    """Unit test: Malformed hunk returns None."""
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

def test_format_file_stats_normal_file():
    """Unit test: Format file stats for normal file."""
    diff_file = DiffFile(
        file_path="test.py",
        added_lines=120,
        removed_lines=45,
        hunks=[DiffHunk(old_start=1, new_start=1, lines=[(' ', 'foo')])] * 5
    )

    result = format_file_stats(diff_file)

    assert result == "5 hunks, +120 -45 lines"

def test_format_file_stats_empty_file():
    """Unit test: Format file stats for empty file."""
    diff_file = DiffFile(
        file_path="test.py",
        added_lines=0,
        removed_lines=0,
        hunks=[]
    )

    result = format_file_stats(diff_file)

    assert result == "0 hunks, +0 -0 lines"
```

### tests/integration/test_markdown_output.py

**Purpose**: End-to-end integration tests

**Test count**: Minimum 5 new tests

**Examples**:

```python
def test_end_to_end_line_comment_with_diff_segment(tmp_path):
    """Integration: Create comment, serialize, verify diff segment in file."""
    # Setup: Create diff and session
    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        lines=[
            (' ', 'def foo():'),
            ('-', '    old'),
            ('+', '    new'),
        ]
    )

    diff_file = DiffFile(file_path="test.py", hunks=[hunk])
    diff_summary = DiffSummary(files=[diff_file])

    comment = LineComment(line_number=3, text="Why?", status="open")
    session = ReviewSession(
        review_id="test",
        branch_name="branch",
        commit_sha="sha",
        file_reviews={
            "test.py": FileReview(file_path="test.py", comments=[comment])
        }
    )

    # Execute: Serialize and write
    output = serialize_review_session(session, diff_summary)
    output_file = tmp_path / "review.md"
    from racgoat.services.markdown_writer import write_markdown_output
    write_markdown_output(output, output_file)

    # Assert: File contains diff segment
    content = output_file.read_text()
    assert "```diff" in content
    assert "-    old" in content
    assert "+    new" in content
```

## Success Criteria Validation

### SC-001: Diff segments in 100% of cases (when diff_summary available)

**Validation**:
- Run all contract tests with `diff_summary` provided
- Assert Context section present in all line/range comment tests
- Verify FR-001 through FR-005 tests pass

### SC-002: Edge case handling without errors

**Validation**:
- FR-007 test: Boundary conditions
- FR-008 test: Malformed hunks
- FR-012 test: Removed-only, added-only, empty hunks
- All tests should pass without exceptions

### SC-003: AI agents can parse output

**Validation**:
- Manual verification: Feed output to GitHub Copilot / Claude
- Check that AI understands "what changed" from diff segments
- Verify FR-011: Standard unified diff format

### SC-004: Performance impact <100ms for 100 comments

**Validation**:
```python
# tests/integration/test_performance/test_diff_segment_performance.py

def test_diff_segment_extraction_performance():
    """Validate <100ms for 100 comments."""
    import time

    # Setup: 100 comments on same diff file
    diff_file = create_large_diff_file()  # Helper function
    comments = [LineComment(line_number=i*10, text=f"Comment {i}", status="open")
                for i in range(100)]

    # Execute: Extract diff segments
    start = time.perf_counter()
    for comment in comments:
        extract_diff_segment(diff_file, line_number=comment.line_number)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    assert elapsed_ms < 100, f"Extraction took {elapsed_ms:.2f}ms (expected <100ms)"
```

### SC-005: Existing tests pass (backward compatibility)

**Validation**:
- Run full test suite: `uv run pytest tests/`
- All 98 existing tests (M1-M7) must pass
- Specifically check Milestone 7 tests (enhanced markdown format)

### SC-006: Minimum 10 new tests

**Validation**:
- Count new tests across test_diff_segments.py (13) + unit tests (12) + integration (5)
- Total: 30 new tests (exceeds requirement)

### SC-007: Human reviewers report improved clarity

**Validation**:
- Manual review of generated output files
- Compare before/after examples (see data-model.md)
- Subjective assessment: Is context clearer with diff segments?

## Test Execution Plan

### Phase 1: Contract Tests (TDD)

1. Create `tests/contract/test_diff_segments.py`
2. Write all 13 FR tests (FR-001 to FR-013)
3. Run tests → All fail (red)
4. Proceed to implementation

### Phase 2: Implementation

1. Implement `extract_diff_segment()` function
2. Implement `format_file_stats()` function
3. Modify `serialize_review_session()` to use new functions
4. Run contract tests → All pass (green)

### Phase 3: Unit Tests

1. Add unit tests to `tests/unit/test_markdown_writer.py`
2. Cover edge cases and individual function behavior
3. Run tests → All pass

### Phase 4: Integration Tests

1. Add integration tests to `tests/integration/test_markdown_output.py`
2. Test end-to-end workflows
3. Run tests → All pass

### Phase 5: Performance Tests

1. Add performance test to `tests/integration/test_performance/`
2. Validate <100ms target
3. Run test → Pass

### Phase 6: Regression Validation

1. Run full test suite: `uv run pytest tests/`
2. Verify all existing tests pass (SC-005)
3. Fix any regressions

## Test Data Requirements

### Sample Diff Files

**Normal diff** (additions + deletions + context):
```python
DiffHunk(
    old_start=10,
    new_start=10,
    lines=[
        (' ', 'def process_data(data):'),
        (' ', '    # Step 1: Validate'),
        ('-', '    if not data:'),
        ('-', '        return None'),
        ('+', '    if not data or not data.is_valid():'),
        ('+', '        raise ValueError("Invalid data")'),
        (' ', '    # Step 2: Process'),
        (' ', '    return transform(data)'),
    ]
)
```

**New file** (only additions):
```python
DiffHunk(
    old_start=0,
    new_start=1,
    lines=[
        ('+', 'def new_function():'),
        ('+', '    pass'),
    ]
)
```

**Deleted file** (only deletions):
```python
DiffHunk(
    old_start=1,
    new_start=0,
    lines=[
        ('-', 'def old_function():'),
        ('-', '    pass'),
    ]
)
```

**Malformed hunk**:
```python
DiffHunk(
    old_start=1,
    new_start=1,
    lines=[],
    is_malformed=True,
    raw_text="@@ -1,5 +1,5 @@\ngarbled content",
    parse_error="Invalid hunk header format"
)
```

**Large hunk** (100+ lines):
```python
large_lines = [(' ', f'line {i}') for i in range(120)]
large_lines[60] = ('+', 'modified line 60')

DiffHunk(old_start=1, new_start=1, lines=large_lines)
```

## Coverage Goals

**Target**: 100% coverage for new/modified functions

**Functions to cover**:
- `extract_diff_segment()` - All branches, all edge cases
- `format_file_stats()` - All input variations
- Modified portions of `serialize_review_session()` - All comment types

**Tools**:
- pytest-cov (if added): `uv run pytest --cov=racgoat.services.markdown_writer`
- Manual verification: Review test cases against function branches

## Acceptance Criteria

All tests must pass before feature is considered complete:
- [ ] 13 contract tests pass (FR-001 to FR-013)
- [ ] 12+ unit tests pass
- [ ] 5+ integration tests pass
- [ ] 1 performance test passes (<100ms target)
- [ ] All 98 existing tests pass (regression check)
- [ ] Manual review confirms improved clarity (SC-007)
