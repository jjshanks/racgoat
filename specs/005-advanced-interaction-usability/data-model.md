# Data Model: Advanced Interaction & Usability

**Feature Branch**: `005-advanced-interaction-usability`
**Created**: 2025-10-04
**Status**: Draft

## Overview

This document defines the data entities required to support comment editing/deletion, search functionality, and help overlay features. These entities extend the existing comment models from Milestone 3 (racgoat/models/comments.py).

---

## Core Entities

### 1. EditableComment

**Purpose**: Represents an existing comment (line, range, or file-level) that can be modified or deleted by the user.

**Implementation Note**: EditableComment is a **type alias** to the existing `Comment` model from Milestone 3 (`racgoat/models/comments.py`). It is not a separate model, but rather a semantic distinction to indicate a comment in the context of edit operations.

**Fields** (from Comment model):
- `id: str` - Unique identifier (UUID, auto-generated)
- `text: str` - Comment text content
- `target: CommentTarget` - Location reference (file_path, line_number/line_range)
- `comment_type: CommentType` - Type discriminator (LINE, RANGE, FILE)
- `timestamp: datetime` - Creation timestamp (auto-generated)

**Validation Rules**:
- `id` MUST match an existing comment in the CommentStore
- `text` MUST be 1-10,000 characters when saving (per FR-006: empty text = delete)
- `target` MUST be a valid CommentTarget instance
- `comment_type` MUST match the target configuration:
  - LINE: target.line_number is not None
  - RANGE: target.line_range is not None
  - FILE: both line_number and line_range are None

**Relationships**:
- Is the Comment model from `racgoat.models.comments.py` (Milestone 3)
- Retrieved from CommentStore during edit operations
- Wrapped by EditContext to provide cursor position context

**State Transitions**:
```
[Existing Comment] ---> [User presses 'e'] ---> [EditableComment created]
                                                         |
                                                         v
                                     [Edit Dialog displays with pre-filled text]
                                                         |
                        +--------------------------------+--------------------------------+
                        |                                |                                |
                        v                                v                                v
                [User confirms edit]          [User clears all text]          [User cancels (Esc)]
                        |                                |                                |
                        v                                v                                v
          [Update Comment in store]           [Delete Comment from store]        [No change - discard]
          [Preserve comment_type]              [Remove visual marker]
```

---

### 2. SearchQuery

**Purpose**: Represents the user's search input and associated match state within a specific file context.

**Fields**:
- `pattern: str` - The literal search string entered by user
- `case_sensitive: bool` - Whether search is case-sensitive (always True per FR-020)
- `is_regex: bool` - Whether pattern is regex (always False per FR-019)

**Validation Rules**:
- `pattern` MUST be non-empty when active (empty string = no search)
- `case_sensitive` MUST always be True (literal case-sensitive matching only)
- `is_regex` MUST always be False (no regex support)

**Relationships**:
- Contains 0 or 1 active SearchQuery per file in SearchState
- Produces 0 or more SearchMatch instances when executed
- Cleared when user switches files (per FR-023) or exits search mode (per FR-022)

**State Transitions**:
```
[No search] ---> [User presses '/'] ---> [Search input shown]
                                                |
                                                v
                                    [User types pattern text]
                                                |
                                                v
                                     [User presses Enter]
                                                |
                        +-----------------------+-----------------------+
                        |                                               |
                        v                                               v
                [Matches found]                              [No matches found]
                [Create SearchQuery]                         [Show "0/0 matches"]
                [Create SearchMatch list]                    [SearchQuery active but empty]
                        |
                        v
          [User presses 'n'/'N' to navigate]
                        |
                        v
          [Current match index updated]
                        |
         +--------------+---------------+
         |                              |
         v                              v
[User presses Esc]          [User switches file]
         |                              |
         v                              v
[Clear SearchQuery]         [Reset entire SearchState]
[Clear all highlights]      [Clear query and highlights]
```

---

### 3. SearchMatch

**Purpose**: Represents a single occurrence of the search pattern within diff text.

