"""Integration tests for Milestone 5 edge cases.

These tests validate the raccoon's treasure-finding skills in unusual situations!

Covers:
- Edge Case 1: Edit on uncommented line
- Edge Case 2: Search no matches
- Edge Case 3: File switch resets search
- Edge Case 6: Help scrollable in small terminal
- Edge Case 8: Edit during Select Mode
"""

import pytest
from datetime import datetime

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import Comment, CommentTarget, CommentType


class TestEditOnUncommentedLine:
    """Tests for edit on lines without comments - Edge Case 1."""

    @pytest.mark.asyncio
    async def test_edit_on_uncommented_line_does_nothing(self):
        """Pressing 'e' on uncommented line should be silently ignored.

        The raccoon can't polish a treasure that isn't there!

        User workflow:
        1. Navigate to line 5 (no comment)
        2. Press 'e'

        Expected:
        - Nothing happens (silent ignore)
        - No dialog appears
        - No error message
        - Application remains in normal state
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="no_comment.py",
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

            # Verify line 5 has no comment
            assert len(app.comment_store.get("no_comment.py", 5)) == 0

            # TODO: Navigate to line 5
            # TODO: Press 'e'

            # Expected: No edit dialog appears
            # edit_dialog = app.query("#edit-dialog")
            # assert len(edit_dialog) == 0 or not edit_dialog[0].is_visible

            # No changes to comment store
            assert app.comment_store.count() == 0

    @pytest.mark.asyncio
    async def test_status_bar_hides_edit_on_uncommented_line(self):
        """Status bar should not show 'e - Edit' on uncommented lines.

        The treasure map doesn't show polish option for empty spots!

        Expected: Status bar does not display edit keybinding
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="status_test.py",
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

            # Add comment to line 3 only
            target = CommentTarget(
                file_path="status_test.py",
                line_number=3,
                line_range=None
            )
            comment = Comment(
                text="Only this line has a comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Navigate to line 3 (with comment)
            # status_bar = app.query_one("#status-bar")
            # status_text = status_bar.render_str()
            # assert "e" in status_text.lower() or "edit" in status_text.lower()

            # TODO: Navigate to line 5 (without comment)
            # status_text = status_bar.render_str()
            # assert "e" not in status_text or "edit" not in status_text.lower()


class TestSearchNoMatches:
    """Tests for search with zero matches - Edge Case 2."""

    @pytest.mark.asyncio
    async def test_search_no_matches_shows_zero_counter(self):
        """Search with no matches should display '0/0 matches'.

        The raccoon sniffs but finds no treasure!

        User workflow:
        1. Press '/' to enter search
        2. Type "XYZABC123" (pattern that doesn't exist)
        3. Press Enter

        Expected:
        - Status bar shows "0/0 matches"
        - No highlights in diff
        - Cursor position unchanged
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="no_matches.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def function():'),
                        ('+', '    return 42'),
                        ('+', ''),
                        ('+', 'x = 100'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '/' to search
            # TODO: Type "XYZABC123"
            # TODO: Press Enter

            # Expected: Zero matches
            # search_state = app.diff_pane.search_state
            # assert search_state is not None
            # assert search_state.total_matches == 0
            #
            # status_bar = app.query_one("#status-bar")
            # assert "0/0" in status_bar.render_str()

    @pytest.mark.asyncio
    async def test_search_no_matches_no_highlights(self):
        """No highlights should appear when search finds nothing.

        The raccoon marks no spots when there's no treasure!

        Expected: Diff pane has no highlight styling
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="highlight_test.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'no matches here')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "NOTFOUND"

            # Expected: No highlights in diff pane
            # diff_pane = app.query_one("#diff-pane")
            # diff_text = diff_pane.render_str()
            # assert "highlight" not in diff_text.lower() or highlight count == 0

    @pytest.mark.asyncio
    async def test_search_no_matches_navigation_disabled(self):
        """'n' and 'N' should do nothing when no matches found.

        The raccoon can't jump to treasures that don't exist!

        Expected: Navigation keys have no effect
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="nav_disabled.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test line')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "NOTFOUND" (0 matches)
            # initial_cursor = app.diff_pane.cursor_line

            # TODO: Press 'n' to try next
            # assert app.diff_pane.cursor_line == initial_cursor

            # TODO: Press 'N' to try previous
            # assert app.diff_pane.cursor_line == initial_cursor


class TestFileSwitch:
    """Tests for search state on file switching - Edge Case 3."""

    @pytest.mark.asyncio
    async def test_search_state_resets_on_file_switch(self):
        """Switching files should clear search highlights and state.

        The raccoon's treasure scent resets when moving to a new spot!

        User workflow:
        1. Execute search in file1.py with matches
        2. Tab to Files Pane
        3. Select file2.py
        4. Tab back to Diff Pane

        Expected:
        - Search highlights cleared
        - Match counter cleared
        - Search mode exited
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'TODO: first file'),
                        ('+', 'TODO: another'),
                    ]
                )]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'different content')]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "TODO" in file1.py (2 matches)
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 2

            # TODO: Switch to file2.py

            # Expected: Search state cleared
            # search_state = app.diff_pane.search_state
            # assert search_state is None or search_state.total_matches == 0
            #
            # # No match counter in status bar
            # status_bar = app.query_one("#status-bar")
            # assert "/matches" not in status_bar.render_str().lower()

    @pytest.mark.asyncio
    async def test_search_query_cleared_on_file_switch(self):
        """Search query should be cleared when switching files.

        The raccoon forgets what it was sniffing for!

        Expected: Cannot press 'n' to navigate non-existent matches
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="query1.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'find')])]
            ),
            DiffFile(
                file_path="query2.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'other')])]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "find" in query1.py

            # TODO: Switch to query2.py

            # TODO: Press 'n' to try navigate
            # Expected: Nothing happens (no active search)

    @pytest.mark.asyncio
    async def test_new_search_after_file_switch(self):
        """Should be able to start new search after file switch.

        The raccoon can sniff for new treasures in the new spot!

        Expected: New search works independently
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="search1.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'TODO in first')]
                )]
            ),
            DiffFile(
                file_path="search2.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'FIXME in second'),
                        ('+', 'FIXME again'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "TODO" in search1.py

            # TODO: Switch to search2.py

            # TODO: Search for "FIXME"

            # Expected: 2 matches for FIXME in search2.py
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 2


class TestHelpScrollable:
    """Tests for scrollable help overlay - Edge Case 6."""

    @pytest.mark.asyncio
    async def test_help_overlay_scrollable_in_small_terminal(self):
        """Help overlay should be scrollable in small terminals.

        The treasure map scrolls when the viewport is tiny!

        User workflow:
        1. Resize terminal to small height (simulated)
        2. Press '?' to open help
        3. Use arrow keys or PgUp/PgDown to scroll

        Expected:
        - Help content is scrollable
        - All keybindings accessible
        - Scroll indicator visible (if implemented)
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="small_term.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[('+', 'test')]
                )]
            ),
        ])

        # TODO: Simulate small terminal size (10 lines height)
        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '?' to show help

            # Expected: Help overlay has scroll capability
            # help_overlay = app.query_one("#help-overlay")
            # assert help_overlay.can_scroll_vertically

            # TODO: Scroll down through help content

            # Expected: Can access all keybindings via scrolling

    @pytest.mark.asyncio
    async def test_help_scrollable_shows_all_content(self):
        """All help content should be accessible via scrolling.

        No treasure map entries are hidden!

        Expected: All 15+ keybindings reachable
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="full_content.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'a')])]
            ),
        ])

        # TODO: Simulate very small terminal
        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Open help
            # TODO: Scroll to bottom

            # Expected: Last keybinding visible
            # help_overlay = app.query_one("#help-overlay")
            # # Verify "q - quit" or last entry is accessible


