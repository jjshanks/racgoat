"""
RacGoat Main Application
A TUI that's part raccoon mischief, part goat stubbornness!
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Label, Input
from textual.binding import Binding

from racgoat.parser.diff_parser import parse_diff
from racgoat.parser.models import DiffSummary
from racgoat.ui.widgets import TwoPaneLayout
from racgoat.ui.models import ApplicationMode, PaneFocusState
from racgoat.services.comment_store import CommentStore
from racgoat.models.comments import Comment, CommentTarget, CommentType


class RacGoatApp(App):
    """
    The main RacGoat TUI application.

    Don't be a scapegoat - let's code!
    """

    # Reactive properties for Milestone 3
    mode = reactive(ApplicationMode.NORMAL)
    focus_state = reactive(PaneFocusState.DIFF)

    CSS = """
    Screen {
        layout: vertical;
    }

    #two-pane-layout {
        height: 1fr;
    }

    #empty-message {
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }

    #main-container {
        width: 80;
        height: 20;
        border: heavy $primary;
        padding: 2 4;
        align: center middle;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #message {
        width: 100%;
        content-align: center middle;
        margin-bottom: 2;
    }

    #easter-egg {
        width: 100%;
        content-align: center middle;
        color: $warning;
        margin-bottom: 1;
    }

    Button {
        width: 20;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("tab", "cycle_focus", "Switch", show=True),
        Binding("a", "add_line_comment", "Add Comment", show=False),  # Shown contextually
        Binding("c", "add_file_comment", "File Comment", show=False),
        Binding("s", "enter_select_mode", "Select Range", show=False),
        Binding("escape", "cancel_select_mode", "Cancel", show=False),
        Binding("enter", "confirm_select_mode", "Confirm", show=False),
        Binding("ctrl+t", "toggle_raccoon_mode", "🦝 Raccoon", show=True),
    ]

    # Hidden easter egg flag - shhh, it's a secret! 🦝
    raccoon_mode_active = False

    def __init__(
        self,
        diff_summary: DiffSummary | None = None,
        diff_file: str | None = None,
        output_file: str = "review.md",
    ):
        """Initialize the RacGoat app.

        Args:
            diff_summary: Parsed diff data (preferred for Milestone 2+)
            diff_file: Path to file containing git diff (legacy Milestone 1)
            output_file: Path for output review file (default: review.md)
        """
        super().__init__()
        self.diff_file = diff_file
        self.output_file = output_file
        self.diff_input = None

        # Milestone 3: Comment store
        self.comment_store = CommentStore()

        # Use provided diff_summary if available
        if diff_summary is not None:
            self.diff_summary = diff_summary
        elif diff_file:
            # Legacy: Load diff from file (Milestone 1 mode)
            try:
                with open(diff_file, "r") as f:
                    self.diff_input = f.read()
                # Parse the diff input
                self.diff_summary = parse_diff(
                    self.diff_input.splitlines(keepends=True)
                )
            except (OSError, IOError) as e:
                # File read error - will show error in UI
                self.diff_input = ""
                self.diff_summary = None
        else:
            # No diff provided - empty state
            self.diff_summary = None

    def compose(self) -> ComposeResult:
        """Compose the UI layout.

        For Milestone 3: Show TwoPaneLayout with StatusBar or empty message.
        """
        from racgoat.ui.widgets.status_bar import StatusBar

        yield Header()

        # Check if we have a valid diff
        if self.diff_summary and not self.diff_summary.is_empty:
            # Milestone 3: Show two-pane layout with comment store
            two_pane = TwoPaneLayout(
                self.diff_summary,
                comment_store=self.comment_store,
                id="two-pane-layout"
            )
            yield two_pane
            # Milestone 3: Add status bar
            yield StatusBar(id="status-bar")
        else:
            # Empty diff: Show friendly message
            yield Static(
                "No changes to review 🦝🐐\n\n"
                "The raccoon found no treasures today!\n"
                "The goat climbed an empty cliff!",
                id="empty-message",
            )

        yield Footer()

    def on_mount(self) -> None:
        """Set the app title when mounted."""
        self.title = "RacGoat - TUI Diff Viewer"
        if self.diff_summary and not self.diff_summary.is_empty:
            self.sub_title = (
                f"Viewing {len(self.diff_summary.files)} file(s) | "
                "Tab: Switch pane | q: Quit"
            )
        else:
            self.sub_title = "No changes to review | Press q to quit"

    def watch_mode(self, new_mode: ApplicationMode) -> None:
        """Propagate mode changes to child widgets."""
        if self.diff_summary and not self.diff_summary.is_empty:
            try:
                two_pane = self.query_one(TwoPaneLayout)
                if two_pane._diff_pane:
                    two_pane._diff_pane.app_mode = new_mode
                status_bar = self.query_one("#status-bar")
                if status_bar:
                    status_bar.app_mode = new_mode
            except:
                # Widgets not mounted yet
                pass

    def action_cycle_focus(self) -> None:
        """Cycle focus between panes (Tab key)."""
        # This is handled by TwoPaneLayout in Milestone 2
        pass

    def action_quit(self) -> None:
        """Quit the application and save review if comments exist.

        The raccoon stashes its treasures before departing!
        """
        # Run the actual quit logic in a worker so we can use push_screen_wait
        self.run_worker(self._do_quit(), exclusive=True)

    async def _do_quit(self) -> None:
        """Worker method to handle quit logic with modal support."""
        from pathlib import Path
        from racgoat.services.git_metadata import get_git_metadata
        from racgoat.services.markdown_writer import serialize_review_session, write_markdown_output
        from racgoat.models.comments import (
            ReviewSession,
            FileReview,
            LineComment as SerLineComment,
            RangeComment as SerRangeComment,
            FileComment as SerFileComment,
        )
        from racgoat.ui.widgets.error_dialog import ErrorRecoveryScreen

        # Check if we have any comments
        comment_count = self.comment_store.count()
        if comment_count == 0:
            # No comments, just exit
            self.notify("No comments to save", severity="information")
            self.exit()
            return

        # Diagnostic: Show comment count
        self.notify(f"Saving {comment_count} comment(s)...", severity="information")

        # Convert comment store to ReviewSession
        review_session = self._create_review_session()

        # Get git metadata
        branch_name, commit_sha = get_git_metadata()
        review_session.branch_name = branch_name
        review_session.commit_sha = commit_sha

        # Serialize to Markdown
        content = serialize_review_session(review_session)

        # Try to write to output file
        output_path = Path(self.output_file)
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                write_markdown_output(content, output_path)
                self.notify(f"Review saved to {output_path}", severity="information")
                self.exit()
                return

            except FileExistsError:
                # File already exists - show error recovery dialog
                error_msg = f"Output file already exists: {output_path}"
                result = await self.push_screen_wait(
                    ErrorRecoveryScreen(
                        error_message=error_msg,
                        show_tmp_fallback=True,
                        original_path=str(output_path)
                    )
                )

                if result is None:
                    # User cancelled - exit without saving
                    self.notify("Review not saved (cancelled by user)", severity="warning")
                    self.exit()
                    return
                else:
                    # User provided new path - retry with new path
                    output_path = Path(result)
                    retry_count += 1

            except OSError as e:
                # Write error (permissions, invalid path, etc.)
                error_msg = f"Cannot write to {output_path}: {e}"
                result = await self.push_screen_wait(
                    ErrorRecoveryScreen(
                        error_message=error_msg,
                        show_tmp_fallback=True,
                        original_path=str(output_path)
                    )
                )

                if result is None:
                    # User cancelled - exit without saving
                    self.notify("Review not saved (cancelled by user)", severity="warning")
                    self.exit()
                    return
                else:
                    # User provided new path - retry with new path
                    output_path = Path(result)
                    retry_count += 1

        # Max retries exceeded
        self.notify("Failed to save review after multiple attempts", severity="error")
        self.exit()

    def _create_review_session(self) -> "ReviewSession":
        """Convert comment store to ReviewSession for serialization.

        Returns:
            ReviewSession with all comments organized by file
        """
        from racgoat.models.comments import (
            ReviewSession,
            FileReview,
            LineComment as SerLineComment,
            RangeComment as SerRangeComment,
            FileComment as SerFileComment,
        )

        # Get all unique comments from store using the unique tracker
        file_reviews = {}

        # Iterate through unique comments to avoid duplicates
        for comment_id, comment in self.comment_store._unique_comments.items():
            file_path = comment.target.file_path

            # Create FileReview if not exists
            if file_path not in file_reviews:
                file_reviews[file_path] = FileReview(
                    file_path=file_path,
                    comments=[]
                )

            # Convert to serializable comment based on type
            if comment.target.is_line_comment:
                ser_comment = SerLineComment(
                    text=comment.text,
                    line_number=comment.target.line_number
                )
            elif comment.target.is_range_comment:
                start, end = comment.target.line_range
                ser_comment = SerRangeComment(
                    text=comment.text,
                    start_line=start,
                    end_line=end
                )
            elif comment.target.is_file_comment:
                ser_comment = SerFileComment(text=comment.text)
            else:
                continue  # Skip unknown types

            file_reviews[file_path].comments.append(ser_comment)

        return ReviewSession(
            file_reviews=file_reviews,
            branch_name="Unknown Branch",
            commit_sha="Unknown SHA"
        )

    def action_add_line_comment(self) -> None:
        """Add a comment to the current line (a key).

        The raccoon stashes a thought about this line!
        """
        # Only in NORMAL mode
        if self.mode != ApplicationMode.NORMAL:
            return

        # Get current file and line from DiffPane
        two_pane = self.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file or diff_pane.current_line is None:
            self.notify("No line selected for comment", severity="warning")
            return

        file_path = diff_pane.current_file.file_path
        line_number = diff_pane.current_line

        # Check if comment exists (for editing)
        existing_comments = self.comment_store.get(file_path, line_number)
        prefill = existing_comments[0].text if existing_comments else ""

        prompt = f"Comment on line {line_number}:"

        # Define callback to handle modal result
        def handle_comment_result(result: str | None) -> None:
            if result:  # User provided text
                target = CommentTarget(
                    file_path=file_path,
                    line_number=line_number,
                    line_range=None
                )

                if existing_comments:
                    # Update existing comment
                    self.comment_store.update(target, result)
                    self.notify(f"Comment updated on line {line_number}", severity="information")
                else:
                    # Create new comment
                    comment = Comment(
                        text=result,
                        target=target,
                        timestamp=datetime.now(),
                        comment_type=CommentType.LINE
                    )
                    self.comment_store.add(comment)
                    self.notify(f"Comment added to line {line_number}", severity="information")

                # Refresh display to show marker
                diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        # Show input modal with callback
        from racgoat.ui.widgets.comment_input import CommentInput
        self.push_screen(CommentInput(prompt=prompt, prefill=prefill), handle_comment_result)

    def action_add_file_comment(self) -> None:
        """Add a comment to the current file (c key).

        The goat bleats wisdom about the entire file!
        """
        # Only in NORMAL mode
        if self.mode != ApplicationMode.NORMAL:
            return

        # Get current file
        two_pane = self.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file:
            self.notify("No file selected for comment", severity="warning")
            return

        file_path = diff_pane.current_file.file_path

        # Check if file-level comment exists
        existing_comments = self.comment_store.get(file_path, None)
        prefill = existing_comments[0].text if existing_comments else ""

        prompt = f"Comment on file {file_path}:"

        # Define callback to handle modal result
        def handle_comment_result(result: str | None) -> None:
            if result:  # User provided text
                target = CommentTarget(
                    file_path=file_path,
                    line_number=None,
                    line_range=None
                )

                if existing_comments:
                    # Update existing comment
                    self.comment_store.update(target, result)
                    self.notify(f"File comment updated: {file_path}", severity="information")
                else:
                    # Create new comment
                    comment = Comment(
                        text=result,
                        target=target,
                        timestamp=datetime.now(),
                        comment_type=CommentType.FILE
                    )
                    self.comment_store.add(comment)
                    self.notify(f"File comment added: {file_path}", severity="information")

        # Show input modal with callback
        from racgoat.ui.widgets.comment_input import CommentInput
        self.push_screen(CommentInput(prompt=prompt, prefill=prefill), handle_comment_result)

    def action_enter_select_mode(self) -> None:
        """Enter SELECT mode for range comments (s key).

        The raccoon starts marking a range of treasures!
        """
        if self.mode != ApplicationMode.NORMAL:
            return

        # Get DiffPane
        two_pane = self.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file or diff_pane.current_line is None:
            self.notify("No line selected for range selection", severity="warning")
            return

        # Enter SELECT mode
        self.mode = ApplicationMode.SELECT
        diff_pane.select_start_line = diff_pane.current_line
        diff_pane.select_end_line = diff_pane.current_line

        # Refresh display to show selection highlighting
        diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        self.notify("SELECT mode: Use ↑/↓ to expand, Enter to confirm, Esc to cancel", severity="information")

    def action_cancel_select_mode(self) -> None:
        """Cancel SELECT mode (Esc key).

        The raccoon abandons the selection!
        """
        if self.mode == ApplicationMode.SELECT:
            self.mode = ApplicationMode.NORMAL

            # Clear selection in DiffPane
            two_pane = self.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            if diff_pane:
                diff_pane.select_start_line = None
                diff_pane.select_end_line = None
                # Refresh display to remove visual highlight
                if diff_pane.current_file:
                    diff_pane.display_file(diff_pane.current_file, refresh_only=True)

            self.notify("SELECT mode cancelled", severity="information")

    def action_confirm_select_mode(self) -> None:
        """Confirm SELECT mode and prompt for range comment (Enter key).

        The raccoon finalizes the selection and stashes wisdom!
        """
        if self.mode != ApplicationMode.SELECT:
            return

        # Get selection from DiffPane
        two_pane = self.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file:
            self.notify("No file selected for range comment", severity="warning")
            return

        if diff_pane.select_start_line is None or diff_pane.select_end_line is None:
            self.notify("No range selected", severity="warning")
            return

        file_path = diff_pane.current_file.file_path
        start_line = min(diff_pane.select_start_line, diff_pane.select_end_line)
        end_line = max(diff_pane.select_start_line, diff_pane.select_end_line)

        # Exit SELECT mode first
        self.mode = ApplicationMode.NORMAL
        diff_pane.select_start_line = None
        diff_pane.select_end_line = None

        # Define callback to handle modal result
        def handle_comment_result(result: str | None) -> None:
            if result:  # User provided text
                target = CommentTarget(
                    file_path=file_path,
                    line_number=None,
                    line_range=(start_line, end_line)
                )

                # Create range comment
                comment = Comment(
                    text=result,
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.RANGE
                )
                self.comment_store.add(comment)
                self.notify(f"Range comment added (lines {start_line}-{end_line})", severity="information")

                # Refresh display to show markers
                diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        # Prompt for comment text
        prompt = f"Comment on lines {start_line}-{end_line}:"
        from racgoat.ui.widgets.comment_input import CommentInput
        self.push_screen(CommentInput(prompt=prompt, prefill=""), handle_comment_result)

    def action_toggle_raccoon_mode(self) -> None:
        """
        Toggle raccoon mode! 🦝

        Because every good app needs a trash panda easter egg!
        Triggered by Ctrl+T.
        """
        if not self.raccoon_mode_active:
            self.raccoon_mode_active = True
            # Flash the background - raccoons love shiny things!
            self.notify("Raccoon mode activated! Time to raid the code bins! 🦝",
                       severity="information", timeout=5)


def run_tui(diff_summary: DiffSummary, output_file: str = "review.md") -> None:
    """Launch TUI with diff data (Milestone 2+).

    Args:
        diff_summary: Parsed diff to display
        output_file: Path for output review file (default: review.md)
    """
    app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
    app.run(mouse=False)


def main(diff_file: str | None = None, output_file: str = "review.md"):
    """
    Entry point for the RacGoat application (legacy Milestone 1).

    Args:
        diff_file: Optional path to file containing git diff
        output_file: Path for output review file

    Let's get this goat on the road! 🐐
    """
    app = RacGoatApp(diff_file=diff_file, output_file=output_file)
    app.run(mouse=False)


if __name__ == "__main__":
    import sys
    from racgoat.cli.args import parse_arguments

    # Parse CLI arguments
    args = parse_arguments()

    # Determine diff source
    diff_path = getattr(args, 'diff_file', None)

    main(diff_file=diff_path, output_file=args.output)
