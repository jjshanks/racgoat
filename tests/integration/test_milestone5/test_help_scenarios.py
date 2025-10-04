"""Integration tests for help overlay functionality.

These tests validate that the raccoon can show its treasure map legend
whenever needed!

Covers:
- AS-007: Display help overlay
- AS-008: Dismiss help overlay
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestHelpOverlayDisplay:
    """Tests for displaying help overlay - AS-007."""

    @pytest.mark.asyncio
    async def test_display_help_overlay(self):
        """Pressing '?' should display help overlay with all keybindings.

        The raccoon unfurls its treasure map legend!

        User workflow:
        1. From any screen, press '?'

        Expected:
        - Help overlay appears centered
        - All keybindings displayed organized by category
        - Categories: Navigation, Commenting, Search, General
        - Each binding shows: key, action, description
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="help_test.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # Expected: Help overlay visible
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay is not None
            # assert help_overlay.is_visible
            #
            # # Verify help content contains key categories
            # help_text = help_overlay.render_str()
            # assert "Navigation" in help_text or "navigation" in help_text.lower()
            # assert "Commenting" in help_text or "comment" in help_text.lower()
            # assert "Search" in help_text or "search" in help_text.lower()

    @pytest.mark.asyncio
    async def test_help_shows_all_keybindings(self):
        """Help overlay should list all 15+ keybindings.

        The treasure map legend is complete!

        Expected keybindings:
        - Navigation: Arrow keys, Tab, PgUp/PgDown
        - Commenting: a (line), c (file), s (range), e (edit)
        - Search: / (search), n (next), N (previous), Esc (exit)
        - General: q (quit), ? (help)
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="all_keys.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # Expected: All keybindings present
            # help_overlay = app.query_one("#help-overlay")
            # help_text = help_overlay.render_str().lower()
            #
            # # Navigation keys
            # assert "arrow" in help_text or "↑" in help_text
            # assert "tab" in help_text
            #
            # # Commenting keys
            # assert "a" in help_text and "line" in help_text
            # assert "c" in help_text and "file" in help_text
            # assert "s" in help_text and "range" in help_text or "select" in help_text
            # assert "e" in help_text and "edit" in help_text
            #
            # # Search keys
            # assert "/" in help_text and "search" in help_text
            # assert "n" in help_text and "next" in help_text
            #
            # # General keys
            # assert "q" in help_text and "quit" in help_text
            # assert "?" in help_text and "help" in help_text

    @pytest.mark.asyncio
    async def test_help_overlay_centered_on_screen(self):
        """Help overlay should be centered on screen.

        The treasure map legend floats in the middle!

        Expected: Overlay appears centered, not edge-aligned
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="centered.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # Expected: Overlay centered
            # help_overlay = app.query_one("#help-overlay")
            # # Check CSS or layout properties for centering
            # assert help_overlay.styles.align_horizontal == "center"
            # assert help_overlay.styles.align_vertical == "middle"

    @pytest.mark.asyncio
    async def test_help_from_files_pane(self):
        """Help should work from Files Pane.

        The raccoon can check the legend from the file list!

        Expected: Help works regardless of which pane has focus
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'a')])]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'b')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Ensure Files Pane has focus
            # TODO: Press Tab if needed to focus Files Pane

            # TODO: Press '?' to show help

            # Expected: Help appears regardless of pane focus
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_help_from_diff_pane(self):
        """Help should work from Diff Pane.

        The raccoon can check the legend while viewing code!

        Expected: Help works from Diff Pane too
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="diff_help.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Ensure Diff Pane has focus
            # TODO: Press Tab if needed to focus Diff Pane

            # TODO: Press '?' to show help

            # Expected: Help appears
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible


class TestHelpOverlayDismissal:
    """Tests for dismissing help overlay - AS-008."""

    @pytest.mark.asyncio
    async def test_dismiss_help_overlay(self):
        """Pressing '?' or Esc should close help overlay.

        The raccoon rolls up its treasure map legend!

        User workflow:
        1. Press '?' to open help
        2. Press '?' again to close

        Expected:
        - Help overlay disappears
        - Focus returns to previous widget
        - Application state preserved
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="dismiss.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', f'line{i}') for i in range(1, 11)]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

            # TODO: Press '?' again to dismiss

            # Expected: Help hidden
            # assert not help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_dismiss_help_with_esc(self):
        """Esc should also dismiss help overlay.

        The raccoon can escape from the legend view!

        Expected: Esc closes help, returns to previous state
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="esc_dismiss.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # TODO: Press Esc to dismiss

            # Expected: Help hidden
            # help_overlay = app.query_one("#help-overlay")
            # assert not help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_help_dismissal_preserves_state(self):
        """Dismissing help should not change app state.

        The treasure map didn't move anything!

        Expected:
        - Selected file unchanged
        - Comments intact
        - Search state preserved (if active)
        - Focus returns to original widget
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="state1.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'a')])]
            ),
            DiffFile(
                file_path="state2.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'b')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Select second file
            # TODO: Navigate to state2.py

            # Add a comment
            from datetime import datetime
            from racgoat.models.comments import Comment, CommentTarget, CommentType

            target = CommentTarget(
                file_path="state2.py",
                line_number=1,
                line_range=None
            )
            comment = Comment(
                text="Important note",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            initial_count = app.comment_store.count()
            # TODO: Get current file selection

            # TODO: Press '?' to show help
            # TODO: Press '?' to dismiss help

            # Expected: State unchanged
            # assert app.comment_store.count() == initial_count
            # TODO: Verify same file is selected
            # TODO: Verify focus returned to original widget

    @pytest.mark.asyncio
    async def test_help_does_not_block_interaction(self):
        """Help overlay should be modal - blocks interaction with app.

        The treasure map covers everything until dismissed!

        Expected: Cannot navigate or interact while help is shown
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="modal.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # TODO: Try to press 'a' to add comment (should be blocked)
            # TODO: Try to press arrow keys (should be blocked)

            # Expected: Only help dismissal keys work
            # (Implementation detail: help overlay should be modal)


class TestHelpOverlayEdgeCases:
    """Edge cases for help overlay."""

    @pytest.mark.asyncio
    async def test_help_toggle_rapidly(self):
        """Rapidly toggling help should not cause issues.

        The raccoon flips the map open and closed quickly!

        Expected: Help overlay state consistent
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="rapid.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'test')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' multiple times rapidly
            # TODO: Press '?' (open)
            # TODO: Press '?' (close)
            # TODO: Press '?' (open)
            # TODO: Press '?' (close)

            # Expected: Final state is closed
            # help_overlay = app.query_one("#help-overlay")
            # assert not help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_help_with_no_diff(self):
        """Help should work even with empty diff.

        The treasure map works even in an empty field!

        Expected: Help displays normally
        """
        diff_summary = DiffSummary(files=[])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # Expected: Help appears even with no files
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

    @pytest.mark.asyncio
    async def test_help_during_search_mode(self):
        """Help should override search mode temporarily.

        The treasure map appears even while sniffing!

        Expected: Help shows, search mode paused but preserved
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="search_help.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'TODO: test')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '/' to enter search mode
            # TODO: Type "TODO" (but don't execute yet)

            # TODO: Press '?' to show help

            # Expected: Help appears, search input preserved
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.is_visible

            # TODO: Dismiss help with '?'

            # Expected: Search mode restored
            # search_input = app.query_one("#search-input")
            # assert search_input.value == "TODO"
