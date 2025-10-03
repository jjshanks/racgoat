"""Integration tests for empty diff handling.

When the raccoon finds no treasures, it still stays polite!
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary


class TestEmptyDiffHandling:
    """Integration test for Scenario 4: Empty diff message."""

    @pytest.mark.asyncio
    async def test_empty_diff_shows_no_changes_message_and_stays_open(self):
        """Empty diff should display friendly message, not crash or auto-exit.

        No changes to review 🦝🐐 - but the app stays ready!
        """
        # Setup: Empty diff
        diff_summary = DiffSummary(files=[])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Verify: No two-pane layout
            two_pane = app.query("#two-pane-layout")
            assert len(two_pane) == 0

            # Verify: Empty message is shown
            empty_message = app.query_one("#empty-message")
            assert empty_message is not None

            # Verify: App is still running (doesn't crash or auto-exit)
            assert app.is_running
