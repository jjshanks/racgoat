# Widget Contracts

**Feature**: TUI Rendering & Navigation (Milestone 2)
**Date**: 2025-10-01

## Overview
This document defines the API contracts for UI widgets in Milestone 2. Each widget contract specifies:
- Public methods and their signatures
- Input/output types and validation
- Event emissions
- Composition requirements (child widgets)

Contracts are validated via contract tests in `tests/contract/test_milestone2/`.

---

## FilesPane Widget Contract

### Purpose
Displays a scrollable list of changed files with line count summaries. Handles file selection and focus management.

### Type Definition
```python
class FilesPane(ListView):
    """Files pane widget for displaying changed files list."""
```

### Constructor
```python
def __init__(self, diff_summary: DiffSummary, *, name: str | None = None, id: str | None = None) -> None:
    """Initialize files pane with diff data.

    Args:
        diff_summary: Parsed diff data containing file list
        name: Widget name (optional)
        id: Widget ID (optional, default: "files-pane")

    Raises:
        ValueError: If diff_summary is None
    """
```

### Public Methods

#### `select_file(index: int) -> None`
**Purpose**: Programmatically select a file by index.

**Parameters**:
- `index: int` - Zero-based file index

**Returns**: None

**Emits**: `FileSelected(file: DiffFile)` message

**Raises**:
- `IndexError` if index out of bounds
- `ValueError` if index < 0

**Preconditions**:
- Files pane must be mounted
- `diff_summary.files` must not be empty

**Postconditions**:
- Selected file is highlighted in list view
- `FileSelected` message emitted to app
- Diff pane updates to show selected file's hunks

**Contract Test**: `test_files_pane_select_file_emits_event()`

---

#### `get_selected_file() -> DiffFile | None`
**Purpose**: Get currently selected file.

**Parameters**: None

**Returns**:
- `DiffFile` if a file is selected
- `None` if no selection (empty list)

**Raises**: None

**Preconditions**: Widget must be mounted

**Postconditions**: None (read-only)

**Contract Test**: `test_files_pane_get_selected_file_returns_current()`

---

#### `truncate_path(path: str, max_width: int) -> str`
**Purpose**: Truncate file path to fit pane width.

**Parameters**:
- `path: str` - Full file path
- `max_width: int` - Maximum display width in characters

**Returns**: Truncated path string with "..." in middle if needed

**Raises**:
- `ValueError` if max_width < 10 (too narrow to display anything useful)

**Algorithm**:
```
if len(path) <= max_width:
    return path
available = max_width - 3  # Reserve for "..."
start = available // 2
end = available - start
return path[:start] + "..." + path[-end:]
```

**Contract Test**: `test_files_pane_truncate_path_preserves_start_and_end()`

---

### Properties

#### `file_count: int` (read-only)
**Purpose**: Get count of files in pane.

**Returns**: Number of files in diff_summary

**Contract Test**: `test_files_pane_file_count_matches_diff_summary()`

---

### Events Emitted

#### `FileSelected(file: DiffFile)`
**When**: File selection changes (arrow key navigation OR programmatic select_file())

**Payload**:
- `file: DiffFile` - The newly selected file

**Handled By**: App → forwards to DiffPane.display_file()

**Contract Test**: `test_files_pane_emits_file_selected_on_arrow_key_navigation()`

---

### Keyboard Bindings
- `up` - Move selection up (built-in ListView behavior)
- `down` - Move selection down (built-in ListView behavior)
- `tab` - Move focus to Diff Pane (handled by App)

---

### Composition
```python
def compose(self) -> ComposeResult:
    # Built-in ListView composition
    # ListItem widgets auto-generated from diff_summary.files
    for file in self.diff_summary.files:
        display_text = self._format_file_item(file)
        yield ListItem(Label(display_text), id=f"file-{index}")
```

---

### CSS Styling Requirements
```css
FilesPane {
    width: 30%;  /* 30% of screen width */
    border: solid $accent;
}

FilesPane:focus {
    border: solid $primary;  /* Visual focus indicator */
}

FilesPane ListItem {
    height: 1;  /* Single line per file */
}

FilesPane ListItem.--selected {
    background: $boost;  /* Highlight selected file */
}
```

---

## DiffPane Widget Contract

### Purpose
Displays the diff hunks for the selected file with ANSI color highlighting and post-change line numbers.

### Type Definition
```python
class DiffPane(Static):
    """Diff pane widget for displaying file diff content."""
```

### Constructor
```python
def __init__(self, *, name: str | None = None, id: str | None = None) -> None:
    """Initialize diff pane.

    Args:
        name: Widget name (optional)
        id: Widget ID (optional, default: "diff-pane")

    Note: Initial content is empty. Use display_file() to populate.
    """
```

### Public Methods

#### `display_file(file: DiffFile) -> None`
**Purpose**: Render diff hunks for a file.

**Parameters**:
- `file: DiffFile` - File to display (must have hunks populated)

**Returns**: None

**Raises**:
- `ValueError` if file is None
- `ValueError` if file.hunks is empty (should show "No content" instead)

**Preconditions**:
- Widget must be mounted
- `file.hunks` must be populated by parser

**Postconditions**:
- Diff content rendered with ANSI colors
- Line numbers displayed (post-change, from DiffHunk.new_start)
- Pane scrolled to top

**Contract Test**: `test_diff_pane_display_file_renders_hunks()`

---

#### `clear() -> None`
**Purpose**: Clear diff content (show empty state).

**Parameters**: None

**Returns**: None

**Raises**: None

**Postconditions**: Pane displays empty message or blank content

**Contract Test**: `test_diff_pane_clear_removes_content()`

---

#### `format_hunk(hunk: DiffHunk) -> str`
**Purpose**: Format a single hunk with ANSI colors and line numbers.