**Fields**:
- `line_number: int` - Post-change line number where match occurs (>= 1)
- `char_offset: int` - Character position within the line where match starts (0-indexed)
- `matched_text: str` - The actual text that matched (for highlighting)
- `match_length: int` - Length of matched text in characters

**Validation Rules**:
- `line_number` MUST be >= 1
- `char_offset` MUST be >= 0
- `matched_text` MUST equal the search pattern exactly (case-sensitive)
- `match_length` MUST equal len(matched_text)

**Relationships**:
- Multiple SearchMatch instances belong to one SearchQuery
- Each SearchMatch corresponds to exactly one line in the diff pane
- SearchMatch instances are stored in a list ordered by line_number, then char_offset
- Current match index points to one SearchMatch in the list

**State Transitions**:
```
[SearchQuery executed] ---> [Scan diff text line by line]
                                       |
                                       v
                        [For each line: find all occurrences]
                                       |
                        +--------------+--------------+
                        |                             |
                        v                             v
              [Match found at position]     [No match in line]
                        |                             |
                        v                             v
          [Create SearchMatch]              [Continue to next line]
          [Add to matches list]
                        |
                        v
              [All lines scanned]
                        |
                        v
         [Sort matches by (line_number, char_offset)]
                        |
                        v
              [Set current_index = 0]
              [Jump to first match]
```

---

### 4. SearchState

**Purpose**: Container for search query, matches, and current position state per file.

**Fields**:
- `query: Optional[SearchQuery]` - Active search query (None if no search active)
- `matches: list[SearchMatch]` - All matches in current file (empty if no matches)
- `current_index: int` - Index of currently focused match in matches list (-1 if no matches)
- `file_path: str` - File this search state belongs to

**Validation Rules**:
- `current_index` MUST be -1 when matches is empty
- `current_index` MUST be >= 0 and < len(matches) when matches is non-empty
- If `query` is None, then `matches` MUST be empty and `current_index` MUST be -1
- `file_path` MUST match a file in the current diff

**Relationships**:
- One SearchState per file in the diff
- When user switches files, active SearchState is reset (query cleared, matches cleared)
- Owned by the DiffPane widget
- Influences status bar display (match counter: "3/15 matches")

**State Transitions**:
```
[Initial state: SearchState(query=None, matches=[], current_index=-1)]
                                   |
                                   v
                    [User initiates search with '/']
                                   |
                                   v
           [SearchState.query = SearchQuery(pattern="...")]
                                   |
                                   v
                    [Execute search against diff text]
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
          [Matches found]                [No matches found]
                    |                             |
                    v                             v
    [SearchState.matches = [...]]    [SearchState.matches = []]
    [current_index = 0]              [current_index = -1]
    [Jump to first match]            [Show "0/0 matches"]
                    |
                    v
         [User navigates with 'n'/'N']
                    |
                    v
         [current_index incremented/decremented with wrap-around]
                    |
         +-----------+-----------+
         |                       |
         v                       v
[User exits search]    [User switches file]
         |                       |
         v                       v
[query = None]         [Reset to initial state]
[matches = []]
[current_index = -1]
[Clear highlights]
```

---

### 5. EditContext

**Purpose**: Context object for determining which comment exists at the current cursor position in the diff pane.

**Fields**:
- `file_path: str` - Current file being viewed
- `cursor_line: int` - Current line number where cursor is positioned (post-change line number)
- `existing_comment: Optional[Comment]` - Comment found at cursor position (None if no comment)

**Validation Rules**:
- `file_path` MUST be non-empty
- `cursor_line` MUST be >= 1
- `existing_comment` MUST be None OR a valid Comment from CommentStore

**Relationships**:
- Queries CommentStore to find comment at (file_path, cursor_line)
- For range comments: finds comment if cursor_line is within the range
- For file-level comments: finds comment if cursor is anywhere in the file
- Determines whether 'e' keybinding is shown in status bar (per FR-031)

