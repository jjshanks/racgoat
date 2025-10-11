# Quick Start: Diff Segment Implementation

**Feature**: Include Diff Segments in Review Output
**Branch**: `007-currently-the-review`
**Date**: 2025-10-10

This guide provides a step-by-step walkthrough for implementing diff segment extraction in RacGoat's review output.

## Overview

**Goal**: Replace post-change code context with actual diff segments (showing +/- markers) in review.md output.

**Estimated time**: 4-6 hours (including testing)

**Files to modify**:
- `racgoat/services/markdown_writer.py` (primary target)
- `tests/contract/test_diff_segments.py` (new file - 13 tests)
- `tests/unit/test_markdown_writer.py` (extend with 12+ tests)
- `tests/integration/test_markdown_output.py` (extend with 5+ tests)

## Prerequisites

**Environment setup**:
```bash
# Ensure you're on the feature branch
git checkout 007-currently-the-review

# Verify dependencies
uv sync

# Run existing tests to establish baseline
uv run pytest tests/
# Expected: All 98 tests passing (M1-M7)
```

**Review planning docs**:
- `specs/007-currently-the-review/spec.md` - Requirements
- `specs/007-currently-the-review/research.md` - Algorithm research
- `specs/007-currently-the-review/data-model.md` - Data structures
- `specs/007-currently-the-review/contracts/` - Function contracts

## Implementation Workflow

### Step 1: Write Contract Tests (TDD - Red Phase)

**Time**: 1-2 hours

**Create**: `tests/contract/test_diff_segments.py`

```bash
# Create test file
touch tests/contract/test_diff_segments.py
```

**Add fixtures and tests**:

```python
# tests/contract/test_diff_segments.py

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
        review_id="test-review",
        branch_name="feature-branch",
        commit_sha="abc123",
        file_reviews={}
    )


def test_diff_segment_included_for_line_comment(sample_diff_file, sample_review_session):
    """FR-001: Verify diff segment is included for line comments."""
    # Setup
    comment = LineComment(line_number=3, text="Optimize this", status="open")
    sample_review_session.file_reviews["example.py"] = FileReview(
        file_path="example.py",
        comments=[comment]
    )

    # Execute
    diff_summary = DiffSummary(files=[sample_diff_file])
    output = serialize_review_session(sample_review_session, diff_summary)

    # Assert
    assert "**Context**:" in output
    assert "```diff" in output
    assert "+    return sum(item.price for item in items)" in output


