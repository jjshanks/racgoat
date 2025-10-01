# Data Model: CLI Git Diff Processor

**Feature**: 001-goal-create-a
**Date**: 2025-09-30
**Status**: Complete

## Overview
This document defines the data structures for parsing git diffs and generating file summaries.

---

## Entities

### 1. DiffFile

**Purpose**: Represents a single file in a git diff with its change statistics

**Attributes**:
- `file_path` (str): Path to the file as it appears in the diff (post-change path from "+++ b/..." line)
  - Must preserve exact path including special characters and spaces
  - Required, non-empty
- `added_lines` (int): Count of added lines (lines starting with "+", excluding hunk markers)
  - Must be >= 0
  - Default: 0
- `removed_lines` (int): Count of removed lines (lines starting with "-", excluding hunk markers)
  - Must be >= 0
  - Default: 0
- `is_binary` (bool): Whether file is marked as binary in diff
  - Detected from "Binary files ... differ" marker
  - Default: False

**Validation Rules**:
- `file_path` cannot be empty string
- `added_lines >= 0`
- `removed_lines >= 0`
- At least one of `added_lines` or `removed_lines` must be > 0 for inclusion in output (unless file is new/deleted)

**State Transitions**:
```
Created (added=0, removed=0)
  → Parsing hunks (accumulate added/removed counts)
  → Complete (final counts set)
  → Filtered (if is_binary or matches generated patterns)
  → Output (if not filtered)
```

**Example**:
```python
DiffFile(
    file_path="src/parser/diff_parser.py",
    added_lines=42,
    removed_lines=8,
    is_binary=False
)
```

---

### 2. DiffSummary

**Purpose**: Aggregates all parsed files and metadata for a single diff

**Attributes**:
- `files` (list[DiffFile]): All non-filtered files extracted from diff
  - Ordered by appearance in diff
  - Excludes binary and generated files
- `total_files` (int): Count of files in `files` list
  - Derived property: `len(files)`
- `is_empty` (bool): Whether diff contains no changes
  - True if `total_files == 0`
  - Determines whether output file should be created

**Validation Rules**:
- `files` list can be empty (represents empty diff)
- All items in `files` must be valid DiffFile instances
- No duplicate file paths in `files` (same file appearing multiple times should merge counts)

**Methods**:
- `add_file(file: DiffFile) -> None`: Add file to summary
- `should_create_output() -> bool`: Returns `not is_empty`
- `format_output() -> str`: Generate output text in required format

**State Transitions**:
```
Created (files=[])
  → Accumulating (files.append(...))
  → Complete (all files parsed)
  → Output decision (check is_empty)
```

**Example**:
```python
summary = DiffSummary(files=[
    DiffFile("src/main.py", added_lines=15, removed_lines=3, is_binary=False),
    DiffFile("tests/test_parser.py", added_lines=42, removed_lines=0, is_binary=False)
])
# summary.is_empty == False
# summary.total_files == 2
```

---

### 3. FileFilter

**Purpose**: Encapsulates logic for determining if a file should be excluded from summary

**Attributes**:
- `generated_patterns` (list[str]): File extension patterns to exclude
  - Default: ['.lock', '.min.js', '.min.css', '.map', '.bundle.js']
- `generated_files` (list[str]): Specific filenames to exclude
  - Default: ['package-lock.json', 'yarn.lock', 'poetry.lock']
- `generated_globs` (list[str]): Glob patterns to match
  - Default: ['*.generated.*']
- `excluded_dirs` (list[str]): Directory prefixes to exclude
  - Default: ['dist/', 'build/']

**Methods**:
- `is_filtered(file_path: str) -> bool`: Returns True if file should be excluded
  - Check binary marker (handled in DiffFile)
  - Check extension patterns
  - Check specific filenames
  - Check glob patterns
  - Check directory prefixes

**Validation Rules**:
- All patterns are case-sensitive (match diff output exactly)
- Directory matching checks if path starts with excluded prefix
- Extension matching checks if path ends with pattern

**Example**:
```python
filter = FileFilter()
filter.is_filtered("package-lock.json")  # True
filter.is_filtered("src/main.py")         # False
filter.is_filtered("dist/bundle.js")      # True
filter.is_filtered("build/output.txt")    # True
filter.is_filtered("src/data.generated.json")  # True
```

---

### 4. CLIArguments

**Purpose**: Encapsulates parsed command-line arguments

**Attributes**:
- `output_file` (str): Path to output file
  - Default: "review.md"
  - Must be valid writable path

**Validation Rules**:
- `output_file` cannot be empty string
- Path can be relative or absolute
- Parent directory must exist or be creatable (handled at write time)

**State Transitions**:
```
Default ("review.md")
  → Parsed from args (if -o provided)
  → Validated (check not empty)
  → Used for output
```

**Example**:
```python
# Default case
CLIArguments(output_file="review.md")

# Custom output
CLIArguments(output_file="custom_summary.txt")
```

---

## Relationships

```
CLIArguments
     ↓ (configures output destination)
DiffSummary
     ↓ (contains)
  [DiffFile, DiffFile, ...]
     ↓ (filtered by)
  FileFilter
```

**Flow**:
1. Parse `CLIArguments` from command line
2. Create `DiffSummary` instance
3. For each file in stdin diff:
   - Create `DiffFile` with counts
   - Check `FileFilter.is_filtered()`
   - If not filtered, add to `DiffSummary.files`
4. If `DiffSummary.is_empty == False`:
   - Write `DiffSummary.format_output()` to `CLIArguments.output_file`

---

## Output Format Contract

**Format**: Plain text, one line per file
**Pattern**: `{file_path}: +{added_lines} -{removed_lines}\n`

**Requirements** (from FR-010):
- File path exactly as it appears in diff (preserve spaces, special chars)
- Single space after colon
- Plus sign before added count (even if 0)
- Space between added and removed counts
- Minus sign before removed count (even if 0)
- Newline after each entry

**Example**:
```
src/main.py: +15 -3
tests/test_parser.py: +42 -0
racgoat/utils.py: +8 -12
path/with spaces/file.txt: +5 -5
```

**Edge Cases**:
- File with only additions: `path/to/file: +10 -0`
- File with only deletions: `path/to/file: +0 -8`
- No output if `DiffSummary.is_empty == True`

---

## Implementation Notes

### Python Type Hints
```python
from dataclasses import dataclass
from typing import List

@dataclass
class DiffFile:
    file_path: str
    added_lines: int = 0
    removed_lines: int = 0
    is_binary: bool = False

@dataclass
class DiffSummary:
    files: List[DiffFile]

    @property
    def is_empty(self) -> bool:
        return len(self.files) == 0

    @property
    def total_files(self) -> int:
        return len(self.files)

    def format_output(self) -> str:
        return "\n".join(
            f"{f.file_path}: +{f.added_lines} -{f.removed_lines}"
            for f in self.files
        )
```

### Storage
- **In-memory only**: All data structures exist only during CLI execution
- **No persistence**: No database, no state files
- **Single output**: Write to file system only at end of processing

### Concurrency
- **Not applicable**: Single-threaded CLI tool
- **No shared state**: Each execution is independent

---

## Validation Checklist

- [x] All entities from spec.md "Key Entities" section included
- [x] Each entity has clear purpose and attributes
- [x] Validation rules specified for each attribute
- [x] Relationships between entities documented
- [x] Output format contract specified
- [x] No implementation details (Python code shown only for clarity, not prescription)
- [x] Data model supports all functional requirements (FR-001 through FR-012)

---

## References

- Feature Spec: `./spec.md`
- Research: `./research.md`
- Output format: FR-010 in spec.md
