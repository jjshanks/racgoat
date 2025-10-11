# Data Model: Diff Segment Extraction

**Feature**: Include Diff Segments in Review Output
**Phase**: 1 - Design
**Date**: 2025-10-10

## Overview

This feature does **not introduce new data entities** - it modifies the serialization logic for existing entities. The data model focuses on the **transformation** from `DiffHunk` to formatted diff segments.

## Existing Entities (Read-Only)

### DiffHunk (from `racgoat/parser/models.py`)

**Purpose**: Represents a parsed hunk from a git diff with line-level detail.

**Attributes**:
- `old_start: int` - Starting line number in old file (0 = new file)
- `new_start: int` - Starting line number in new file (0 = deleted file)
- `lines: list[tuple[str, str]]` - List of (change_type, content) tuples
  - `change_type`: '+' (added), '-' (removed), ' ' (context)
  - `content`: Line text without prefix marker
- `is_malformed: bool` - True if hunk failed parsing
- `raw_text: str | None` - Unparsed text for malformed hunks
- `parse_error: str | None` - Error description for malformed hunks

**Validation**:
- Line numbers must be >= 0
- `change_type` must be one of '+', '-', ' '
- Malformed hunks must have `raw_text`

**Usage in this feature**:
- Input to `extract_diff_segment()` function
- Source of diff lines for extraction
- Boundary constraints for context window

### DiffFile (from `racgoat/parser/models.py`)

**Purpose**: Represents a file in the diff with metadata and hunks.

**Attributes**:
- `file_path: str` - Path to file
- `added_lines: int` - Count of '+' lines (calculated by parser)
- `removed_lines: int` - Count of '-' lines (calculated by parser)
- `is_binary: bool` - Binary file marker
- `hunks: list[DiffHunk]` - List of hunks for this file
- `total_lines: int` - Sum of all hunk line counts
- `has_malformed_hunks: bool` - True if any hunk is malformed

**Usage in this feature**:
- Input to `extract_diff_segment()` function
- Source of `added_lines`/`removed_lines` for statistical summary
- Container for hunks to search

### Comment Models (from `racgoat/models/comments.py`)

**Purpose**: Store user comments and their targets.

**Relevant types**:
- `LineComment` - Has `line_number: int` (post-change line number)
- `RangeComment` - Has `start_line: int, end_line: int` (post-change range)
- `FileComment` - No line reference (file-level)

**Usage in this feature**:
- Determines which extraction function to call (`extract_diff_segment()` vs. `format_file_stats()`)
- Provides target line numbers for diff segment extraction

## New Data Structures

### DiffSegment (Conceptual - Not a Class)

**Purpose**: Represents the extracted subset of a hunk for display in review output.

**Structure**: String (formatted text), not a class
- **Format**: Multi-line string with diff markers
- **Example**:
  ```diff
   def calculate_total(items):
  -    return sum(items)
  +    return sum(item.price for item in items)

  ```

**Derivation**: Extracted from `DiffHunk.lines` by filtering and formatting:
1. Filter lines within context window `[target - context, target + context]`
2. Format each line as `{change_type}{content}` (no space after marker for +/-)
3. Join with newlines

**Validation**: None (output-only, no persistence)

### FileStatsSummary (Conceptual - Not a Class)

**Purpose**: Statistical summary of file changes for file-level comments.

**Structure**: String (formatted text), not a class
- **Format**: `"{hunk_count} hunks, +{added} -{removed} lines"`
- **Example**: `"5 hunks, +120 -45 lines"`

**Derivation**: Formatted from `DiffFile` attributes:
```python
f"{len(diff_file.hunks)} hunks, +{diff_file.added_lines} -{diff_file.removed_lines} lines"
```

**Validation**: None (output-only, no persistence)

## Data Flow

