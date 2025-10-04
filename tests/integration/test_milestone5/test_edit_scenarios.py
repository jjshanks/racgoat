"""Integration tests for edit and delete comment functionality.

These tests validate that the raccoon can polish its treasure comments
after they've been cached!

Covers:
- AS-001: Edit line comment
- AS-002: Delete via empty edit
- AS-009: Edit range comment
- AS-010: Edit file comment
- Edge Case 5: Cancel edit preserves original
"""

import pytest
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestEditLineComment:
    """Tests for editing single-line comments - AS-001."""

    @pytest.mark.asyncio
    async def test_edit_line_comment_updates_text(self):
        """Editing a line comment should update its text in the comment store.

        When the raccoon polishes a treasure note, it shines brighter!

        User workflow:
        1. Navigate to line 42
        2. Press 'a' to add comment: "This needs refactoring"
        3. Press 'e' to edit comment
        4. Modify to: "This needs refactoring - extract to helper method"
        5. Press Enter to confirm

        Expected: Comment text updated in store, marker remains visible
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="refactor.py",
                added_lines=50,
                removed_lines=10,
                hunks=[DiffHunk(
                    old_start=40,
                    new_start=40,
                    lines=[
                        ('+', f'line{i}') for i in range(1, 51)
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add initial comment to line 42
            target = CommentTarget(
                file_path="refactor.py",
                line_number=42,
                line_range=None
            )
            comment = Comment(
                text="This needs refactoring",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # Verify initial comment exists
            comments = app.comment_store.get("refactor.py", 42)
            assert len(comments) == 1
            assert comments[0].text == "This needs refactoring"

            # TODO: Simulate pressing 'e' to edit comment
            # TODO: Simulate editing text to "This needs refactoring - extract to helper method"
            # TODO: Simulate pressing Enter to confirm

            # Expected outcome: Comment text should be updated
            # updated_comments = app.comment_store.get("refactor.py", 42)
            # assert len(updated_comments) == 1
            # assert updated_comments[0].text == "This needs refactoring - extract to helper method"
            # assert updated_comments[0].comment_type == CommentType.LINE

    @pytest.mark.asyncio
    async def test_edit_line_comment_preserves_metadata(self):
        """Editing a line comment should preserve its type and target.

        The raccoon polishes the note but keeps the treasure map location!

        Expected: Only text changes, comment type remains LINE
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="metadata.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment
            target = CommentTarget(
                file_path="metadata.py",
                line_number=5,
                line_range=None
            )
            original_timestamp = datetime.now()
            comment = Comment(
                text="Original comment",
                target=target,
                timestamp=original_timestamp,
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Edit comment to "Updated comment"

            # Expected: Type and target preserved
            # updated = app.comment_store.get("metadata.py", 5)[0]
            # assert updated.comment_type == CommentType.LINE
            # assert updated.target.line_number == 5
            # assert updated.target.line_range is None


class TestDeleteComment:
    """Tests for deleting comments by clearing text - AS-002."""

    @pytest.mark.asyncio
    async def test_delete_comment_by_clearing_text(self):
        """Clearing comment text during edit should delete the comment.

        When the raccoon removes a treasure marker, it vanishes completely!

        User workflow:
        1. Navigate to line 15 with existing comment
        2. Press 'e' to edit
        3. Clear all text (Ctrl+U or backspace)
        4. Press Enter to confirm

        Expected: Comment removed from store, no visual marker
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="delete_me.py",
                added_lines=20,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 21)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment to be deleted
            target = CommentTarget(
                file_path="delete_me.py",
                line_number=15,
                line_range=None
            )
            comment = Comment(
                text="This comment will be deleted",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # Verify comment exists
            assert app.comment_store.count() == 1
            assert len(app.comment_store.get("delete_me.py", 15)) == 1

            # TODO: Simulate pressing 'e' to edit
            # TODO: Simulate clearing all text
            # TODO: Simulate pressing Enter to confirm

            # Expected: Comment should be deleted
            # assert app.comment_store.count() == 0
            # assert len(app.comment_store.get("delete_me.py", 15)) == 0

    @pytest.mark.asyncio
    async def test_delete_preserves_other_comments(self):
        """Deleting one comment should not affect others on the same line.

        Removing one treasure doesn't disturb the raccoon's other shinies!

        Expected: Only the edited comment is deleted
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="overlap.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add line comment
            line_target = CommentTarget(
                file_path="overlap.py",
                line_number=5,
                line_range=None
            )
            line_comment = Comment(
                text="Line comment to delete",
                target=line_target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(line_comment)

            # Add range comment that includes line 5
            range_target = CommentTarget(
                file_path="overlap.py",
                line_number=None,
                line_range=(3, 7)
            )
            range_comment = Comment(
                text="Range comment to keep",
                target=range_target,
                timestamp=datetime.now(),
                comment_type=CommentType.RANGE
            )
            app.comment_store.add(range_comment)

            # Verify both comments exist
            assert app.comment_store.count() == 2
            assert len(app.comment_store.get("overlap.py", 5)) == 2

            # TODO: Edit line comment and clear text to delete it

            # Expected: Only line comment deleted, range comment remains
            # assert app.comment_store.count() == 1
            # remaining = app.comment_store.get("overlap.py", 5)
            # assert len(remaining) == 1
            # assert remaining[0].comment_type == CommentType.RANGE


class TestEditRangeComment:
    """Tests for editing range comments - AS-009."""

    @pytest.mark.asyncio
    async def test_edit_range_comment_preserves_type(self):
        """Editing a range comment should preserve its RANGE type.

        The raccoon polishes the range marker but keeps it spanning the territory!

        User workflow:
        1. Create range comment on lines 10-15
        2. Navigate to any line in range (e.g., line 12)
        3. Press 'e' to edit
        4. Modify text
        5. Press Enter

        Expected: Comment updated, type remains RANGE, range unchanged
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="range_edit.py",
                added_lines=20,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 21)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add range comment
            target = CommentTarget(
                file_path="range_edit.py",
                line_number=None,
                line_range=(10, 15)
            )
            comment = Comment(
                text="This block handles error cases",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.RANGE
            )
            app.comment_store.add(comment)

            # Verify comment exists on all lines in range
            for line in range(10, 16):
                comments = app.comment_store.get("range_edit.py", line)
                assert len(comments) == 1
                assert comments[0].text == "This block handles error cases"

            # TODO: Navigate to line 12 (middle of range)
            # TODO: Press 'e' to edit
            # TODO: Modify to "This block handles error cases - consider extracting"

            # Expected: Comment updated across entire range
            # for line in range(10, 16):
            #     updated = app.comment_store.get("range_edit.py", line)
            #     assert len(updated) == 1
            #     assert updated[0].text == "This block handles error cases - consider extracting"
            #     assert updated[0].comment_type == CommentType.RANGE
            #     assert updated[0].target.line_range == (10, 15)

    @pytest.mark.asyncio
    async def test_edit_range_from_any_line_in_range(self):
        """Pressing 'e' on any line in range should edit the same comment.

        The raccoon can polish the treasure from any spot in the marked zone!

        Expected: Editing from line 10, 12, or 15 all edit the same comment
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="any_line.py",
                added_lines=20,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 21)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add range comment on lines 10-15
            target = CommentTarget(
                file_path="any_line.py",
                line_number=None,
                line_range=(10, 15)
            )
            comment = Comment(
                text="Range comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.RANGE
            )
            app.comment_store.add(comment)

            # TODO: Test editing from line 10 (start of range)
            # TODO: Verify same comment is retrieved
            # TODO: Test editing from line 12 (middle of range)
            # TODO: Verify same comment is retrieved
            # TODO: Test editing from line 15 (end of range)
            # TODO: Verify same comment is retrieved

            # All should edit the same comment object


class TestEditFileComment:
    """Tests for editing file-level comments - AS-010."""

    @pytest.mark.asyncio
    async def test_edit_file_comment_preserves_type(self):
        """Editing a file comment should preserve its FILE type.

        The raccoon polishes the file-wide treasure marker!

        User workflow:
        1. Navigate to file in Files Pane
        2. Press 'c' to add file comment
        3. Press 'e' to edit file comment
        4. Modify text
        5. Press Enter

        Expected: Comment updated, type remains FILE
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="security.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add file-level comment
            target = CommentTarget(
                file_path="security.py",
                line_number=None,
                line_range=None
            )
            comment = Comment(
                text="Review security implications",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.FILE
            )
            app.comment_store.add(comment)

            # Verify file comment exists
            file_comments = app.comment_store.get_file_comments("security.py")
            assert len(file_comments) == 1
            assert file_comments[0].text == "Review security implications"

            # TODO: Press 'e' to edit file comment
            # TODO: Modify to "Review security implications - check auth flow"

            # Expected: File comment updated
            # updated = app.comment_store.get_file_comments("security.py")
            # assert len(updated) == 1
            # assert updated[0].text == "Review security implications - check auth flow"
            # assert updated[0].comment_type == CommentType.FILE


class TestCancelEdit:
    """Tests for canceling edit operation - Edge Case 5."""

    @pytest.mark.asyncio
    async def test_cancel_edit_preserves_original(self):
        """Pressing Esc during edit should preserve original comment.

        The raccoon decides not to polish this treasure after all!

        User workflow:
        1. Navigate to comment: "Original comment"
        2. Press 'e' to edit
        3. Change text to "Modified comment"
        4. Press Esc to cancel

        Expected: Original text preserved, no changes saved
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="cancel.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment
            target = CommentTarget(
                file_path="cancel.py",
                line_number=5,
                line_range=None
            )
            original_timestamp = datetime.now()
            comment = Comment(
                text="Original comment",
                target=target,
                timestamp=original_timestamp,
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Press 'e' to start editing
            # TODO: Modify text to "Modified comment"
            # TODO: Press Esc to cancel

            # Expected: Original comment unchanged
            # unchanged = app.comment_store.get("cancel.py", 5)
            # assert len(unchanged) == 1
            # assert unchanged[0].text == "Original comment"
            # assert unchanged[0].timestamp == original_timestamp

    @pytest.mark.asyncio
    async def test_cancel_edit_on_empty_input(self):
        """Pressing Esc after clearing text should preserve original.

        The raccoon changes its mind about removing the treasure!

        Expected: Comment not deleted if edit is canceled
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="cancel_delete.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 6)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment
            target = CommentTarget(
                file_path="cancel_delete.py",
                line_number=3,
                line_range=None
            )
            comment = Comment(
                text="Don't delete me!",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Press 'e' to edit
            # TODO: Clear all text
            # TODO: Press Esc to cancel (not Enter)

            # Expected: Comment still exists
            # preserved = app.comment_store.get("cancel_delete.py", 3)
            # assert len(preserved) == 1
            # assert preserved[0].text == "Don't delete me!"
