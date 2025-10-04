"""Integration tests for Milestone 5 performance requirements.

These tests validate that the raccoon's treasure polishing and sniffing
remain speedy even with many shinies!

Covers:
- Performance Test 1: Search in large diff (<200ms)
- Performance Test 2: Edit with large comment store (<100ms)
"""

import pytest
import time
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestSearchPerformance:
    """Performance tests for search functionality - Performance Test 1."""

    @pytest.mark.asyncio
    async def test_search_large_file_performance(self):
        """Search should complete in <200ms for files up to 2000 lines.

        The raccoon's nose is quick even in vast treasure fields!

        Test setup:
        - Create file with 2000 lines
        - Insert common pattern ("def") throughout
        - Measure search execution time

        Expected: Search completes in <200ms
        """
        # Generate 2000 lines with "def" pattern scattered
        lines = []
        for i in range(1, 2001):
            if i % 20 == 0:
                lines.append(('+', f'def function_{i}():'))
            else:
                lines.append(('+', f'    line {i}'))

        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="large_search.py",
                added_lines=2000,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=lines
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Measure time for search operation
            # start_time = time.perf_counter()

            # TODO: Press '/' to initiate search
            # TODO: Type "def"
            # TODO: Press Enter to execute

            # end_time = time.perf_counter()
            # search_duration = (end_time - start_time) * 1000  # Convert to ms

            # Expected: <200ms
            # assert search_duration < 200, f"Search took {search_duration}ms, expected <200ms"

            # Verify search worked (should find 100 matches: 2000/20)
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 100

    @pytest.mark.asyncio
    async def test_search_highlight_rendering_performance(self):
        """Highlighting many matches should not cause lag.

        The raccoon marks all treasures swiftly!

        Test: Search pattern appearing 100+ times
        Expected: UI remains responsive, no freezing
        """
        # Create file where "x" appears 150 times
        lines = [('+', f'x = {i}, x += 1, x -= 2') for i in range(50)]

        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="many_matches.py",
                added_lines=50,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=lines
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "x" (150+ matches)
            # start_time = time.perf_counter()

            # TODO: Execute search

            # end_time = time.perf_counter()
            # highlight_duration = (end_time - start_time) * 1000

            # Expected: <200ms for highlighting
            # assert highlight_duration < 200

    @pytest.mark.asyncio
    async def test_search_navigation_performance(self):
        """Navigating between matches should be instant.

        The raccoon jumps between treasures without delay!

        Expected: Each 'n' or 'N' press completes in <50ms
        """
        lines = [('+', f'FIND on line {i}') for i in range(100)]

        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="nav_perf.py",
                added_lines=100,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=lines
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Execute search for "FIND" (100 matches)

            # Measure navigation time
            # start_time = time.perf_counter()

            # TODO: Press 'n' 10 times
            # for _ in range(10):
            #     # press 'n'
            #     pass

            # end_time = time.perf_counter()
            # avg_nav_time = ((end_time - start_time) * 1000) / 10

            # Expected: <50ms average per navigation
            # assert avg_nav_time < 50


