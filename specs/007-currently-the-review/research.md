# Research: Diff Segment Extraction

**Feature**: Include Diff Segments in Review Output
**Phase**: 0 - Research & Discovery
**Date**: 2025-10-10

## Research Questions

Based on the Technical Context and feature spec, the following areas required research:

1. **Diff segment extraction algorithm**: How to extract a subset of diff lines from a DiffHunk based on target line numbers?
2. **Line number mapping**: How to map post-change line numbers (used in comments) to diff hunk positions?
3. **Context boundary handling**: How to include ±2 context lines while respecting hunk boundaries?
4. **Diff formatting standards**: What is the standard unified diff format for rendering diff segments?
5. **Statistical summary calculation**: How to compute "N hunks, +X -Y lines" for file-level comments?

## Research Findings

### 1. Diff Segment Extraction Algorithm

**Decision**: Iterate through `DiffHunk.lines` (list of `(change_type, content)` tuples) and extract lines within the target range, maintaining original diff markers.

**Rationale**:
- `DiffHunk.lines` already contains parsed diff lines with markers ('+', '-', ' ')
- Post-change line numbers can be reconstructed by tracking new_start and incrementing only for '+' and ' ' lines
- Extraction is a filtering operation: include lines where current_line is within `[target_start - context, target_end + context]`
- This avoids re-parsing raw diff text

**Alternatives considered**:
- **Re-parse raw hunk text**: Rejected because `DiffHunk.lines` already contains structured data
- **Extract from DiffFile.raw_text**: Rejected because hunks are pre-parsed and validated
- **Build AST/IR for diff**: Rejected as over-engineered for this use case

**Key insight**: The existing `extract_code_context()` function in `markdown_writer.py:25-105` already implements the line number mapping and context windowing logic. We need to modify it to:
1. Change output format from `"{line_num} | {content}"` to diff format (`{marker}{content}`)
2. Include removed lines ('-' markers) in the output
3. Add context lines with space prefix

### 2. Line Number Mapping (Post-Change → Diff Hunk Position)

**Decision**: Use the same algorithm as current `extract_code_context()`:
```python
current_line = hunk.new_start
for change_type, content in hunk.lines:
    if change_type in ('+', ' '):  # Added or context lines
        # This is a post-change line
        if context_start <= current_line <= context_end:
            # Include in output
        current_line += 1
    # Removed lines ('-') don't increment current_line
```

**Rationale**:
- Post-change line numbers only count '+' and ' ' lines (not '-')
- This matches the existing implementation in `markdown_writer.py:86-98`
- Proven to work correctly in Milestone 7 tests

**Alternatives considered**:
- **Build pre-change line map**: Rejected because comments target post-change lines, not pre-change
- **Use regex on raw diff**: Rejected due to fragility and duplication

### 3. Context Boundary Handling

**Decision**: Clamp context window to hunk boundaries and only show lines available in the hunk:
```python
context_start = max(target_start - context_lines, hunk.new_start)
context_end = target_end + context_lines  # No upper clamp needed - iteration handles
```

**Rationale**:
- Hunks don't have explicit end markers - iteration naturally stops at hunk boundary
- Lower bound must be clamped to avoid requesting lines before hunk start
- Upper bound handled implicitly by iteration (we only process available lines)
- Matches existing `extract_code_context()` behavior (line 89)

