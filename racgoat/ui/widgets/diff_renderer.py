"""Diff Renderer - Handles diff content rendering and formatting.

The goat's artistic eye for painting diffs!
"""

from typing import TYPE_CHECKING

from rich.text import Text

from racgoat.parser.models import DiffFile, DiffHunk
from racgoat.ui.models import ApplicationMode, SearchState

if TYPE_CHECKING:
    from racgoat.services.comment_store import CommentStore
    from textual.app import App


class DiffRenderer:
    """Handles rendering of diff content with syntax highlighting and markers."""

    def __init__(
        self,
        *,
        comment_store: "CommentStore | None" = None,
        app: "App | None" = None,
    ):
        """Initialize the diff renderer.

        Args:
            comment_store: Reference to comment store for gutter markers
            app: Reference to app for easter egg mode detection
        """
        self.comment_store = comment_store
        self.app = app

    def render_file(
        self,
        file: DiffFile,
        current_line: int | None,
        app_mode: ApplicationMode,
        select_start_line: int | None,
        select_end_line: int | None,
        search_state: SearchState,
    ) -> Text:
        """Render diff content for a file.

        Args:
            file: DiffFile to render
            current_line: Current cursor line number
            app_mode: Current application mode
            select_start_line: Start of selection range (SELECT mode)
            select_end_line: End of selection range (SELECT mode)
            search_state: Current search state

        Returns:
            Rich Text object with formatted diff
        """
        # If no hunks, show message
        if not file.hunks:
            text = Text(
                f"📄 {file.file_path}\n\n"
                "File metadata only (no diff content available)",
                style="dim",
            )
            return text

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

            hunk_text = self.format_hunk(
                hunk=hunk,
                file=file,
                current_line=current_line,
                app_mode=app_mode,
                select_start_line=select_start_line,
                select_end_line=select_end_line,
                search_state=search_state,
            )
            text.append(hunk_text)

        return text

    def format_hunk(
        self,
        hunk: DiffHunk,
        file: DiffFile,
        current_line: int | None,
        app_mode: ApplicationMode,
        select_start_line: int | None,
        select_end_line: int | None,
        search_state: SearchState,
    ) -> Text:
        """Format a single hunk with ANSI colors, line numbers, and gutter markers.

        Args:
            hunk: Hunk to format
            file: Parent DiffFile (for gutter markers)
            current_line: Current cursor line number
            app_mode: Current application mode
            select_start_line: Start of selection range
            select_end_line: End of selection range
            search_state: Current search state

        Returns:
            Rich Text object with formatted hunk

        Format (with gutter):
            [gutter] [dim]  124[/]  context line
            *        [dim]  125[/] [green]+added line[/]  (has comment)
            [red]-removed line[/]  (no line number for removed)
            [dim]  126[/]  context line

        Malformed hunks:
            [⚠ UNPARSEABLE]
            raw hunk text preserved
        """
        text = Text()

        # Handle malformed hunks
        if hunk.is_malformed:
            text.append("[⚠ UNPARSEABLE]\n", style="dim red")
            if hunk.raw_text:
                text.append(hunk.raw_text, style="dim red")
                if not hunk.raw_text.endswith('\n'):
                    text.append('\n')
            return text

        # Track current line number (post-change)
        current_line_num = hunk.new_start

        # Determine selection range if in SELECT mode
        select_min = None
        select_max = None
        if select_start_line is not None and select_end_line is not None:
            select_min = min(select_start_line, select_end_line)
            select_max = max(select_start_line, select_end_line)

        for change_type, content in hunk.lines:
            # Determine gutter marker
            gutter = self._get_gutter_marker(
                file.file_path, current_line_num if change_type != "-" else None
            )

            # Check if line is in selection
            is_selected = (
                select_min is not None and
                select_max is not None and
                change_type != "-" and
                select_min <= current_line_num <= select_max
            )

            # Check if this is the current line (for cursor in NORMAL mode)
            is_current = (
                app_mode == ApplicationMode.NORMAL and
                change_type != "-" and
                current_line_num == current_line
            )

            if change_type == "+":
                # Added line: green, with line number
                if is_selected:
                    text.append(">", style="bold yellow")  # Selection marker
                elif is_current:
                    text.append(">", style="bold cyan")  # Cursor marker
                else:
                    text.append(gutter, style=self._get_gutter_style(file.file_path, current_line_num))
                text.append(f"  {current_line_num:4} ", style="dim")
                line_style = "bold green on #333333" if is_selected else "green"
                # Apply search highlighting if active
                self._append_with_search_highlights(
                    text, f"+{content}\n", current_line_num, line_style, search_state
                )
                current_line_num += 1
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
                    text.append(gutter, style=self._get_gutter_style(file.file_path, current_line_num))
                text.append(f"  {current_line_num:4} ", style="dim")
                line_style = "bold on #333333" if is_selected else "dim"
                # Apply search highlighting if active
                self._append_with_search_highlights(
                    text, f" {content}\n", current_line_num, line_style, search_state
                )
                current_line_num += 1

        return text

    def _get_gutter_marker(self, file_path: str, line_number: int | None) -> str:
        """Get gutter marker for a line.

        Args:
            file_path: Path of file containing line
            line_number: Line number (None for removed lines)

        Returns:
            Gutter marker string ("* " for comment, "**" for overlap, "  " for none)
            In raccoon mode, returns "🦝" instead of "*"
            In goat mode, returns "🐐" instead of "*"
        """
        if line_number is None or not self.comment_store:
            return "  "

        comments = self.comment_store.get(file_path, line_number)
        count = len(comments)

        # Check if easter egg modes are active
        raccoon_mode = getattr(self.app, 'raccoon_mode_active', False) if self.app else False
        goat_mode = getattr(self.app, 'goat_mode_active', False) if self.app else False

        if count == 0:
            return "  "
        elif count == 1:
            if goat_mode:
                return "🐐"
            elif raccoon_mode:
                return "🦝"
            else:
                return "* "
        else:  # count > 1 (overlap)
            if goat_mode:
                return "🐐🐐"
            elif raccoon_mode:
                return "🦝🦝"
            else:
                return "**"

    def _get_gutter_style(self, file_path: str, line_number: int | None) -> str:
        """Get style for gutter marker.

        Args:
            file_path: Path of file containing line
            line_number: Line number

        Returns:
            Style string for Rich Text
        """
        if line_number is None or not self.comment_store:
            return ""

        comments = self.comment_store.get(file_path, line_number)
        count = len(comments)

        if count == 0:
            return ""
        elif count == 1:
            return "yellow"
        else:  # count > 1 (overlap)
            return "red"

    def _append_with_search_highlights(
        self,
        text: Text,
        content: str,
        line_number: int,
        base_style: str,
        search_state: SearchState,
    ) -> None:
        """Append content to text with search match highlighting.

        The raccoon makes the shiny parts glow!

        Args:
            text: Rich Text object to append to
            content: Content to append (may include newline)
            line_number: Line number of this content
            base_style: Base style for non-highlighted parts
            search_state: Current search state
        """
        # If no search active, just append with base style
        if not search_state.query or not search_state.matches:
            text.append(content, style=base_style)
            return

        # Find matches for this line
        line_matches = [
            m for m in search_state.matches if m.line_number == line_number
        ]

        if not line_matches:
            # No matches on this line, append normally
            text.append(content, style=base_style)
            return

        # Apply highlighting for matches
        pattern = search_state.query.pattern
        current_match_line = None
        if search_state.current_index >= 0 and search_state.current_index < len(search_state.matches):
            current_match = search_state.matches[search_state.current_index]
            if current_match.line_number == line_number:
                current_match_line = current_match

        # Split content and apply highlights
        # Note: content includes the leading '+' or ' ' and trailing '\n'
        prefix = content[0]  # '+' or ' '
        line_content = content[1:-1] if content.endswith('\n') else content[1:]
        newline = '\n' if content.endswith('\n') else ''

        # Append prefix
        text.append(prefix, style=base_style)

        # Find all occurrences of pattern in line_content
        last_pos = 0
        for match in sorted(line_matches, key=lambda m: m.char_offset):
            # Append text before match
            if match.char_offset > last_pos:
                text.append(line_content[last_pos:match.char_offset], style=base_style)

            # Determine highlight style for this match
            is_current_match = (current_match_line and match.char_offset == current_match_line.char_offset)
            if is_current_match:
                # Current match: bold yellow on black (high contrast)
                highlight_style = "bold yellow on black"
            else:
                # Other matches: yellow on dark gray
                highlight_style = "yellow on #1a1a1a"

            # Append highlighted match
            match_end = match.char_offset + match.match_length
            text.append(line_content[match.char_offset:match_end], style=highlight_style)
            last_pos = match_end

        # Append remaining text after last match
        if last_pos < len(line_content):
            text.append(line_content[last_pos:], style=base_style)

        # Append newline
        if newline:
            text.append(newline)
