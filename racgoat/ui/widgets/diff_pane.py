"""DiffPane widget - the goat's detailed view of changes.

This pane displays the actual diff content with ANSI colors and line numbers.
Like a goat carefully examining each foothold on the cliff!
"""

from rich.text import Text
from textual.widgets import Static

from racgoat.parser.models import DiffFile, DiffHunk


class DiffPane(Static):
    """Diff pane widget for displaying file diff content.

    This widget renders diff hunks with ANSI color highlighting and
    post-change line numbers. The goat sees every detail!

    Attributes:
        can_focus: Allow this pane to receive keyboard focus
        current_file: The DiffFile currently being displayed
    """

    can_focus = True
    DEFAULT_CSS = """
    DiffPane {
        width: 70%;
        border: solid $accent;
        overflow-y: auto;
        padding: 1;
    }

    DiffPane:focus {
        border: solid $primary;
    }
    """

    def __init__(self, *, name: str | None = None, id: str | None = None) -> None:
        """Initialize diff pane.

        Args:
            name: Widget name (optional)
            id: Widget ID (optional, default: "diff-pane")

        Note: Initial content is empty. Use display_file() to populate.
        """
        super().__init__("", name=name, id=id or "diff-pane")
        self.current_file: DiffFile | None = None

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
            self.update(
                Text(
                    f"📄 {file.file_path}\n\n"
                    "File metadata only (no diff content available)",
                    style="dim",
                )
            )
            return

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

        self.update(text)
        # Scroll to top when new file displayed
        self.scroll_home(animate=False)

    def format_hunk(self, hunk: DiffHunk) -> Text:
        """Format a single hunk with ANSI colors and line numbers.

        Args:
            hunk: Hunk to format

        Returns:
            Rich Text object with formatted hunk

        Format:
            [dim]  124[/]  context line
            [dim]  125[/] [green]+added line[/]
            [red]-removed line[/]  (no line number for removed)
            [dim]  126[/]  context line
        """
        text = Text()

        # Track current line number (post-change)
        current_line = hunk.new_start

        for change_type, content in hunk.lines:
            if change_type == "+":
                # Added line: green, with line number
                text.append(f"  {current_line:4} ", style="dim")
                text.append(f"+{content}\n", style="green")
                current_line += 1
            elif change_type == "-":
                # Removed line: red, no line number
                text.append("       ", style="dim")  # Indent for alignment
                text.append(f"-{content}\n", style="red")
                # Removed lines don't increment post-change line number
            elif change_type == " ":
                # Context line: dim, with line number
                text.append(f"  {current_line:4} ", style="dim")
                text.append(f" {content}\n", style="dim")
                current_line += 1

        return text

    def clear(self) -> None:
        """Clear diff content (show empty state).

        The goat steps back, leaving the cliff bare!
        """
        self.current_file = None
        self.update(Text("", style="dim"))
