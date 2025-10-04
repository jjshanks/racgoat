# Milestone 5 Research: Advanced Interaction & Usability

**Research Date**: 2025-10-03
**Focus Areas**: ModalScreen patterns, Text highlighting, Input patterns, Edit/Delete flows
**Target Features**: Help overlay (?), Search (/), Comment edit/delete (e)

---

## 1. ModalScreen Pattern for Help Overlay

### Decision

Use `ModalScreen` from `textual.screen.ModalScreen` to create a dismissible help overlay that displays keybindings in a scrollable modal dialog.

### Rationale

- **Perfect fit for help overlay**: ModalScreen is explicitly designed for temporary dialogs that disable the main interface while keeping it visible underneath
- **Built-in behavior**: Automatically prevents app key bindings from being processed and adds a translucent background
- **Existing pattern in RacGoat**: We already use ModalScreen in `CommentInput` and `ErrorRecoveryScreen`, so this maintains consistency
- **Scrollable content**: ModalScreen can compose any widgets, including `VerticalScroll` containers, to handle help content taller than terminal
- **Clean dismissal**: Built-in `dismiss()` method with typed return values (we can use `ModalScreen[None]` for help since we don't need to return data)

### Implementation Pattern

From existing RacGoat modals and Textual docs:

```python
from textual.screen import ModalScreen
from textual.containers import Container, VerticalScroll
from textual.widgets import Static
from textual.binding import Binding

class HelpScreen(ModalScreen[None]):
    """Help overlay displaying all keybindings."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 80;
        height: auto;
        max-height: 90%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("question_mark", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            with VerticalScroll():
                yield Static("Help content here...")

    def action_dismiss(self) -> None:
        """Dismiss help overlay."""
        self.dismiss(None)
```

### Alternatives Considered

1. **Full-screen overlay without modal**: Would require manual key binding interception and wouldn't preserve the translucent background effect
2. **Inline help panel**: Would require significant layout changes and wouldn't preserve context of what user was reviewing
3. **External help command**: Would take user out of the TUI entirely, breaking flow

### Implementation Notes

- **Keybinding**: `?` to open, `?` or `Esc` to close (both registered in BINDINGS)
- **Content organization**: Group keybindings by context (Navigation, Commenting, Search, Application)
- **Scrollability**: Use `VerticalScroll` container within modal to handle terminals shorter than help content
- **Styling**: Match RacGoat theme (raccoon/goat playful aesthetic with clear visual hierarchy)
- **Display method**: Use `app.push_screen(HelpScreen())` from main app's action_show_help

---

## 2. Text Highlighting for Search

### Decision

Use Rich Text markup with `update()` method on the DiffPane's Static widget to dynamically highlight search matches. Track current match separately for visual distinction.

### Rationale

- **Rich Text is already in use**: DiffPane already uses `rich.text.Text` for diff rendering (see `format_hunk()` method)
- **Markup efficiency**: Rich supports inline markup like `[bold yellow on black]match[/]` for highlighting
- **Update method available**: Static widget's `update()` method allows replacing content dynamically without recreating widget
- **Existing pattern**: DiffPane already has `display_file()` with `refresh_only` parameter for re-rendering without state changes
- **No external dependencies**: All needed functionality already in Rich Text library

### Implementation Pattern

From RacGoat's existing DiffPane and Rich Text docs:

```python
from rich.text import Text

def highlight_search_matches(self, search_term: str) -> None:
    """Re-render diff with search matches highlighted."""
    if not self.current_file or not search_term:
        return

    # Build text with highlighting (similar to format_hunk())
    text = Text()
    # ... existing rendering logic ...

    # For each line, highlight matches
    if search_term.lower() in content.lower():
        # Current match: bold yellow with black background
        # Other matches: yellow with dark gray background
        if line_number == self.current_search_line:
            text.append(highlighted_part, style="bold yellow on black")
        else:
            text.append(highlighted_part, style="yellow on #1a1a1a")

    # Update widget
    if self._content_widget:
        self._content_widget.update(text)
```

### Visual Distinction

- **Current match**: `bold yellow on black` (high contrast, eye-catching)
- **Other matches**: `yellow on #1a1a1a` (visible but less prominent)
- **Match counter**: Display "Match 2/5" in status bar

### Alternatives Considered

1. **Scrolling to matches without highlighting**: Less visual feedback, harder to spot match in context
2. **Changing line background entirely**: Would interfere with existing diff colors (green for additions, etc.)
3. **Using separate overlay widget**: More complex, harder to keep in sync with diff content

### Implementation Notes

- **Search state tracking**: Add fields to DiffPane: `search_term`, `search_matches` (list of line numbers), `current_match_index`
- **Case sensitivity**: Default to case-insensitive search (convert both to lowercase for comparison)
- **Match navigation**: `n` for next, `N` for previous (vi-style)
- **Clear on file change**: Reset search state when changing files
- **Performance**: Only re-highlight when search term changes or user navigates matches (not on every render)
- **Integration with existing rendering**: Modify `format_hunk()` to accept optional search parameters

---

## 3. Input Patterns for Search Field

### Decision

Capture `/` key to show an inline Input widget in the status bar (replacing normal status text temporarily), with `Esc` to cancel and `Enter` to execute search.

### Rationale

- **Inline approach fits TUI patterns**: Similar to vi/less/tmux search - minimal disruption to main content
- **Status bar is ideal location**: Already present at bottom of screen, naturally draws eye for input
- **Input widget already used**: RacGoat uses Input in CommentInput and ErrorRecoveryScreen modals
- **Event handling built-in**: Input widget provides `Input.Submitted` and key events for Esc
- **Focus management**: Can programmatically focus Input when `/` pressed, return focus to DiffPane on Enter/Esc

### Implementation Pattern

From Textual docs and RacGoat's existing widgets:

```python
from textual.widgets import Input

class StatusBar(Static):
    """Status bar with optional inline search input."""

    def __init__(self):
        super().__init__()
        self.search_input: Input | None = None
        self.search_active = False

    def compose(self) -> ComposeResult:
        # Initially show normal status text
        yield Static("", id="status-text")
        # Create search input (hidden by default)
        self.search_input = Input(placeholder="Search...", id="search-input")
        self.search_input.display = False
        yield self.search_input

    def activate_search(self) -> None:
        """Show search input and hide status text."""
        status_text = self.query_one("#status-text", Static)
        status_text.display = False
        self.search_input.display = True
        self.search_input.value = ""
        self.search_input.focus()
        self.search_active = True

    def deactivate_search(self) -> None:
        """Hide search input and restore status text."""
        status_text = self.query_one("#status-text", Static)
        status_text.display = True
        self.search_input.display = False
        self.search_active = False
```

### Keybinding Flow

1. User presses `/` in NORMAL mode → App calls `status_bar.activate_search()`
2. User types search term in Input widget
3. User presses `Enter` → `Input.Submitted` event → Execute search, deactivate input, focus DiffPane
4. User presses `Esc` → Cancel search, deactivate input, focus DiffPane
5. User presses `n`/`N` → Navigate to next/previous match (search stays active in background)

### Alternatives Considered

1. **Modal dialog for search**: More intrusive, blocks view of content while searching
2. **Dedicated search pane**: Takes up too much screen space, not needed for simple text search
3. **Command palette pattern**: Overkill for single search feature, better suited for multi-command interfaces

### Implementation Notes

- **Display toggle**: Use `widget.display = True/False` to show/hide search input vs status text
- **Focus restoration**: Track which widget had focus before search activated, restore on cancel
- **Search on type vs Enter**: Start with Enter-to-search (less disruptive), consider live search later
- **History**: Consider adding up/down arrow to cycle through previous searches (future enhancement)
- **Visual indicator**: Prefix search input with `/` label to match user's mental model
- **Empty search**: Pressing Enter with empty input clears current search highlights

---

## 4. Reusing CommentInput for Edit/Delete

### Decision

Reuse the existing `CommentInput` modal for editing comments. Pre-populate with existing text. If user submits empty text, interpret as delete and show confirmation.

### Rationale

- **Pattern already exists**: `CommentInput` already supports `prefill` parameter for pre-populating text (line 69-70)
- **Consistent UX**: Same dialog for add/edit reduces cognitive load
- **Empty text = delete**: Natural pattern (clear text → delete) matches user expectations
- **Confirmation built-in**: Can show confirmation by detecting empty submission and prompting
- **No new code needed**: Leverages existing modal infrastructure

### Implementation Pattern

From existing CommentInput (racgoat/ui/widgets/comment_input.py):

```python
# Add comment (existing)
def action_add_comment(self) -> None:
    self.app.push_screen(
        CommentInput(prompt="Add comment:"),
        callback=self._handle_comment_result
    )

# Edit comment (new)
def action_edit_comment(self) -> None:
    """Edit existing comment at current line."""
    if not self.current_line:
        return

    # Get existing comment
    comments = self.comment_store.get(self.current_file.file_path, self.current_line)
    if not comments:
        return

    existing_text = comments[0].text  # Get first comment (or show list if multiple)

    # Pre-fill input with existing text
    self.app.push_screen(
        CommentInput(
            prompt="Edit comment:",
            prefill=existing_text
        ),
        callback=lambda result: self._handle_edit_result(result, self.current_line)
    )

def _handle_edit_result(self, result: str | None, line: int) -> None:
    """Handle comment edit submission."""
    if result is None:
        return  # Cancelled

    if result == "":
        # Empty text = delete confirmation
        self.app.push_screen(
            ConfirmDialog("Delete this comment?"),
            callback=lambda confirmed: self._delete_if_confirmed(confirmed, line)
        )
    else:
        # Update comment
        self.comment_store.update(self.current_file.file_path, line, result)
        self.refresh_diff_display()
```

### Delete Confirmation Pattern

Option 1: Reuse ErrorRecoveryScreen pattern (buttons + modal)
Option 2: Create simple ConfirmDialog (Yes/No buttons)

**Decision**: Create `ConfirmDialog` (simpler, reusable for future confirmations)

```python
class ConfirmDialog(ModalScreen[bool]):
    """Simple Yes/No confirmation dialog."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(self.message)
            with Horizontal():
                yield Button("Yes", variant="error", id="yes")
                yield Button("No", variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
```

### Alternatives Considered

1. **Separate EditCommentInput widget**: Unnecessary duplication, prefill parameter already handles this
2. **Immediate delete without confirmation**: Too destructive, no undo mechanism in place
3. **Inline editing in diff pane**: Complex to implement, doesn't fit modal pattern used elsewhere

### Implementation Notes

- **Multiple comments on same line**: Show list picker first, then edit selected comment
- **Comment selection**: If multiple comments at line, show numbered list in initial modal
- **Keybinding**: `e` when focused on line with comment (only show binding in status bar when applicable)
- **Error handling**: If comment was deleted by another process, show error message
- **Refresh after edit**: Call `display_file(refresh_only=True)` to update gutter markers
- **UX feedback**: After edit/delete, briefly show success message in status bar

---

## 5. Screen Stack Management

### Decision

Use Textual's `push_screen()` with callbacks for all modal interactions (help, search input confirmation, edit/delete confirmations).

### Implementation Pattern

From Textual docs on screen management:

```python
# Push screen with callback
self.app.push_screen(HelpScreen(), callback=self._on_help_closed)

# Push screen and wait (async)
result = await self.app.push_screen_wait(CommentInput())

# Dismiss with result
self.dismiss(result_value)
```

### RacGoat Usage

**Synchronous pattern** (preferred for consistency with existing code):

```python
# Help overlay (no result needed)
self.app.push_screen(HelpScreen())

# Comment input (returns str | None)
self.app.push_screen(
    CommentInput(prompt="Add comment:"),
    callback=self._handle_comment_result
)

# Confirmation (returns bool)
self.app.push_screen(
    ConfirmDialog("Delete comment?"),
    callback=self._handle_delete_confirm
)
```

### Implementation Notes

- **Callback pattern**: All existing RacGoat modals use callbacks, maintain consistency
- **Screen stacking**: ModalScreen prevents interaction with screens below (desired behavior)
- **Esc handling**: Each modal handles its own Esc binding to dismiss appropriately
- **Focus restoration**: Textual automatically restores focus when modal is dismissed

---

## 6. Scrolling to Search Matches

### Decision

Reuse DiffPane's existing `_scroll_to_cursor()` pattern, but adapt for search match scrolling via `scroll_to_region()`.

### Rationale

- **Pattern exists**: DiffPane already has `_scroll_to_cursor()` using `scroll_to_region()` (lines 328-344)
- **Region-based scrolling**: Textual's `scroll_to_region(region, center=True)` centers content in viewport
- **Line-to-row mapping**: `_get_cursor_screen_row()` already converts line numbers to screen rows (lines 289-326)
- **Reusable logic**: Can create `_scroll_to_line()` helper that both cursor and search use

### Implementation Pattern

From existing DiffPane scrolling code:

```python
def _scroll_to_line(self, line_number: int, animate: bool = False) -> None:
    """Scroll viewport to show a specific line number.

    Args:
        line_number: Line number to scroll to
        animate: Whether to animate the scroll
    """
    cursor_row = self._get_cursor_screen_row(line_number)
    if cursor_row is None:
        return

    # Create region for line (x, y, width, height)
    region = Region(0, cursor_row, self.size.width, 1)

    # Scroll to center the line in viewport
    self.scroll_to_region(region, center=True, animate=animate)

def scroll_to_next_match(self) -> None:
    """Scroll to next search match."""
    if not self.search_matches or self.current_match_index is None:
        return

    # Move to next match (wrap around)
    self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
    match_line = self.search_matches[self.current_match_index]

    # Scroll to match and re-render with updated highlighting
    self._scroll_to_line(match_line, animate=True)
    self.display_file(self.current_file, refresh_only=True)
```

### Implementation Notes

- **Animation**: Use `animate=True` for search navigation (gives visual cue of movement)
- **Center vs top**: Use `center=True` to show context around match
- **Wrap-around**: When at last match, `n` wraps to first (vi-style behavior)
- **Match persistence**: Search matches persist until new search or file change

---

## 7. Status Bar Integration

### Decision

Extend existing StatusBar to support three states: normal keybindings, search input, and search results display.

### Implementation Pattern

```python
class StatusBar(Static):
    """Context-sensitive status bar."""

    def update_mode(self, mode: StatusBarMode) -> None:
        """Update status bar based on application mode."""
        if mode == StatusBarMode.NORMAL:
            self.update("q: Quit | ?: Help | /: Search | a: Comment | Tab: Focus")
        elif mode == StatusBarMode.SEARCH_INPUT:
            self.update("[/] Search: [input here] | Enter: Execute | Esc: Cancel")
        elif mode == StatusBarMode.SEARCH_RESULTS:
            self.update(f"Match {self.current_match}/{self.total_matches} | n: Next | N: Prev | Esc: Clear")
```

### Alternatives Considered

1. **Separate search bar widget**: Additional screen space, not needed
2. **Floating search indicator**: Complex positioning, modal approach simpler

### Implementation Notes

- **State machine**: Track current status bar state (normal, search_input, search_results, comment_mode)
- **Dynamic updates**: React to app mode changes and search state changes
- **Context-sensitive**: Show different keybindings based on what's focused and what mode is active

---

## Summary of Unknowns / Future Research

1. **Search performance**: Need to benchmark search across large diffs (10k+ lines) to see if incremental matching needed
2. **Comment list UI**: If multiple comments on same line, need to design picker/list interface (deferred to implementation)
3. **Search regex support**: Basic substring search sufficient for M5? Or should we support regex patterns?
4. **Keyboard shortcuts conflicts**: Verify no conflicts between diff pane bindings and new search/help bindings

---

## References

- **Textual ModalScreen**: https://textual.textualize.io/guide/screens/#modal-screens
- **Textual Input Widget**: https://textual.textualize.io/widgets/input/
- **Rich Text Markup**: https://rich.readthedocs.io/en/stable/markup.html
- **Textual Static Widget**: https://textual.textualize.io/widgets/static/
- **Existing RacGoat Modals**:
  - `/home/jjshanks/workspace/racgoat/racgoat/ui/widgets/comment_input.py`
  - `/home/jjshanks/workspace/racgoat/racgoat/ui/widgets/error_dialog.py`
- **Existing DiffPane**: `/home/jjshanks/workspace/racgoat/racgoat/ui/widgets/diff_pane.py`

---

**Next Steps**: Use this research to create detailed design in `design.md` for Phase 1 (spec → design → tasks → implement).