class TestEditDuringSelectMode:
    """Tests for edit during Select Mode - Edge Case 8."""

    @pytest.mark.asyncio
    async def test_edit_during_select_mode(self):
        """Pressing 'e' during Select Mode should have defined behavior.

        The raccoon tries to polish while marking territory!

        User workflow:
        1. Press 's' to enter Select Mode
        2. Begin selecting a range
        3. Press 'e' while in Select Mode

        Expected (implementation-dependent):
        - Option A: Edit dialog appears if line has comment, Select Mode exits
        - Option B: 'e' is ignored while in Select Mode
        - Behavior is consistent and doesn't crash
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="select_edit.py",
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

            # Add comment to line 5
            target = CommentTarget(
                file_path="select_edit.py",
                line_number=5,
                line_range=None
            )
            comment = Comment(
                text="Existing comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Navigate to line 5
            # TODO: Press 's' to enter Select Mode
            # TODO: Press 'e' to attempt edit

            # Expected: Consistent behavior (no crash)
            # Either edit dialog appears or 'e' is ignored
            # Application state remains valid

    @pytest.mark.asyncio
    async def test_edit_exits_select_mode_cleanly(self):
        """If edit works in Select Mode, it should exit cleanly.

        The raccoon can switch from marking to polishing smoothly!

        Expected: Select Mode properly exited, no visual artifacts
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="clean_exit.py",
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

            # Add comment
            target = CommentTarget(
                file_path="clean_exit.py",
                line_number=3,
                line_range=None
            )
            comment = Comment(
                text="Test comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Enter Select Mode
            # TODO: Press 'e' on commented line

            # Expected: Select Mode indicators cleared
            # No selection highlighting remains


class TestSearchEdgeCases:
    """Additional search-related edge cases."""

    @pytest.mark.asyncio
    async def test_search_preserves_comments(self):
        """Search mode should not affect existing comments.

        The raccoon's sniffing doesn't disturb its cached treasures!

        Expected: Comments unchanged during/after search
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="preserve.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'TODO line'),
                        ('+', 'regular line'),
                        ('+', 'TODO again'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment
            target = CommentTarget(
                file_path="preserve.py",
                line_number=1,
                line_range=None
            )
            comment = Comment(
                text="My comment",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            initial_count = app.comment_store.count()

            # TODO: Search for "TODO"
            # TODO: Navigate matches with 'n'
            # TODO: Exit search with Esc

            # Expected: Comments unchanged
            assert app.comment_store.count() == initial_count
            comments = app.comment_store.get("preserve.py", 1)
            assert len(comments) == 1
            assert comments[0].text == "My comment"

    @pytest.mark.asyncio
    async def test_edit_comment_while_search_active(self):
        """Should be able to edit comment while search is active.

        The raccoon can polish a treasure while sniffing!

        Expected: Edit works, search state optionally preserved or exited
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="edit_search.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'TODO: comment on this'),
                        ('+', 'regular'),
                        ('+', 'TODO: another'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add comment to first TODO line
            target = CommentTarget(
                file_path="edit_search.py",
                line_number=1,
                line_range=None
            )
            comment = Comment(
                text="Original",
                target=target,
                timestamp=datetime.now(),
                comment_type=CommentType.LINE
            )
            app.comment_store.add(comment)

            # TODO: Search for "TODO" (2 matches, cursor on line 1)
            # TODO: Press 'e' to edit comment on line 1
            # TODO: Change to "Updated"

            # Expected: Comment updated
            # updated = app.comment_store.get("edit_search.py", 1)
            # assert updated[0].text == "Updated"
