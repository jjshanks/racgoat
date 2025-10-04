"""DiffPane widget - the goat's detailed view of changes.

This pane displays the actual diff content with ANSI colors and line numbers.
Like a goat carefully examining each foothold on the cliff!
"""

from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.geometry import Region
from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import VerticalScroll

from racgoat.parser.models import DiffFile, DiffHunk
from racgoat.ui.models import ApplicationMode

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

    # Note: We don't need custom bindings for up/down - we override
    # VerticalScroll's action_scroll_up/down methods instead

    DEFAULT_CSS = """
    DiffPane {
        width: 70%;
        border: solid $accent;
        padding: 1;
    }

    DiffPane:focus-within {
        border: solid $primary;
    }

    DiffPane > Static {
        width: 100%;
    }
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
        self._content_widget: Static | None = None
        # Per-file state tracking: {file_path: (scroll_y, current_line)}
        self._file_states: dict[str, tuple[float, int]] = {}

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
                self.current_line = self._get_first_valid_line(file)

        # If no hunks, show message
        if not file.hunks:
            text = Text(
                f"📄 {file.file_path}\n\n"
                "File metadata only (no diff content available)",
                style="dim",
            )
        else:
            # Build Rich Text with all hunks
            text = Text()
            text.append(f"📄 {file.file_path}\n", style="bold cyan")
            text.append(
                f"   +{file.added_lines} -{file.removed_lines} lines\n\n",
                style="dim italic",
            )

            # Render each hunk
            for hunk_idx, hunk in enumerate(file.hunks):
                if hunk_idx > 0:
                    text.append("\n")  # Spacing between hunks

                hunk_text = self.format_hunk(hunk)
                text.append(hunk_text)

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

    def format_hunk(self, hunk: DiffHunk) -> Text:
        """Format a single hunk with ANSI colors, line numbers, and gutter markers.

        Args:
            hunk: Hunk to format

        Returns:
            Rich Text object with formatted hunk

        Format (with gutter):
            [gutter] [dim]  124[/]  context line
            *        [dim]  125[/] [green]+added line[/]  (has comment)
            [red]-removed line[/]  (no line number for removed)
            [dim]  126[/]  context line
        """
        text = Text()

        # Track current line number (post-change)
        current_line = hunk.new_start

        # Determine selection range if in SELECT mode
        select_min = None
        select_max = None
        if self.select_start_line is not None and self.select_end_line is not None:
            select_min = min(self.select_start_line, self.select_end_line)
            select_max = max(self.select_start_line, self.select_end_line)

        for change_type, content in hunk.lines:
            # Determine gutter marker
            gutter = self._get_gutter_marker(current_line if change_type != "-" else None)

            # Check if line is in selection
            is_selected = (
                select_min is not None and
                select_max is not None and
                change_type != "-" and
                select_min <= current_line <= select_max
            )

            # Check if this is the current line (for cursor in NORMAL mode)
            is_current = (
                self.app_mode == ApplicationMode.NORMAL and
                change_type != "-" and
                current_line == self.current_line
            )

            if change_type == "+":
                # Added line: green, with line number
                if is_selected:
                    text.append(">", style="bold yellow")  # Selection marker
                elif is_current:
                    text.append(">", style="bold cyan")  # Cursor marker
                else:
                    text.append(gutter, style=self._get_gutter_style(current_line))
                text.append(f"  {current_line:4} ", style="dim")
                line_style = "bold green on #333333" if is_selected else "green"
                text.append(f"+{content}\n", style=line_style)
                current_line += 1
            elif change_type == "-":
                # Removed line: red, no line number, no gutter marker
                text.append("  ")  # Gutter space
                text.append("       ", style="dim")  # Indent for alignment
                text.append(f"-{content}\n", style="red")
                # Removed lines don't increment post-change line number
            elif change_type == " ":
                # Context line: dim, with line number
                if is_selected:
                    text.append(">", style="bold yellow")  # Selection marker
                elif is_current:
                    text.append(">", style="bold cyan")  # Cursor marker
                else:
                    text.append(gutter, style=self._get_gutter_style(current_line))
                text.append(f"  {current_line:4} ", style="dim")
                line_style = "bold on #333333" if is_selected else "dim"
                text.append(f" {content}\n", style=line_style)
                current_line += 1

        return text

    def _get_gutter_marker(self, line_number: int | None) -> str:
        """Get gutter marker for a line.

        Args:
            line_number: Line number (None for removed lines)

        Returns:
            Gutter marker string ("* " for comment, "**" for overlap, "  " for none)
        """
        if line_number is None or not self.comment_store or not self.current_file:
            return "  "

        comments = self.comment_store.get(self.current_file.file_path, line_number)
        count = len(comments)

        if count == 0:
            return "  "
        elif count == 1:
            return "* "
        else:  # count > 1 (overlap)
            return "**"

    def _get_gutter_style(self, line_number: int | None) -> str:
        """Get style for gutter marker.

        Args:
            line_number: Line number

        Returns:
            Style string for Rich Text
        """
        if line_number is None or not self.comment_store or not self.current_file:
            return ""

        comments = self.comment_store.get(self.current_file.file_path, line_number)
        count = len(comments)

        if count == 0:
            return ""
        elif count == 1:
            return "yellow"
        else:  # count > 1 (overlap)
            return "red"

    def _get_cursor_screen_row(self, line_number: int) -> int | None:
        """Calculate which screen row a line number appears on.

        Args:
            line_number: Line number to find

        Returns:
            0-based row index in rendered content, or None if not found
        """
        if not self.current_file or not self.current_file.hunks:
            return None

        row = 0

        # Header rows: file path + stats + blank line
        row += 3

        # Iterate through hunks to find target line
        for hunk_idx, hunk in enumerate(self.current_file.hunks):
            # Add spacing between hunks (except before first)
            if hunk_idx > 0:
                row += 1

            # Track current line number in this hunk
            current_line = hunk.new_start

            for change_type, _ in hunk.lines:
                # Check if this is our target line (only for lines with numbers)
                if change_type in ('+', ' '):
                    if current_line == line_number:
                        return row
                    current_line += 1

                # All lines (including removed) take one row
                row += 1

        # Line number not found in any hunk
        return None

    def _scroll_to_cursor(self) -> None:
        """Scroll viewport to center the cursor line.

        The goat ensures you can always see where it stands!
        """
        if self.current_line is None:
            return

        cursor_row = self._get_cursor_screen_row(self.current_line)
        if cursor_row is None:
            return

        # Create region for cursor line (x, y, width, height)
        region = Region(0, cursor_row, self.size.width, 1)

        # Scroll to center the cursor in viewport (no animation for responsiveness)
        self.scroll_to_region(region, center=True, animate=False)

    def clear(self) -> None:
        """Clear diff content (show empty state).

        The goat steps back, leaving the cliff bare!
        """
        self.current_file = None
        if self._content_widget:
            self._content_widget.update(Text("", style="dim"))

    def on_mount(self) -> None:
        """Initialize cursor position when mounted."""
        self.current_line = None

    def _get_first_valid_line(self, file: DiffFile) -> int | None:
        """Get the first valid line number in a file.

        Args:
            file: DiffFile to get first line from

        Returns:
            First valid line number, or None if no valid lines
        """
        if not file.hunks:
            return None

        # Get first hunk's first non-removed line
        first_hunk = file.hunks[0]
        if first_hunk.lines:
            for change_type, _ in first_hunk.lines:
                if change_type in ('+', ' '):
                    return first_hunk.new_start

        return first_hunk.new_start if first_hunk.new_start else None

    def _get_valid_lines_list(self) -> list[int]:
        """Get ordered list of all valid line numbers in current file.

        Returns:
            List of line numbers (excludes removed lines), or empty list if no file
        """
        if not self.current_file or not self.current_file.hunks:
            return []

        valid_lines = []
        for hunk in self.current_file.hunks:
            current_line = hunk.new_start
            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    valid_lines.append(current_line)
                    current_line += 1

        return valid_lines

    def _update_current_line_from_scroll(self) -> None:
        """Update current_line based on scroll position.

        This is a simplified approach - gets the first visible line.
        """
        if not self.current_file or not self.current_file.hunks:
            self.current_line = None
            return

        # Get first hunk's first line as default
        first_hunk = self.current_file.hunks[0]
        if first_hunk.lines:
            for change_type, _ in first_hunk.lines:
                if change_type in ('+', ' '):
                    self.current_line = first_hunk.new_start
                    return

        self.current_line = first_hunk.new_start if first_hunk.new_start else None

    def on_show(self) -> None:
        """Update current line when shown."""
        self._update_current_line_from_scroll()

    def on_focus(self) -> None:
        """Update current line when focused."""
        # Ensure current line is set when focused (needed for commenting)
        if self.current_file and self.current_line is None:
            self._update_current_line_from_scroll()

        # Refresh display to show cursor marker (without changing scroll/cursor state)
        if self.current_file:
            self.display_file(self.current_file, refresh_only=True)
            # Scroll to cursor to ensure it's visible when pane gains focus
            self._scroll_to_cursor()

    def action_move_up(self) -> None:
        """Move cursor/selection up one line."""
        from racgoat.ui.models import ApplicationMode

        if not self.current_file or self.current_line is None:
            return

        if self.app_mode == ApplicationMode.SELECT:
            # SELECT mode: expand selection upward
            if self.select_end_line is not None and self.current_file.hunks:
                # Get min line from first hunk
                first_hunk = self.current_file.hunks[0]
                min_line = first_hunk.new_start

                if self.select_end_line > min_line:
                    self.select_end_line -= 1
                    self.display_file(self.current_file, refresh_only=True)
            return

        # NORMAL mode: move cursor up
        # Find previous valid line
        for hunk in self.current_file.hunks:
            current_line = hunk.new_start
            prev_line = None

            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    if current_line == self.current_line and prev_line is not None:
                        # Found current line, move to previous
                        self.current_line = prev_line
                        self.display_file(self.current_file, refresh_only=True)
                        self._scroll_to_cursor()
                        return
                    prev_line = current_line
                    current_line += 1

    def action_move_down(self) -> None:
        """Move cursor/selection down one line."""
        from racgoat.ui.models import ApplicationMode

        if not self.current_file or self.current_line is None:
            return

        if self.app_mode == ApplicationMode.SELECT:
            # SELECT mode: expand selection downward
            if self.select_end_line is not None and self.current_file.hunks:
                # Get max line from last hunk
                last_hunk = self.current_file.hunks[-1]
                max_line = last_hunk.new_start + sum(1 for ct, _ in last_hunk.lines if ct != '-') - 1

                if self.select_end_line < max_line:
                    self.select_end_line += 1
                    self.display_file(self.current_file, refresh_only=True)
            return

        # NORMAL mode: move cursor down
        # Find next valid line
        found_current = False
        for hunk in self.current_file.hunks:
            current_line = hunk.new_start

            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    if found_current:
                        # This is the next line
                        self.current_line = current_line
                        self.display_file(self.current_file, refresh_only=True)
                        self._scroll_to_cursor()
                        return
                    if current_line == self.current_line:
                        found_current = True
                    current_line += 1

    def action_page_up(self) -> None:
        """Move cursor up by approximately one page (viewport height).

        The goat leaps up the cliff in great bounds!
        """
        if not self.current_file or self.current_line is None:
            return

        # Get all valid lines
        valid_lines = self._get_valid_lines_list()
        if not valid_lines:
            return

        # Find current cursor index
        try:
            current_idx = valid_lines.index(self.current_line)
        except ValueError:
            # Current line not in valid lines - shouldn't happen, but recover gracefully
            self.current_line = valid_lines[0] if valid_lines else None
            return

        # Calculate page size (approximate viewport height minus a few lines for context)
        page_size = max(1, self.size.height - 3)

        # Jump up by page_size lines
        new_idx = max(0, current_idx - page_size)
        self.current_line = valid_lines[new_idx]

        # Refresh display and scroll to cursor
        self.display_file(self.current_file, refresh_only=True)
        self._scroll_to_cursor()

    def action_page_down(self) -> None:
        """Move cursor down by approximately one page (viewport height).

        The goat leaps down the cliff in great bounds!
        """
        if not self.current_file or self.current_line is None:
            return

        # Get all valid lines
        valid_lines = self._get_valid_lines_list()
        if not valid_lines:
            return

        # Find current cursor index
        try:
            current_idx = valid_lines.index(self.current_line)
        except ValueError:
            # Current line not in valid lines - shouldn't happen, but recover gracefully
            self.current_line = valid_lines[0] if valid_lines else None
            return

        # Calculate page size (approximate viewport height minus a few lines for context)
        page_size = max(1, self.size.height - 3)

        # Jump down by page_size lines
        new_idx = min(len(valid_lines) - 1, current_idx + page_size)
        self.current_line = valid_lines[new_idx]

        # Refresh display and scroll to cursor
        self.display_file(self.current_file, refresh_only=True)
        self._scroll_to_cursor()
