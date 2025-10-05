"""Contract tests for binary file filtering (Milestone 6).

Milestone 6: TUI tests verify binary files are excluded from file list,
per parser-contracts.md Scenarios 1-2.

Old CLI tests removed - RacGoat is now a TUI application.
"""

import pytest


# Milestone 6: TUI-specific binary filtering tests (T013-T014)


@pytest.mark.asyncio
async def test_binary_files_excluded_from_tui_list():
    """Binary files should be excluded from TUI file list (not CLI exit).

    The raccoon only displays treasures it can review!

    Contract: parser-contracts.md Scenario 1
    Requirement: FR-020 (binary files excluded from TUI, not CLI rejection)
    """
    from racgoat.main import RacGoatApp
    from racgoat.ui.widgets.files_pane import FilesPane
    from racgoat.parser.diff_parser import DiffParser
    from textual.widgets import ListView

    diff_input = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
diff --git a/package-lock.json b/package-lock.json
index 1234567..abcdefg 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,2 +1,2 @@
-old lock
+new lock
diff --git a/main.py b/main.py
index 1234567..abcdefg 100644
--- a/main.py
+++ b/main.py
@@ -1,1 +1,1 @@
-print("old")
+print("new")
"""

    # Parse diff first
    parser = DiffParser()
    summary = parser.parse(diff_input)

    # Verify parser excluded binary and generated files
    # Should have only main.py (image.png and package-lock.json excluded)
    assert len(summary.files) == 1
    assert summary.files[0].file_path == "main.py"

    # Create app with parsed diff
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        # Wait for app to render
        await pilot.pause()

        # Get files pane and check visible files
        files_pane = app.query_one(FilesPane)
        file_list = files_pane.query_one(ListView)

        # Should only show text files (main.py)
        visible_items = list(file_list.children)

        # Should have only 1 file (main.py) - binary and generated excluded
        assert len(visible_items) == 1

        # The fact that we have exactly 1 item and the parser returned
        # only main.py means the binary filtering worked correctly


@pytest.mark.asyncio
async def test_all_binary_shows_placeholder():
    """When all files are binary, TUI shows empty message (not exit).

    The raccoon stays put even when there's nothing to review!

    Contract: parser-contracts.md Scenario 2
    Requirement: FR-021 (placeholder when no reviewable files)
    """
    from racgoat.main import RacGoatApp
    from racgoat.parser.diff_parser import DiffParser
    from textual.widgets import Static

    diff_input = """diff --git a/logo.png b/logo.png
Binary files a/logo.png and b/logo.png differ
diff --git a/icon.jpg b/icon.jpg
Binary files a/icon.jpg and b/icon.jpg differ
"""

    # Parse diff
    parser = DiffParser()
    summary = parser.parse(diff_input)

    # Should have no files (all binary)
    assert len(summary.files) == 0
    assert summary.is_empty is True

    # Create app with empty summary
    app = RacGoatApp(diff_summary=summary)

    async with app.run_test() as pilot:
        # Wait for app to render
        await pilot.pause()

        # App should show empty message
        empty_message = app.query_one("#empty-message", Static)

        # The Static widget was created with text content in main.py
        # We need to check if the widget exists (which proves empty state is shown)
        # The actual text is set in main.py:182-186
        assert empty_message is not None

        # Verify the app shows the empty state (not the two-pane layout)
        # If we can query empty-message, it means we're showing the placeholder
        from racgoat.ui.widgets import TwoPaneLayout
        two_pane_exists = len(app.query(TwoPaneLayout)) > 0
        assert not two_pane_exists, "Should not show two-pane layout when all files are binary"

        # App should remain open (not exit like old CLI behavior)
        # This is implicit - if we get here, app didn't exit
