# CLI Interface Contract

**Feature**: 001-goal-create-a
**Date**: 2025-09-30
**Version**: 1.0

## Overview
This contract defines the command-line interface for the git diff processor tool.

---

## Command Invocation

### Syntax
```bash
python -m racgoat [-o OUTPUT_FILE]
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `-o`, `--output` | string | No | `review.md` | Output file path for summary |

---

## Input Contract

### Source
- **Stream**: stdin
- **Format**: Git unified diff format
- **Encoding**: UTF-8

### Expected Input Structure
```
diff --git a/path/to/file b/path/to/file
index 1234567..abcdefg 100644
--- a/path/to/file
+++ b/path/to/file
@@ -X,Y +A,B @@ context
-removed line
+added line
 unchanged line
```

### Input Validation
- **Empty input**: Valid (represents empty diff)
- **Malformed diff**: Invalid (exit 1)
- **Binary file marker**: Valid (file excluded from output)
- **Non-UTF-8 encoding**: Invalid (exit 1)

---

## Output Contract

### File Format
- **Location**: Path specified by `-o` argument (default: `review.md`)
- **Encoding**: UTF-8
- **Line Endings**: Platform-specific (`\n` on Unix, `\r\n` on Windows)

### Content Format
```
{file_path}: +{added_lines} -{removed_lines}
```

**Schema**:
- `file_path`: String, exact path from diff (preserve spaces/special chars)
- `added_lines`: Non-negative integer
- `removed_lines`: Non-negative integer

**Example**:
```
src/main.py: +15 -3
tests/test_parser.py: +42 -0
racgoat/utils.py: +8 -12
```

### Output Conditions

| Condition | Behavior | File Created | Exit Code |
|-----------|----------|--------------|-----------|
| Empty diff (no changes) | No output | No | 0 |
| Only filtered files (binary/generated) | No output | No | 0 |
| At least one non-filtered file | Write summary | Yes | 0 |
| Malformed diff | Error message to stderr | No | 1 |
| Invalid arguments | Error + usage to stderr | No | 1 |
| Output file write failure | Error to stderr | No | 1 |

---

## Exit Codes

| Code | Meaning | Scenarios |
|------|---------|-----------|
| 0 | Success | Valid diff processed (including empty diff handled) |
| 1 | Failure | Invalid arguments, malformed diff, write error, any exception |

---

## Error Messages

### Invalid Arguments
```
usage: python -m racgoat [-o OUTPUT_FILE]
error: argument -o/--output: expected one argument
```

### Malformed Diff
```
Error: Invalid diff format
```

### Write Failure
```
Error: Cannot write to output file: {file_path}
```

---

## Contract Test Scenarios

### Test 1: Default Output File
```bash
echo "diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 line1
+line2" | python -m racgoat
```

**Expected**:
- File created: `review.md`
- Content: `test.py: +1 -0\n`
- Exit code: 0

---

### Test 2: Custom Output File
```bash
echo "diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,2 +1,1 @@
-line1
 line2" | python -m racgoat -o summary.txt
```

**Expected**:
- File created: `summary.txt`
- Content: `test.py: +0 -1\n`
- Exit code: 0

---

### Test 3: Empty Diff
```bash
echo "" | python -m racgoat
```

**Expected**:
- No file created
- Exit code: 0

---

### Test 4: Binary File (Filtered)
```bash
echo "diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ" | python -m racgoat
```

**Expected**:
- No file created (all files filtered)
- Exit code: 0

---

### Test 5: Generated File (Filtered)
```bash
echo "diff --git a/package-lock.json b/package-lock.json
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2" | python -m racgoat
```

**Expected**:
- No file created (all files filtered)
- Exit code: 0

---

### Test 6: Mixed Files (Some Filtered)
```bash
echo "diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/package-lock.json b/package-lock.json
Binary files differ" | python -m racgoat
```

**Expected**:
- File created: `review.md`
- Content: `src/main.py: +1 -0\n`
- Exit code: 0

---

### Test 7: Invalid Argument
```bash
python -m racgoat -o
```

**Expected**:
- No file created
- stderr: Usage message + error
- Exit code: 1

---

### Test 8: File Path with Spaces
```bash
echo "diff --git a/path with spaces/file.py b/path with spaces/file.py
--- a/path with spaces/file.py
+++ b/path with spaces/file.py
@@ -1,1 +1,2 @@
 line1
+line2" | python -m racgoat
```

**Expected**:
- File created: `review.md`
- Content: `path with spaces/file.py: +1 -0\n`
- Exit code: 0

---

## Implementation Checklist

Contract tests MUST be implemented before any implementation code:

- [ ] Test default output file (`review.md`)
- [ ] Test custom output file (via `-o` flag)
- [ ] Test empty diff (no output file, exit 0)
- [ ] Test binary file filtering (no output, exit 0)
- [ ] Test generated file filtering (no output, exit 0)
- [ ] Test mixed files (only non-filtered in output)
- [ ] Test invalid arguments (usage + exit 1)
- [ ] Test file paths with special characters
- [ ] Test malformed diff (exit 1)
- [ ] Test write failure (exit 1)

---

## Backwards Compatibility

N/A - This is the initial implementation (Milestone 1).

---

## Future Evolution

- Milestone 2+ will add TUI mode (different entry point, not replacing this CLI)
- CLI mode may gain additional flags in future milestones (e.g., `--format json`)
- This contract remains stable as the non-interactive processing mode

---

## References

- Feature Spec: `../spec.md` (FR-007, FR-008, FR-009, FR-010, FR-011, FR-012)
- Data Model: `../data-model.md`
- Research: `../research.md` (Section 3: CLI Argument Parsing)
