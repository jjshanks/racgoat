"""Performance contract tests for scroll responsiveness (T018).

Validates that scrolling through large files maintains < 100ms response time.
Contract: performance-contracts.md - Scroll Responsiveness
"""

import pytest
import time
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T018: Scroll responsiveness (<100ms)


@pytest.mark.asyncio
async def test_rapid_scroll():
    """Rapid scrolling should maintain < 100ms per action.

    The goat leaps from rock to rock without hesitation!

    Contract: performance-contracts.md Scenario 2
    Threshold: 100ms per scroll action
    """
    # Generate diff with large file (1000 lines)
    diff_text = _generate_large_file_diff(lines=1000)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Perform rapid scrolling
        timings = []

        for _ in range(20):  # 20 rapid scroll actions
            start_time = time.perf_counter()

            await pilot.press("down")  # Scroll down one line
            await pilot.pause()

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            timings.append(duration_ms)

        # Assert: All scrolls < 100ms
        max_scroll = max(timings)
        avg_scroll = sum(timings) / len(timings)

        assert max_scroll < 100, f"Slowest scroll: {max_scroll:.1f}ms, expected < 100ms"
        assert avg_scroll < 50, f"Average scroll: {avg_scroll:.1f}ms, should be well under threshold"


@pytest.mark.asyncio
async def test_page_down_performance():
    """Page down jumps should be < 100ms.

    Big leaps require steady footing - even for the mountain goat!

    Contract: performance-contracts.md Scenario 1
    Threshold: 100ms for large jumps
    """
    # Generate large file
    diff_text = _generate_large_file_diff(lines=2000)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Test page down performance
        start_time = time.perf_counter()

        await pilot.press("pagedown")
        await pilot.pause()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        # Assert: Page down < 100ms
        assert duration_ms < 100, f"PageDown took {duration_ms:.1f}ms, expected < 100ms"


@pytest.mark.asyncio
async def test_jump_to_end_performance():
    """Jumping to end of large file should be < 200ms.

    The goat knows shortcuts to the summit!

    Contract: performance-contracts.md Scenario 3
    Threshold: 200ms for large jumps
    """
    # Generate very large file
    diff_text = _generate_large_file_diff(lines=5000)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Jump to end
        start_time = time.perf_counter()

        await pilot.press("end")
        await pilot.pause()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        # Assert: Jump to end < 200ms
        assert duration_ms < 200, f"Jump to end took {duration_ms:.1f}ms, expected < 200ms"


# Helper functions


def _generate_large_file_diff(lines: int) -> str:
    """Generate diff with a single large file.

    Args:
        lines: Number of lines in the file

    Returns:
        Diff text with large file
    """
    diff_parts = [f"""diff --git a/large_file.py b/large_file.py
index 1234567..abcdefg 100644
--- a/large_file.py
+++ b/large_file.py
@@ -1,{lines} +1,{lines} @@
"""]

    for i in range(lines):
        diff_parts.append(f"+def function_{i:04d}():\n")

    return "".join(diff_parts)
