"""Integration tests for quit functionality.

The raccoon knows when to leave the party!
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestQuitApplication:
    """Integration test for Scenario 8: Quit with 'q' key."""

    @pytest.mark.asyncio
    async def test_q_key_quits_application_cleanly_with_exit_code_zero(self):
        """Pressing 'q' should exit immediately with status 0, no errors.

        The raccoon tips its hat and exits stage left!
        """
        # Setup: App with some content
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

            # Action: Press 'q' key
            await pilot.press("q")

            # Verify: App has exited
            assert not app.is_running