```
[User creates comment in TUI]
    ↓
[Comment stored with line_number/range] (LineComment/RangeComment/FileComment)
    ↓
[User quits TUI → serialize_review_session() called]
    ↓
┌─────────────────────────────────────────────────┐
│ For each comment:                                │
│   if LineComment or RangeComment:               │
│     → extract_diff_segment(diff_file, ...)       │
│       → Find relevant hunk                       │
│       → Filter lines in context window          │
│       → Format as diff segment                  │
│   elif FileComment:                             │
│     → format_file_stats(diff_file)              │
│       → Count hunks                             │
│       → Format as statistical summary           │
└─────────────────────────────────────────────────┘
    ↓
[Markdown output with diff segments / stats]
    ↓
[write_markdown_output() writes to file]
```

## Function Contracts

### extract_diff_segment()

**Signature**:
```python
def extract_diff_segment(
    diff_file: DiffFile,
    line_number: int | None = None,
    line_range: tuple[int, int] | None = None,
    context_lines: int = DEFAULT_CONTEXT_LINES
) -> str | None
```

**Inputs**:
- `diff_file`: DiffFile containing hunks to search (required, non-null)
- `line_number`: Target line for line comment (post-change numbering), mutually exclusive with `line_range`
- `line_range`: Target range (start, end) for range comment (post-change numbering), mutually exclusive with `line_number`
- `context_lines`: Number of context lines before/after target (default: 2)

**Outputs**:
- Returns: String containing diff segment with markers, or None if:
  - Both `line_number` and `line_range` are None (file-level comment)
  - No hunk found containing target line(s)
  - Hunk is malformed
  - No lines within context window (edge case)

**Preconditions**:
- `diff_file` is not None
- If `line_number` provided: `line_number > 0`
- If `line_range` provided: `start <= end` and both `> 0`
- Exactly one of `line_number`, `line_range`, or neither (file-level) is provided

**Postconditions**:
- If return value is not None:
  - String contains only lines from the relevant hunk
  - Each line starts with '+', '-', or ' '
  - Lines are ordered as they appear in hunk
  - Context window respects hunk boundaries
- If return value is None:
  - No exception raised (graceful fallback)

**Edge cases**:
- Target line at hunk boundary → Context window clamped to hunk bounds
- Malformed hunk → Returns None
- Empty hunk (impossible per DiffHunk validation) → N/A
- Target line not found in any hunk → Returns None

### format_file_stats()

**Signature**:
```python
def format_file_stats(diff_file: DiffFile) -> str
```

**Inputs**:
- `diff_file`: DiffFile containing hunks and line counts (required, non-null)

**Outputs**:
- Returns: String in format `"{hunk_count} hunks, +{added} -{removed} lines"`
- Never returns None (always produces output, even if counts are 0)

**Preconditions**:
- `diff_file` is not None

**Postconditions**:
- String matches format exactly: `"{int} hunks, +{int} -{int} lines"`
- Counts are non-negative

**Edge cases**:
- No hunks (empty file) → `"0 hunks, +0 -0 lines"`
- Binary file → Uses available counts (may be 0)

## Serialization Format Changes

### Before (Milestone 7 - Post-change code context)

```markdown
### Line 50
Consider using a more efficient algorithm here.

**Context**:
```
48 | def calculate_total(items):
49 |     # TODO: optimize
50 |     return sum(item.price for item in items)
51 |
52 | def process_order(order):
```
```

**Issues**:
- Only shows post-change code (no before state)
- Includes line numbers (redundant with heading)
- Missing context about what was removed/modified

### After (This Feature - Diff segment)

```markdown
### Line 50
Consider using a more efficient algorithm here.

**Context**:
```diff
 def calculate_total(items):
-    return sum(items)
+    return sum(item.price for item in items)

```
```

**Improvements**:
- Shows before/after with -/+ markers
- No redundant line numbers
- Clear indication of what changed
- Standard diff format parseable by AI agents

### File-level Comment

```markdown
### File-level comment
This file needs comprehensive test coverage.

**File changes**: 5 hunks, +120 -45 lines
```

