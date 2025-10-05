# Data Model: Performance Hardening & Final Polish

## Enhanced Parser Models

### DiffHunk (Extended)
**Purpose**: Represent a contiguous block of changes with malformed hunk support

**Fields**:
- `old_start: int` - Starting line number in original file
- `old_count: int` - Number of lines in original file
- `new_start: int` - Starting line number in modified file
- `new_count: int` - Number of lines in modified file
- `lines: List[str]` - Actual diff lines (with +/- prefixes)
- `is_malformed: bool` - NEW: True if hunk failed parsing validation
- `raw_text: Optional[str]` - NEW: Unparsed hunk text when is_malformed=True
- `parse_error: Optional[str]` - NEW: Error description for debugging

**Validation Rules**:
- If `is_malformed=True`: `raw_text` must be non-empty, `lines` should be empty or contain fallback
- Line count must match header declaration unless `is_malformed=True`
- `parse_error` only populated when `is_malformed=True`

**State Transitions**:
1. PARSING → VALID: Successful hunk extraction, `is_malformed=False`
2. PARSING → MALFORMED: Parse failure, `is_malformed=True`, raw text preserved

### DiffFile (Enhanced)
**Purpose**: File metadata with validation state

**Fields**:
- `old_path: str` - Original file path
- `new_path: str` - Modified file path
- `hunks: List[DiffHunk]` - List of hunks (may include malformed)
- `is_binary: bool` - Existing binary file flag
- `total_lines: int` - NEW: Sum of all hunk line counts (for size limit check)
- `has_malformed_hunks: bool` - NEW: True if any hunk is malformed

**Validation Rules**:
- `total_lines` = sum of `hunk.new_count` across all hunks
- `has_malformed_hunks` = any(hunk.is_malformed for hunk in hunks)
- Binary files excluded from file list (existing Milestone 1 behavior)

### DiffSummary (Enhanced)
**Purpose**: Top-level diff container with size validation

**Fields**:
- `files: List[DiffFile]` - List of parsed files (excludes binary)
- `total_line_count: int` - NEW: Sum of all file total_lines
- `exceeds_limit: bool` - NEW: True if total_line_count > 10,000
- `binary_files_skipped: int` - Existing count of excluded binary files

**Validation Rules**:
- `total_line_count` calculated during parse: sum(file.total_lines for file in files)
- `exceeds_limit` = total_line_count > 10_000
- If `exceeds_limit=True`: raise `DiffTooLargeError` before returning summary

## UI Models

### ViewportState (NEW)
**Purpose**: Track visible portion of diff for rendering optimization

**Fields**:
- `start_line: int` - First visible line index
- `end_line: int` - Last visible line index
- `total_lines: int` - Total lines in current file
- `visible_height: int` - Terminal viewport height in lines

**Lifecycle**:
1. INIT: Created when file selected, `start_line=0`, `end_line=visible_height`
2. SCROLL: Updated on scroll event, recalculate start/end based on offset
3. FILE_SWITCH: Reset to start_line=0 for new file

### LazyFileContent (NEW)
**Purpose**: Deferred rich text generation for unselected files

**Fields**:
- `file_path: str` - File identifier
- `diff_file: DiffFile` - Parsed file data
- `rich_text: Optional[Text]` - Materialized Rich Text (None until selected)
- `is_materialized: bool` - True when rich_text populated

**Lifecycle**:
1. PARSED: `is_materialized=False`, `rich_text=None`
2. SELECTED: Build Rich Text from diff_file hunks, `is_materialized=True`
3. DESELECTED: Optionally clear `rich_text` to free memory (implementation decision)

## Performance Models

### PerformanceBenchmark (NEW)
**Purpose**: Capture timing data for automated tests

**Fields**:
- `operation: str` - Operation name ("initial_load", "file_switch", "scroll", "comment_add")
- `diff_size: str` - Test fixture ("small", "medium", "large")
- `duration_ms: float` - Measured execution time
- `threshold_ms: float` - Required max duration per FR-001 to FR-004
- `passed: bool` - True if duration_ms < threshold_ms

**Validation Rules**:
- `threshold_ms` based on operation:
  - "initial_load" → 2000ms (FR-001)
  - "file_switch", "comment_add" → 200ms (FR-004)
  - "scroll" → 100ms (FR-003)
- `passed` = duration_ms < threshold_ms

**Usage**:
```python
benchmark = PerformanceBenchmark(
    operation="initial_load",
    diff_size="large",
    duration_ms=1850.5,
    threshold_ms=2000.0,
    passed=True
)
assert benchmark.passed, f"Performance regression: {benchmark.operation} took {benchmark.duration_ms}ms"
```

## Error Models

### DiffTooLargeError (NEW)
**Purpose**: Exception for size limit enforcement

**Fields**:
- `actual_lines: int` - Actual diff line count
- `limit: int` - Max allowed (10,000)
- `message: str` - User-friendly error text

**Error Message Template**:
```
🦝 This diff is too large! RacGoat can handle up to {limit:,} lines,
but this diff has {actual_lines:,}. Consider reviewing in smaller chunks. 🐐
```

### MalformedHunkError (NEW)
**Purpose**: Exception for hunk parse failures (caught internally, not raised to user)

**Fields**:
- `hunk_index: int` - Position in file's hunk list
- `raw_hunk: str` - Unparsed hunk text
- `reason: str` - Parse failure description ("invalid header", "mismatched counts", etc.)

**Usage**:
- Raised during parsing
- Caught by parser, converted to `DiffHunk(is_malformed=True, raw_text=raw_hunk, parse_error=reason)`
- Never propagates to UI layer

## Entity Relationships

```
DiffSummary
├── files: List[DiffFile]
│   ├── hunks: List[DiffHunk]
│   │   ├── is_malformed: bool
│   │   └── raw_text: Optional[str]  # Only if malformed
│   └── total_lines: int
└── total_line_count: int  # sum(file.total_lines)

RacGoatApp
├── diff_summary: DiffSummary
└── lazy_files: Dict[str, LazyFileContent]  # Keyed by file path

DiffPane
├── viewport_state: ViewportState
└── current_file_content: Optional[Text]  # From LazyFileContent.rich_text
```

## Validation Summary

**Pre-Parse Validation**:
- None (accept stdin as-is)

**Parse-Time Validation**:
1. Per-hunk: Regex match header, count validation → MalformedHunkError if fail
2. Per-file: Binary detection (existing), line count summation
3. Summary level: Total line count → DiffTooLargeError if > 10k

**Post-Parse Validation** (in tests):
1. Viewport state: start_line < total_lines
2. Performance benchmarks: duration_ms < threshold_ms
3. Lazy files: rich_text materialized only for selected file
