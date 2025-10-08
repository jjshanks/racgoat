"""Performance contract tests for file switching latency (T017).

Validates that switching between files happens within 200ms.
Contract: performance-contracts.md - File Switching Latency
"""

import pytest
import time
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T017: File switch latency (<200ms)


@pytest.mark.asyncio
async def test_file_switch_latency():
    """File switching should complete in < 200ms.

    The raccoon hops from treasure to treasure with lightning speed!

    Contract: performance-contracts.md Scenario 1-2
    Threshold: 200ms
    """
    # Generate diff with multiple files
    diff_text = _generate_multi_file_diff(files=10, lines_per_file=100)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Measure file switch time
        timings = []

        for _ in range(5):  # Test 5 file switches
            start_time = time.perf_counter()

            # Switch to next file (down arrow)
            await pilot.press("down")
            await pilot.pause()

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            timings.append(duration_ms)

        # All switches should be < 200ms
        max_time = max(timings)
        avg_time = sum(timings) / len(timings)

        assert max_time < 200, f"Slowest file switch: {max_time:.1f}ms, expected < 200ms"
        assert avg_time < 150, f"Average switch time: {avg_time:.1f}ms, should be well under threshold"


@pytest.mark.asyncio
async def test_large_file_switch():
    """Switching to large file (1000 lines) should be < 200ms.

    Even a big treasure gets unwrapped quickly!

    Contract: performance-contracts.md Scenario 2
    Threshold: 200ms
    """
    # Generate diff with one large file
    diff_text = _generate_multi_file_diff(files=1, lines_per_file=1000)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # File should already be selected, but measure render time
        # by forcing a re-selection
        start_time = time.perf_counter()

        # Trigger file selection event
        await pilot.press("down")  # Move to next (wraps to first if only one)
        await pilot.pause()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        # Assert: Switch time < 200ms even for large file
        assert duration_ms < 200, f"Large file switch took {duration_ms:.1f}ms, expected < 200ms"


# Helper functions


def _generate_multi_file_diff(files: int, lines_per_file: int) -> str:
    """Generate diff with multiple files for switch testing.

    Args:
        files: Number of files
        lines_per_file: Lines per file

    Returns:
        Multi-file diff text
    """
    diff_parts = []

    for i in range(files):
        filename = f"module{i}.py"
        diff_parts.append(f"""diff --git a/{filename} b/{filename}
index abc123..def456 100644
--- a/{filename}
+++ b/{filename}
@@ -1,{lines_per_file} +1,{lines_per_file} @@
""")
        for j in range(lines_per_file):
            diff_parts.append(f"+def function_{j}():\n")

    return "".join(diff_parts)
