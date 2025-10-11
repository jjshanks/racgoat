# Function Contracts: Diff Segment Extraction

**Feature**: Include Diff Segments in Review Output
**Date**: 2025-10-10

This document defines the formal contracts for all modified and new functions in this feature.

## Modified Functions

### extract_diff_segment()

**Purpose**: Extract diff segment from hunks for display in review output (replaces `extract_code_context()`).

**Signature**:
```python
def extract_diff_segment(
    diff_file: DiffFile,
    line_number: int | None = None,
    line_range: tuple[int, int] | None = None,
    context_lines: int = DEFAULT_CONTEXT_LINES
) -> str | None
```

**Contract**:

**Preconditions**:
- `diff_file` is not None
- Exactly one of the following holds:
  - `line_number` is an int > 0 and `line_range` is None (line comment)
  - `line_range` is a tuple (start, end) with start <= end, both > 0, and `line_number` is None (range comment)
  - Both `line_number` and `line_range` are None (file-level comment)
- `context_lines >= 0`

**Postconditions**:
- Returns None if:
  - Both `line_number` and `line_range` are None (file-level comment case)
  - No hunk found containing target line(s)
  - Target hunk is malformed (`hunk.is_malformed == True`)
  - No lines within context window (edge case - empty result)
- Returns non-empty string if:
  - Target line(s) found in a well-formed hunk
  - At least one line within context window exists
- If return value is a string:
  - Each line starts with exactly one character: '+', '-', or ' '
  - Lines are in hunk order (preserves original sequence)
  - Context window is clamped to hunk boundaries
  - Format matches unified diff standard (no line numbers)

**Error Handling**:
- Does not raise exceptions (returns None on error/edge cases)
- Malformed hunks are skipped (graceful degradation)

**Performance**:
- Time complexity: O(n) where n = number of lines in the target hunk
- Space complexity: O(m) where m = number of lines in context window (typically ~5)
- Target: <100ms for hunks with 100+ lines

**Examples**:

```python
# Example 1: Line comment at line 50 with default context (±2 lines)
result = extract_diff_segment(diff_file, line_number=50)
# Returns:
# " def calculate_total(items):\n"
# "-    return sum(items)\n"
# "+    return sum(item.price for item in items)\n"
# " \n"

# Example 2: Range comment spanning lines 10-15
result = extract_diff_segment(diff_file, line_range=(10, 15))
# Returns diff segment with all changes in that range + ±2 context

# Example 3: File-level comment
result = extract_diff_segment(diff_file, line_number=None, line_range=None)
# Returns: None

# Example 4: Target line not in any hunk
result = extract_diff_segment(diff_file, line_number=9999)
# Returns: None

# Example 5: Malformed hunk
result = extract_diff_segment(diff_file_with_malformed_hunk, line_number=50)
# Returns: None (graceful fallback)
```

**Test Coverage Required**:
1. Line comment with context → Returns correct segment
2. Range comment → Returns full range + context
3. File-level comment → Returns None
4. Target at hunk start boundary → Context clamped correctly
5. Target at hunk end boundary → Context clamped correctly
6. Malformed hunk → Returns None
7. Target not found in any hunk → Returns None
8. Removed-only lines in window → Included in output
9. Added-only lines in window → Included in output
10. Mixed +/- lines → Both included in output
11. Empty hunk (not possible per DiffHunk validation) → N/A
12. Context lines = 0 → Only target line(s) included

---

### serialize_review_session()

**Purpose**: Serialize ReviewSession to Markdown format with enhanced diff segments.

**Signature** (unchanged):
```python
def serialize_review_session(
    session: ReviewSession,
    diff_summary: DiffSummary | None = None
) -> str
```

**Contract Changes**:

**Postconditions (Modified)**:
- For `LineComment` or `RangeComment`:
  - If `diff_summary` provided and diff segment extracted successfully:
    - **Context** section contains fenced code block with `diff` syntax
    - Code block contains diff segment with +/- markers (no line numbers)
  - If `diff_summary` is None or extraction fails:
    - **Context** section is omitted (backward compatibility)
- For `FileComment`:
  - If `diff_summary` provided:
    - **File changes** section shows statistical summary: `"{N} hunks, +{X} -{Y} lines"`
  - If `diff_summary` is None:
    - **File changes** section is omitted

**Backward Compatibility**:
- When `diff_summary` is None, behavior is identical to Milestone 7 (no context display)
- Existing tests that don't provide `diff_summary` see no changes

