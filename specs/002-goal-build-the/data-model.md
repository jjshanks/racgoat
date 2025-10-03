# Phase 1: Data Model

**Feature**: TUI Rendering & Navigation (Milestone 2)
**Date**: 2025-10-01

## Entity Definitions

### DiffHunk (NEW - extends Milestone 1)
**Purpose**: Represents a contiguous block of diff changes with line-level detail for UI rendering.

**Attributes**:
- `old_start: int` - Starting line number in old file (before changes)
- `new_start: int` - Starting line number in new file (after changes, used for display)
- `lines: list[tuple[str, str]]` - List of (change_type, content) tuples
  - `change_type` ∈ {'+', '-', ' '} (add, remove, context)
  - `content: str` - Actual line text without prefix

**Validation Rules**:
- `old_start >= 1` (line numbers are 1-indexed)
- `new_start >= 1`
- `lines` cannot be empty (hunk must have at least one line)
- `change_type` must be one of '+', '-', ' ' (validated at parse time)

**State Transitions**: Immutable after creation (dataclass frozen)

**Relationships**:
- Belongs to exactly one `DiffFile`
- `DiffFile.hunks: list[DiffHunk]` (one-to-many)

### DiffFile (EXTENDED from Milestone 1)
**Purpose**: Represents a single changed file with summary statistics AND detailed hunks.

**Existing Attributes** (from Milestone 1):
- `file_path: str` - Relative path to file
- `added_lines: int` - Total count of added lines
- `removed_lines: int` - Total count of removed lines
- `is_binary: bool` - Whether file is binary (filtered out)

**NEW Attributes** (Milestone 2):
- `hunks: list[DiffHunk]` - Ordered list of diff hunks for this file

**Validation Rules**:
- All Milestone 1 rules still apply (file_path non-empty, line counts >= 0)
- `hunks` list order matches diff file order (top to bottom)
- Sum of added lines in hunks MUST equal `added_lines`
- Sum of removed lines in hunks MUST equal `removed_lines`

**Relationships**:
- Belongs to exactly one `DiffSummary`
- Has zero or more `DiffHunk` objects (zero = file deleted/created with no context)

### DiffSummary (NO CHANGES from Milestone 1)
**Purpose**: Aggregates all parsed files for a git diff.

**Attributes**:
- `files: list[DiffFile]` - All non-filtered files

**Properties**:
- `is_empty: bool` - True if no files in summary
- `total_files: int` - Count of files

**Methods**:
- `add_file(file: DiffFile) -> None` - Add or merge file
- `format_output() -> str` - Generate Milestone 1 text output

**Relationships**:
- Has zero or more `DiffFile` objects
- Root entity for diff data

### FilesListItem (NEW - UI-specific)
**Purpose**: Represents a single item in the Files Pane list view.

**Attributes**:
- `file: DiffFile` - Reference to underlying DiffFile data
- `display_text: str` - Formatted display text with truncation and stats
  - Format: `{truncated_path} (+{added} -{removed})`
  - Example: `src/.../widgets/files_pane.py (+15 -3)`

**Validation Rules**:
- `display_text` width MUST be ≤ Files Pane width (truncation applied)
- Truncation preserves start and end of path, replaces middle with "..."

**Relationships**:
- Wraps exactly one `DiffFile`
- Displayed in `FilesPane` widget (UI layer)

### PaneFocusState (NEW - UI-specific)
**Purpose**: Tracks which pane currently has input focus.

**Values**:
- `FILES` - Files Pane has focus (arrow keys navigate file list)
- `DIFF` - Diff Pane has focus (arrow keys scroll diff content)

**State Transitions**:
- `FILES <-> DIFF` via Tab key
- Initial state: `DIFF` (per clarification: Diff Pane receives initial focus)

**Validation Rules**:
- Enum ensures only valid states (no invalid focus state possible)
- Transition only via Tab key or explicit focus action

**Relationships**:
- Singleton state for the App
- Determines which widget receives keyboard input

## Data Flow

