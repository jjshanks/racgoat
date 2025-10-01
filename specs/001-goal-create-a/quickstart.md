# Quickstart: CLI Git Diff Processor

**Feature**: 001-goal-create-a
**Date**: 2025-09-30
**Purpose**: End-to-end validation scenarios for the CLI diff processor

---

## Overview

This quickstart provides executable test scenarios that validate the complete CLI workflow from stdin to output file. Each scenario maps to acceptance criteria from the feature spec.

---

## Prerequisites

```bash
# Ensure in project root
cd /home/jjshanks/workspace/racgoat

# Install dependencies
uv sync

# Verify Python version
python --version  # Should be 3.12+
```

---

## Scenario 1: Basic Diff Processing (Default Output)

**User Story**: Process a simple diff with one modified file using default output filename

**Commands**:
```bash
# Generate sample diff
echo "diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
     print('hello')
-    return 0
+    return 1" | python -m racgoat

# Verify output file created
test -f review.md && echo "✓ Output file exists"

# Verify content
cat review.md
```

**Expected Output**:
```
src/main.py: +3 -2
```

**Validation**:
- Exit code: 0
- File `review.md` exists
- Content matches format: `{path}: +{added} -{removed}`
- Added count: 3 (two new lines at top, one modified line)
- Removed count: 2 (one removed line, one modified line)

**Cleanup**:
```bash
rm -f review.md
```

---

## Scenario 2: Custom Output File

**User Story**: Specify custom output filename with `-o` flag

**Commands**:
```bash
echo "diff --git a/tests/test_parser.py b/tests/test_parser.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/tests/test_parser.py
@@ -0,0 +1,10 @@
+def test_parse():
+    pass
+
+def test_filter():
+    pass" | python -m racgoat -o custom_summary.txt

# Verify custom file created
test -f custom_summary.txt && echo "✓ Custom output file exists"

# Verify default file NOT created
! test -f review.md && echo "✓ Default file not created"

cat custom_summary.txt
```

**Expected Output**:
```
tests/test_parser.py: +10 -0
```

**Validation**:
- Exit code: 0
- File `custom_summary.txt` exists
- File `review.md` does NOT exist
- Content shows new file with only additions

**Cleanup**:
```bash
rm -f custom_summary.txt
```

---

## Scenario 3: Empty Diff

**User Story**: Handle empty diff gracefully without creating output file

**Commands**:
```bash
echo "" | python -m racgoat
echo "Exit code: $?"

# Verify no file created
! test -f review.md && echo "✓ No output file created for empty diff"
```

**Expected Behavior**:
- Exit code: 0
- No `review.md` file created
- No error messages

**Validation**:
- Tool exits successfully (code 0)
- File system unchanged

---

## Scenario 4: Binary Files Filtered

**User Story**: Exclude binary files from summary

**Commands**:
```bash
echo "diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,1 +1,2 @@
 line1
+line2" | python -m racgoat

cat review.md
```

**Expected Output**:
```
src/main.py: +1 -0
```

**Validation**:
- Exit code: 0
- Binary file (`image.png`) excluded from output
- Text file (`src/main.py`) included

**Cleanup**:
```bash
rm -f review.md
```

---

## Scenario 5: Generated Files Filtered

**User Story**: Exclude common generated files (.lock, .min.js, package managers)

**Commands**:
```bash
echo "diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/dist/bundle.min.js b/dist/bundle.min.js
index 1234567..abcdefg 100644
--- a/dist/bundle.min.js
+++ b/dist/bundle.min.js
@@ -1,1 +1,2 @@
 code
+more code
diff --git a/src/utils.py b/src/utils.py
index 1234567..abcdefg 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -1,1 +1,3 @@
 def util():
+    pass
+    return True" | python -m racgoat

cat review.md
```

**Expected Output**:
```
src/utils.py: +2 -0
```

**Validation**:
- `package-lock.json` excluded (generated file)
- `dist/bundle.min.js` excluded (dist/ directory + .min.js extension)
- `src/utils.py` included (source file)

**Cleanup**:
```bash
rm -f review.md
```

---

## Scenario 6: Multiple Files with Mixed Changes

**User Story**: Process diff with multiple files showing additions, deletions, and modifications

**Commands**:
```bash
echo "diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,8 @@
+import sys
+import os
+
 def main():
-    print('hello')
-    x = 1
+    print('world')
     return 0
diff --git a/tests/test_main.py b/tests/test_main.py
index 1234567..abcdefg 100644
--- a/tests/test_main.py
+++ b/tests/test_main.py
@@ -1,10 +1,5 @@
 def test_one():
-    assert True
-
-def test_two():
-    assert True
-
-def test_three():
     assert True
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,1 +1,1 @@
-# Old Title
+# New Title" | python -m racgoat

cat review.md
```

