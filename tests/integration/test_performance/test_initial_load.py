"""Performance contract tests for initial load time (T015-T016).

Validates that diffs of various sizes load within acceptable thresholds.
Contract: performance-contracts.md Scenarios 1-3
"""

import pytest
import time
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T015: Small diff initial load (<500ms)


@pytest.mark.asyncio
async def test_small_diff_load():
    """Small diffs (10 files, 100 lines) should load in < 500ms.

    The nimble raccoon doesn't hesitate with small treasures!

    Contract: performance-contracts.md Scenario 1
    Threshold: 500ms
    """
    # Generate small diff: 10 files, 100 total lines
    diff_text = _generate_diff(files=10, lines_per_file=10)

    parser = DiffParser()
    app = RacGoatApp()

    start_time = time.perf_counter()

    async with app.run_test() as pilot:
        # Parse and load diff
        summary = parser.parse(diff_text)
        app.diff_summary = summary

        # Wait for first render
        await pilot.pause()

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    # Assert: Load time < 500ms
    assert duration_ms < 500, f"Small diff load took {duration_ms:.1f}ms, expected < 500ms"

    # Verify files loaded correctly
    assert len(summary.files) == 10
    assert summary.total_line_count == 100


# T016: Large diff initial load (<2s)


@pytest.mark.asyncio
async def test_large_diff_load():
    """Large diffs (100 files, 10k lines) should load in < 2s.

    Even with a mountain of treasures, the goat finds its footing quickly!

    Contract: performance-contracts.md Scenario 3
    Threshold: 2000ms (2 seconds)
    """
    # Generate large diff: 100 files, 10,000 total lines (max supported)
    diff_text = _generate_diff(files=100, lines_per_file=100)

    parser = DiffParser()
    app = RacGoatApp()

    start_time = time.perf_counter()

    async with app.run_test() as pilot:
        # Parse and load diff
        summary = parser.parse(diff_text)
        app.diff_summary = summary

        # Wait for first render
        await pilot.pause()

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    # Assert: Load time < 2000ms
    assert duration_ms < 2000, f"Large diff load took {duration_ms:.1f}ms, expected < 2000ms"

    # Verify files loaded correctly
    assert len(summary.files) == 100
    assert summary.total_line_count == 10000
    assert summary.exceeds_limit is False


@pytest.mark.asyncio
async def test_medium_diff_load():
    """Medium diffs (50 files, 1000 lines) should load in < 1s.

    A moderate pile of treasures for the eager raccoon!

    Contract: performance-contracts.md Scenario 2
    Threshold: 1000ms (1 second)
    """
    # Generate medium diff: 50 files, 1000 total lines
    diff_text = _generate_diff(files=50, lines_per_file=20)

    parser = DiffParser()
    app = RacGoatApp()

    start_time = time.perf_counter()

    async with app.run_test() as pilot:
        # Parse and load diff
        summary = parser.parse(diff_text)
        app.diff_summary = summary

        # Wait for first render
        await pilot.pause()

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    # Assert: Load time < 1000ms
    assert duration_ms < 1000, f"Medium diff load took {duration_ms:.1f}ms, expected < 1000ms"

    # Verify files loaded correctly
    assert len(summary.files) == 50
    assert summary.total_line_count == 1000


# Helper functions


def _generate_diff(files: int, lines_per_file: int) -> str:
    """Generate a diff with specified number of files and lines.

    Args:
        files: Number of files to include
        lines_per_file: Lines per file (distributed across hunks)

    Returns:
        Diff text with exact structure
    """
    diff_parts = []

    for i in range(files):
        filename = f"file{i:03d}.py"
        diff_parts.append(f"""diff --git a/{filename} b/{filename}
index 1234567..abcdefg 100644
--- a/{filename}
+++ b/{filename}
@@ -1,{lines_per_file} +1,{lines_per_file} @@
""")
        # Add lines
        for j in range(lines_per_file):
            diff_parts.append(f"+line {j} in {filename}\n")

    return "".join(diff_parts)