# Add remaining 12 tests (FR-002 to FR-013)
# See contracts/test_requirements.md for full test list
```

**Run tests (should fail)**:
```bash
uv run pytest tests/contract/test_diff_segments.py -v
# Expected: All tests fail (functions not yet implemented)
```

**Checkpoint**: All 13 contract tests written and failing (RED).

### Step 2: Implement `extract_diff_segment()` Function

**Time**: 1-2 hours

**Edit**: `racgoat/services/markdown_writer.py`

**Action 1**: Replace `extract_code_context()` with `extract_diff_segment()`

**Location**: Lines 25-105 in `markdown_writer.py`

**New implementation**:

```python
def extract_diff_segment(
    diff_file: DiffFile,
    line_number: int | None = None,
    line_range: tuple[int, int] | None = None,
    context_lines: int = DEFAULT_CONTEXT_LINES
) -> str | None:
    """Extract diff segment from hunks for a comment.

    Args:
        diff_file: DiffFile containing hunks to search
        line_number: Target line number for line comments (post-change)
        line_range: Target line range for range comments (start, end) (post-change)
        context_lines: Number of context lines before/after target (default: DEFAULT_CONTEXT_LINES)

    Returns:
        Formatted diff segment with +/- markers, or None if unavailable

    Logic:
        - For line comments: Extract ±context_lines around line_number
        - For range comments: Extract ±context_lines around range boundaries
        - For file comments (both None): Return None
        - Include removed lines ('-') in the context window
        - Format: "{marker}{content}" (no space after marker)
    """
    # File-level comment - no segment
    if line_number is None and line_range is None:
        return None

    # Determine target range
    if line_number is not None:
        target_start = line_number
        target_end = line_number
    else:
        if line_range is None:
            return None
        target_start, target_end = line_range

    # Find hunk containing target line(s)
    relevant_hunk = None
    for hunk in diff_file.hunks:
        # Skip malformed hunks
        if hunk.is_malformed:
            continue

        # Calculate line range for this hunk (post-change)
        hunk_start = hunk.new_start
        # Count added and context lines to find end
        new_line_count = sum(1 for change_type, _ in hunk.lines if change_type in ('+', ' '))
        hunk_end = hunk_start + new_line_count - 1

        # Check if target is within this hunk
        if hunk_start <= target_start <= hunk_end:
            relevant_hunk = hunk
            break

    # No hunk found
    if relevant_hunk is None:
        return None

    # Build diff segment with line markers
    diff_lines = []
    current_new_line = relevant_hunk.new_start

    # Calculate context window
    context_start = max(target_start - context_lines, relevant_hunk.new_start)
    context_end = target_end + context_lines

    for change_type, content in relevant_hunk.lines:
        in_window = False

        # Determine if line is within context window
        if change_type == '-':
            # Removed line: associate with current new_line position
            in_window = (context_start <= current_new_line <= context_end)
        elif change_type in ('+', ' '):
            # Added or context line: check against new_line position
            in_window = (context_start <= current_new_line <= context_end)
            current_new_line += 1

        # Include line if in window
        if in_window:
            diff_lines.append(f"{change_type}{content}")

    # Format as diff segment
    if not diff_lines:
        return None

    return "\n".join(diff_lines)
```

**Key changes from old `extract_code_context()`**:
1. **Function name**: `extract_code_context` → `extract_diff_segment`
2. **Output format**: `"{line_num} | {content}"` → `"{marker}{content}"`
3. **Include removed lines**: Now includes '-' lines in output
4. **Removed line handling**: Track `current_new_line` to associate removed lines with context window

**Action 2**: Add `format_file_stats()` function

**Location**: After `extract_diff_segment()`, before `serialize_review_session()`

```python
def format_file_stats(diff_file: DiffFile) -> str:
    """Format statistical summary for file-level comments.

    Args:
        diff_file: DiffFile containing hunks and line counts

    Returns:
        String like "5 hunks, +120 -45 lines"
    """
    hunk_count = len(diff_file.hunks)
    return f"{hunk_count} hunks, +{diff_file.added_lines} -{diff_file.removed_lines} lines"
```

**Checkpoint**: Functions implemented but not yet integrated.

### Step 3: Update `serialize_review_session()` Function

**Time**: 30 minutes

**Edit**: `racgoat/services/markdown_writer.py` (around line 220)

**Find this section**:
```python
# Code context (if available)
if diff_file:
    if isinstance(comment, LineComment):
        context = extract_code_context(diff_file, line_number=comment.line_number)
    elif isinstance(comment, RangeComment):
        context = extract_code_context(
            diff_file,
            line_range=(comment.start_line, comment.end_line)
        )
    else:
        context = None

    if context:
        lines.append("**Context**:")
        lines.append("```")
        lines.append(context)
        lines.append("```")
        lines.append("")
```

**Replace with**:
```python
# Code context (if available)
if diff_file:
    if isinstance(comment, LineComment):
        diff_segment = extract_diff_segment(diff_file, line_number=comment.line_number)
        if diff_segment:
            lines.append("**Context**:")
            lines.append("```diff")  # Changed: add 'diff' syntax
            lines.append(diff_segment)
            lines.append("```")
            lines.append("")
    elif isinstance(comment, RangeComment):
        diff_segment = extract_diff_segment(
            diff_file,
            line_range=(comment.start_line, comment.end_line)
        )
        if diff_segment:
            lines.append("**Context**:")
            lines.append("```diff")  # Changed: add 'diff' syntax
            lines.append(diff_segment)
            lines.append("```")
            lines.append("")
    elif isinstance(comment, FileComment):
        # NEW: File-level comment shows statistical summary
        stats = format_file_stats(diff_file)
        lines.append(f"**File changes**: {stats}")
        lines.append("")
