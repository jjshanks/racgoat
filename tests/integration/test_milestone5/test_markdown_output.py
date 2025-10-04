"""Integration tests for Milestone 5 markdown output validation.

These tests validate that edited and deleted comments appear correctly
in the treasure scroll (review.md)!

Covers:
- Markdown Validation 1: Edited comments in output
- Markdown Validation 2: Deleted comments not in output
"""

import pytest
import tempfile
import os
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestEditedCommentsOutput:
    """Tests for edited comments in markdown output - Validation 1."""

    @pytest.mark.asyncio
    async def test_edited_comments_appear_in_output(self):
        """Edited comment text should appear in review.md, not original.

        The treasure scroll shows the polished notes!

        User workflow:
        1. Create line comment: "Original text"
        2. Edit to: "Updated text"
        3. Quit with 'q'

        Expected:
        - review.md contains "Updated text"
        - "Original text" not present
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="edited.py",
                    added_lines=10,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', f'line{i}') for i in range(1, 11)]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add original comment
                target = CommentTarget(
                    file_path="edited.py",
                    line_number=5,
                    line_range=None
                )
                comment = Comment(
                    text="Original text",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

                # TODO: Edit comment to "Updated text"
                # (Simulate edit operation)

                # For now, manually update to simulate edit
                # In real test, would use UI actions
                comments = app.comment_store.get("edited.py", 5)
                if comments:
                    comments[0].text = "Updated text"

                # TODO: Press 'q' to quit and trigger markdown write

            # Verify output file contains updated text
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Updated text" in content
            #     assert "Original text" not in content

    @pytest.mark.asyncio
    async def test_edited_range_comment_in_output(self):
        """Edited range comment should show updated text in output.

        The polished range marker appears on the treasure scroll!

        Expected: Range section shows edited text
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

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

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add range comment
                target = CommentTarget(
                    file_path="range_edit.py",
                    line_number=None,
                    line_range=(10, 15)
                )
                comment = Comment(
                    text="Original range comment",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.RANGE
                )
                app.comment_store.add(comment)

                # TODO: Edit to "Updated range comment"
                # Simulate edit
                comment.text = "Updated range comment"

                # TODO: Quit

            # Expected: Output shows updated range comment
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Updated range comment" in content
            #     assert "Original range comment" not in content
            #     assert "Lines 10-15" in content or "10-15" in content

    @pytest.mark.asyncio
    async def test_edited_file_comment_in_output(self):
        """Edited file-level comment should show updated text.

        The polished file marker shines on the scroll!

        Expected: File-level section shows edited text
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="file_edit.py",
                    added_lines=10,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', f'line{i}') for i in range(1, 11)]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add file comment
                target = CommentTarget(
                    file_path="file_edit.py",
                    line_number=None,
                    line_range=None
                )
                comment = Comment(
                    text="Original file comment",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.FILE
                )
                app.comment_store.add(comment)

                # TODO: Edit to "Updated file comment"
                comment.text = "Updated file comment"

                # TODO: Quit

            # Expected: Output shows updated file comment
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Updated file comment" in content
            #     assert "Original file comment" not in content

    @pytest.mark.asyncio
    async def test_multiple_edits_show_final_version(self):
        """Multiple edits to same comment should show only final version.

        The treasure scroll shows the final polished note!

        Expected: Only the last edited version appears
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="multi_edit.py",
                    added_lines=5,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', 'test')]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comment
                target = CommentTarget(
                    file_path="multi_edit.py",
                    line_number=1,
                    line_range=None
                )
                comment = Comment(
                    text="Version 1",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

                # Simulate multiple edits
                # TODO: Edit to "Version 2"
                comment.text = "Version 2"
                # TODO: Edit to "Version 3"
                comment.text = "Version 3"
                # TODO: Edit to "Final version"
                comment.text = "Final version"

                # TODO: Quit

            # Expected: Only final version in output
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Final version" in content
            #     assert "Version 1" not in content
            #     assert "Version 2" not in content
            #     assert "Version 3" not in content


class TestDeletedCommentsOutput:
    """Tests for deleted comments in markdown output - Validation 2."""

    @pytest.mark.asyncio
    async def test_deleted_comments_not_in_output(self):
        """Deleted comments should not appear in review.md.

        Removed treasures don't appear on the scroll!

        User workflow:
        1. Create comment: "To be deleted"
        2. Edit and clear text to delete
        3. Quit with 'q'

        Expected:
        - review.md does not contain "To be deleted"
        - Line number not referenced
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="deleted.py",
                    added_lines=10,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', f'line{i}') for i in range(1, 11)]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comment
                target = CommentTarget(
                    file_path="deleted.py",
                    line_number=5,
                    line_range=None
                )
                comment = Comment(
                    text="To be deleted",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

                # TODO: Delete comment (edit with empty text)
                delete_target = CommentTarget(
                    file_path="deleted.py",
                    line_number=5,
                    line_range=None
                )
                app.comment_store.delete(delete_target)

                # TODO: Quit

            # Expected: Deleted comment not in output
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "To be deleted" not in content
            #     # Line 5 should not be referenced for this file
            #     # (unless other comments exist on that line)

    @pytest.mark.asyncio
    async def test_partial_deletion_preserves_remaining(self):
        """Deleting one comment on a line should keep others.

        Removing one treasure keeps the other shinies on the scroll!

        Expected: Remaining comments still appear in output
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="partial.py",
                    added_lines=10,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', f'line{i}') for i in range(1, 11)]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add line comment
                line_target = CommentTarget(
                    file_path="partial.py",
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
                    file_path="partial.py",
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

                # TODO: Delete line comment
                # (In real implementation, would use UI to delete specific comment)
                # For now, delete using the store method with comment_id
                # (required because there are multiple comments on line 5)
                app.comment_store.delete(line_target, comment_id=line_comment.id)

                # TODO: Quit

            # Expected: Range comment present, line comment absent
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Range comment to keep" in content
            #     assert "Line comment to delete" not in content

    @pytest.mark.asyncio
    async def test_delete_all_comments_no_output(self):
        """Deleting all comments should result in no output file.

        No treasures means no scroll is written!

        Expected: No review.md created (or empty/skipped per M4 spec)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="all_deleted.py",
                    added_lines=5,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', 'test')]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comment then delete it
                target = CommentTarget(
                    file_path="all_deleted.py",
                    line_number=1,
                    line_range=None
                )
                comment = Comment(
                    text="Temporary",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

                # Delete it
                delete_target = CommentTarget(
                    file_path="all_deleted.py",
                    line_number=1,
                    line_range=None
                )
                app.comment_store.delete(delete_target)

                # TODO: Quit

            # Expected: No output file created (M4 spec: skip if no comments)
            # assert not os.path.exists(output_file) or os.path.getsize(output_file) == 0

    @pytest.mark.asyncio
    async def test_mix_edited_and_deleted_comments(self):
        """Output should show edited comments and omit deleted ones.

        The treasure scroll shows polished notes, hides removed ones!

        Expected: Edited present, deleted absent
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "review.md")

            diff_summary = DiffSummary(files=[
                DiffFile(
                    file_path="mixed.py",
                    added_lines=20,
                    removed_lines=0,
                    hunks=[DiffHunk(
                        old_start=1,
                        new_start=1,
                        lines=[('+', f'line{i}') for i in range(1, 21)]
                    )]
                ),
            ])

            app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Add comment to keep and edit
                keep_target = CommentTarget(
                    file_path="mixed.py",
                    line_number=5,
                    line_range=None
                )
                keep_comment = Comment(
                    text="Keep original",
                    target=keep_target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(keep_comment)

                # Add comment to edit
                edit_target = CommentTarget(
                    file_path="mixed.py",
                    line_number=10,
                    line_range=None
                )
                edit_comment = Comment(
                    text="Edit this",
                    target=edit_target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(edit_comment)

                # Add comment to delete
                delete_target = CommentTarget(
                    file_path="mixed.py",
                    line_number=15,
                    line_range=None
                )
                delete_comment = Comment(
                    text="Delete me",
                    target=delete_target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(delete_comment)

                # Perform operations
                # Edit line 10 comment
                edit_comment.text = "Edited version"

                # Delete line 15 comment
                delete_target = CommentTarget(
                    file_path="mixed.py",
                    line_number=15,
                    line_range=None
                )
                app.comment_store.delete(delete_target)

                # TODO: Quit

            # Expected output:
            # - "Keep original" present
            # - "Edited version" present
            # - "Edit this" absent
            # - "Delete me" absent
            # with open(output_file, 'r') as f:
            #     content = f.read()
            #     assert "Keep original" in content
            #     assert "Edited version" in content
            #     assert "Edit this" not in content
            #     assert "Delete me" not in content
