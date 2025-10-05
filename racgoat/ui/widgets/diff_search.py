"""Diff Search - Handles search functionality within diffs.

The raccoon's pattern-sniffing logic!
"""

from racgoat.parser.models import DiffFile
from racgoat.ui.models import SearchState, SearchQuery, SearchMatch


class DiffSearch:
    """Handles search functionality within diff content."""

    def __init__(self):
        """Initialize the search handler."""
        self.search_state: SearchState = SearchState()

    def execute_search(self, file: DiffFile, pattern: str) -> SearchState:
        """Execute search and populate matches list.

        The raccoon sniffs through the trash, finding all the shiny patterns!

        Args:
            file: DiffFile to search in
            pattern: Search pattern (case-sensitive literal string)

        Returns:
            Updated SearchState with matches
        """
        if not file or not pattern:
            self.search_state = SearchState()
            return self.search_state

        # Create search query
        self.search_state.query = SearchQuery(pattern=pattern, case_sensitive=True, is_regex=False)
        self.search_state.matches = []
        self.search_state.current_index = -1
        self.search_state.file_path = file.file_path

        # Scan all hunks for matches
        for hunk in file.hunks:
            current_line = hunk.new_start

            for change_type, content in hunk.lines:
                # Only search in lines with line numbers (not removed lines)
                if change_type in ('+', ' '):
                    # Find all occurrences of pattern in this line (case-sensitive)
                    char_offset = 0
                    while True:
                        pos = content.find(pattern, char_offset)
                        if pos == -1:
                            break

                        # Create match
                        match = SearchMatch(
                            line_number=current_line,
                            char_offset=pos,
                            matched_text=pattern,
                            match_length=len(pattern)
                        )
                        self.search_state.matches.append(match)
                        char_offset = pos + 1  # Continue searching for overlapping matches

                    current_line += 1

        # Set current index to first match if any matches found
        if self.search_state.matches:
            self.search_state.current_index = 0

        return self.search_state

    def scroll_to_next_match(self) -> int | None:
        """Navigate to next search match with wrap-around.

        The raccoon hops to the next shiny thing!

        Returns:
            Line number of next match, or None if no matches
        """
        if not self.search_state.matches:
            return None

        # Increment index with wrap-around
        self.search_state.current_index = (self.search_state.current_index + 1) % len(self.search_state.matches)

        # Return match line number
        match = self.search_state.matches[self.search_state.current_index]
        return match.line_number

    def scroll_to_previous_match(self) -> int | None:
        """Navigate to previous search match with wrap-around.

        The raccoon hops back to the previous shiny thing!

        Returns:
            Line number of previous match, or None if no matches
        """
        if not self.search_state.matches:
            return None

        # Decrement index with wrap-around
        self.search_state.current_index = (self.search_state.current_index - 1) % len(self.search_state.matches)

        # Return match line number
        match = self.search_state.matches[self.search_state.current_index]
        return match.line_number

    def clear_search(self) -> None:
        """Clear search state and remove all highlights.

        The raccoon forgets what it was looking for!
        """
        self.search_state = SearchState()