class TestEditPerformance:
    """Performance tests for edit functionality - Performance Test 2."""

    @pytest.mark.asyncio
    async def test_edit_comment_performance_with_large_store(self):
        """Edit operation should complete in <100ms with 100 comments.

        The raccoon polishes one treasure quickly even with many cached!

        Test setup:
        - Create 100 comments across multiple files (max capacity)
        - Measure time to edit one comment

        Expected: Edit dialog appears and saves in <100ms
        """
        # Create 5 files with 20 comments each (100 total, max capacity)
        files = []
        for file_idx in range(5):
            lines = [('+', f'line {i}') for i in range(1, 51)]
            files.append(DiffFile(
                file_path=f"file{file_idx}.py",
                added_lines=50,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=lines)]
            ))

        diff_summary = DiffSummary(files=files)

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add 100 comments (20 per file, max capacity)
            for file_idx in range(5):
                for line in range(1, 21):
                    target = CommentTarget(
                        file_path=f"file{file_idx}.py",
                        line_number=line,
                        line_range=None
                    )
                    comment = Comment(
                        text=f"Comment {file_idx}-{line}",
                        target=target,
                        timestamp=datetime.now(),
                        comment_type=CommentType.LINE
                    )
                    app.comment_store.add(comment)

            # Verify we have 100 comments (max capacity)
            assert app.comment_store.count() == 100

            # Measure edit operation time
            # TODO: Navigate to file0.py, line 10
            # start_time = time.perf_counter()

            # TODO: Press 'e' to initiate edit
            # TODO: Modify text to "Updated comment"
            # TODO: Press Enter to save

            # end_time = time.perf_counter()
            # edit_duration = (end_time - start_time) * 1000

            # Expected: <100ms
            # assert edit_duration < 100, f"Edit took {edit_duration}ms, expected <100ms"

            # Verify edit worked
            # updated = app.comment_store.get("file0.py", 10)
            # assert updated[0].text == "Updated comment"

    @pytest.mark.asyncio
    async def test_delete_comment_performance_with_large_store(self):
        """Delete operation should complete in <100ms with many comments.

        The raccoon removes one treasure marker swiftly!

        Expected: Delete (edit with empty text) completes in <100ms
        """
        # Create file with many comments
        lines = [('+', f'line {i}') for i in range(1, 101)]
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="delete_perf.py",
                added_lines=100,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=lines)]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add 100 comments (max capacity)
            for line in range(1, 101):
                target = CommentTarget(
                    file_path="delete_perf.py",
                    line_number=line,
                    line_range=None
                )
                comment = Comment(
                    text=f"Comment {line}",
                    target=target,
                    timestamp=datetime.now(),
                    comment_type=CommentType.LINE
                )
                app.comment_store.add(comment)

            assert app.comment_store.count() == 100

            # Measure delete time
            # TODO: Navigate to line 50
            # start_time = time.perf_counter()

            # TODO: Press 'e'
            # TODO: Clear all text
            # TODO: Press Enter

            # end_time = time.perf_counter()
            # delete_duration = (end_time - start_time) * 1000

            # Expected: <100ms
            # assert delete_duration < 100

            # Verify delete worked
            # assert app.comment_store.count() == 99

    @pytest.mark.asyncio
    async def test_edit_range_comment_performance(self):
        """Editing range comment should be fast regardless of range size.

        The raccoon polishes a territory marker swiftly!

        Expected: Edit completes in <100ms even for large ranges
        """
        lines = [('+', f'line {i}') for i in range(1, 201)]
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="range_perf.py",
                added_lines=200,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=lines)]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add large range comment (100 lines)
            target = CommentTarget(
                file_path="range_perf.py",
                line_number=None,
                line_range=(1, 100)
            )
            comment = Comment(
                text="Large range comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.RANGE
            )
            app.comment_store.add(comment)

            # Measure edit time
            # TODO: Navigate to line 50 (middle of range)
            # start_time = time.perf_counter()

            # TODO: Press 'e'
            # TODO: Modify text
            # TODO: Press Enter

            # end_time = time.perf_counter()
            # edit_duration = (end_time - start_time) * 1000

            # Expected: <100ms
            # assert edit_duration < 100


class TestHelpPerformance:
    """Performance tests for help overlay."""

    @pytest.mark.asyncio
    async def test_help_overlay_display_performance(self):
        """Help overlay should appear instantly.

        The treasure map unfurls swiftly!

        Expected: Help displays in <50ms
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="help_perf.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Measure help display time
            # start_time = time.perf_counter()

            # TODO: Press '?' to show help

            # end_time = time.perf_counter()
            # display_duration = (end_time - start_time) * 1000

            # Expected: <50ms
            # assert display_duration < 50

            # Verify help visible
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_help_dismiss_performance(self):
        """Help overlay should dismiss instantly.

        The treasure map rolls up swiftly!

        Expected: Dismissal completes in <50ms
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="dismiss_perf.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'a')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Show help first
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

            # Measure dismiss time
            # start_time = time.perf_counter()

            # TODO: Press '?' to dismiss

            # end_time = time.perf_counter()
            # dismiss_duration = (end_time - start_time) * 1000

            # Expected: <50ms
            # assert dismiss_duration < 50

            # Verify help hidden
            # assert not help_overlay.is_visible
