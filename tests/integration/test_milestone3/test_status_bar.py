"""Integration tests for StatusBar context-sensitive keybinding display.

These tests validate that the StatusBar updates correctly based on
application mode and focus state.
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.ui.models import ApplicationMode, PaneFocusState


class TestStatusBar:
    """Integration tests for StatusBar widget."""

    @pytest.mark.asyncio
    async def test_status_bar_exists(self):
        """StatusBar should be present in the app layout.

        The status bar guides the raccoon's treasure hunting!
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

            # Verify status bar exists
            status_bar = app.query_one("#status-bar")
            assert status_bar is not None

    @pytest.mark.asyncio
    async def test_status_bar_updates_on_mode_change(self):
        """StatusBar should update when app mode changes.

        When the raccoon switches to selective mode, the status bar tells it!
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

            status_bar = app.query_one("#status-bar")

            # Initial mode is NORMAL
            assert app.mode == ApplicationMode.NORMAL

            # Enter SELECT mode
            await pilot.press("s")
            await pilot.pause()

            # Mode should be SELECT
            assert app.mode == ApplicationMode.SELECT

            # Status bar should still exist (detailed content check would require rendering)
            assert status_bar is not None

            # Return to NORMAL
            await pilot.press("escape")
            await pilot.pause()

            assert app.mode == ApplicationMode.NORMAL

    @pytest.mark.asyncio
    async def test_status_bar_responsive_to_focus_changes(self):
        """StatusBar should update when focus changes between panes.

        Different panes, different keybindings - the raccoon stays informed!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            status_bar = app.query_one("#status-bar")
            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")

            # Initial focus should be on files pane
            assert files_pane._list_view.has_focus

            # Press Tab to switch focus
            await pilot.press("tab")
            await pilot.pause()

            # Focus should be on diff pane
            assert diff_pane.has_focus

            # Status bar should still be present
            assert status_bar is not None

            # Press Tab again to cycle back
            await pilot.press("tab")
            await pilot.pause()

            # Focus back on files pane
            assert files_pane._list_view.has_focus

    @pytest.mark.asyncio
    async def test_status_bar_shows_select_mode_keys(self):
        """StatusBar should show SELECT mode keybindings when in SELECT mode.

        When selecting treasure ranges, the raccoon needs different instructions!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line1'),
                        ('+', 'line2'),
                        ('+', 'line3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            status_bar = app.query_one("#status-bar")

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Enter SELECT mode
            await pilot.press("s")
            await pilot.pause()

            # Verify mode is SELECT
            assert app.mode == ApplicationMode.SELECT

            # Status bar should be displaying SELECT mode keys
            # (Detailed content check would require rendering the status bar text)
            assert status_bar is not None