**State Transitions**:
```
[Cursor moves to new line] ---> [Create EditContext]
                                        |
                                        v
                        [Query CommentStore for comment at position]
                                        |
                        +---------------+---------------+
                        |                               |
                        v                               v
              [Comment found]                 [No comment found]
                        |                               |
                        v                               v
    [existing_comment = Comment]        [existing_comment = None]
    [Show 'e' in status bar]            [Hide 'e' from status bar]
                        |
                        v
           [User presses 'e' key]
                        |
         +--------------+--------------+
         |                             |
         v                             v
[existing_comment present]   [existing_comment is None]
         |                             |
         v                             v
[Open edit dialog]          [Silently ignore per FR-034]
[Pre-fill with text]
```

---

### 6. HelpEntry

**Purpose**: Represents a single keybinding in the help overlay.

**Fields**:
- `key: str` - Keyboard key or combination (e.g., "e", "/", "?", "Esc", "n", "N")
- `action: str` - Short action name (e.g., "Edit comment", "Search", "Help")
- `description: str` - Detailed description of what the keybinding does
- `context: str` - Functional category for grouping (e.g., "Navigation", "Commenting", "Search", "General")

**Validation Rules**:
- `key` MUST be non-empty
- `action` MUST be non-empty
- `description` MUST be non-empty
- `context` MUST be one of: "Navigation", "Commenting", "Search", "General"

**Relationships**:
- Multiple HelpEntry instances compose the HelpOverlay widget
- HelpEntry instances are grouped by `context` for display organization
- HelpEntry data is static (hardcoded in application, not user-modifiable)

**State Transitions**:
```
[Application starts] ---> [Initialize HelpEntry list]
                                   |
                                   v
                    [HelpEntry instances created for each keybinding]
                                   |
                                   v
                    [Group by context category]
                                   |
                                   v
                    [Store in HelpOverlay widget]
                                   |
                                   v
                    [User presses '?']
                                   |
                                   v
                    [Display all HelpEntry items in overlay]
                    [Scrollable if exceeds terminal height]
                                   |
                    +---------------+
                    |               |
                    v               v
          [User presses '?']  [User presses Esc]
                    |               |
                    +---------+-----+
                              |
                              v
                    [Dismiss overlay]
                    [Return to previous context]
```

**Example HelpEntry instances**:

| Key | Action | Description | Context |
|-----|--------|-------------|---------|
| `↑/↓` | Navigate files | Move cursor up/down in file list | Navigation |
| `Tab` | Switch pane | Cycle focus between files and diff pane | Navigation |
| `a` | Add line comment | Create comment for current line | Commenting |
| `s` | Select range | Enter Select Mode to mark range for comment | Commenting |
| `c` | Add file comment | Create file-level comment | Commenting |
| `e` | Edit comment | Edit or delete existing comment at cursor | Commenting |
| `/` | Search | Enter search mode to find text in diff | Search |
| `n` | Next match | Jump to next search result | Search |
| `N` | Previous match | Jump to previous search result | Search |
| `Esc` | Exit mode | Exit search or select mode | General |
| `?` | Help | Show/hide this help overlay | General |
| `q` | Quit | Exit application and save review | General |

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│   CommentStore      │
│   (from M3)         │
└──────────┬──────────┘
           │
           │ contains
           │
           ▼
    ┌─────────────┐
    │   Comment   │◄──────────┐
    │   (from M3) │           │
    └──────┬──────┘           │
           │                  │ references
           │ uses             │
           │                  │
           ▼            ┌─────┴───────────┐
    ┌─────────────┐    │ EditableComment │
    │CommentTarget│    └─────────────────┘
    │  (from M3)  │            ▲
    └─────────────┘            │
                               │ created by
                               │
                        ┌──────┴────────┐
                        │  EditContext  │
                        └───────────────┘
                               ▲
                               │ queries
                               │
                        ┌──────┴────────┐
                        │   DiffPane    │
                        │   (widget)    │
                        └───────────────┘
                               │
                               │ manages
                               │
                               ▼
                        ┌──────────────┐
                        │ SearchState  │
                        └──────┬───────┘
                               │
                               │ contains
                               │
                  +────────────┴────────────+
                  │                         │
                  ▼                         ▼
          ┌──────────────┐         ┌──────────────┐
          │ SearchQuery  │         │ SearchMatch  │
          └──────────────┘         └──────────────┘
                                           │
                                           │ produces
                                           │
                                           ▼
                                   (0 or more matches)


                        ┌──────────────┐
                        │ HelpOverlay  │
                        │  (widget)    │
                        └──────┬───────┘
                               │
                               │ displays
                               │
                               ▼
                        ┌──────────────┐
                        │  HelpEntry   │
                        └──────────────┘
                               │
                               │ grouped by
                               │
                               ▼
                        (context category)