**Example Output Diff**:

**Before (Milestone 7)**:
```markdown
### Line 50
Consider optimizing this loop.

**Context**:
```
48 | def calculate_total(items):
49 |     # TODO: optimize
50 |     return sum(item.price for item in items)
51 |
52 | def process_order(order):
```
```

**After (This Feature)**:
```markdown
### Line 50
Consider optimizing this loop.

**Context**:
```diff
 def calculate_total(items):
-    return sum(items)
+    return sum(item.price for item in items)

```
```

---

## New Functions

### format_file_stats()

**Purpose**: Format statistical summary of file changes for file-level comments.

**Signature**:
```python
def format_file_stats(diff_file: DiffFile) -> str
```

**Contract**:

**Preconditions**:
- `diff_file` is not None

**Postconditions**:
- Returns string in exact format: `"{hunk_count} hunks, +{added} -{removed} lines"`
- `hunk_count = len(diff_file.hunks)`
- `added = diff_file.added_lines`
- `removed = diff_file.removed_lines`
- Never returns None or empty string
- All counts are non-negative integers

**Error Handling**:
- Does not raise exceptions
- Handles edge cases gracefully (0 hunks, binary files, etc.)

**Performance**:
- Time complexity: O(1) (all values pre-calculated)
- Space complexity: O(1)

**Examples**:

```python
# Example 1: Normal file
result = format_file_stats(diff_file)
# Returns: "5 hunks, +120 -45 lines"

# Example 2: New file (only additions)
result = format_file_stats(new_file)
# Returns: "3 hunks, +150 -0 lines"

# Example 3: Deleted file (only removals)
result = format_file_stats(deleted_file)
# Returns: "2 hunks, +0 -100 lines"

# Example 4: Empty file (no changes)
result = format_file_stats(empty_file)
# Returns: "0 hunks, +0 -0 lines"

# Example 5: Binary file
result = format_file_stats(binary_file)
# Returns: "0 hunks, +0 -0 lines" (binary files have no hunks)
```

**Test Coverage Required**:
1. Normal file → Correct format
2. New file (only additions) → "+N -0"
3. Deleted file (only removals) → "+0 -N"
4. Empty file → "0 hunks, +0 -0 lines"
5. Binary file → "0 hunks, +0 -0 lines"
6. Single hunk → "1 hunks, ..." (grammatically awkward but consistent)

---

## Integration Points

### Caller: serialize_review_session()

**Current Implementation** (Milestone 7):
```python
# Around line 220 in markdown_writer.py
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

**New Implementation**:
```python
# Modified version
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
        # NEW: File-level comment shows stats
        stats = format_file_stats(diff_file)
        lines.append(f"**File changes**: {stats}")
        lines.append("")
```

**Changes**:
1. Rename `extract_code_context()` calls to `extract_diff_segment()`
2. Change fenced code block from ` ``` ` to ` ```diff `
3. Add file-level comment handling with `format_file_stats()`

---

## Backward Compatibility Guarantees

1. **When `diff_summary` is None**:
   - No context sections are added (same as before)
   - All tests without `diff_summary` pass unchanged

2. **Existing function signatures**:
   - `serialize_review_session()` signature unchanged
   - `write_markdown_output()` signature unchanged

3. **Markdown structure**:
   - YAML frontmatter unchanged
   - HTML comment metadata unchanged
   - File/comment ordering unchanged
   - Only **Context** section format changes (code → diff)

4. **Data models**:
   - No changes to Comment models
   - No changes to DiffHunk/DiffFile/DiffSummary
   - Pure transformation layer modification

---

## Validation & Testing Strategy

### Contract Test Suite (tests/contract/test_diff_segments.py)

**Purpose**: Validate all 13 functional requirements (FR-001 to FR-013)

**Test cases** (minimum 13 tests, one per FR):

1. **FR-001**: `test_diff_segment_included_for_line_comment()`
   - Create line comment → Serialize → Assert Context section exists with diff markers

2. **FR-002**: `test_before_after_states_shown()`
   - Diff with modification (- and + lines) → Assert both markers present in output

3. **FR-003**: `test_context_lines_included()`
   - Line comment with surrounding context → Assert context lines have space prefix

4. **FR-004**: `test_line_comment_has_two_context_lines()`
   - Line comment at line 50 → Assert ±2 lines included (lines 48-52)

5. **FR-005**: `test_range_comment_includes_full_range_plus_context()`
   - Range comment 10-15 → Assert all lines 8-17 included (±2 context)

6. **FR-006**: `test_file_comment_shows_statistical_summary()`
   - File comment → Assert "N hunks, +X -Y lines" format in output

7. **FR-007**: `test_boundary_respect()`
   - Comment at hunk start (new_start=1) → Assert no lines before hunk

8. **FR-008**: `test_malformed_hunk_graceful_handling()`
   - Comment on malformed hunk → Assert no Context section (no crash)

9. **FR-009**: `test_fenced_code_block_with_diff_syntax()`
   - Any comment → Assert ` ```diff ` in output

