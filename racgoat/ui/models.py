"""UI-specific data models for TUI rendering.

This module contains models that bridge parser data and Textual widgets.
"""

from dataclasses import dataclass
from enum import Enum

from racgoat.parser.models import DiffFile


class PaneFocusState(Enum):
    """Tracks which pane currently has input focus.

    The goat hops between panes with the grace of a mountain climber!

    Values:
        FILES: Files Pane has focus (arrow keys navigate file list)
        DIFF: Diff Pane has focus (arrow keys scroll diff content)

    Transitions:
        FILES <-> DIFF via Tab key
        Initial state: DIFF (Diff Pane receives initial focus per spec)
    """

    FILES = "files"
    DIFF = "diff"


class ApplicationMode(Enum):
    """Represents the current interaction mode of the TUI.

    The raccoon switches between its normal scavenging mode and its
    selective treasure-hoarding mode!

    Values:
        NORMAL: Standard navigation and commenting (default mode)
        SELECT: Range selection active (user is marking lines for a range comment)

    State Transitions:
        NORMAL --[user presses 's' in diff pane]--> SELECT
        SELECT --[user presses Esc]--> NORMAL
        SELECT --[user presses Enter after selecting range]--> NORMAL (after creating comment)
        SELECT --[user cancels input prompt]--> NORMAL (no comment created)

    Constraints:
        - File navigation is disabled in SELECT mode
        - Single-line and file-level comment actions disabled in SELECT mode
        - Only arrow keys, Enter, and Esc are active in SELECT mode
    """

    NORMAL = "normal"
    SELECT = "select"


@dataclass
class FilesListItem:
    """Represents a single item in the Files Pane list view.

    Like a raccoon organizing its treasures, this item wraps a DiffFile
    with display-friendly formatting.

    Attributes:
        file: Reference to underlying DiffFile data
        display_text: Formatted display text with truncation and stats
                     Format: {truncated_path} (+{added} -{removed})
                     Example: "src/.../widgets/files_pane.py (+15 -3)"

    Validation:
        - display_text width must be <= Files Pane width (truncation applied)
        - Truncation preserves start and end of path, replaces middle with "..."
    """

    file: DiffFile
    display_text: str

    @staticmethod
    def from_file(file: DiffFile, max_width: int | None = None) -> "FilesListItem":
        """Create FilesListItem from DiffFile with optional truncation.

        Args:
            file: DiffFile to wrap
            max_width: Maximum display width (None = no truncation)

        Returns:
            FilesListItem with formatted display text
        """
        # Format: path (+added -removed)
        stats = f" (+{file.added_lines} -{file.removed_lines})"
        path = file.file_path

        # Truncate path if needed
        if max_width is not None:
            stats_len = len(stats)
            path_max = max_width - stats_len
            if path_max >= 10 and len(path) > path_max:
                path = FilesListItem._truncate_path(path, path_max)

        display_text = f"{path}{stats}"
        return FilesListItem(file=file, display_text=display_text)

    @staticmethod
    def _truncate_path(path: str, max_width: int) -> str:
        """Truncate file path to fit width, preserving start and end.

        Args:
            path: Full file path
            max_width: Maximum display width

        Returns:
            Truncated path with "..." in middle

        Raises:
            ValueError: If max_width < 10 (too narrow)
        """
        if max_width < 10:
            raise ValueError(f"max_width must be >= 10, got {max_width}")

        if len(path) <= max_width:
            return path

        # Reserve 3 chars for "..."
        available = max_width - 3
        start_chars = available // 2
        end_chars = available - start_chars

        return f"{path[:start_chars]}...{path[-end_chars:]}"


@dataclass
class CommentMarker:
    """Visual indicator for comments in the diff pane gutter.

    Like a shiny wrapper on the raccoon's favorite trash can - it marks
    the spot where wisdom is stashed!

    Attributes:
        symbol: Character to display ("*" for single comment, "**" for overlapping)
        style: Rich Text style string (e.g., "[yellow]*[/yellow]")
        line_number: Which line this marker appears on
        comment_count: Number of comments on this line (for overlap indication)

    Validation:
        - symbol defaults to "*" if comment_count == 1, "**" if comment_count > 1
        - style varies based on comment_count (e.g., yellow for single, red for overlapping)
        - line_number must be a valid post-change line number from the diff
    """

    symbol: str
    style: str
    line_number: int
    comment_count: int

    @property
    def has_overlap(self) -> bool:
        """True if comment_count > 1."""
        return self.comment_count > 1

    @staticmethod
    def from_count(line_number: int, comment_count: int) -> "CommentMarker":
        """Create CommentMarker from line number and comment count.

        Args:
            line_number: Line number for this marker
            comment_count: Number of comments on this line

        Returns:
            CommentMarker with appropriate symbol and style
        """
        if comment_count == 1:
            return CommentMarker(
                symbol="*",
                style="yellow",
                line_number=line_number,
                comment_count=comment_count
            )
        else:  # comment_count > 1 (overlap)
            return CommentMarker(
                symbol="**",
                style="red",
                line_number=line_number,
                comment_count=comment_count
            )
