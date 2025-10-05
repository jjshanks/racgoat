"""Search Controller - Handles search and navigation actions.

The raccoon's sniffing logic lives here!
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from racgoat.main import RacGoatApp


class SearchController:
    """Controller for search and navigation actions."""

    def __init__(self, app: "RacGoatApp"):
        """Initialize the search controller.

        Args:
            app: Reference to the main RacGoatApp instance
        """
        self.app = app

    def action_initiate_search(self) -> None:
        """Initiate search mode (/ key).

        The raccoon starts sniffing for patterns!
        """
        # Get DiffPane
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file:
            self.app.notify("No file to search", severity="warning")
            return

        # Show input for search pattern
        from racgoat.ui.widgets.comment_input import CommentInput

        def handle_search_input(result: str | None) -> None:
            if result:  # User provided search pattern
                diff_pane.execute_search(result)
                match_count = len(diff_pane.search_state.matches)
                if match_count > 0:
                    self.app.notify(f"Found {match_count} match(es)", severity="information")
                else:
                    self.app.notify("No matches found", severity="information")

        self.app.push_screen(CommentInput(prompt="Search:", prefill=""), handle_search_input)

    def _is_search_active(self) -> bool:
        """Check if search mode is active with matches.

        Returns:
            True if DiffPane has active search with matches
        """
        try:
            from racgoat.ui.widgets import TwoPaneLayout

            two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            return diff_pane and bool(diff_pane.search_state.matches)
        except:
            return False

    def action_cancel_search(self) -> None:
        """Clear search state (Esc key).

        The raccoon forgets what it was looking for!
        """
        # Clear search state
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane
        if diff_pane:
            diff_pane.clear_search()
        self.app.notify("Search cleared", severity="information")

    def action_next_item(self) -> None:
        """Navigate to next item (search match or file) (n key).

        Context-sensitive: If search is active, go to next match.
        Otherwise, go to next file.
        """
        if self._is_search_active():
            # Search mode: navigate to next match
            from racgoat.ui.widgets import TwoPaneLayout

            two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            diff_pane.scroll_to_next_match()
        else:
            # Normal mode: navigate to next file
            try:
                from racgoat.ui.widgets import TwoPaneLayout

                two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
                files_pane = two_pane._files_pane
                if files_pane:
                    files_pane.next_file()
            except:
                pass

    def action_previous_item(self) -> None:
        """Navigate to previous item (search match or file) (p key).

        Context-sensitive: If search is active, go to previous match.
        Otherwise, go to previous file.
        """
        if self._is_search_active():
            # Search mode: navigate to previous match
            from racgoat.ui.widgets import TwoPaneLayout

            two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            diff_pane.scroll_to_previous_match()
        else:
            # Normal mode: navigate to previous file
            try:
                from racgoat.ui.widgets import TwoPaneLayout

                two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
                files_pane = two_pane._files_pane
                if files_pane:
                    files_pane.previous_file()
            except:
                pass

    def action_show_help(self) -> None:
        """Show help overlay with all keybindings (? key).

        The raccoon's complete treasure map!
        """
        from racgoat.ui.widgets.help_screen import HelpScreen
        self.app.push_screen(HelpScreen())