```

---

## Implementation Notes

### EditableComment Usage
- When user presses 'e', create EditContext to check for existing comment
- If comment exists, extract Comment object from CommentStore by ID
- Use Comment data to create EditableComment (effectively a view model)
- EditableComment is short-lived: created for edit operation, discarded after save/cancel
- On save: update original Comment in CommentStore with new text
- On delete (empty text): remove Comment from CommentStore entirely

### SearchState Lifecycle
- SearchState is per-file and managed by DiffPane widget
- When file changes: reset SearchState to initial values (query=None, matches=[], current_index=-1)
- When search activated ('/'): create SearchQuery, keep matches empty until Enter pressed
- On Enter: execute search, populate matches list, set current_index to 0 (if matches exist)
- On 'n'/'N': increment/decrement current_index with wrap-around (0 to len-1 to 0...)
- On Esc: clear query and matches immediately
- SearchMatch highlighting must be visually distinct from current match

### HelpEntry Organization
- All HelpEntry instances are statically defined at application startup
- Organized by context: Navigation, Commenting, Search, General
- Help overlay renders entries grouped by context with section headers
- If total entries exceed terminal height, overlay must be scrollable (per FR-030)
- Help is global (accessible from any screen per FR-029)

### Data Flow Summary

**Edit Flow**:
```
User presses 'e'
  → Create EditContext(file_path, cursor_line)
  → Query CommentStore for comment at position
  → If found: Create EditableComment from Comment
  → Show edit dialog with pre-filled text
  → On confirm: Update Comment in store OR delete if text empty
  → Refresh diff pane to update markers
```

**Search Flow**:
```
User presses '/'
  → Show search input field
  → User types pattern
  → User presses Enter
  → Create SearchQuery(pattern, case_sensitive=True, is_regex=False)
  → Scan diff text for matches
  → For each match: Create SearchMatch(line_number, char_offset, matched_text, length)
  → Store in SearchState.matches list
  → Set SearchState.current_index = 0
  → Jump to first match
  → User presses 'n'/'N' to navigate matches
  → Update current_index and scroll to match
```

**Help Flow**:
```
Application startup
  → Initialize list of HelpEntry instances
  → Group by context category
User presses '?'
  → Show HelpOverlay with all entries
  → Render sections: Navigation, Commenting, Search, General
  → Enable scrolling if needed
User presses '?' or Esc
  → Dismiss overlay
  → Return to previous screen state
```

---

## Validation Summary

All entities must enforce these constraints:

| Entity | Key Validation Rules |
|--------|---------------------|
| EditableComment | comment_id exists in store, text 1-10k chars (or empty=delete), comment_type matches target |
| SearchQuery | pattern non-empty, case_sensitive=True, is_regex=False |
| SearchMatch | line_number >= 1, char_offset >= 0, matched_text equals pattern |
| SearchState | current_index in valid range (-1 or 0 to len-1), query/matches/index consistency |
| EditContext | file_path non-empty, cursor_line >= 1, existing_comment valid or None |
| HelpEntry | key/action/description non-empty, context in allowed categories |

---

## Status

- [x] Entities extracted from spec.md
- [x] Fields and types documented
- [x] Validation rules specified
- [x] Relationships mapped
- [x] State transitions defined
- [x] Implementation notes added
