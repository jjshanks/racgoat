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
