"""Comment Controller - Handles all comment-related actions.

The raccoon's treasure stashing logic lives here!
"""

from datetime import datetime
from typing import TYPE_CHECKING

from racgoat.models.comments import Comment, CommentTarget, CommentType
from racgoat.ui.models import ApplicationMode

if TYPE_CHECKING:
    from racgoat.main import RacGoatApp


class CommentController:
    """Controller for comment-related actions."""

    def __init__(self, app: "RacGoatApp"):
        """Initialize the comment controller.

        Args:
            app: Reference to the main RacGoatApp instance
        """
        self.app = app

    def _prompt_for_comment(
        self,
        target: CommentTarget,
        comment_type: CommentType,
        prompt_text: str,
        success_message_add: str,
        success_message_update: str,
        success_message_delete: str,
        diff_pane,
    ) -> None:
        """Unified comment prompting logic.

        Args:
            target: The comment target (file/line/range)
            comment_type: Type of comment (LINE/FILE/RANGE)
            prompt_text: Text to show in prompt dialog
            success_message_add: Notification message when adding
            success_message_update: Notification message when updating
            success_message_delete: Notification message when deleting
            diff_pane: Reference to diff pane for refresh
        """
        # Check if comment exists at target (for editing)
        existing_comments = self.app.comment_store.get(
            target.file_path, target.line_number
        )
        prefill = existing_comments[0].text if existing_comments else ""

        # Define callback to handle modal result
        def handle_comment_result(result: str | None) -> None:
            if result is None:
                # User cancelled (Esc) - do nothing
                return

            # Check for empty string when editing existing comment (deletion request)
            if result == "" and existing_comments:
                # Show confirmation dialog for deletion
                from racgoat.ui.widgets.dialogs import ConfirmDialog

                def handle_delete_confirmation(confirmed: bool) -> None:
                    if confirmed:
                        # Delete the comment
                        self.app.comment_store.delete(existing_comments[0].id)
                        self.app.notify(success_message_delete, severity="information")
                        # Refresh display to remove marker
                        if diff_pane and diff_pane.current_file:
                            diff_pane.display_file(diff_pane.current_file, refresh_only=True)

                self.app.push_screen(
                    ConfirmDialog(
                        "Delete this comment?\n\n"
                        "Press Enter to confirm or Escape to cancel."
                    ),
                    handle_delete_confirmation,
                )
                return

            if result:  # User provided text
                if existing_comments:
                    # Update existing comment
                    self.app.comment_store.update(target, result)
                    self.app.notify(success_message_update, severity="information")
                else:
                    # Create new comment
                    comment = Comment(
                        text=result,
                        target=target,
                        timestamp=datetime.now(),
                        comment_type=comment_type,
                    )
                    self.app.comment_store.add(comment)
                    self.app.notify(success_message_add, severity="information")

                # Refresh display to show marker
                if diff_pane and diff_pane.current_file:
                    diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        # Show input modal with callback
        from racgoat.ui.widgets.comment_input import CommentInput

        self.app.push_screen(
            CommentInput(prompt=prompt_text, prefill=prefill), handle_comment_result
        )

    def action_add_line_comment(self) -> None:
        """Add a comment to the current line (c key).

        The raccoon stashes a thought about this line!
        """
        # Only in NORMAL mode
        if self.app.mode != ApplicationMode.NORMAL:
            return

        # Get current file and line from DiffPane
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file or diff_pane.current_line is None:
            self.app.notify("No line selected for comment", severity="warning")
            return

        file_path = diff_pane.current_file.file_path
        line_number = diff_pane.current_line

        target = CommentTarget(
            file_path=file_path, line_number=line_number, line_range=None
        )

        self._prompt_for_comment(
            target=target,
            comment_type=CommentType.LINE,
            prompt_text=f"Comment on line {line_number}:",
            success_message_add=f"Comment added to line {line_number}",
            success_message_update=f"Comment updated on line {line_number}",
            success_message_delete=f"Comment deleted from line {line_number}",
            diff_pane=diff_pane,
        )

    def action_add_file_comment(self) -> None:
        """Add a comment to the current file (Shift+C key).

        The goat bleats wisdom about the entire file!
        """
        # Only in NORMAL mode
        if self.app.mode != ApplicationMode.NORMAL:
            return

        # Get current file
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file:
            self.app.notify("No file selected for comment", severity="warning")
            return

        file_path = diff_pane.current_file.file_path

        target = CommentTarget(file_path=file_path, line_number=None, line_range=None)

        self._prompt_for_comment(
            target=target,
            comment_type=CommentType.FILE,
            prompt_text=f"Comment on file {file_path}:",
            success_message_add=f"File comment added: {file_path}",
            success_message_update=f"File comment updated: {file_path}",
            success_message_delete=f"File comment deleted: {file_path}",
            diff_pane=diff_pane,
        )

    def action_enter_select_mode(self) -> None:
        """Enter SELECT mode for range comments (s key).

        The raccoon starts marking a range of treasures!
        """
        if self.app.mode != ApplicationMode.NORMAL:
            return

        # Get DiffPane
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file or diff_pane.current_line is None:
            self.app.notify("No line selected for range selection", severity="warning")
            return

        # Enter SELECT mode
        self.app.mode = ApplicationMode.SELECT
        diff_pane.select_start_line = diff_pane.current_line
        diff_pane.select_end_line = diff_pane.current_line

        # Refresh display to show selection highlighting
        diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        self.app.notify("SELECT mode: Use ↑/↓ to expand, Enter to confirm, Esc to cancel", severity="information")

    def action_cancel_select_mode(self) -> None:
        """Cancel SELECT mode (Esc key).

        The raccoon abandons the selection!
        """
        if self.app.mode == ApplicationMode.SELECT:
            self.app.mode = ApplicationMode.NORMAL

            # Clear selection in DiffPane
            from racgoat.ui.widgets import TwoPaneLayout

            two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            if diff_pane:
                diff_pane.select_start_line = None
                diff_pane.select_end_line = None
                # Refresh display to remove visual highlight
                if diff_pane.current_file:
                    diff_pane.display_file(diff_pane.current_file, refresh_only=True)

            self.app.notify("SELECT mode cancelled", severity="information")

    def action_confirm_select_mode(self) -> None:
        """Confirm SELECT mode and prompt for range comment (Enter key).

        The raccoon finalizes the selection and stashes wisdom!
        """
        if self.app.mode != ApplicationMode.SELECT:
            return

        # Get selection from DiffPane
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if not diff_pane or not diff_pane.current_file:
            self.app.notify("No file selected for range comment", severity="warning")
            return

        if diff_pane.select_start_line is None or diff_pane.select_end_line is None:
            self.app.notify("No range selected", severity="warning")
            return

        file_path = diff_pane.current_file.file_path
        start_line = min(diff_pane.select_start_line, diff_pane.select_end_line)
        end_line = max(diff_pane.select_start_line, diff_pane.select_end_line)

        # Exit SELECT mode first
        self.app.mode = ApplicationMode.NORMAL
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
                self.app.comment_store.add(comment)
                self.app.notify(f"Range comment added (lines {start_line}-{end_line})", severity="information")

                # Refresh display to show markers
                diff_pane.display_file(diff_pane.current_file, refresh_only=True)

        # Prompt for comment text
        prompt = f"Comment on lines {start_line}-{end_line}:"
        from racgoat.ui.widgets.comment_input import CommentInput
        self.app.push_screen(CommentInput(prompt=prompt, prefill=""), handle_comment_result)

    def action_edit_comment(self) -> None:
        """Edit or delete comment at cursor (e key).

        The goat polishes its treasured notes!
        """
        # Get DiffPane and delegate to its edit action
        from racgoat.ui.widgets import TwoPaneLayout

        two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
        diff_pane = two_pane._diff_pane

        if diff_pane:
            diff_pane.action_edit_comment()
