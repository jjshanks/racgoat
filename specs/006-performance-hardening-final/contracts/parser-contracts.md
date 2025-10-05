# Parser Contracts: Error Handling & Size Limits

## Contract: Malformed Hunk Detection

**Interface**: `DiffParser.parse_hunks(file_content: str) -> List[DiffHunk]`

### Scenario 1: Invalid Hunk Header
**Given**: Hunk header with malformed line range
```diff
@@ -1,5 +10 @@  # Missing new line count
 context line
```

**Then**:
- Return `DiffHunk(is_malformed=True, raw_text=<hunk>, parse_error="Invalid header format")`
- Application continues parsing remaining hunks
- Visual indicator shown in DiffPane: `[⚠ UNPARSEABLE] @@ -1,5 +10 @@`

### Scenario 2: Mismatched Line Counts
**Given**: Hunk declares 5 lines but contains 3
```diff
@@ -1,5 +1,5 @@
-old line 1
+new line 1
-old line 2
```

**Then**:
- Return `DiffHunk(is_malformed=True, raw_text=<hunk>, parse_error="Mismatched line count")`
- Raw text preserved for display
- No crash, no data loss

### Scenario 3: Mixed Valid and Malformed Hunks
**Given**: File with 3 hunks, 2nd is malformed
```diff
@@ -1,2 +1,2 @@
-old
+new

@@ invalid @@
broken content

@@ -5,1 +5,1 @@
-last
+change
```

**Then**:
- Return list: `[DiffHunk(is_malformed=False, ...), DiffHunk(is_malformed=True, ...), DiffHunk(is_malformed=False, ...)]`
- File appears in FilesPane with count: "2 hunks + 1 unparseable"
- User can review valid hunks and see malformed raw text

---

## Contract: Size Limit Enforcement

**Interface**: `DiffParser.parse(diff_text: str) -> DiffSummary`

### Scenario 1: Under Limit
**Given**: Diff with 50 files, 8,000 total lines

**Then**:
- Return `DiffSummary(total_line_count=8000, exceeds_limit=False, files=[...])`
- Application launches normally
- No error modal

### Scenario 2: Exactly at Limit
**Given**: Diff with 100 files, exactly 10,000 total lines

**Then**:
- Return `DiffSummary(total_line_count=10000, exceeds_limit=False, files=[...])`
- Application launches (10k is allowed, > 10k triggers error)

### Scenario 3: Exceeds Limit
**Given**: Diff with 120 files, 12,500 total lines

**Then**:
- Raise `DiffTooLargeError(actual_lines=12500, limit=10000)`
- RacGoatApp catches exception
- Display error modal with raccoon/goat themed message
- Application exits gracefully on modal dismiss

**Error Modal Text**:
```
🦝 This diff is too large!

RacGoat can handle up to 10,000 lines,
but this diff has 12,500.

Consider reviewing in smaller chunks. 🐐

[Press any key to exit]
```

### Scenario 4: Line Count Calculation
**Given**: 3 files with hunks:
- File 1: 2 hunks (50 lines, 30 lines) = 80 lines
- File 2: 1 hunk (100 lines) = 100 lines
- File 3: 5 hunks (10, 20, 30, 15, 25 lines) = 100 lines

**Then**:
- `total_line_count` = 80 + 100 + 100 = 280
- Calculation uses `new_count` from each hunk (post-change line count)

---

## Contract: Binary File Exclusion (Rewritten for TUI)

**Interface**: `DiffParser.parse(diff_text: str) -> DiffSummary`

### Scenario 1: Binary Files Excluded from File List (TUI Behavior)
**Given**: Diff containing:
- `image.png` (binary)
- `package-lock.json` (generated)
- `main.py` (reviewable)

**Then**:
- `DiffSummary.files` contains only `main.py`
- `DiffSummary.binary_files_skipped = 2`
- FilesPane displays 1 file in list
- Footer shows: "1 file (2 binary/generated skipped)"

### Scenario 2: All Files Binary (Edge Case)
**Given**: Diff with only binary files
```diff
diff --git a/logo.png b/logo.png
Binary files differ
```

**Then**:
- `DiffSummary.files = []` (empty list)
- FilesPane shows placeholder: "No reviewable files (all binary/generated)"
- DiffPane shows empty state
- Application remains open (does NOT exit - TUI behavior, not CLI)

### Scenario 3: Binary Detection Patterns
**Given**: Files with extensions: `.png`, `.jpg`, `.pdf`, `.lock`, `.min.js`, `.woff`, `.ttf`

**Then**:
- All marked as binary/generated
- Excluded from `DiffSummary.files`
- Counted in `binary_files_skipped`

**Expected Test Assertion** (TUI test, not CLI):
```python
async def test_binary_files_excluded_from_tui_list():
    diff = create_diff_with_binaries_and_text()
    app = RacGoatApp()
    async with app.run_test() as pilot:
        files_pane = app.query_one(FilesPane)
        file_items = files_pane.query(ListView).children
        # Assert only text files in list
        assert all(".png" not in item.file_path for item in file_items)
        assert all(".lock" not in item.file_path for item in file_items)
```

---

## Contract: Error Recovery and Data Integrity

### Scenario 1: Comment Preservation on Parse Error
**Given**:
1. User loads valid diff, adds 5 comments
2. User switches to malformed file (parse error in hunk 3)

**Then**:
- Existing 5 comments retained in CommentStore
- Malformed hunk displayed as raw text
- User can still add comments to valid hunks in same file
- No comment data loss

### Scenario 2: Graceful Exit on Size Limit Error
**Given**: User pipes 15k line diff to RacGoat

**Then**:
- Error modal appears before TUI fully renders
- No partial state (file list not populated)
- Clean exit (no crash, no orphaned processes)
- Exit code: 1 (error state)

**Test Assertion**:
```python
def test_graceful_exit_on_oversized_diff():
    large_diff = generate_diff_with_lines(15000)
    with pytest.raises(DiffTooLargeError) as exc_info:
        parser.parse(large_diff)
    assert exc_info.value.actual_lines == 15000
    assert exc_info.value.limit == 10000
```