### Parse to UI Flow
```
1. Parser (Milestone 1 + extensions)
   ├─ Read git diff from stdin
   ├─ Parse into DiffSummary with DiffFile objects
   ├─ NEW: Parse hunks into DiffHunk objects
   └─ Filter binary/generated files

2. App initialization (Milestone 2)
   ├─ Receive DiffSummary from parser
   ├─ Check is_empty → show "No diff" message OR two-pane layout
   └─ Pass DiffSummary to UI widgets

3. FilesPane widget
   ├─ Iterate DiffSummary.files
   ├─ Create FilesListItem for each DiffFile
   ├─ Truncate file paths if needed
   └─ Render ListView with items

4. DiffPane widget
   ├─ Receive selected DiffFile from FilesPane
   ├─ Iterate DiffFile.hunks
   ├─ Format each DiffHunk.lines with ANSI colors
   │  ├─ '+' lines → [green]+{content}[/]
   │  ├─ '-' lines → [red]-{content}[/]
   │  └─ ' ' lines → [dim] {content}[/]
   ├─ Add post-change line numbers from DiffHunk.new_start
   └─ Render in RichLog or Static widget
```

### Focus Management Flow
```
1. User presses Tab
   ├─ App action_focus_next() triggered
   ├─ Current focus: FILES → focus(DiffPane)
   │  └─ Update PaneFocusState to DIFF
   ├─ Current focus: DIFF → focus(FilesPane)
   │  └─ Update PaneFocusState to FILES
   └─ Visual indicator updated (border color, status bar text)

2. Arrow key pressed
   ├─ If PaneFocusState == FILES
   │  └─ ListView navigates file list (built-in behavior)
   │     └─ On selection change → update DiffPane content
   ├─ If PaneFocusState == DIFF
   │  └─ ScrollView scrolls diff content (built-in behavior)
```

## Validation Strategy

### Parser Layer Validation
- `DiffHunk.lines` cannot be empty → assert during parsing
- Line counts match hunk content → calculate during parsing, compare on DiffFile creation
- Invalid change_type → raise ParseError with helpful message

### UI Layer Validation
- File path truncation width → clamp to minimum 20 characters (show at least filename)
- Empty DiffSummary → display "No diff" message (not an error)
- Missing hunks on DiffFile → display "File metadata only (no content)" in Diff Pane

### Contract Test Coverage
- `test_diff_hunk_validates_line_numbers()` - old_start/new_start >= 1
- `test_diff_hunk_rejects_empty_lines()` - hunks must have content
- `test_diff_file_hunk_counts_match_totals()` - sum(hunk lines) == added_lines/removed_lines
- `test_files_list_item_truncates_long_paths()` - truncation preserves start/end
- `test_pane_focus_state_transitions_on_tab()` - FILES <-> DIFF only

## Entity Relationship Diagram (ASCII)

```
┌─────────────────┐
│  DiffSummary    │
│  - files: list  │
│  - is_empty     │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│   DiffFile      │
│  - file_path    │
│  - added_lines  │
│  - removed_lines│
│  - hunks: list  │ ◄─── Extended from Milestone 1
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│   DiffHunk      │ ◄─── NEW for Milestone 2
│  - old_start    │
│  - new_start    │
│  - lines: list  │
└─────────────────┘

                    ┌──────────────────┐
                    │ PaneFocusState   │ ◄─── NEW (UI state)
                    │  - FILES | DIFF  │
                    └──────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ FilesListItem   │ ◄───┐ │   FilesPane     │ ◄─── NEW (UI widgets)
│  - file         │     │ │  (ListView)     │
│  - display_text │     │ └─────────────────┘
└─────────────────┘     │
                        │ ┌─────────────────┐
                        └─│   DiffPane      │
                          │  (RichLog)      │
                          └─────────────────┘
```

## Extensions for Future Milestones

### Milestone 3 (Commenting Engine)
- Add `Comment` entity with `line_number`, `content`, `type` (line/range/file)
- Add `DiffFile.comments: list[Comment]` relationship
- Add `DiffHunk.line_has_comment(line_num: int) -> bool` method

### Milestone 4 (Markdown Output)
- Add `DiffSummary.branch_name: str | None` and `commit_sha: str | None` attributes
- Add `Comment.to_markdown() -> str` method
- Add `DiffSummary.export_review(comments: list[Comment], output_path: Path) -> None`

### Milestone 6 (Performance Hardening)
- Add `DiffFile.hunk_count: int` property for lazy loading decision
- Add `DiffHunk.is_loaded: bool` for deferred content loading
- Add `DiffPane.load_visible_hunks(viewport_range: range) -> None` for virtual scrolling

---
**Phase 1 Data Model Complete**: Entities defined, validation rules established, relationships documented. Ready for contract generation.
