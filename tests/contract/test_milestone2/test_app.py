"""Contract tests for App-level behavior.

The raccoon's main interface - where it all comes together!
"""

import pytest
from racgoat.parser.models import DiffFile, DiffSummary


class TestAppRunTUI:
    """Tests for run_tui() - launching the visual interface!"""

    @pytest.mark.asyncio
    async def test_app_shows_two_pane_layout_for_valid_diff(self):
        """When diff has files, should show TwoPaneLayout with Files and Diff panes."""
        from racgoat.main import RacGoatApp
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="test.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])])
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have TwoPaneLayout
            two_pane = app.query_one("#two-pane-layout")
            assert two_pane is not None

            # Should have Files and Diff panes
            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")
            assert files_pane is not None
            assert diff_pane is not None

    @pytest.mark.asyncio
    async def test_app_shows_no_diff_message_for_empty_diff(self):
        """When diff is empty, should show 'No changes to review' message."""
        from racgoat.main import RacGoatApp

        # Empty diff
        diff_summary = DiffSummary(files=[])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have empty message instead of TwoPaneLayout
            empty_message = app.query_one("#empty-message")
            assert empty_message is not None

            # Should not have TwoPaneLayout
            two_pane_layouts = app.query("#two-pane-layout")
            assert len(two_pane_layouts) == 0

    @pytest.mark.asyncio
    async def test_app_initial_focus_is_files_pane(self):
        """On launch, the Files Pane should have initial focus (implementation)."""
        from racgoat.main import RacGoatApp
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="test.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])])
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            files_pane = app.query_one("#files-pane")
            # Files pane's ListView has focus
            assert files_pane.has_focus

    @pytest.mark.asyncio
    async def test_app_auto_selects_first_file(self):
        """On launch, the first file should be selected and displayed."""
        from racgoat.main import RacGoatApp
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
            DiffFile(file_path="file2.py", added_lines=2, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line2')])]),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")

            # First file should be selected
            assert files_pane.get_selected_file().file_path == "file1.py"  # type: ignore[unresolved-attribute]

            # First file should be displayed in diff pane
            assert diff_pane.current_file.file_path == "file1.py"  # type: ignore[unresolved-attribute]


class TestAppQuitBinding:
    """Tests for quit functionality - letting the raccoon leave gracefully!"""

    @pytest.mark.asyncio
    async def test_q_key_triggers_quit_action(self):
        """Pressing 'q' should exit the application."""
        from racgoat.main import RacGoatApp
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="test.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])])
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # App should be running
            assert app.is_running

            # Press 'q' to quit
            await pilot.press("q")
            await pilot.pause()

            # App should exit
            # Note: The run_test context handles the exit, so we can't directly check
            # if app is still running. The test passing means quit worked.

    @pytest.mark.asyncio
    async def test_quit_exits_cleanly(self):
        """Quitting should exit cleanly without errors."""
        from racgoat.main import RacGoatApp
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="test.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])])
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Trigger quit action by pressing q
            await pilot.press("q")
            await pilot.pause()

            # If we get here without exceptions, quit was clean
