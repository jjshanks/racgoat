"""Performance contract tests for lazy loading efficiency (T020).

Validates that lazy loading conserves memory by not materializing unselected files.
Contract: performance-contracts.md - Lazy Loading Behavior
"""

import pytest
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T020: Lazy loading memory efficiency


@pytest.mark.asyncio
async def test_lazy_loading_memory():
    """Unselected files should not be materialized.

    The raccoon doesn't unwrap every treasure - only the shiny one in its paws!

    Contract: performance-contracts.md Scenario 1
    Requirement: Only selected file materialized
    """
    # Generate diff with 100 files
    diff_text = _generate_many_files_diff(files=100, lines_per_file=50)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Check lazy files dict
        lazy_files = getattr(app, 'lazy_files', {})

        # Count materialized files
        materialized_count = sum(
            1 for lf in lazy_files.values()
            if lf.is_materialized
        )

        # Assert: Only 1 file materialized (the selected one)
        assert materialized_count == 1, f"Expected 1 materialized file, got {materialized_count}"

        # Total files should be 100
        assert len(lazy_files) == 100


@pytest.mark.asyncio
async def test_materialization_on_selection():
    """Selecting a file should materialize it.

    When the raccoon picks up a treasure, it unwraps it to see what's inside!

    Contract: performance-contracts.md Scenario 2
    Requirement: File materialized on selection
    """
    # Generate diff with multiple files
    diff_text = _generate_many_files_diff(files=10, lines_per_file=20)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Initially, only first file materialized
        lazy_files = getattr(app, 'lazy_files', {})
        initial_count = sum(1 for lf in lazy_files.values() if lf.is_materialized)
        assert initial_count == 1

        # Switch to next file
        await pilot.press("down")
        await pilot.pause()

        # Now 2 files should be materialized (or 1 if memory released)
        new_count = sum(1 for lf in lazy_files.values() if lf.is_materialized)

        # Implementation can choose to keep or release old file
        # Accept either 1 (released) or 2 (kept)
        assert new_count in [1, 2], f"Expected 1 or 2 materialized files, got {new_count}"


@pytest.mark.asyncio
async def test_lazy_loading_with_large_diff():
    """Lazy loading should work efficiently with 10k line diff.

    Even with a mountain of treasures, the raccoon only holds one at a time!

    Contract: performance-contracts.md - Memory efficiency at scale
    """
    # Generate max-size diff: 100 files, 10k lines
    diff_text = _generate_many_files_diff(files=100, lines_per_file=100)

    parser = DiffParser()
    summary = parser.parse(diff_text)
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Check that not all files are materialized
        lazy_files = getattr(app, 'lazy_files', {})
        materialized_count = sum(1 for lf in lazy_files.values() if lf.is_materialized)

        # Should be far less than total files (ideally 1-2)
        assert materialized_count <= 2, f"Too many files materialized: {materialized_count}, expected <= 2"
        assert len(lazy_files) == 100, "Should have 100 lazy file entries"


# Helper functions


def _generate_many_files_diff(files: int, lines_per_file: int) -> str:
    """Generate diff with many files for lazy loading testing.

    Args:
        files: Number of files
        lines_per_file: Lines per file

    Returns:
        Multi-file diff text
    """
    diff_parts = []

    for i in range(files):
        filename = f"src/module_{i:03d}.py"
        diff_parts.append(f"""diff --git a/{filename} b/{filename}
index abc123..def456 100644
--- a/{filename}
+++ b/{filename}
@@ -1,{lines_per_file} +1,{lines_per_file} @@
""")
        for j in range(lines_per_file):
            diff_parts.append(f"+line {j}\n")

    return "".join(diff_parts)
