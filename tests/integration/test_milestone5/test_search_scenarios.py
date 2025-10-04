"""Integration tests for search functionality in the diff pane.

These tests validate that the raccoon can quickly sniff out patterns
in the code treasure!

Covers:
- AS-003: Initiate search mode
- AS-004: Execute search with highlights
- AS-005: Navigate to next match
- AS-006: Navigate to previous match
- Edge Case 4: Exit search clears highlights
- Edge Case 7: Search wraps around
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestSearchInitiation:
    """Tests for initiating search mode - AS-003."""

    @pytest.mark.asyncio
    async def test_initiate_search_mode(self):
        """Pressing '/' should activate search mode in diff pane.

        The raccoon's nose twitches, ready to sniff out treasures!

        User workflow:
        1. Navigate to Diff Pane (Tab if needed)
        2. Press '/' to initiate search

        Expected:
        - Search input field appears
        - Search input has focus
        - Status bar shows search keybindings
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="search_target.py",
                added_lines=30,
                removed_lines=5,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def function_one():'),
                        ('+', '    return TODO'),
                        ('+', 'def function_two():'),
                        ('+', '    # TODO: implement'),
                        ('+', '    return None'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Focus diff pane
            # TODO: Press '/' to initiate search

            # Expected: Search mode activated
            # search_input = app.query_one("#search-input")
            # assert search_input is not None
            # assert search_input.has_focus
            #
            # status_bar = app.query_one("#status-bar")
            # status_text = status_bar.render_str()
            # assert "Enter" in status_text or "search" in status_text.lower()

    @pytest.mark.asyncio
    async def test_search_input_accepts_text(self):
        """Search input should accept typed text.

        The raccoon types out the scent of the treasure!

        Expected: Can type search query in input field
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="text_input.py",
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

            # TODO: Initiate search with '/'
            # TODO: Type "TODO" into search input

            # Expected: Search query captured
            # search_input = app.query_one("#search-input")
            # assert search_input.value == "TODO"


class TestSearchExecution:
    """Tests for executing search and highlighting matches - AS-004."""

    @pytest.mark.asyncio
    async def test_search_highlights_all_matches(self):
        """Executing search should highlight all matches in current file.

        The raccoon marks every shiny treasure it sniffs out!

        User workflow:
        1. Press '/' to enter search
        2. Type "TODO"
        3. Press Enter to execute

        Expected:
        - All "TODO" instances highlighted
        - Cursor jumps to first match
        - Match counter shows "1/5" (if 5 matches)
        - Current match visually distinguished
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="todos.py",
                added_lines=20,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', '# TODO: fix this'),
                        ('+', 'def function():'),
                        ('+', '    # TODO: implement'),
                        ('+', '    pass'),
                        ('+', ''),
                        ('+', '# TODO: refactor'),
                        ('+', 'def another():'),
                        ('+', '    return TODO'),  # Variable named TODO
                        ('+', ''),
                        ('+', '# TODO: test this'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Press '/' to search
            # TODO: Type "TODO"
            # TODO: Press Enter

            # Expected: All 5 TODO instances highlighted
            # search_state = app.diff_pane.search_state
            # assert search_state is not None
            # assert search_state.total_matches == 5
            # assert search_state.current_match_index == 0  # First match
            #
            # # Cursor should be on first match (line 1)
            # assert app.diff_pane.cursor_line == 1
            #
            # # Match counter in status bar
            # status_bar = app.query_one("#status-bar")
            # assert "1/5" in status_bar.render_str()

    @pytest.mark.asyncio
    async def test_search_case_sensitive(self):
        """Search should be case-sensitive by default.

        The raccoon's nose is precise - TODO and todo smell different!

        Expected: Only exact case matches highlighted
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="case_test.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', '# TODO: uppercase'),
                        ('+', '# todo: lowercase'),
                        ('+', '# Todo: titlecase'),
                        ('+', '# TODO: another'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "TODO"

            # Expected: Only 2 matches (lines 1 and 4), not "todo" or "Todo"
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 2

    @pytest.mark.asyncio
    async def test_search_scrolls_to_first_match(self):
        """First match should be scrolled into view.

        The raccoon scurries to the first treasure!

        Expected: Viewport scrolls to show first match
        """
        # Create large file where first match is far down
        lines = [('+', f'line{i}') for i in range(1, 101)]
        lines[49] = ('+', 'FINDME: first match at line 50')
        lines[74] = ('+', 'FINDME: second match at line 75')

        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="large_file.py",
                added_lines=100,
                removed_lines=0,
                hunks=[DiffHunk(old_start=1, new_start=1, lines=lines)]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "FINDME"

            # Expected: Cursor at line 50, viewport scrolled to show it
            # assert app.diff_pane.cursor_line == 50
            # assert app.diff_pane.is_line_visible(50)


class TestSearchNavigation:
    """Tests for navigating between search matches - AS-005, AS-006."""

    @pytest.mark.asyncio
    async def test_navigate_next_match(self):
        """Pressing 'n' should jump to next match.

        The raccoon scurries to the next shiny treasure!

        User workflow:
        1. Execute search with multiple matches
        2. Press 'n' to go to next match
        3. Press 'n' again

        Expected:
        - Cursor moves to next match
        - Match counter updates: "2/7", then "3/7"
        - Current match visually distinguished
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="multi_match.py",
                added_lines=20,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'return 1'),  # Line 1
                        ('+', 'x = 2'),
                        ('+', 'return 3'),  # Line 3
                        ('+', 'y = 4'),
                        ('+', 'return 5'),  # Line 5
                        ('+', 'z = 6'),
                        ('+', 'return 7'),  # Line 7
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "return" (should find 4 matches)
            # TODO: Press 'n' to go to second match
            # TODO: Press 'n' to go to third match

            # Expected: At third match (line 5)
            # search_state = app.diff_pane.search_state
            # assert search_state.current_match_index == 2  # 0-indexed
            # assert app.diff_pane.cursor_line == 5
            #
            # status_bar = app.query_one("#status-bar")
            # assert "3/4" in status_bar.render_str()

    @pytest.mark.asyncio
    async def test_navigate_previous_match(self):
        """Pressing 'N' (Shift+n) should jump to previous match.

        The raccoon backtracks to the previous treasure!

        User workflow:
        1. Execute search with multiple matches
        2. Navigate to third match with 'n' twice
        3. Press 'N' to go back

        Expected:
        - Cursor moves to previous match
        - Match counter decrements: "2/7"
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="backward.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def func1():'),  # Line 1
                        ('+', '    pass'),
                        ('+', 'def func2():'),  # Line 3
                        ('+', '    pass'),
                        ('+', 'def func3():'),  # Line 5
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "def" (3 matches)
            # TODO: Press 'n' twice to reach match 3
            # TODO: Press 'N' to go back to match 2

            # Expected: At second match (line 3)
            # search_state = app.diff_pane.search_state
            # assert search_state.current_match_index == 1
            # assert app.diff_pane.cursor_line == 3

    @pytest.mark.asyncio
    async def test_search_navigation_wraps_around(self):
        """Navigation should wrap from last to first and vice versa.

        The raccoon's treasure hunt goes in circles!

        User workflow:
        1. Search with 3 matches
        2. Navigate to third match (3/3)
        3. Press 'n' to wrap to first

        Expected: Wraps to match 1/3

        Also test:
        4. Press 'N' at first match wraps to last
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="wrap.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'MATCH here'),   # Line 1
                        ('+', 'no match'),
                        ('+', 'MATCH again'),  # Line 3
                        ('+', 'no match'),
                        ('+', 'MATCH final'),  # Line 5
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "MATCH" (3 matches)
            # TODO: Press 'n' twice to reach match 3 (line 5)
            # TODO: Press 'n' again to wrap around

            # Expected: Wraps to first match (line 1)
            # search_state = app.diff_pane.search_state
            # assert search_state.current_match_index == 0
            # assert app.diff_pane.cursor_line == 1
            # assert "1/3" in app.query_one("#status-bar").render_str()

            # TODO: Press 'N' at first match

            # Expected: Wraps to last match (line 5)
            # search_state = app.diff_pane.search_state
            # assert search_state.current_match_index == 2
            # assert app.diff_pane.cursor_line == 5
            # assert "3/3" in app.query_one("#status-bar").render_str()


class TestExitSearch:
    """Tests for exiting search mode - Edge Case 4."""

    @pytest.mark.asyncio
    async def test_exit_search_clears_highlights(self):
        """Pressing Esc should clear all search highlights.

        The raccoon stops sniffing and all the treasure marks vanish!

        User workflow:
        1. Execute search with matches highlighted
        2. Press Esc to exit search mode

        Expected:
        - All highlights cleared
        - Search query cleared
        - Status bar returns to normal
        - Cursor position unchanged
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="exit_search.py",
                added_lines=10,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'find this'),
                        ('+', 'and this'),
                        ('+', 'find again'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "find" (2 matches)
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 2

            # TODO: Press Esc to exit search

            # Expected: Search state cleared
            # search_state = app.diff_pane.search_state
            # assert search_state is None or search_state.total_matches == 0
            #
            # # No match counter in status bar
            # status_bar = app.query_one("#status-bar")
            # assert "/matches" not in status_bar.render_str().lower()
            #
            # # Normal keybindings shown
            # assert "a - " in status_bar.render_str() or "Add comment" in status_bar.render_str()

    @pytest.mark.asyncio
    async def test_exit_search_before_execution(self):
        """Pressing Esc while typing query should cancel search.

        The raccoon changes its mind before sniffing!

        Expected: Search input closes, no search executed
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="cancel_query.py",
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

            # TODO: Press '/' to initiate search
            # TODO: Type partial query "TE"
            # TODO: Press Esc before Enter

            # Expected: No search executed, input closed
            # search_state = app.diff_pane.search_state
            # assert search_state is None or search_state.total_matches == 0


class TestSearchEdgeCases:
    """Additional search edge cases."""

    @pytest.mark.asyncio
    async def test_search_with_regex_special_chars(self):
        """Search should handle regex special characters literally.

        The raccoon searches for the exact symbols, not patterns!

        Expected: Characters like . * + ? should be literal
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="special.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'price = 3.99'),
                        ('+', 'total = 3 * 99'),
                        ('+', 'regex = r".*"'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # TODO: Search for "3.99"
            # Expected: Only matches "3.99", not "3*99" or other variants
            # search_state = app.diff_pane.search_state
            # assert search_state.total_matches == 1

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Submitting empty search query should be a no-op.

        The raccoon can't sniff nothing!

        Expected: No search executed, search mode remains active
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="empty.py",
                added_lines=3,
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

            # TODO: Press '/' to search
            # TODO: Press Enter without typing

            # Expected: No matches, search remains active
            # search_state = app.diff_pane.search_state
            # assert search_state is None or search_state.total_matches == 0
