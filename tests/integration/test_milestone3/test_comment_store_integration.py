"""Integration tests for CommentStore service integration with RacGoatApp.

These tests validate that the CommentStore service is properly integrated
into the application and can be accessed by UI components.
"""

import pytest
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestCommentStoreIntegration:
    """Integration tests for CommentStore with RacGoatApp."""

    @pytest.mark.asyncio
    async def test_app_has_comment_store(self):
        """RacGoatApp should have a CommentStore instance available.

        The raccoon needs its treasure cache ready!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Verify comment store exists
            assert hasattr(app, 'comment_store')
            assert app.comment_store is not None
            assert app.comment_store.count() == 0

    @pytest.mark.asyncio
    async def test_comment_store_accepts_comments(self):
        """CommentStore in app should accept and store comments.

        The raccoon can stash treasures in its cache!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="treasure.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[
                    ('+', 'line1'),
                    ('+', 'line2'),
                    ('+', 'line3'),
                ])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a comment via the store
            target = CommentTarget(
                file_path="treasure.py",
                line_number=2,
                line_range=None
            )
            comment = Comment(
                text="Shiny treasure found here!",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # Verify comment is retrievable
            retrieved = app.comment_store.get("treasure.py", 2)
            assert len(retrieved) == 1
            assert retrieved[0].text == "Shiny treasure found here!"
            assert app.comment_store.count() == 1

    @pytest.mark.asyncio
    async def test_multiple_comments_in_app(self):
        """App's CommentStore should handle multiple comments across files.

        The raccoon's treasure cache can hold many shinies!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comments to different files
            for file_idx in [1, 2]:
                target = CommentTarget(
                    file_path=f"file{file_idx}.py",
                    line_number=1,
                    line_range=None
                )
                comment = Comment(
                    text=f"Comment on file {file_idx}",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

            # Verify both comments exist
            assert app.comment_store.count() == 2
            assert len(app.comment_store.get("file1.py", 1)) == 1
            assert len(app.comment_store.get("file2.py", 1)) == 1

    @pytest.mark.asyncio
    async def test_app_mode_transitions(self):
        """RacGoatApp should support mode transitions for SELECT mode.

        The raccoon can switch between normal and selective treasure-hunting!
        """
        from racgoat.ui.models import ApplicationMode

        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Verify initial mode is NORMAL
            assert app.mode == ApplicationMode.NORMAL

            # Simulate SELECT mode entry (via action)
            await pilot.press("s")
            await pilot.pause()

            # Mode should change to SELECT
            assert app.mode == ApplicationMode.SELECT

            # Simulate cancel (Esc)
            await pilot.press("escape")
            await pilot.pause()

            # Mode should return to NORMAL
            assert app.mode == ApplicationMode.NORMAL
