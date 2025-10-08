"""DiffPane widget - the goat's detailed view of changes.

This pane displays the actual diff content with ANSI colors and line numbers.
Like a goat carefully examining each foothold on the cliff!
"""

from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import VerticalScroll

from racgoat.parser.models import DiffFile
from racgoat.constants import DIFF_PANE_WIDTH_PERCENT
from racgoat.ui.models import ApplicationMode, SearchState
from racgoat.ui.widgets.diff_renderer import DiffRenderer
from racgoat.ui.widgets.diff_navigation import DiffNavigation
from racgoat.ui.widgets.diff_search import DiffSearch

if TYPE_CHECKING:
    from racgoat.services.comment_store import CommentStore


class DiffPane(VerticalScroll):
    """Diff pane widget for displaying file diff content.

    This widget renders diff hunks with ANSI color highlighting and
    post-change line numbers. The goat sees every detail!

    Attributes:
        can_focus: Allow this pane to receive keyboard focus
        current_file: The DiffFile currently being displayed
        current_line: Current cursor line number (for comment operations)
        app_mode: Current application mode (reactive)
        comment_store: Reference to comment store for markers
    """

    app_mode = reactive(ApplicationMode.NORMAL)

    DEFAULT_CSS = f"""
    DiffPane {{
        width: {DIFF_PANE_WIDTH_PERCENT}%;
        border: solid $accent;
        padding: 1;
    }}

    DiffPane:focus-within {{
        border: solid $primary;
    }}

    DiffPane > Static {{
        width: 100%;
    }}
    """

    def __init__(
        self,
        *,
        comment_store: "CommentStore | None" = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize diff pane.

        Args:
            comment_store: Reference to comment store for markers (optional)
            name: Widget name (optional)
            id: Widget ID (optional, default: "diff-pane")

        Note: Initial content is empty. Use display_file() to populate.
        """
        super().__init__(name=name, id=id or "diff-pane")
        self.current_file: DiffFile | None = None
        self.current_line: int | None = None
        self.comment_store = comment_store

        # SELECT mode state
        self.select_start_line: int | None = None
        self.select_end_line: int | None = None

        # Content widget
        self._content_widget: Static | None = None

        # Per-file state tracking: {file_path: (scroll_y, current_line)}
        self._file_states: dict[str, tuple[float, int]] = {}

        # Initialize helper modules
        self.renderer = DiffRenderer(comment_store=comment_store, app=None)
        self.navigation = DiffNavigation(self)
        self.search = DiffSearch()

        # Expose search_state for compatibility
        self.search_state = self.search.search_state

    def on_mount(self) -> None:
        """Initialize when mounted - set app reference for renderer."""
        self.renderer.app = self.app
        self.current_line = None

    def action_scroll_up(self) -> None:
        """Override VerticalScroll's scroll_up to use our cursor movement."""
        self.action_move_up()

    def action_scroll_down(self) -> None:
        """Override VerticalScroll's scroll_down to use our cursor movement."""
        self.action_move_down()

    def compose(self) -> ComposeResult:
        """Compose the diff pane with a Static widget inside for content."""
        self._content_widget = Static("", id="diff-content")
        yield self._content_widget

    def display_file(self, file: DiffFile, refresh_only: bool = False) -> None:
        """Render diff hunks for a file.

        The goat carefully walks through each hunk, painting it with colors!

        Args:
            file: File to display (must have hunks populated)
            refresh_only: If True, only refresh rendering without changing scroll/cursor state

        Raises:
            ValueError: If file is None
        """
        if file is None:
            raise ValueError("file cannot be None")

        # Save current file's state before switching (unless refreshing current file)
        if not refresh_only and self.current_file and self.current_file.file_path != file.file_path:
            if self.current_line is not None:
                self._file_states[self.current_file.file_path] = (self.scroll_y, self.current_line)

        self.current_file = file

        # Restore or initialize state for this file (unless just refreshing)
        if not refresh_only:
            if file.file_path in self._file_states:
                # Restore saved state
                saved_scroll_y, saved_line = self._file_states[file.file_path]
                self.current_line = saved_line
            else:
                # First time viewing this file - start at top
                self.current_line = self.navigation.get_first_valid_line(file)

        # Render content using renderer
        text = self.renderer.render_file(
            file=file,
            current_line=self.current_line,
            app_mode=self.app_mode,
            select_start_line=self.select_start_line,
            select_end_line=self.select_end_line,
            search_state=self.search_state,
        )

        if self._content_widget:
            self._content_widget.update(text)

        # Restore scroll position or scroll to top
        if not refresh_only:
            if file.file_path in self._file_states:
                saved_scroll_y, _ = self._file_states[file.file_path]
                self.scroll_y = saved_scroll_y
            else:
                # First time viewing - scroll to top
                self.scroll_home(animate=False)

    def clear(self) -> None:
        """Clear diff content (show empty state).

        The goat steps back, leaving the cliff bare!
        """
        self.current_file = None
        if self._content_widget:
            self._content_widget.update(Text("", style="dim"))

    def on_show(self) -> None:
        """Update current line when shown."""
        if self.current_file and self.current_line is None:
            self.current_line = self.navigation.get_first_valid_line(self.current_file)

    def on_focus(self) -> None:
        """Update current line when focused."""
        # Ensure current line is set when focused (needed for commenting)
        if self.current_file and self.current_line is None:
            self.current_line = self.navigation.get_first_valid_line(self.current_file)

        # Refresh display to show cursor marker (without changing scroll/cursor state)
        if self.current_file:
            self.display_file(self.current_file, refresh_only=True)
            # Scroll to cursor to ensure it's visible when pane gains focus
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)

    def action_move_up(self) -> None:
        """Move cursor/selection up one line."""
        if not self.current_file or self.current_line is None:
            return

        new_current, new_select_end = self.navigation.move_up(
            self.current_file,
            self.current_line,
            self.app_mode,
            self.select_end_line,
        )

        if new_current != self.current_line or new_select_end != self.select_end_line:
            self.current_line = new_current
            self.select_end_line = new_select_end
            self.display_file(self.current_file, refresh_only=True)
            if self.app_mode == ApplicationMode.NORMAL:
                self.navigation.scroll_to_cursor(self.current_file, self.current_line)

    def action_move_down(self) -> None:
        """Move cursor/selection down one line."""
        if not self.current_file or self.current_line is None:
            return

        new_current, new_select_end = self.navigation.move_down(
            self.current_file,
            self.current_line,
            self.app_mode,
            self.select_end_line,
        )

        if new_current != self.current_line or new_select_end != self.select_end_line:
            self.current_line = new_current
            self.select_end_line = new_select_end
            self.display_file(self.current_file, refresh_only=True)
            if self.app_mode == ApplicationMode.NORMAL:
                self.navigation.scroll_to_cursor(self.current_file, self.current_line)

    def action_page_up(self) -> None:
        """Move cursor up by approximately one page (viewport height).

        The goat leaps up the cliff in great bounds!
        """
        if not self.current_file or self.current_line is None:
            return

        new_line = self.navigation.page_up(
            self.current_file,
            self.current_line,
            self.size.height,
        )

        if new_line and new_line != self.current_line:
            self.current_line = new_line
            self.display_file(self.current_file, refresh_only=True)
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)

    def action_page_down(self) -> None:
        """Move cursor down by approximately one page (viewport height).

        The goat leaps down the cliff in great bounds!
        """
        if not self.current_file or self.current_line is None:
            return

        new_line = self.navigation.page_down(
            self.current_file,
            self.current_line,
            self.size.height,
        )

        if new_line and new_line != self.current_line:
            self.current_line = new_line
            self.display_file(self.current_file, refresh_only=True)
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)

    # Search Functionality

    def execute_search(self, pattern: str) -> None:
        """Execute search and populate matches list.

        The raccoon sniffs through the trash, finding all the shiny patterns!

        Args:
            pattern: Search pattern (case-sensitive literal string)
        """
        if not self.current_file or not pattern:
            self.search_state = SearchState()
            return

        # Execute search using search module
        self.search_state = self.search.execute_search(self.current_file, pattern)

        # Jump to first match if any found
        if self.search_state.matches:
            first_match = self.search_state.matches[0]
            self.current_line = first_match.line_number
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)

        # Refresh display to show highlights
        self.display_file(self.current_file, refresh_only=True)

    def scroll_to_next_match(self) -> None:
        """Navigate to next search match with wrap-around.

        The raccoon hops to the next shiny thing!
        """
        new_line = self.search.scroll_to_next_match()
        if new_line:
            self.current_line = new_line
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)
            # Refresh display to update current match highlighting
            if self.current_file:
                self.display_file(self.current_file, refresh_only=True)

    def scroll_to_previous_match(self) -> None:
        """Navigate to previous search match with wrap-around.

        The raccoon hops back to the previous shiny thing!
        """
        new_line = self.search.scroll_to_previous_match()
        if new_line:
            self.current_line = new_line
            self.navigation.scroll_to_cursor(self.current_file, self.current_line)
            # Refresh display to update current match highlighting
            if self.current_file:
                self.display_file(self.current_file, refresh_only=True)

    def clear_search(self) -> None:
        """Clear search state and remove all highlights.

        The raccoon forgets what it was looking for!
        """
        self.search.clear_search()
        self.search_state = self.search.search_state

        # Refresh display to remove highlights
        if self.current_file:
            self.display_file(self.current_file, refresh_only=True)

    # Edit Functionality

    def action_edit_comment(self) -> None:
        """Edit or delete existing comment at cursor.

        The goat polishes its treasured notes!
        """
        if not self.current_file or not self.current_line or not self.comment_store:
            return

        # Get comment at cursor
        existing_comment = self.comment_store.get_comment_at_cursor(
            self.current_file.file_path, self.current_line
        )

        if not existing_comment:
            # Silent no-op if no comment at cursor (per FR-034)
            return

        # Import here to avoid circular dependency
        from racgoat.ui.widgets.comment_input import CommentInput

        # Show edit dialog with pre-filled text
        if self.app:
            self.app.push_screen(
                CommentInput(prompt="Edit comment:", prefill=existing_comment.text),
                callback=lambda result: self._handle_edit_result(result, existing_comment)
            )

    def _handle_edit_result(self, result: str | None, comment) -> None:
        """Handle edit dialog result (update or delete).

        Args:
            result: New comment text (None if cancelled, "" if delete requested)
            comment: The Comment object being edited
        """
        if result is None:
            # User cancelled (Esc) - do nothing
            return

        if result == "" or not result.strip():
            # Empty text = delete request, show confirmation
            self._show_delete_confirmation(comment)
        else:
            # Update comment text
            if self.comment_store:
                self.comment_store.update(comment.id, result)
                # Refresh display to update markers (no scroll/cursor changes)
                if self.current_file:
                    self.display_file(self.current_file, refresh_only=True)

    def _show_delete_confirmation(self, comment) -> None:
        """Show confirmation dialog for comment deletion.

        Args:
            comment: The Comment object to potentially delete
        """
        from racgoat.ui.widgets.dialogs import ConfirmDialog

        if self.app:
            self.app.push_screen(
                ConfirmDialog(
                    "Delete this comment?\n\n"
                    "Press Enter to confirm or Escape to cancel."
                ),
                callback=lambda confirmed: self._delete_if_confirmed(confirmed, comment)
            )

    def _delete_if_confirmed(self, confirmed: bool, comment) -> None:
        """Delete comment if user confirmed.

        Args:
            confirmed: True if user clicked Yes, False otherwise
            comment: The Comment object to delete
        """
        if confirmed and self.comment_store:
            self.comment_store.delete(comment.id)
            # Refresh display to remove markers
            if self.current_file:
                self.display_file(self.current_file, refresh_only=True)

    # Compatibility method for tests
    def format_hunk(self, hunk, file=None, current_line=None, app_mode=None,
                    select_start_line=None, select_end_line=None, search_state=None):
        """Proxy to renderer.format_hunk for backward compatibility.

        This method exists to maintain compatibility with tests that were
        written before the renderer refactoring.

        Args:
            hunk: DiffHunk to format
            file: DiffFile (default: create stub with empty path)
            current_line: Current cursor line
            app_mode: Application mode
            select_start_line: Selection start
            select_end_line: Selection end
            search_state: Search state

        Returns:
            Rich Text object with formatted hunk
        """
        # Import here to avoid circular dependency
        from racgoat.parser.models import DiffFile
        from racgoat.ui.models import ApplicationMode, SearchState

        # Provide defaults for backward compatibility
        if file is None:
            file = DiffFile(file_path="", added_lines=0, removed_lines=0, hunks=[hunk])
        if app_mode is None:
            app_mode = ApplicationMode.NORMAL
        if search_state is None:
            search_state = SearchState()

        return self.renderer.format_hunk(
            hunk=hunk,
            file=file,
            current_line=current_line,
            app_mode=app_mode,
            select_start_line=select_start_line,
            select_end_line=select_end_line,
            search_state=search_state,
        )
