# Data Model: Core Commenting Engine

**Feature**: Core Commenting Engine (Milestone 3)
**Date**: 2025-10-02

## Entities

### Comment

Represents a piece of user feedback attached to a specific target in the diff.

**Fields**:
- `id` (str): Unique identifier for the comment (UUID, auto-generated on creation)
- `text` (str): The comment content provided by the user
- `target` (CommentTarget): Reference to what this comment is attached to
- `timestamp` (datetime): When the comment was created
- `comment_type` (CommentType): Enum indicating single-line, range, or file-level

**Validation Rules**:
- `id` is auto-generated (UUID) and immutable
- `text` must not be empty (trimmed length > 0)
- `target` must be a valid CommentTarget instance
- `timestamp` is auto-generated on creation
- `comment_type` must be inferred from target (line vs range vs file)

**State Transitions**: Comments are mutable (text can be updated via CommentStore.update()). Timestamp preserves original creation time. Target and type remain immutable after creation.

### CommentTarget

Identifies what a comment is attached to (line, range, or file).

**Fields**:
- `file_path` (str): Path to the file being commented on
- `line_number` (int | None): Specific line number (None for file-level comments)
- `line_range` (tuple[int, int] | None): Start and end line numbers for range comments (None for single-line/file)

**Validation Rules**:
- `file_path` must not be empty
- For single-line comments: `line_number` is set, `line_range` is None
- For range comments: `line_range` is set (start ≤ end), `line_number` is None
- For file-level comments: both `line_number` and `line_range` are None
- Cannot have both `line_number` and `line_range` set simultaneously

**Derived Properties**:
- `is_line_comment`: True if line_number is set
- `is_range_comment`: True if line_range is set
- `is_file_comment`: True if both are None

### ApplicationMode (Enum)

Represents the current interaction mode of the TUI.

**Values**:
- `NORMAL`: Standard navigation and commenting (default mode)
- `SELECT`: Range selection active (user is marking lines for a range comment)

**State Transitions**:
```
NORMAL --[user presses 's' in diff pane]--> SELECT
SELECT --[user presses Esc]--> NORMAL
SELECT --[user presses Enter after selecting range]--> NORMAL (after creating comment)
SELECT --[user cancels input prompt]--> NORMAL (no comment created)
```

**Constraints**:
- File navigation is disabled in SELECT mode (FR-016)
- Single-line and file-level comment actions disabled in SELECT mode
- Only arrow keys, Enter, and Esc are active in SELECT mode

### CommentMarker (UI Model)

Visual indicator for comments in the diff pane gutter.

**Fields**:
- `symbol` (str): Character to display ("*" for single comment, "**" for overlapping)
- `style` (str): Rich Text style string (e.g., "[yellow]*[/yellow]")
- `line_number` (int): Which line this marker appears on
- `comment_count` (int): Number of comments on this line (for overlap indication)

**Validation Rules**:
- `symbol` defaults to "*" if comment_count == 1, "**" if comment_count > 1
- `style` varies based on comment_count (e.g., yellow for single, red for overlapping)
- `line_number` must be a valid post-change line number from the diff

**Derived Properties**:
- `has_overlap`: True if comment_count > 1

## Relationships

```
Comment 1:1 CommentTarget
  - Each comment has exactly one target
  - Targets can have multiple comments (overlap scenario)

CommentStore manages:
  - Comments are indexed by (file_path, line_number) or (file_path, None)
  - Lookup returns list[Comment] to support overlaps
  - Storage structure: dict[tuple[str, int | None], list[Comment]]

ApplicationMode affects:
  - Which widgets accept input (FilesPane checks mode before navigation)
  - Which keybindings are active (StatusBar displays mode-appropriate keys)
  - Visual state of DiffPane (SELECT mode shows selection highlight)

CommentMarker is computed from:
  - CommentStore lookup for current file + visible line range
  - Rendered by DiffPane when building Rich Text content
```

## Data Flow

### Adding a Single-Line Comment (FR-001)
1. User has focus on DiffPane, mode is NORMAL
2. User presses `a` key
3. App queries current line number from DiffPane
4. App prompts for comment text (Input widget)
5. If text provided:
   - Create CommentTarget(file_path, line_number, None)
   - Create Comment(text, target, timestamp, CommentType.LINE)
   - CommentStore.add(comment)
   - DiffPane re-renders with new marker
6. If text empty/cancelled: return to NORMAL with no changes

### Adding a File-Level Comment (FR-002)
1. User is viewing any file (FilesPane or DiffPane)
2. User presses `c` key
3. App gets current file path from active pane
4. App prompts for comment text
5. If text provided:
   - Create CommentTarget(file_path, None, None)
   - Create Comment(text, target, timestamp, CommentType.FILE)
   - CommentStore.add(comment)
   - FilesPane updates to show file has comment (optional visual indicator)
6. If text empty/cancelled: return to previous state

### Adding a Range Comment (FR-003)
1. User has focus on DiffPane, mode is NORMAL
2. User presses `s` key → mode changes to SELECT
3. App records start_line = current line
4. User navigates with arrow keys → selection highlight expands/contracts
5. User presses Enter → mode changes to NORMAL, prompt for text
6. If text provided:
   - Create CommentTarget(file_path, None, (start_line, end_line))
   - Create Comment(text, target, timestamp, CommentType.RANGE)
   - CommentStore.add(comment) → stores one entry per line in range
   - DiffPane re-renders with markers on all lines in range
7. If text empty/cancelled or user presses Esc: mode → NORMAL, no comment created

### Handling Comment Overlap (FR-017)
1. User adds comment to line that already has one
2. CommentStore lookup returns existing list[Comment]
3. For single-line add (FR-001): Show existing text, allow edit (FR-015)
4. For range add (FR-003): Append new comment to list
5. DiffPane queries CommentStore for marker rendering
6. If len(comments) > 1: Display "**" with distinct style

### Preventing File Switch in SELECT Mode (FR-016)
1. User is in SELECT mode (selecting range)
2. User presses arrow key in FilesPane
3. FilesPane.on_key() checks app.mode
4. If mode == SELECT: Display message "Exit Select Mode first (Esc)", ignore input
5. If mode == NORMAL: Process navigation normally

## Storage Constraints

- **Capacity**: Up to 100 comments per session (FR-018)
- **Memory**: ~200 bytes per comment → 20KB total (negligible)
- **Persistence**: In-memory only (Milestone 3); output to Markdown in Milestone 4
- **Concurrency**: Single-threaded TUI, no locking needed

## Validation Summary

From Functional Requirements:

- **FR-005**: Comments stored with associations (file path + line number/range)
  → Validated by CommentTarget fields

- **FR-014**: Distinguish comment types in memory
  → Validated by CommentType enum

- **FR-015**: Edit existing comment on re-add to same line
  → Handled by CommentStore.get() returning existing comment

- **FR-018**: Support 100 comments without degradation
  → Validated by performance constraints (O(1) lookups, 20KB memory)
