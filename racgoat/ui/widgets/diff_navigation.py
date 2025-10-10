"""Diff Navigation - Handles cursor movement and scrolling.

The goat's sure-footed traversal logic!
"""

from typing import TYPE_CHECKING

from textual.geometry import Region

from racgoat.parser.models import DiffFile
from racgoat.ui.models import ApplicationMode

if TYPE_CHECKING:
    from textual.widgets import VerticalScroll


class DiffNavigation:
    """Handles cursor movement and scrolling within diff content."""

    def __init__(self, scroll_widget: "VerticalScroll"):
        """Initialize the navigation handler.

        Args:
            scroll_widget: The VerticalScroll widget to control
        """
        self.scroll_widget = scroll_widget

    def get_first_valid_line(self, file: DiffFile) -> int | None:
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

    def get_valid_lines_list(self, file: DiffFile) -> list[int]:
        """Get ordered list of all valid line numbers in a file.

        Args:
            file: DiffFile to extract line numbers from

        Returns:
            List of line numbers (excludes removed lines), or empty list if no file
        """
        if not file or not file.hunks:
            return []

        valid_lines = []
        for hunk in file.hunks:
            current_line = hunk.new_start
            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    valid_lines.append(current_line)
                    current_line += 1

        return valid_lines

    def get_cursor_screen_row(self, file: DiffFile, line_number: int) -> int | None:
        """Calculate which screen row a line number appears on.

        Args:
            file: DiffFile to search in
            line_number: Line number to find

        Returns:
            0-based row index in rendered content, or None if not found
        """
        if not file or not file.hunks:
            return None

        row = 0

        # Header rows: file path + stats + blank line
        row += 3

        # Iterate through hunks to find target line
        for hunk_idx, hunk in enumerate(file.hunks):
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

    def scroll_to_cursor(self, file: DiffFile, line_number: int | None) -> None:
        """Scroll viewport to center the cursor line.

        The goat ensures you can always see where it stands!

        Args:
            file: Current DiffFile
            line_number: Line number to scroll to
        """
        if line_number is None:
            return

        cursor_row = self.get_cursor_screen_row(file, line_number)
        if cursor_row is None:
            return

        # Create region for cursor line (x, y, width, height)
        region = Region(0, cursor_row, self.scroll_widget.size.width, 1)

        # Scroll to center the cursor in viewport (no animation for responsiveness)
        self.scroll_widget.scroll_to_region(region, center=True, animate=False)

    def move_up(
        self,
        file: DiffFile,
        current_line: int,
        app_mode: ApplicationMode,
        select_end_line: int | None,
    ) -> tuple[int | None, int | None]:
        """Move cursor/selection up one line.

        Args:
            file: Current DiffFile
            current_line: Current cursor line number
            app_mode: Current application mode
            select_end_line: Current selection end line (SELECT mode only)

        Returns:
            Tuple of (new_current_line, new_select_end_line)
        """
        if app_mode == ApplicationMode.SELECT:
            # SELECT mode: expand selection upward
            if select_end_line is not None and file.hunks:
                # Get min line from first hunk
                first_hunk = file.hunks[0]
                min_line = first_hunk.new_start

                if select_end_line > min_line:
                    return current_line, select_end_line - 1

            return current_line, select_end_line

        # NORMAL mode: move cursor up
        # Find previous valid line
        prev_line = None
        for hunk in file.hunks:
            current_line_num = hunk.new_start

            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    if current_line_num == current_line and prev_line is not None:
                        # Found current line, move to previous
                        return prev_line, None
                    prev_line = current_line_num
                    current_line_num += 1

        return current_line, None

    def move_down(
        self,
        file: DiffFile,
        current_line: int,
        app_mode: ApplicationMode,
        select_end_line: int | None,
    ) -> tuple[int | None, int | None]:
        """Move cursor/selection down one line.

        Args:
            file: Current DiffFile
            current_line: Current cursor line number
            app_mode: Current application mode
            select_end_line: Current selection end line (SELECT mode only)

        Returns:
            Tuple of (new_current_line, new_select_end_line)
        """
        if app_mode == ApplicationMode.SELECT:
            # SELECT mode: expand selection downward
            if select_end_line is not None and file.hunks:
                # Get max line from last hunk
                last_hunk = file.hunks[-1]
                max_line = last_hunk.new_start + sum(1 for ct, _ in last_hunk.lines if ct != '-') - 1

                if select_end_line < max_line:
                    return current_line, select_end_line + 1

            return current_line, select_end_line

        # NORMAL mode: move cursor down
        # Find next valid line
        found_current = False
        for hunk in file.hunks:
            current_line_num = hunk.new_start

            for change_type, _ in hunk.lines:
                if change_type in ('+', ' '):
                    if found_current:
                        # This is the next line
                        return current_line_num, None
                    if current_line_num == current_line:
                        found_current = True
                    current_line_num += 1

        return current_line, None

    def page_up(
        self,
        file: DiffFile,
        current_line: int,
        viewport_height: int,
    ) -> int | None:
        """Move cursor up by approximately one page (viewport height).

        The goat leaps up the cliff in great bounds!

        Args:
            file: Current DiffFile
            current_line: Current cursor line number
            viewport_height: Height of the viewport in rows

        Returns:
            New cursor line number
        """
        # Get all valid lines
        valid_lines = self.get_valid_lines_list(file)
        if not valid_lines:
            return current_line

        # Find current cursor index
        try:
            current_idx = valid_lines.index(current_line)
        except ValueError:
            # Current line not in valid lines - shouldn't happen, but recover gracefully
            return valid_lines[0] if valid_lines else None

        # Calculate page size (approximate viewport height minus a few lines for context)
        page_size = max(1, viewport_height - 3)

        # Jump up by page_size lines
        new_idx = max(0, current_idx - page_size)
        return valid_lines[new_idx]

    def page_down(
        self,
        file: DiffFile,
        current_line: int,
        viewport_height: int,
    ) -> int | None:
        """Move cursor down by approximately one page (viewport height).

        The goat leaps down the cliff in great bounds!

        Args:
            file: Current DiffFile
            current_line: Current cursor line number
            viewport_height: Height of the viewport in rows

        Returns:
            New cursor line number
        """
        # Get all valid lines
        valid_lines = self.get_valid_lines_list(file)
        if not valid_lines:
            return current_line

        # Find current cursor index
        try:
            current_idx = valid_lines.index(current_line)
        except ValueError:
            # Current line not in valid lines - shouldn't happen, but recover gracefully
            return valid_lines[0] if valid_lines else None

        # Calculate page size (approximate viewport height minus a few lines for context)
        page_size = max(1, viewport_height - 3)

        # Jump down by page_size lines
        new_idx = min(len(valid_lines) - 1, current_idx + page_size)
        return valid_lines[new_idx]
