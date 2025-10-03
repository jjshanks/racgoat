# Contract: CommentStore API

**Module**: `racgoat.services.comment_store`
**Version**: 1.0.0

## Overview

The CommentStore is the central service for managing all comments in memory during a review session. It provides CRUD operations for comments with efficient lookup by file path and line number.

## API Specification

### `add(comment: Comment) -> None`

**Purpose**: Add a new comment to the store

**Preconditions**:
- `comment` is a valid Comment instance
- `comment.text` is not empty (after trimming)
- `comment.target` is a valid CommentTarget

**Postconditions**:
- Comment is retrievable via `get()` with matching target
- For range comments: One entry stored per line in range
- Total comment count ≤ 100 (enforced limit)

**Errors**:
- Raises `ValueError` if comment.text is empty
- Raises `ValueError` if total comments would exceed 100
- Raises `TypeError` if comment is not a Comment instance

### `get(file_path: str, line_number: int | None) -> list[Comment]`

**Purpose**: Retrieve all comments for a specific target

**Preconditions**:
- `file_path` is a non-empty string
- `line_number` is None (file-level) or positive int (line/range)

**Postconditions**:
- Returns empty list if no comments exist for target
- Returns list of 1+ comments if any exist (supports overlaps)
- List is sorted by timestamp (oldest first)

**Errors**: None (returns empty list for invalid lookups)

### `get_file_comments(file_path: str) -> list[Comment]`

**Purpose**: Get all comments associated with a file (any type)

**Preconditions**:
- `file_path` is a non-empty string

**Postconditions**:
- Returns all line, range, and file-level comments for the file
- Sorted by line number (file-level comments first)
- Empty list if no comments exist for file

**Errors**: None

### `update(target: CommentTarget, new_text: str) -> None`

**Purpose**: Update the text of an existing comment

**Preconditions**:
- Comment exists at `target` location
- `new_text` is not empty (after trimming)

**Postconditions**:
- Comment text updated to `new_text`
- Timestamp remains unchanged (original creation time preserved)
- Comment type and target unchanged

**Errors**:
- Raises `KeyError` if no comment exists at target
- Raises `ValueError` if new_text is empty
- Raises `ValueError` if multiple comments exist (ambiguous update - requires delete + add)

### `delete(target: CommentTarget, comment_id: str | None = None) -> None`

**Purpose**: Remove a comment from the store

**Preconditions**:
- Comment exists at `target` location
- If multiple comments exist at target, `comment_id` must be provided

**Postconditions**:
- Specified comment no longer retrievable via `get()`
- For range comments: All entries for that range removed
- Total comment count decremented

**Errors**:
- Raises `KeyError` if no comment exists at target
- Raises `ValueError` if multiple comments exist and `comment_id` is None (ambiguous delete)
- Raises `KeyError` if `comment_id` provided but no matching comment found

### `has_comment(file_path: str, line_number: int | None) -> bool`

**Purpose**: Check if a comment exists at a specific location

**Preconditions**:
- `file_path` is a non-empty string
- `line_number` is None or positive int

**Postconditions**:
- Returns True if one or more comments exist
- Returns False otherwise

**Errors**: None

### `count() -> int`

**Purpose**: Get total number of unique comments in store

**Preconditions**: None

**Postconditions**:
- Returns integer between 0 and 100 (inclusive)
- Range comments count as one comment (not one per line)

**Errors**: None

### `clear() -> None`

**Purpose**: Remove all comments from the store

**Preconditions**: None

**Postconditions**:
- All comments removed
- `count()` returns 0
- All subsequent `get()` calls return empty lists

**Errors**: None

## Usage Examples

### Adding a single-line comment
```python
store = CommentStore()
target = CommentTarget(file_path="foo.py", line_number=42, line_range=None)
comment = Comment(text="Fix this bug", target=target, timestamp=now(), comment_type=CommentType.LINE)
store.add(comment)

# Retrieve it
comments = store.get("foo.py", 42)
assert len(comments) == 1
assert comments[0].text == "Fix this bug"
```

### Adding a range comment (stores one entry per line)
```python
target = CommentTarget(file_path="bar.py", line_number=None, line_range=(10, 15))
comment = Comment(text="Refactor this block", target=target, timestamp=now(), comment_type=CommentType.RANGE)
store.add(comment)

# Retrieval works for any line in range
for line in range(10, 16):
    comments = store.get("bar.py", line)
    assert len(comments) == 1
    assert comments[0].text == "Refactor this block"
```

### Handling overlaps
```python
# Line comment at line 20
target1 = CommentTarget(file_path="baz.py", line_number=20, line_range=None)
comment1 = Comment(text="First comment", target=target1, timestamp=now(), comment_type=CommentType.LINE)
store.add(comment1)

# Range comment covering lines 15-25 (overlaps line 20)
target2 = CommentTarget(file_path="baz.py", line_number=None, line_range=(15, 25))
comment2 = Comment(text="Second comment", target=target2, timestamp=now(), comment_type=CommentType.RANGE)
store.add(comment2)

# Line 20 now has two comments
comments = store.get("baz.py", 20)
assert len(comments) == 2
assert comments[0].text == "First comment"
assert comments[1].text == "Second comment"
```

### Checking for existing comments before adding
```python
if store.has_comment("foo.py", 42):
    # Edit existing comment (Milestone 5)
    existing = store.get("foo.py", 42)[0]
    new_text = prompt_with_prefill(existing.text)
    store.update(existing.target, new_text)
else:
    # Add new comment
    new_text = prompt_for_comment()
    # ... create and add comment
```

## Contract Tests

The following test scenarios MUST pass before implementation:

1. **test_add_single_line_comment**: Add comment, verify retrievable
2. **test_add_file_level_comment**: Add file comment, verify retrieval with line_number=None
3. **test_add_range_comment**: Add range, verify all lines have same comment
4. **test_get_nonexistent_returns_empty**: get() returns [] for missing target
5. **test_overlapping_comments**: Add line + range to same line, verify both returned
6. **test_comment_capacity_limit**: Adding 101st comment raises ValueError
7. **test_update_existing_comment**: Update text, verify timestamp unchanged
8. **test_delete_removes_comment**: Delete, verify no longer retrievable
9. **test_clear_removes_all**: clear(), verify count() == 0
10. **test_empty_text_raises_error**: Adding comment with "" text raises ValueError

## Performance Requirements

- `add()`: O(1) for line/file, O(n) for range where n = range size (typically < 50)
- `get()`: O(1) lookup
- `has_comment()`: O(1) lookup
- `get_file_comments()`: O(m) where m = total comments in file (typically < 20)
- Memory: ~200 bytes per comment, max 20KB for 100 comments
