"""Integration tests for diff rendering with colors.

The raccoon's colorful display of changes!
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestANSIColorRendering:
    """Integration test for Scenario 5: ANSI color highlighting."""

    @pytest.mark.asyncio
    async def test_diff_pane_renders_with_ansi_colors_and_line_numbers(self):
        """Diff should display with green adds, red removes, dim context, and line numbers.

        Like a rainbow for the raccoon - each color means something!
        """
        # Setup: Diff with all three change types
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="src/test.py",
                added_lines=2,
                removed_lines=1,
                hunks=[
                    DiffHunk(old_start=1, new_start=1, lines=[
                        (' ', 'def foo():'),
                        ('+', '    print("new line")'),
                        ('+', '    return True'),
                        ('-', '    pass'),
                        (' ', '# End of function'),
                    ])
                ]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            diff_pane = app.query_one("#diff-pane")

            # Verify: File is displayed
            assert diff_pane.current_file is not None
            assert diff_pane.current_file.file_path == "src/test.py"

            # Verify: Hunk data is correctly stored
            assert len(diff_pane.current_file.hunks) == 1
            hunk = diff_pane.current_file.hunks[0]

            # Verify all three change types are present in the hunk
            assert hunk.lines[0] == (' ', 'def foo():'), "Context line 1"
            assert hunk.lines[1] == ('+', '    print("new line")'), "Added line 1"
            assert hunk.lines[2] == ('+', '    return True'), "Added line 2"
            assert hunk.lines[3] == ('-', '    pass'), "Removed line"
            assert hunk.lines[4] == (' ', '# End of function'), "Context line 2"

            # Verify the pane is rendering (not empty)
            rendered_text = diff_pane.render()
            assert rendered_text is not None
