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
from textual.binding import Binding

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

    def compose(self) -> ComposeResult:
        """Compose the diff pane with a Static widget inside for content."""
        self._content_widget = Static("", id="diff-content")
        yield self._content_widget

    def display_file(self, file: DiffFile) -> None:
        """Render diff hunks for a file.

        The goat carefully walks through each hunk, painting it with colors!

        Args:
            file: File to display (must have hunks populated)

        Raises:
            ValueError: If file is None
        """
        if file is None:
            raise ValueError("file cannot be None")

        self.current_file = file

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
        # Scroll to top when new file displayed
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

        for change_type, content in hunk.lines:
            # Determine gutter marker
            gutter = self._get_gutter_marker(current_line if change_type != "-" else None)

            if change_type == "+":
                # Added line: green, with line number
                text.append(gutter, style=self._get_gutter_style(current_line))
                text.append(f"  {current_line:4} ", style="dim")
                text.append(f"+{content}\n", style="green")
                current_line += 1
            elif change_type == "-":
                # Removed line: red, no line number, no gutter marker
                text.append("  ")  # Gutter space
                text.append("       ", style="dim")  # Indent for alignment
                text.append(f"-{content}\n", style="red")
                # Removed lines don't increment post-change line number
            elif change_type == " ":
                # Context line: dim, with line number
                text.append(gutter, style=self._get_gutter_style(current_line))
                text.append(f"  {current_line:4} ", style="dim")
                text.append(f" {content}\n", style="dim")
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
        self._update_current_line_from_scroll()
