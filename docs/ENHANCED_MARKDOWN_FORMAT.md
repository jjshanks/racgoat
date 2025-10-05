# Enhanced Markdown Output Format

## Overview

RacGoat now generates enhanced Markdown output files that are both human-readable and machine-parseable. This format adds structured metadata, code context, and visual improvements to facilitate automated processing by AI coding agents while maintaining readability.

## Key Features

### 1. YAML Frontmatter
Every review file starts with YAML frontmatter containing review metadata:

```yaml
---
review_id: "20251004-143022"
branch: "feature/auth"
base_commit: "abc123def"
files_reviewed: 3
total_comments: 12
---
```

**Fields:**
- `review_id`: Timestamp-based unique identifier (format: `YYYYMMDD-HHMMSS`)
- `branch`: Git branch name being reviewed
- `base_commit`: Git commit SHA (short or full)
- `files_reviewed`: Total number of files with comments
- `total_comments`: Total comment count across all files

### 2. HTML Comment Metadata
Each comment has structured metadata in HTML comments:

```html
<!--comment
id: c1
status: open
line: 42
-->
```

**Fields:**
- `id`: Unique sequential comment identifier (c1, c2, c3...)
- `status`: Comment status (values: `open`, `addressed`, `wontfix`)
- `line`: Single line number (for line comments)
- `lines`: Line range (for range comments, format: `start-end`)
- File-level comments omit `line`/`lines` field

### 3. Code Context Blocks
Comments include surrounding code context with line numbers:

```markdown
**Context**:
```
40 | def login(user):
41 | # No validation here
42 | db.query(user.email)  # ← Comment target
43 | return user
```
```

**Features:**
- ±2 lines of context around target line/range
- Line numbers match post-change state
- Plain code format (no diff syntax)
- Automatically extracted from diff hunks
- Handles edge cases (file boundaries, malformed hunks)

### 4. Visual Separators
Horizontal rules separate comments within the same file:

```markdown
### Line 42
First comment

---

### Line 50
Second comment
```

## Format Example

Complete example showing all features:

```markdown
---
review_id: "20251004-143022"
branch: "feature/auth"
base_commit: "def456abc"
files_reviewed: 1
total_comments: 2
---

# Code Review

## File: `auth/login.py`

<!--comment
id: c1
status: open
line: 42
-->
### Line 42
Missing input validation before database query

**Context**:
```
40 | def login(user):
41 | # No validation here
42 | db.query(user.email)
43 | return user
```

---

<!--comment
id: c2
status: open
-->
### File-level comment
Consider adding unit tests for edge cases
```

## Backward Compatibility

The enhanced format is **fully backward compatible**:
- Works without `diff_summary` (skips code context)
- All existing test cases pass
- Human-readable output maintained
- Performance benchmarks met (<5s for 100 comments)

## Use Cases

### For AI Coding Agents
- Parse YAML frontmatter for review metadata
- Extract HTML metadata for structured comment data
- Use code context to understand comment location
- Track comment status (open/addressed/wontfix)
- Follow sequential comment IDs for processing

### For Humans
- Clear visual structure with headings and separators
- Code context provides immediate understanding
- Metadata is unobtrusive (HTML comments)
- Familiar Markdown rendering in viewers

## Implementation Details

### Data Model Changes
- `ReviewSession.review_id`: Property generating timestamp-based ID
- `ReviewSession.files_reviewed`: Property returning file count
- `SerializableComment.comment_id`: Optional field for unique ID
- `SerializableComment.status`: Status field (default: "open")

### Serialization Changes
- `serialize_review_session()` accepts optional `diff_summary` parameter
- YAML frontmatter generation at top of output
- HTML metadata generation per comment
- Code context extraction from diff hunks
- Sequential comment ID assignment (c1, c2, c3...)
- Horizontal rule insertion between comments

### Context Extraction Logic
- Finds relevant `DiffHunk` containing target line/range
- Extracts ±2 lines of context
- Formats with line numbers: `{line_num} | {code}`
- Handles edge cases: file boundaries, malformed hunks
- Returns `None` for file-level comments

## Testing

### Contract Tests (15 tests)
- YAML frontmatter structure validation
- HTML metadata parsing
- Code context extraction accuracy
- Sequential comment IDs
- File-level comment handling (no line field)
- Horizontal rule separators

### Integration Tests (5 tests)
- End-to-end with all comment types
- Malformed hunk handling
- Context at file boundaries
- Multiple files with sequential IDs
- Horizontal rules across files

### Performance Tests (2 tests)
- 100 comments serialization <5s ✅
- File write <1s ✅

## Files Changed

### Core Implementation
- `racgoat/models/comments.py`: Added `review_id`, `files_reviewed`, `comment_id`, `status`
- `racgoat/services/markdown_writer.py`: Enhanced serialization with YAML, HTML, context
- `racgoat/main.py`: Pass `diff_summary` to serialization

### Tests
- `tests/contract/test_enhanced_markdown.py`: New contract tests (15 tests)
- `tests/contract/test_markdown_output.py`: Updated for new format (6 tests)
- `tests/integration/test_enhanced_output.py`: New integration tests (5 tests)
- `tests/performance/test_serialization_perf.py`: Validated benchmarks (2 tests)

### Documentation
- `demo_enhanced_output.py`: Demo script showcasing features
- `docs/ENHANCED_MARKDOWN_FORMAT.md`: This document

## Success Criteria ✅

- [x] AI agents can parse YAML frontmatter and HTML metadata without errors
- [x] Human readability maintained or improved
- [x] All existing markdown tests pass (6/6)
- [x] New tests validate enhanced format (20/20)
- [x] Performance benchmarks met (2/2)
- [x] Backward compatible (works without diff_summary)

## Future Enhancements

Potential future additions:
- Comment threading (reply-to mechanism)
- Priority/severity levels
- Tags/categories for comments
- Inline suggestions (diff format)
- Automated status updates (addressed detection)