10. **FR-010**: `test_backward_compatibility_no_diff_summary()`
    - Serialize without diff_summary → Assert no Context section

11. **FR-011**: `test_unified_diff_format()`
    - Verify output matches regex: `^[ +-].*$` for each line (no line numbers)

12. **FR-012**: `test_edge_cases()`
    - Subtest: Removed-only hunk → Assert '-' markers
    - Subtest: Added-only hunk → Assert '+' markers
    - Subtest: Boundary line (at hunk end) → Assert correct context

13. **FR-013**: `test_no_truncation_for_large_hunks()`
    - Hunk with 100+ lines, comment in middle → Assert full context included (not truncated)

### Unit Test Suite (tests/unit/test_markdown_writer.py)

**Purpose**: Validate individual function behavior in isolation

**Test cases** (minimum 12 tests):

1. `test_extract_diff_segment_line_comment()`
2. `test_extract_diff_segment_range_comment()`
3. `test_extract_diff_segment_file_comment_returns_none()`
4. `test_extract_diff_segment_boundary_start()`
5. `test_extract_diff_segment_boundary_end()`
6. `test_extract_diff_segment_malformed_hunk()`
7. `test_extract_diff_segment_target_not_found()`
8. `test_extract_diff_segment_removed_lines_included()`
9. `test_extract_diff_segment_context_zero()`
10. `test_format_file_stats_normal_file()`
11. `test_format_file_stats_new_file()`
12. `test_format_file_stats_empty_file()`

### Integration Test Suite (tests/integration/test_markdown_output.py)

**Purpose**: Validate end-to-end workflow

**Test cases** (minimum 5 tests):

1. `test_end_to_end_line_comment_with_diff_segment()`
   - Create comment in TUI → Serialize → Verify diff segment in file

2. `test_end_to_end_range_comment_with_diff_segment()`
   - Create range comment → Serialize → Verify diff segment

3. `test_end_to_end_file_comment_with_stats()`
   - Create file comment → Serialize → Verify statistical summary

4. `test_multiple_comments_same_file()`
   - 3 comments in one file → Verify each has correct segment

5. `test_large_hunk_no_truncation()`
   - 100+ line hunk → Verify full context included

---

## Performance Contracts

### Performance Targets (from SC-004)

**Target**: Extracting and formatting diff segments adds <100ms to serialization time for 100 comments

**Breakdown**:
- Per-comment extraction: <1ms (100 comments × 1ms = 100ms total)
- Allows for 10x safety margin on individual calls

**Measurement Strategy**:
```python
# In performance test
import time

start = time.perf_counter()
for comment in comments:  # 100 comments
    extract_diff_segment(diff_file, line_number=comment.line_number)
end = time.perf_counter()

assert (end - start) < 0.1  # <100ms for 100 comments
```

**Optimization Notes**:
- Hunk search is O(n) per comment (unavoidable)
- Could optimize with hunk line range index (future enhancement)
- String concatenation uses list + join (efficient)

---

## Deprecation Plan

### Option A: In-place Replacement (Recommended)

1. Rename `extract_code_context()` to `extract_diff_segment()`
2. Update all callers in `serialize_review_session()`
3. Update all tests in single commit
4. No deprecation period needed (internal function)

**Pros**: Clean, no legacy code
**Cons**: Larger single commit

### Option B: Gradual Migration

1. Create new `extract_diff_segment()` function
2. Mark `extract_code_context()` as deprecated (docstring + comment)
3. Migrate callers incrementally
4. Remove deprecated function in follow-up PR

**Pros**: Smaller commits, easier review
**Cons**: More code churn, temporary duplication

**Decision**: **Option A** - Internal function, single feature branch, cleaner outcome
