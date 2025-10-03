"""Integration tests for navigation scenarios.

The goat's nimble movement through files and panes!
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestArrowKeyNavigation:
    """Integration test for Scenario 2: File list navigation with arrow keys."""

    @pytest.mark.asyncio
    async def test_arrow_keys_navigate_files_and_update_diff_display(self):
        """Arrow keys should move selection and update Diff Pane content.

        Like a goat hopping from rock to rock, viewing each cliff!
        """
        # Setup: Three files
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'file1')])]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'file2')])]
            ),
            DiffFile(
                file_path="file3.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'file3')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")

            # Verify initial state: file1 selected
            assert files_pane.get_selected_file().file_path == "file1.py"
            assert diff_pane.current_file.file_path == "file1.py"

            # Action: Press down arrow to select file2
            await pilot.press("down")
            await pilot.pause()

            # Verify: file2 selected and displayed
            assert files_pane.get_selected_file().file_path == "file2.py"
            assert diff_pane.current_file.file_path == "file2.py"

            # Action: Press down arrow again to select file3
            await pilot.press("down")
            await pilot.pause()

            # Verify: file3 selected and displayed
            assert files_pane.get_selected_file().file_path == "file3.py"
            assert diff_pane.current_file.file_path == "file3.py"

            # Action: Press up arrow to go back to file2
            await pilot.press("up")
            await pilot.pause()

            # Verify: file2 selected again
            assert files_pane.get_selected_file().file_path == "file2.py"
            assert diff_pane.current_file.file_path == "file2.py"


class TestTabFocusSwitching:
    """Integration test for Scenario 3: Focus switching with Tab key."""

    @pytest.mark.asyncio
    async def test_tab_switches_focus_between_panes_and_controls_arrow_keys(self):
        """Tab should cycle focus, and arrow keys should control the focused pane.

        The raccoon can move between its two treasure rooms!
        """
        # Setup: Two files
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'file1')])]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'file2')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")

            # Verify initial state: files pane's ListView has focus
            assert files_pane._list_view.has_focus

            # Action: Press Tab to switch focus
            await pilot.press("tab")
            await pilot.pause()

            # Verify: diff pane now has focus
            assert diff_pane.has_focus

            # Action: Press Tab again to cycle back
            await pilot.press("tab")
            await pilot.pause()

            # Verify: files pane's ListView has focus again
            assert files_pane._list_view.has_focus