**Parameters**:
- `hunk: DiffHunk` - Hunk to format

**Returns**: Rich-formatted string ready for display

**Format**:
```
[dim]  124[/]  context line
[dim]  125[/] [green]+added line[/]
[red]-removed line[/]  (no line number for removed)
[dim]  126[/]  context line
```

**Contract Test**: `test_diff_pane_format_hunk_applies_ansi_colors()`

---

### Properties

#### `current_file: DiffFile | None` (read-only)
**Purpose**: Get currently displayed file.

**Returns**:
- `DiffFile` if a file is displayed
- `None` if pane is empty

**Contract Test**: `test_diff_pane_current_file_reflects_display_state()`

---

### Events Emitted

None. DiffPane is a display-only widget (no user interactions beyond scrolling).

---

### Keyboard Bindings
- `up` - Scroll up (built-in Static/ScrollView behavior)
- `down` - Scroll down (built-in Static/ScrollView behavior)
- `tab` - Move focus to Files Pane (handled by App)

---

### Composition
```python
def compose(self) -> ComposeResult:
    # Static widget with Rich markup content
    # Content set via update() in display_file()
    yield Static("", id="diff-content", classes="diff-content")
```

---

### CSS Styling Requirements
```css
DiffPane {
    width: 70%;  /* 70% of screen width */
    border: solid $accent;
    overflow-y: auto;  /* Enable vertical scrolling */
}

DiffPane:focus {
    border: solid $primary;  /* Visual focus indicator */
}

.diff-content {
    padding: 1;
}
```

---

## TwoPaneLayout Widget Contract

### Purpose
Container widget that manages the two-pane layout (Files Pane + Diff Pane) and focus switching.

### Type Definition
```python
class TwoPaneLayout(Horizontal):
    """Container for two-pane diff viewer layout."""
```

### Constructor
```python
def __init__(self, diff_summary: DiffSummary, *, name: str | None = None, id: str | None = None) -> None:
    """Initialize two-pane layout.

    Args:
        diff_summary: Parsed diff data
        name: Widget name (optional)
        id: Widget ID (optional, default: "two-pane-layout")
    """
```

### Public Methods

#### `action_focus_next() -> None`
**Purpose**: Cycle focus between panes (Tab key handler).

**Parameters**: None

**Returns**: None

**Behavior**:
- If Files Pane focused → focus Diff Pane
- If Diff Pane focused → focus Files Pane

**Contract Test**: `test_two_pane_layout_tab_cycles_focus()`

---

### Properties

#### `focused_pane: str` (read-only)
**Purpose**: Get ID of currently focused pane.

**Returns**: `"files-pane"` or `"diff-pane"`

**Contract Test**: `test_two_pane_layout_focused_pane_reflects_state()`

---

### Events Handled

#### `FileSelected(file: DiffFile)`
**Source**: FilesPane

**Handler**: Forward to DiffPane.display_file()

**Contract Test**: `test_two_pane_layout_forwards_file_selected_to_diff_pane()`

---

### Keyboard Bindings
- `tab` - Cycle focus between panes (action_focus_next)

---

### Composition
```python
def compose(self) -> ComposeResult:
    yield FilesPane(self.diff_summary, id="files-pane")
    yield DiffPane(id="diff-pane")
```

---

### CSS Styling Requirements
```css
TwoPaneLayout {
    height: 100%;
    layout: horizontal;
}
```

---

## App-Level Contract

### RacGoatApp.run_tui(diff_summary: DiffSummary) -> None
**Purpose**: Launch TUI with diff data.

**Parameters**:
- `diff_summary: DiffSummary` - Parsed diff to display

**Returns**: None (blocks until user quits)

**Behavior**:
- If `diff_summary.is_empty` → show "No diff" message
- Else → show TwoPaneLayout with data
- Initial focus: Diff Pane (per clarification)
- Quit on `q` key

**Contract Test**: `test_app_run_tui_shows_two_pane_layout_for_valid_diff()`
**Contract Test**: `test_app_run_tui_shows_no_diff_message_for_empty_diff()`

---

## Contract Test Checklist

### FilesPane Tests
- [ ] `test_files_pane_select_file_emits_event()` - Programmatic selection emits FileSelected
- [ ] `test_files_pane_get_selected_file_returns_current()` - get_selected_file() reflects selection
- [ ] `test_files_pane_truncate_path_preserves_start_and_end()` - Path truncation algorithm
- [ ] `test_files_pane_file_count_matches_diff_summary()` - file_count property
- [ ] `test_files_pane_emits_file_selected_on_arrow_key_navigation()` - Arrow keys emit event

### DiffPane Tests
- [ ] `test_diff_pane_display_file_renders_hunks()` - Hunks rendered with colors
- [ ] `test_diff_pane_clear_removes_content()` - Clear empties pane
- [ ] `test_diff_pane_format_hunk_applies_ansi_colors()` - Color format correctness
- [ ] `test_diff_pane_current_file_reflects_display_state()` - current_file property

### TwoPaneLayout Tests
- [ ] `test_two_pane_layout_tab_cycles_focus()` - Tab switches panes
- [ ] `test_two_pane_layout_focused_pane_reflects_state()` - focused_pane property
- [ ] `test_two_pane_layout_forwards_file_selected_to_diff_pane()` - Event forwarding

### App-Level Tests
- [ ] `test_app_run_tui_shows_two_pane_layout_for_valid_diff()` - Normal case
- [ ] `test_app_run_tui_shows_no_diff_message_for_empty_diff()` - Empty diff edge case
- [ ] `test_app_initial_focus_is_diff_pane()` - Focus starts on Diff Pane

---
**Phase 1 Contracts Complete**: 15 widget contract tests defined. Ready for implementation.