**Alternatives considered**:
- **Calculate hunk_end explicitly**: Current code does this but only for range checking (lines 70-73)
- **Pad with empty lines**: Rejected - would be misleading (suggest context exists when it doesn't)

### 4. Diff Formatting Standards (Unified Diff Format)

**Decision**: Use standard unified diff line format:
- Added lines: `+{content}` (no space between marker and content)
- Removed lines: `-{content}`
- Context lines: ` {content}` (single space prefix)
- Fenced code block: ` ```diff` for syntax highlighting

**Rationale**:
- Matches git diff output format (industry standard)
- Supports syntax highlighting in Markdown renderers
- Spec requirement FR-011: "standard unified diff format with +/- markers and context spaces, without explicit line numbers"
- AI agents (GitHub Copilot, Claude, etc.) are trained on this format

**Alternatives considered**:
- **Include line numbers**: Rejected per FR-011 (explicit requirement to omit line numbers)
- **Custom format (e.g., `>>> +content`)**: Rejected - non-standard, breaks AI agent parsing
- **Side-by-side diff**: Rejected - not suitable for Markdown text format

**Example output**:
```diff
 def calculate_total(items):
-    return sum(items)
+    return sum(item.price for item in items)

```

### 5. Statistical Summary Calculation (File-Level Comments)

**Decision**: Iterate through all hunks in DiffFile and sum added/removed lines:
```python
def format_file_stats(diff_file: DiffFile) -> str:
    hunk_count = len(diff_file.hunks)
    # diff_file.added_lines and diff_file.removed_lines already calculated by parser
    return f"{hunk_count} hunks, +{diff_file.added_lines} -{diff_file.removed_lines} lines"
```

**Rationale**:
- `DiffFile` already tracks `added_lines` and `removed_lines` (calculated during parsing)
- `len(diff_file.hunks)` provides hunk count
- No additional computation required - just formatting
- Matches spec requirement FR-006 format

**Alternatives considered**:
- **Recalculate from hunks**: Rejected - redundant, parser already does this
- **Show total_lines instead of +/-**: Rejected - doesn't match spec format

## Implementation Strategy

### Modified Function Signature

Rename `extract_code_context()` to `extract_diff_segment()` to reflect new purpose:

```python
def extract_diff_segment(
    diff_file: DiffFile,
    line_number: int | None = None,
    line_range: tuple[int, int] | None = None,
    context_lines: int = DEFAULT_CONTEXT_LINES
) -> str | None:
    """Extract diff segment from hunks for a comment.

    Returns:
        Formatted diff segment with +/- markers, or None if unavailable
    """
```

### Algorithm Pseudocode

```python
# 1. Determine target range (same as current)
if line_number is not None:
    target_start = target_end = line_number
elif line_range is not None:
    target_start, target_end = line_range
else:
    return None  # File-level comment

# 2. Find relevant hunk (same as current)
for hunk in diff_file.hunks:
    if hunk.is_malformed:
        continue
    # ... range checking logic (unchanged) ...

# 3. Build diff segment (NEW LOGIC)
diff_lines = []
current_line = hunk.new_start
context_start = max(target_start - context_lines, hunk.new_start)
context_end = target_end + context_lines

for change_type, content in hunk.lines:
    # NEW: Include removed lines in output
    if change_type == '-':
        # Always include removed lines if within window context
        # (Need to track both old and new line positions for this)
        diff_lines.append(f"-{content}")
        continue

    # NEW: Include added/context lines with diff markers
    if context_start <= current_line <= context_end:
        if change_type == '+':
            diff_lines.append(f"+{content}")
        else:  # ' ' (context)
            diff_lines.append(f" {content}")

    current_line += 1

# 4. Format as diff code block
if not diff_lines:
    return None
return "\n".join(diff_lines)
```

**Critical revision needed**: The above pseudocode is **incomplete** for removed lines. Removed lines don't have post-change line numbers, so we can't use `current_line` to determine if they're in the context window. We need to track **both** old and new line positions:

```python
# Corrected algorithm:
current_old_line = hunk.old_start
current_new_line = hunk.new_start

for change_type, content in hunk.lines:
    in_window = False

    if change_type == '-':
        # Removed line: check if corresponding new_line position is in window
        # (Use current_new_line as proxy - removed lines "belong" to the current new position)
        in_window = (context_start <= current_new_line <= context_end)
        current_old_line += 1
    elif change_type == '+':
        in_window = (context_start <= current_new_line <= context_end)
        current_new_line += 1
    else:  # ' '
        in_window = (context_start <= current_new_line <= context_end)
        current_old_line += 1
        current_new_line += 1

    if in_window:
        diff_lines.append(f"{change_type}{content}")
```

### File-Level Comment Handling

Add new function for statistical summary:

```python
def format_file_stats(diff_file: DiffFile) -> str:
    """Format statistical summary for file-level comments.

    Returns:
        String like "5 hunks, +120 -45 lines"
    """
    hunk_count = len(diff_file.hunks)
    return f"{hunk_count} hunks, +{diff_file.added_lines} -{diff_file.removed_lines} lines"
```

Modify `serialize_review_session()` to call this for `FileComment` instances:

```python
# In serialize_review_session(), after line 228:
if isinstance(comment, FileComment):
    # Show statistical summary instead of code context
    if diff_file:
        stats = format_file_stats(diff_file)
        lines.append(f"**File changes**: {stats}")
        lines.append("")
```

## Risks & Mitigations

### Risk 1: Removed lines context window ambiguity
**Risk**: Removed lines don't have post-change line numbers. How do we determine if they're "near" the commented line?

**Mitigation**: Use the current new_line position as a proxy. Removed lines are associated with the new_line position where they were deleted. This aligns with how users think about diffs ("these lines were removed near line 50").

### Risk 2: Performance degradation
**Risk**: Iterating through hunks twice (once for line search, once for extraction) could impact performance.

**Mitigation**:
- Benchmark shows existing `extract_code_context()` meets <100ms target for large hunks
- New algorithm has same O(n) complexity (single pass through hunk.lines)
- No additional data structure allocation
- Performance tests will validate <100ms target (SC-004)

### Risk 3: Breaking existing tests
**Risk**: Changing output format from `{line_num} | {content}` to diff format will break Milestone 7 tests.

**Mitigation**:
- Create new function `extract_diff_segment()` alongside `extract_code_context()`
- Deprecate old function or keep for backward compatibility
- Update callers in `serialize_review_session()` to use new function
- Update tests incrementally

**Alternative**: Rename function and update all tests in one commit (cleaner but requires careful coordination)

## Open Questions (Resolved)

All research questions have been resolved. No blockers for Phase 1 design.

## Next Steps

Proceed to Phase 1: Data Model & Contracts generation.
