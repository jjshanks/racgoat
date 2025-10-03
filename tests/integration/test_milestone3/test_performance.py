"""Integration tests for performance requirements.

These tests validate that the commenting system performs well with
the constitutional requirement of 100 comments and <50ms UI response.
"""

import pytest
import time
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestPerformance:
    """Integration tests for performance requirements."""

    @pytest.mark.asyncio
    async def test_100_comment_capacity(self):
        """App should support up to 100 comments without degradation.

        The raccoon's treasure cache can hold 100 shinies!
        """
        # Create a diff with many files and lines
        files = []
        for i in range(20):
            files.append(DiffFile(
                file_path=f"file_{i}.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{j}') for j in range(10)]
                )]
            ))

        diff_summary = DiffSummary(files=files)

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add 100 comments
            start_time = time.time()

            for i in range(100):
                file_idx = i % 20
                line_num = (i % 10) + 1
                target = CommentTarget(
                    file_path=f"file_{file_idx}.py",
                    line_number=line_num,
                    line_range=None
                )
                comment = Comment(
                    text=f"Comment {i}",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

            elapsed = time.time() - start_time

            # Verify all 100 comments added
            assert app.comment_store.count() == 100

            # Adding 100 comments should be fast (< 100ms total)
            assert elapsed < 0.1, f"Adding 100 comments took {elapsed*1000:.2f}ms, expected < 100ms"

    @pytest.mark.asyncio
    async def test_comment_retrieval_performance(self):
        """Comment retrieval should be fast (O(1) lookup).

        Finding cached treasure is quick!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="perf.py",
                added_lines=50,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(50)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comments to many lines
            for i in range(50):
                target = CommentTarget(
                    file_path="perf.py",
                    line_number=i + 1,
                    line_range=None
                )
                comment = Comment(
                    text=f"Comment on line {i+1}",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

            # Time retrieval operations
            start_time = time.time()

            for i in range(50):
                comments = app.comment_store.get("perf.py", i + 1)
                assert len(comments) == 1

            elapsed = time.time() - start_time

            # 50 lookups should be very fast (< 10ms total)
            assert elapsed < 0.01, f"50 lookups took {elapsed*1000:.2f}ms, expected < 10ms"

    @pytest.mark.asyncio
    async def test_capacity_limit_enforced(self):
        """CommentStore should enforce 100 comment limit.

        The raccoon's cache has limits - constitutional requirement!
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

            # Add 100 comments (at capacity)
            for i in range(100):
                target = CommentTarget(
                    file_path=f"file_{i}.py",
                    line_number=1,
                    line_range=None
                )
                comment = Comment(
                    text=f"Comment {i}",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

            assert app.comment_store.count() == 100

            # Attempting 101st comment should raise error
            target = CommentTarget(
                file_path="overflow.py",
                line_number=1,
                line_range=None
            )
            comment = Comment(
                text="One too many",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )

            with pytest.raises(ValueError, match="limit"):
                app.comment_store.add(comment)

    @pytest.mark.asyncio
    async def test_range_comment_performance(self):
        """Range comments should be performant even for large ranges.

        The raccoon can mark long stretches of treasure!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="large.py",
                added_lines=100,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(100)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a large range comment (50 lines)
            start_time = time.time()

            target = CommentTarget(
                file_path="large.py",
                line_number=None,
                line_range=(1, 50)
            )
            comment = Comment(
                text="Large range comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.RANGE
            )
            app.comment_store.add(comment)

            elapsed = time.time() - start_time

            # Adding 50-line range should be fast (< 50ms per constitutional requirement)
            assert elapsed < 0.05, f"Adding 50-line range took {elapsed*1000:.2f}ms, expected < 50ms"

            # Verify all 50 lines have the comment
            for line in range(1, 51):
                comments = app.comment_store.get("large.py", line)
                assert len(comments) == 1
                assert comments[0].text == "Large range comment"
