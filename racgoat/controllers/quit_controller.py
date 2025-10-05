"""Quit Controller - Handles application exit and review saving.

The raccoon's final treasure stashing before departure!
"""

from pathlib import Path
from typing import TYPE_CHECKING

from racgoat.models.comments import (
    ReviewSession,
    FileReview,
    LineComment as SerLineComment,
    RangeComment as SerRangeComment,
    FileComment as SerFileComment,
)
from racgoat.ui.widgets.error_dialog import ErrorRecoveryScreen

if TYPE_CHECKING:
    from racgoat.main import RacGoatApp


class QuitController:
    """Controller for quit and save operations."""

    def __init__(self, app: "RacGoatApp"):
        """Initialize the quit controller.

        Args:
            app: Reference to the main RacGoatApp instance
        """
        self.app = app

    def action_quit(self) -> None:
        """Quit the application and save review if comments exist.

        The raccoon stashes its treasures before departing!
        """
        # Run the actual quit logic in a worker so we can use push_screen_wait
        self.app.run_worker(self._do_quit(), exclusive=True)

    async def _do_quit(self) -> None:
        """Worker method to handle quit logic with modal support."""
        # Check if we have any comments
        comment_count = self.app.comment_store.count()
        if comment_count == 0:
            # No comments, just exit
            self.app.notify("No comments to save", severity="information")
            self.app.exit()
            return

        # Diagnostic: Show comment count
        self.app.notify(f"Saving {comment_count} comment(s)...", severity="information")

        # Convert comment store to ReviewSession
        review_session = self._create_review_session()

        # Get git metadata (from service container)
        branch_name, commit_sha = self.app.services.get_git_metadata()
        review_session.branch_name = branch_name
        review_session.commit_sha = commit_sha

        # Serialize to Markdown (pass diff_summary for code context)
        content = self.app.services.serialize_review_session(review_session, diff_summary=self.app.diff_summary)

        # Try to write to output file
        output_path = Path(self.app.output_file)
        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                self.app.services.write_markdown_output(content, output_path)
                self.app.notify(f"Review saved to {output_path}", severity="information")
                self.app.exit()
                return

            except FileExistsError:
                # File already exists - show error recovery dialog
                error_msg = f"Output file already exists: {output_path}"
                last_error = error_msg
                result = await self.app.push_screen_wait(
                    ErrorRecoveryScreen(
                        error_message=error_msg,
                        show_tmp_fallback=True,
                        original_path=str(output_path)
                    )
                )

                if result is None:
                    # User cancelled - exit without saving
                    self.app.notify("Review not saved (cancelled by user)", severity="warning")
                    self.app.exit()
                    return
                else:
                    # User provided new path - retry with new path
                    output_path = Path(result)
                    retry_count += 1

            except OSError as e:
                # Write error (permissions, invalid path, etc.)
                error_msg = f"Cannot write to {output_path}: {e}"
                last_error = error_msg
                result = await self.app.push_screen_wait(
                    ErrorRecoveryScreen(
                        error_message=error_msg,
                        show_tmp_fallback=True,
                        original_path=str(output_path)
                    )
                )

                if result is None:
                    # User cancelled - exit without saving
                    self.app.notify("Review not saved (cancelled by user)", severity="warning")
                    self.app.exit()
                    return
                else:
                    # User provided new path - retry with new path
                    output_path = Path(result)
                    retry_count += 1

        # Max retries exceeded - provide helpful guidance
        error_details = f"Last error: {last_error}" if last_error else "Unknown error occurred"
        self.app.notify(
            f"Failed to save review after {max_retries} attempts.\n"
            f"{error_details}\n"
            f"Review data preserved in memory. Try:\n"
            f"  1. Check file permissions for {output_path}\n"
            f"  2. Choose a different output path\n"
            f"  3. Save to /tmp and move manually",
            severity="error"
        )
        self.app.exit()

    def _create_review_session(self) -> ReviewSession:
        """Convert comment store to ReviewSession for serialization.

        Returns:
            ReviewSession with all comments organized by file
        """
        # Get all unique comments from store using the unique tracker
        file_reviews = {}

        # Iterate through unique comments to avoid duplicates
        for comment_id, comment in self.app.comment_store._unique_comments.items():
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