```

**Changes**:
1. Rename `extract_code_context()` calls to `extract_diff_segment()`
2. Change ` ``` ` to ` ```diff ` for syntax highlighting
3. Add file-level comment handling with `format_file_stats()`

**Checkpoint**: Integration complete.

### Step 4: Run Contract Tests (TDD - Green Phase)

**Time**: 15 minutes

```bash
uv run pytest tests/contract/test_diff_segments.py -v
```

**Expected**: All 13 tests passing (GREEN).

**If tests fail**:
- Review error messages
- Check diff segment format (markers, line content)
- Verify context window logic
- Debug with print statements or pytest's `-s` flag

### Step 5: Write Unit Tests

**Time**: 1 hour

**Edit**: `tests/unit/test_markdown_writer.py`

**Add tests** (see `contracts/test_requirements.md` for full list):

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

    # Assert
    assert result is not None
    assert ' def foo():' in result
    assert '-    return 1' in result
    assert '+    return 2' in result


def test_extract_diff_segment_file_comment_returns_none():
    """Unit test: File-level comment returns None."""
    diff_file = DiffFile(file_path="test.py", hunks=[])

    result = extract_diff_segment(diff_file, line_number=None, line_range=None)

    assert result is None


def test_format_file_stats_normal_file():
    """Unit test: Format file stats."""
    diff_file = DiffFile(
        file_path="test.py",
        added_lines=120,
        removed_lines=45,
        hunks=[DiffHunk(old_start=1, new_start=1, lines=[(' ', 'x')])] * 5
    )

    result = format_file_stats(diff_file)

    assert result == "5 hunks, +120 -45 lines"


# Add remaining 9 unit tests (see contracts/test_requirements.md)
```

**Run tests**:
```bash
uv run pytest tests/unit/test_markdown_writer.py -v
```

**Expected**: All new unit tests passing.

### Step 6: Add Integration Tests

**Time**: 30 minutes

**Edit**: `tests/integration/test_markdown_output.py`

**Add end-to-end tests**:

```python
def test_end_to_end_line_comment_with_diff_segment(tmp_path):
    """Integration: Create comment, serialize, verify diff segment in file."""
    from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
    from racgoat.models.comments import ReviewSession, FileReview, LineComment
    from racgoat.parser.models import DiffFile, DiffHunk, DiffSummary

    # Setup
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

    # Execute
    output = serialize_review_session(session, diff_summary)
    output_file = tmp_path / "review.md"
    write_markdown_output(output, output_file)

    # Assert
    content = output_file.read_text()
    assert "```diff" in content
    assert "-    old" in content
    assert "+    new" in content


# Add remaining 4 integration tests
```

**Run tests**:
```bash
uv run pytest tests/integration/test_markdown_output.py -v
```

### Step 7: Run Full Test Suite (Regression Check)

**Time**: 5 minutes

```bash
uv run pytest tests/ -v
```

**Expected**: All 128+ tests passing (98 existing + 30 new)

**If any existing tests fail**:
- Check if tests rely on old `extract_code_context()` format
- Update test expectations to match new diff format
- Ensure backward compatibility (diff_summary=None case)

### Step 8: Performance Validation

**Time**: 15 minutes

**Create**: `tests/integration/test_performance/test_diff_segment_performance.py`

```python
import time
import pytest
from racgoat.services.markdown_writer import extract_diff_segment
from racgoat.parser.models import DiffFile, DiffHunk


def test_diff_segment_extraction_performance():
    """Validate <100ms for 100 comments."""
    # Create large hunk
    large_lines = [(' ', f'line {i}') for i in range(1000)]
    large_hunk = DiffHunk(old_start=1, new_start=1, lines=large_lines)
    diff_file = DiffFile(file_path="large.py", hunks=[large_hunk])

    # Execute 100 extractions
    start = time.perf_counter()
    for i in range(100):
        extract_diff_segment(diff_file, line_number=i * 10)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    assert elapsed_ms < 100, f"Extraction took {elapsed_ms:.2f}ms (expected <100ms)"
