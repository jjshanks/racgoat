# Data Model: End-to-End Workflow & Markdown Output

**Feature**: End-to-End Workflow & Markdown Output
**Branch**: 004-end-to-end
**Date**: 2025-10-02

---

## Overview

This data model defines the comment storage system and Markdown output structure for persisting code review feedback. The model supports three comment types (line, range, file-level), organizes comments by file, and includes git metadata for review context.

---

## Core Entities

### 1. Comment (Abstract Base)

**Purpose**: Represents a user-provided annotation on a diff

**Fields**:
- `text: str` - The comment content (user input, Markdown preserved)
- `comment_type: Literal["line", "range", "file"]` - Discriminator field

**Validation Rules**:
- `text` must not be empty (min length 1 char)
- `text` preserves special Markdown characters (no escaping per FR-010a)
- Maximum comment length: 10,000 characters (reasonable limit for review feedback)

**Invariants**:
- Comment instances are immutable once created (frozen dataclass)
- Comment type cannot change after creation

---

### 2. LineComment (extends Comment)

**Purpose**: Annotation attached to a specific line in the diff

**Fields**:
- Inherits: `text`, `comment_type`
- `line_number: int` - Post-change line number (1-indexed, matches diff display)

**Validation Rules**:
- `line_number` must be positive (>= 1)
- `comment_type` is always `"line"`

**Examples**:
```python
LineComment(
    text="This function should handle None case",
    line_number=42
)
```

---

### 3. RangeComment (extends Comment)

**Purpose**: Annotation spanning multiple consecutive lines

**Fields**:
- Inherits: `text`, `comment_type`
- `start_line: int` - First line of range (inclusive, 1-indexed)
- `end_line: int` - Last line of range (inclusive, 1-indexed)

**Validation Rules**:
- `start_line` must be positive (>= 1)
- `end_line` must be >= `start_line` (range must be valid)
- `comment_type` is always `"range"`

**Examples**:
```python
RangeComment(
    text="This entire block needs error handling",
    start_line=50,
    end_line=55
)
```

---

### 4. FileComment (extends Comment)

**Purpose**: Annotation about the file as a whole (not tied to specific lines)

**Fields**:
- Inherits: `text`, `comment_type`

**Validation Rules**:
- `comment_type` is always `"file"`

**Examples**:
```python
FileComment(
    text="This file should be split into smaller modules"
)
```

---

### 5. FileReview

**Purpose**: Container for all comments on a single file

**Fields**:
- `file_path: str` - Relative path to the file (from repository root)
- `comments: list[Comment]` - All comments for this file (line, range, file-level)

**Validation Rules**:
- `file_path` must not be empty
- `file_path` uses forward slashes (cross-platform consistency)
- `comments` list may be empty (file with no comments)
- Maximum 100 comments per file (per spec NFR-001)

**Invariants**:
- Comments are stored in order added (preserves user's review flow)
- Duplicate comments allowed (same line can have line + range comments per spec)

---

### 6. ReviewSession

**Purpose**: Top-level container for an entire review session

**Fields**:
- `file_reviews: dict[str, FileReview]` - Map of file path → FileReview
- `branch_name: str` - Git branch being reviewed (or "Unknown Branch")
- `commit_sha: str` - Git commit SHA (or "Unknown SHA")

**Validation Rules**:
- `file_reviews` can be empty (no comments made)
- `branch_name` and `commit_sha` are always present (placeholders if git unavailable)
- Maximum 100 total comments across all files (per spec NFR-001)

**Derived Properties**:
- `total_comment_count: int` - Sum of all comments across files
- `has_comments: bool` - Whether any comments exist (determines file output per FR-004)

---

## Data Model Diagram

```
ReviewSession
├── branch_name: str
├── commit_sha: str
└── file_reviews: dict[str, FileReview]
    └── FileReview
        ├── file_path: str
        └── comments: list[Comment]
            ├── LineComment
            │   ├── text: str
            │   ├── comment_type: "line"
            │   └── line_number: int
            ├── RangeComment
            │   ├── text: str
            │   ├── comment_type: "range"
            │   ├── start_line: int
            │   └── end_line: int
            └── FileComment
                ├── text: str
                └── comment_type: "file"
```

---

## State Transitions

### ReviewSession Lifecycle

1. **Created**: Empty session at app startup
   - `file_reviews = {}`
   - `branch_name`, `commit_sha` not yet populated

2. **Active**: User adds comments during review
   - Comments appended to `FileReview.comments`
   - New `FileReview` created when first comment added to a file

3. **Finalized**: User quits application
   - Git metadata extracted (`branch_name`, `commit_sha` populated)
   - If `has_comments == True`: Serialize to Markdown
   - If `has_comments == False`: No output file created (per FR-004)

**Transition Rules**:
- Cannot remove comments once added (immutable for data integrity)
- Cannot modify comment text after creation
- Can add comments until quit initiated

---

## Serialization Format (Markdown)

### Output Structure

```markdown
# Code Review

**Branch**: {branch_name}
**Commit**: {commit_sha}

## File: {file_path_1}

### Line {line_number}
{comment_text}

### Lines {start_line}-{end_line}
{comment_text}

### File-level comment
{comment_text}

## File: {file_path_2}
...
```

### Serialization Rules

1. **Header**: H1 title "Code Review" + metadata (branch, commit)
2. **File Sections**: H2 per file (`## File: path/to/file`)
3. **Comment Headings**: H3 with location (`### Line 42`, `### Lines 50-55`, `### File-level comment`)
4. **Comment Text**: Verbatim user input (Markdown preserved per FR-010a)
5. **File Order**: Alphabetical by file path (predictable output)
6. **Comment Order**: Within each file, order added (preserves review flow)

### Edge Cases in Serialization

- **Empty file_reviews**: No output file created (per FR-004)
- **Special chars in text**: Preserved as-is (no escaping)
- **File path with spaces**: No escaping needed (Markdown handles it)
- **Nested code blocks**: CommonMark supports nested fenced blocks

---

## Relationships to Existing Models

### Integration with Diff Parser Models

**Existing Models** (from `racgoat/parser/models.py`):
- `DiffFile`: Has `file_path` (reused in `FileReview`)
- `DiffHunk`: Has line numbers (reused in `LineComment`, `RangeComment`)

**Relationship**:
- `FileReview.file_path` matches `DiffFile.file_path` (same file)
- `LineComment.line_number` references line from `DiffHunk` (post-change)
- Comment model is independent (diff parsing and comment storage are separate concerns)

---

## Storage Considerations

### In-Memory Storage

- `ReviewSession` lives in `RacGoatApp` instance (single session per app run)
- No persistence during app runtime (comments only saved on quit)
- Maximum memory footprint: ~100 comments × 100 chars × 2 bytes = ~20KB (negligible)

### File Output

- Single Markdown file per review session
- File size estimate: ~10KB for 100 comments with metadata
- File write happens once on quit (no incremental saves)

---

## Validation Summary

| Entity | Key Validations |
|--------|----------------|
| Comment | Non-empty text, type consistency |
| LineComment | Positive line number |
| RangeComment | Valid range (start <= end) |
| FileComment | Type="file" only |
| FileReview | Non-empty file path, max 100 comments |
| ReviewSession | Max 100 total comments, git metadata present |

---

## References

- Feature Spec: `specs/004-end-to-end/spec.md` (FR-001 through FR-012)
- Research Doc: `specs/004-end-to-end/research.md` (Comment Data Model section)
- Existing Parser Models: `racgoat/parser/models.py`

---

**Status**: Complete ✅
**Next**: API Contracts (OpenAPI schema for Markdown output format)
