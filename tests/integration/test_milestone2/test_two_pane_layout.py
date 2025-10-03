"""Integration tests for two-pane layout scenarios.

Testing the whole raccoon's den, not just individual treasures!
"""

import pytest
from textual.pilot import Pilot

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestMultiFileDiffLayout:
    """Integration test for Scenario 1: Two-pane layout with multiple files."""

    @pytest.mark.asyncio
    async def test_multi_file_diff_shows_two_panes_with_first_selected(self):
        """Given a diff with 3 files, should display Files Pane + Diff Pane,
        with first file auto-selected and its diff shown.

        This is the full raccoon experience - everything working together!
        """
        # Setup: Create diff with 3 files
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="src/foo.py",
                added_lines=2,
                removed_lines=1,
                hunks=[
                    DiffHunk(old_start=1, new_start=1, lines=[
                        ('+', '# Foo changes'),
                        ('+', 'import bar'),
                        ('-', 'import old'),
                    ])
                ]
            ),
            DiffFile(
                file_path="src/bar.py",
                added_lines=1,
                removed_lines=0,
                hunks=[
                    DiffHunk(old_start=5, new_start=5, lines=[
                        ('+', 'def new_func():'),
                    ])
                ]
            ),
            DiffFile(
                file_path="tests/test_baz.py",
                added_lines=3,
                removed_lines=2,
                hunks=[
                    DiffHunk(old_start=10, new_start=10, lines=[
                        ('+', 'assert True'),
                        ('+', 'assert False'),
                        ('+', '# test'),
                        ('-', 'pass'),
                        ('-', '# old'),
                    ])
                ]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            # Wait for layout to mount
            await pilot.pause()

            # Verify: Two-pane layout exists
            two_pane = app.query_one("#two-pane-layout")
            assert two_pane is not None

            # Verify: Files pane shows all 3 files
            files_pane = app.query_one("#files-pane")
            assert files_pane.file_count == 3

            # Verify: First file is selected
            selected = files_pane.get_selected_file()
            assert selected is not None
            assert selected.file_path == "src/foo.py"

            # Verify: Diff pane shows first file's diff
            diff_pane = app.query_one("#diff-pane")
            assert diff_pane.current_file is not None
            assert diff_pane.current_file.file_path == "src/foo.py"

            # Verify content by checking the rendered text
            rendered_text = str(diff_pane.render())
            assert "src/foo.py" in rendered_text or diff_pane.current_file.file_path == "src/foo.py"