## Validation Rules

### Input Validation

1. **Line number validity** (enforced by existing code):
   - Must be > 0 (post-change line numbering starts at 1)
   - Must fall within a hunk's range

2. **Range validity** (enforced by existing code):
   - `start_line <= end_line`
   - Both must be > 0

3. **Context lines** (new):
   - Must be >= 0
   - DEFAULT_CONTEXT_LINES = 2 (from constants.py)

### Output Validation

1. **Diff segment format**:
   - Each line must start with exactly one of: '+', '-', ' '
   - No empty lines (unless hunk contains empty lines with markers)
   - Lines must be in hunk order (no sorting/reordering)

2. **Statistical summary format**:
   - Must match regex: `^\d+ hunks, \+\d+ -\d+ lines$`

## Migration Notes

**Backward Compatibility**:
- FR-010 requires: When `diff_summary` is None, skip diff segment display
- Existing tests that don't provide `diff_summary` will see no change
- Tests that provide `diff_summary` will need output format updates

**No Database/Schema Changes**:
- This is a pure transformation layer change
- No persistent storage modifications
- In-memory data structures unchanged

**Deprecation**:
- `extract_code_context()` function can be:
  - **Option A**: Replaced entirely (cleaner, requires all tests updated)
  - **Option B**: Deprecated with new `extract_diff_segment()` alongside (safer, supports gradual migration)
- Recommendation: **Option A** - Single feature branch, update all callers in one commit

## Testing Implications

### Unit Tests (test_markdown_writer.py)

Test coverage required for `extract_diff_segment()`:
1. Line comment → Extracts correct segment with context
2. Range comment → Extracts full range with context
3. File-level comment → Returns None
4. Boundary conditions: Target at hunk start/end
5. Malformed hunk → Returns None gracefully
6. No hunk found → Returns None
7. Removed-only lines in window → Included in output
8. Added-only lines in window → Included in output
9. Mixed additions/deletions → Both included

Test coverage required for `format_file_stats()`:
1. Normal file → Correct format
2. Empty file (0 hunks) → "0 hunks, +0 -0 lines"
3. Binary file → Uses available counts

### Contract Tests (test_diff_segments.py)

Validate requirements FR-001 through FR-013:
1. FR-001: Diff segments included for line/range comments
2. FR-002: Before/after states shown with +/- markers
3. FR-003: Context lines included with space prefix
4. FR-004: Line comments have ±2 context
5. FR-005: Range comments include full range + ±2 context
6. FR-006: File comments show statistical summary
7. FR-007: Boundary respect (no out-of-hunk context)
8. FR-008: Malformed hunk handling
9. FR-009: Fenced code blocks with ```diff
10. FR-010: Backward compatibility (no diff_summary)
11. FR-011: Standard unified diff format
12. FR-012: Edge cases (boundary, removed-only, added-only, empty)
13. FR-013: No truncation for large hunks

### Integration Tests (test_markdown_output.py)

End-to-end scenarios:
1. Create comment → Serialize → Verify diff segment in output
2. Multiple comments in same file → All have correct segments
3. File comment → Verify statistical summary
4. Large hunk (100+ lines) → No truncation

## Performance Considerations

**Time Complexity**:
- `extract_diff_segment()`: O(n) where n = number of lines in hunk
- `format_file_stats()`: O(1) (counts pre-calculated by parser)

**Space Complexity**:
- O(m) where m = number of lines in context window (typically ±2, so ~5 lines)

**Expected Performance**:
- Target: <100ms per comment (SC-004)
- Existing `extract_code_context()` meets this target
- New implementation has same complexity

**Bottlenecks**:
- Hunk iteration (unavoidable - O(n))
- String concatenation (use list + join pattern)

**Optimizations**:
- Pre-calculate hunk line ranges (existing code does this)
- Early exit when hunk found (existing code does this)
- Reuse DEFAULT_CONTEXT_LINES constant (avoid parameter passing)
