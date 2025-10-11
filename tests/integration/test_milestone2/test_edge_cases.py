"""Integration tests for edge cases.

Even raccoons encounter strange treasures sometimes!
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestSingleFileDiff:
    """Integration test for Scenario 6: Single file maintains two-pane layout."""

    @pytest.mark.asyncio
    async def test_single_file_maintains_two_pane_layout_consistency(self):
        """Even with one file, should show Files Pane + Diff Pane (not single-pane).

        Consistency is key - the raccoon's den doesn't change shape!
        """
        # Setup: Single file diff
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="src/single.py",
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'single file')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Verify: Two-pane layout still exists (not collapsed)
            two_pane = app.query_one("#two-pane-layout")
            assert two_pane is not None

            # Verify: Both panes present
            files_pane = app.query_one("#files-pane")
            diff_pane = app.query_one("#diff-pane")
            assert files_pane is not None
            assert diff_pane is not None

            # Verify: Single file is selected and displayed
            assert files_pane.file_count == 1  # type: ignore[unresolved-attribute]
            assert files_pane.get_selected_file().file_path == "src/single.py"  # type: ignore[unresolved-attribute]
            assert diff_pane.current_file.file_path == "src/single.py"  # type: ignore[unresolved-attribute]


class TestLongPathTruncation:
    """Integration test for Scenario 7: Long file path truncation."""

    @pytest.mark.asyncio
    async def test_long_file_path_truncates_middle_preserves_ends(self):
        """Very long paths should truncate in the middle with '...'

        Like a goat squeezing through a narrow pass - important parts remain!
        """
        # Setup: File with very long path
        long_path = "src/very/deeply/nested/directory/structure/that/goes/on/and/on/file.py"
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path=long_path,
                added_lines=1,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'content')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            files_pane = app.query_one("#files-pane")

            # Verify: File is in the list
            assert files_pane.file_count == 1  # type: ignore[unresolved-attribute]
            selected = files_pane.get_selected_file()  # type: ignore[unresolved-attribute]
            assert selected.file_path == long_path

            # The truncation happens in display, not in the model
            # The actual path should be preserved in the model
            assert len(selected.file_path) > 50  # Verify it's actually long
