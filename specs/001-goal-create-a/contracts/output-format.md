# Output Format Contract

**Feature**: 001-goal-create-a
**Date**: 2025-09-30
**Version**: 1.0

## Overview
This contract defines the exact output format for the diff summary file.

---

## Format Specification

### Line Format
```
{file_path}: +{added_lines} -{removed_lines}
```

### Format Rules

| Component | Rule | Example |
|-----------|------|---------|
| `file_path` | Exact path from diff (preserve all characters) | `src/main.py` |
| `:` | Literal colon separator | `:` |
| ` ` (space) | Single space after colon | ` ` |
| `+` | Literal plus sign | `+` |
| `added_lines` | Non-negative integer, no leading zeros | `15` or `0` |
| ` ` (space) | Single space between counts | ` ` |
| `-` | Literal minus sign | `-` |
| `removed_lines` | Non-negative integer, no leading zeros | `3` or `0` |
| `\n` | Newline at end of line | (platform-specific) |

---

## Examples

### Standard Case
```
src/main.py: +15 -3
tests/test_parser.py: +42 -0
racgoat/utils.py: +8 -12
```

### Edge Cases

**Only Additions**:
```
new_file.py: +100 -0
```

**Only Deletions**:
```
deleted_file.py: +0 -50
```

**Equal Additions and Deletions**:
```
refactored.py: +20 -20
```

**Zero Changes** (should not appear in output):
```
# Files with +0 -0 are excluded from output
```

**File Path with Spaces**:
```
path with spaces/file.py: +5 -2
```

**File Path with Special Characters**:
```
src/models/__init__.py: +3 -1
tests/test_@decorator.py: +10 -0
files/file(v2).py: +8 -3
```

**Nested Directories**:
```
src/api/v2/endpoints/users.py: +25 -10
```

---

## Regular Expression Pattern

For validation/testing:
```regex
^[^\n]+: \+\d+ -\d+$
```

**Breakdown**:
- `^` - Start of line
- `[^\n]+` - File path (one or more non-newline characters)
- `:` - Literal colon
- ` ` - Single space
- `\+` - Literal plus sign
- `\d+` - One or more digits (added count)
- ` ` - Single space
- `-` - Literal minus sign
- `\d+` - One or more digits (removed count)
- `$` - End of line

---

## Ordering

**Default**: Files appear in the order they are encountered in the diff

**Example**:
If diff contains files in order: `main.py`, `utils.py`, `test.py`
Output will be:
```
main.py: +10 -5
utils.py: +3 -8
test.py: +20 -0
```

**Note**: No alphabetical sorting required for this milestone.

---

## File-Level Requirements

### Encoding
- UTF-8

### Line Endings
- Platform-specific (handled by Python's text mode)
- Unix: `\n`
- Windows: `\r\n`

### Trailing Newline
- Yes - final line ends with newline

**Example** (showing newlines):
```
src/main.py: +15 -3\n
tests/test_parser.py: +42 -0\n
```

---

## Empty Output Conditions

**No file is created** when:
1. Diff is empty (no changes at all)
2. All files are filtered (binary or generated files only)

**File IS created** when:
- At least one non-filtered file has changes

---

## Contract Test Assertions

### Test 1: Format Validation
```python
def test_output_format_matches_pattern():
    output = "src/main.py: +15 -3\n"
    pattern = r'^[^\n]+: \+\d+ -\d+$'
    assert re.match(pattern, output.strip())
```

### Test 2: Multiple Lines
```python
def test_multiple_files_format():
    output = """src/main.py: +15 -3
tests/test_parser.py: +42 -0
"""
    lines = output.strip().split('\n')
    assert len(lines) == 2
    for line in lines:
        assert re.match(r'^[^\n]+: \+\d+ -\d+$', line)
```

### Test 3: Special Characters Preserved
```python
def test_file_path_special_chars():
    output = "path with spaces/file.py: +5 -2\n"
    assert "path with spaces/file.py" in output
```

### Test 4: Zero Counts Valid
```python
def test_zero_counts_allowed():
    output1 = "new_file.py: +10 -0\n"
    output2 = "deleted_file.py: +0 -5\n"
    assert "+10 -0" in output1
    assert "+0 -5" in output2
```

### Test 5: No Leading Zeros
```python
def test_no_leading_zeros():
    # Invalid: "file.py: +05 -03"
    # Valid:   "file.py: +5 -3"
    output = "file.py: +5 -3\n"
    assert re.match(r'\+0\d', output) is None  # No leading zeros
```

---

## Invalid Examples

**Missing Space After Colon**:
```
file.py:+10 -5  # INVALID
```

**Missing Plus/Minus Signs**:
```
file.py: 10 5  # INVALID
```

**Leading Zeros**:
```
file.py: +05 -03  # INVALID
```

**Extra Spaces**:
```
file.py:  +10  -5  # INVALID (extra spaces)
```

**Missing Newline Between Entries**:
```
file1.py: +10 -5file2.py: +3 -2  # INVALID (no newline)
```

---

## Compliance Checklist

- [x] Format pattern specified: `{path}: +{added} -{removed}`
- [x] Spacing rules defined (single space after colon and between counts)
- [x] Sign requirements defined (+ before added, - before removed)
- [x] Zero handling defined (allowed, no leading zeros)
- [x] Special character handling defined (preserve as-is)
- [x] Ordering defined (diff order, no sorting)
- [x] Empty output conditions defined
- [x] Regular expression pattern provided for validation
- [x] Test assertions specified

---

## References

- Feature Spec: `../spec.md` (FR-010)
- Data Model: `../data-model.md` (DiffSummary.format_output)
- CLI Interface: `./cli-interface.md` (Output Contract section)