**Expected Output**:
```
src/main.py: +4 -3
tests/test_main.py: +0 -5
README.md: +1 -1
```

**Validation**:
- All three files included in output
- Line counts accurate for each file
- Files appear in diff order

**Cleanup**:
```bash
rm -f review.md
```

---

## Scenario 7: File Paths with Special Characters

**User Story**: Preserve file paths with spaces and special characters

**Commands**:
```bash
echo "diff --git a/path with spaces/file.py b/path with spaces/file.py
index 1234567..abcdefg 100644
--- a/path with spaces/file.py
+++ b/path with spaces/file.py
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/src/__init__.py b/src/__init__.py
index 1234567..abcdefg 100644
--- a/src/__init__.py
+++ b/src/__init__.py
@@ -1,1 +1,3 @@
 # init
+
+__version__ = '1.0'" | python -m racgoat

cat review.md
```

**Expected Output**:
```
path with spaces/file.py: +1 -0
src/__init__.py: +2 -0
```

**Validation**:
- Path with spaces preserved exactly
- Dunder file (`__init__.py`) preserved

**Cleanup**:
```bash
rm -f review.md
```

---

## Scenario 8: Invalid Arguments

**User Story**: Display usage help for invalid command-line arguments

**Commands**:
```bash
# Missing argument after -o
python -m racgoat -o 2>&1
echo "Exit code: $?"

# Unknown flag
python -m racgoat --invalid-flag 2>&1
echo "Exit code: $?"
```

**Expected Behavior**:
- Exit code: 1 (failure)
- stderr contains usage message and error description
- No output file created

**Validation**:
- Tool exits with error code 1
- Help message printed to stderr
- Descriptive error message included

---

## Scenario 9: All Files Filtered (Edge Case)

**User Story**: Handle diff where all files are filtered (binary/generated)

**Commands**:
```bash
echo "diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/yarn.lock b/yarn.lock
index 1234567..abcdefg 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -1,1 +1,2 @@
 dep1
+dep2" | python -m racgoat

echo "Exit code: $?"

# Verify no file created
! test -f review.md && echo "✓ No output file (all files filtered)"
```

**Expected Behavior**:
- Exit code: 0 (success, treated as empty diff)
- No `review.md` file created

**Validation**:
- Tool recognizes all files are filtered
- Exits successfully without creating empty output

---

## Integration Test Checklist

Map to acceptance scenarios in spec.md:

- [x] Scenario 1: Process multiple modified text files → **Scenario 6** above
- [x] Scenario 2: Filter binary files → **Scenario 4** above
- [x] Scenario 3: Filter generated files → **Scenario 5** above
- [x] Scenario 4: Handle empty diff → **Scenario 3** above
- [x] Scenario 5: Use default output filename → **Scenario 1** above
- [x] Additional: Custom output file → **Scenario 2** above
- [x] Additional: Special characters in paths → **Scenario 7** above
- [x] Additional: Invalid arguments → **Scenario 8** above
- [x] Additional: All files filtered → **Scenario 9** above

---

## Performance Validation

**Target**: Process 100 files with 10k diff lines (per PRD constraints)

**Test Approach** (for future performance testing):
```bash
# Generate large diff (100 files, 10k lines)
# This would require a script to generate synthetic diff data

time python -m racgoat -o large_output.txt < large_diff.txt
```

**Expected Performance**:
- Completion time: < 1 second for 10k lines
- Memory usage: < 50MB

**Note**: Full performance testing deferred until implementation complete.

---

## Automated Test Execution

These scenarios will be implemented as pytest integration tests in:
- `tests/integration/test_cli_workflow.py`

**Run all integration tests**:
```bash
uv run pytest tests/integration/ -v
```

---

## Success Criteria

All scenarios must pass for feature acceptance:
- ✅ All exit codes correct (0 for success, 1 for failure)
- ✅ Output files created only when expected
- ✅ Output format matches contract exactly
- ✅ File filtering works for all patterns (binary, .lock, .min.js, dist/, build/)
- ✅ Edge cases handled gracefully (empty diff, all filtered, special chars)
- ✅ Error handling provides clear messages

---

## References

- Feature Spec: `./spec.md` (Acceptance Scenarios section)
- CLI Contract: `./contracts/cli-interface.md`
- Output Contract: `./contracts/output-format.md`
- Data Model: `./data-model.md`