```

**Run test**:
```bash
uv run pytest tests/integration/test_performance/test_diff_segment_performance.py -v
```

**Expected**: Test passes (<100ms).

## Verification Checklist

Before marking feature complete, verify:

- [ ] All 13 contract tests pass (FR-001 to FR-013)
- [ ] All 12+ unit tests pass
- [ ] All 5+ integration tests pass
- [ ] Performance test passes (<100ms for 100 comments)
- [ ] All 98 existing tests pass (no regressions)
- [ ] Manual review of sample output (improved clarity)

## Manual Testing

**Generate sample review**:

```bash
# Create a sample diff
git diff HEAD~1 > sample.diff

# Run RacGoat
uv run python -m racgoat -o review.md < sample.diff

# In TUI:
# - Add a line comment (press 'c' on a modified line)
# - Add a range comment (press 's' to enter Select Mode, then 's' again to add comment)
# - Add a file-level comment (press 'Shift+C')
# - Quit (press 'q')

# Review output
cat review.md
```

**Verify output**:
1. Line comment has `**Context**:` section with ` ```diff ` block
2. Diff segment shows +/- markers (not line numbers)
3. Range comment shows full range with context
4. File comment shows "N hunks, +X -Y lines"

## Example Output (Before vs. After)

### Before (Milestone 7)

```markdown
### Line 50
Consider using a more efficient algorithm.

**Context**:
```
48 | def calculate_total(items):
49 |     # TODO: optimize
50 |     return sum(item.price for item in items)
51 |
52 | def process_order(order):
```
```

### After (This Feature)

```markdown
### Line 50
Consider using a more efficient algorithm.

**Context**:
```diff
 def calculate_total(items):
-    return sum(items)
+    return sum(item.price for item in items)

```
```

**Improvement**: Clear before/after context with standard diff markers.

## Troubleshooting

### Issue: Tests fail with "extract_code_context not found"

**Cause**: Old function name still referenced somewhere.

**Fix**: Search codebase for `extract_code_context` and replace with `extract_diff_segment`:
```bash
grep -r "extract_code_context" racgoat/ tests/
```

### Issue: Diff segment missing removed lines

**Cause**: Removed lines ('-') not included in context window logic.

**Fix**: Verify `in_window` logic for `change_type == '-'` uses `current_new_line` position.

### Issue: Performance test fails (>100ms)

**Cause**: Inefficient string concatenation or hunk iteration.

**Fix**:
- Use list + join pattern (already implemented)
- Profile with `pytest --profile` or manual timing
- Check if hunk iteration can be optimized

### Issue: Output has extra blank lines

**Cause**: Diff format includes empty context lines with space prefix.

**Expected**: This is correct behavior (matches unified diff format).

## Next Steps

After implementation complete:

1. **Code review**: Review changes for readability and adherence to contracts
2. **Documentation**: Update CLAUDE.md if needed (likely not required)
3. **Commit**: Create commit with episodic story format (see /ep-commit command)
4. **Manual testing**: Test with real diffs from the repository
5. **Phase 2**: Run `/speckit.tasks` to generate implementation tasks (if needed)

## Success Criteria Summary

**Functionality**:
- ✅ Diff segments included for line/range comments (FR-001 to FR-005)
- ✅ File-level comments show statistical summary (FR-006)
- ✅ Edge cases handled gracefully (FR-007, FR-008, FR-012)
- ✅ Standard unified diff format (FR-009, FR-011)
- ✅ Backward compatible (FR-010)

**Quality**:
- ✅ Minimum 30 tests added (exceeds 10-test requirement)
- ✅ All existing tests pass (no regressions)
- ✅ Performance target met (<100ms for 100 comments)

**Usability**:
- ✅ Human reviewers can see before/after context
- ✅ AI agents can parse diff segments
