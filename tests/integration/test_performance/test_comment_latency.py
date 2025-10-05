"""Performance contract tests for comment addition latency (T019).

Validates that adding comments maintains < 200ms response time.
Contract: performance-contracts.md - Comment Addition Latency
"""

import pytest
import time
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T019: Comment addition latency (<200ms)


@pytest.mark.asyncio
async def test_comment_addition_performance():
    """Adding a comment should complete in < 200ms.

    The raccoon marks its treasures swiftly!

    Contract: performance-contracts.md Scenario 1
    Threshold: 200ms from key press to store update
    """
    # Generate diff
    diff_text = _generate_test_diff()

    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        # Parse and load diff
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Measure comment addition time
        start_time = time.perf_counter()

        # Press 'a' to add comment
        await pilot.press("a")
        await pilot.pause()

        # Type comment text
        await pilot.press(*"Test comment")
        await pilot.pause()

        # Submit comment
        await pilot.press("enter")
        await pilot.pause()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        # Assert: Comment addition < 200ms
        assert duration_ms < 200, f"Comment addition took {duration_ms:.1f}ms, expected < 200ms"


@pytest.mark.asyncio
async def test_comment_with_existing_comments():
    """Adding comments with 100 existing should still be < 200ms.

    The pile of marked treasures doesn't slow the raccoon down!

    Contract: performance-contracts.md Scenario 2
    Threshold: 200ms even with 100+ existing comments
    """
    # Generate diff
    diff_text = _generate_test_diff()

    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        # Parse and load diff
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Add 100 comments first
        for i in range(100):
            await pilot.press("a")
            await pilot.pause()
            await pilot.press(*f"Comment {i}")
            await pilot.press("enter")
            await pilot.pause()

        # Now measure 101st comment
        start_time = time.perf_counter()

        await pilot.press("a")
        await pilot.pause()
        await pilot.press(*"Final comment")
        await pilot.press("enter")
        await pilot.pause()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        # Assert: Still < 200ms with many existing comments
        assert duration_ms < 200, f"Comment addition with 100 existing took {duration_ms:.1f}ms, expected < 200ms"


# Helper functions


def _generate_test_diff() -> str:
    """Generate simple diff for comment testing.

    Returns:
        Basic diff with enough lines for testing
    """
    return """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,50 +1,50 @@
+def test_function():
+    pass
+def another_function():
+    pass
"""
