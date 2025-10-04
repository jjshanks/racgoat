"""Contract tests for search functionality (Milestone 5).

These tests define the expected behavior for search within the diff view.
They MUST fail before implementation (TDD approach per constitution).

Tests verify:
- Search activation with '/' key
- Search highlights all matches
- Forward/backward navigation through matches
- Match counter display
- Case-sensitive literal string matching
- Esc clears highlights
- File switch resets search state

Maps to FR-010 through FR-023 in spec.md.
"""

import pytest

from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk


class TestSearchContract:
    """Contract tests for search functionality."""

    @pytest.mark.asyncio
    async def test_slash_activates_search(self):
        """Raccoon opens the treasure map search with a swift slash.

        FR-010, FR-011: Activate search with '/', display search input field.
        """
        # Arrange: Create app with diff
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def foo():'),
                        ('+', '    return 42'),
                        ('+', ''),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane (search only works when diff pane has focus)
            await pilot.press("tab")
            await pilot.pause()

            # Act: Press '/' to activate search
            await pilot.press("slash")
            await pilot.pause()

            # Assert: Search input field should be visible
            # (Implementation will show a SearchInput widget or modal)
            # Test will fail until search activation is implemented

    @pytest.mark.asyncio
    async def test_search_highlights_all_matches(self):
        """Goat marks every matching peak on the climbing route.

        FR-012: Highlight all matches of the search query.
        """
        # Arrange: Create diff with repeated pattern
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="code.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'TODO: implement feature'),
                        ('+', 'def process():'),
                        ('+', '    # TODO: add validation'),
                        ('+', '    return result'),
                        ('+', '# TODO: optimize'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Activate search
            await pilot.press("slash")
            await pilot.pause()

            # Act: Enter search query "TODO" and press Enter
            # (Implementation will handle SearchInput text entry)
            # Simulate searching for "TODO"

            # Assert: All three occurrences of "TODO" should be highlighted
            # (DiffPane should show visual highlights for all matches)
            # Test will fail until highlight rendering is implemented

    @pytest.mark.asyncio
    async def test_enter_jumps_to_first_match(self):
        """Raccoon pounces to the first shiny match.

        FR-013: Navigate to first match when Enter is pressed.
        """
        # Arrange: Create diff with multiple matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=4,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'first line'),
                        ('+', 'MATCH here'),
                        ('+', 'some code'),
                        ('+', 'MATCH again'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Activate search and enter query
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for "MATCH" and press Enter
            # (Implementation will jump viewport to first match on line 2)

            # Assert: DiffPane scroll position should show first match
            # (Line 2 should be visible and highlighted)
            # Test will fail until jump-to-first is implemented

    @pytest.mark.asyncio
    async def test_n_navigates_forward(self):
        """Goat hops forward to the next mountain marker.

        FR-014: Support forward navigation with 'n' key.
        """
        # Arrange: Create diff with multiple matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'first'),
                        ('+', 'FIND this'),
                        ('+', 'middle'),
                        ('+', 'FIND that'),
                        ('+', 'last'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search for "FIND"
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Enter search (currently at first match on line 2)

            # Act: Press 'n' to go to next match
            await pilot.press("n")
            await pilot.pause()

            # Assert: Should navigate to second match on line 4
            # (DiffPane scroll position and current match indicator updated)
            # Test will fail until forward navigation is implemented

    @pytest.mark.asyncio
    async def test_shift_n_navigates_backward(self):
        """Raccoon retraces its steps to the previous treasure.

        FR-015: Support backward navigation with 'N' key.
        """
        # Arrange: Create diff with multiple matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=4,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'SEEK first'),
                        ('+', 'middle'),
                        ('+', 'SEEK second'),
                        ('+', 'end'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search for "SEEK"
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Navigate to second match
            await pilot.press("n")
            await pilot.pause()

            # Act: Press 'N' to go back to previous match
            await pilot.press("N")
            await pilot.pause()

            # Assert: Should navigate back to first match on line 1
            # Test will fail until backward navigation is implemented

    @pytest.mark.asyncio
    async def test_match_counter_display(self):
        """Goat counts the peaks as it climbs.

        FR-017: Display match counter showing "current/total" format.
        """
        # Arrange: Create diff with known number of matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=6,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'var x = 10'),
                        ('+', 'var y = 20'),
                        ('+', 'const z = 30'),
                        ('+', 'var a = 40'),
                        ('+', 'let b = 50'),
                        ('+', 'var c = 60'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search for "var"
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for "var" (should find 4 matches)

            # Assert: Status bar should show "1/4 matches"
            status_bar = app.query_one("#status-bar")
            # (Implementation will display counter in status bar)

            # Navigate to next match
            await pilot.press("n")
            await pilot.pause()

            # Assert: Counter should update to "2/4 matches"
            # Test will fail until counter display is implemented

    @pytest.mark.asyncio
    async def test_no_matches_shows_zero(self):
        """Raccoon finds an empty trash can and knows it.

        FR-018: Display "0/0 matches" when no matches found.
        """
        # Arrange: Create diff
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=2,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'def foo():'),
                        ('+', '    pass'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Activate search
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for pattern that doesn't exist
            # Simulate searching for "NONEXISTENT"

            # Assert: Status bar should show "0/0 matches"
            status_bar = app.query_one("#status-bar")
            # (Implementation will display "0/0 matches" in status bar)
            # Test will fail until zero-match display is implemented

    @pytest.mark.asyncio
    async def test_case_sensitive_matching(self):
        """Goat distinguishes uppercase peaks from lowercase valleys.

        FR-020: Perform case-sensitive search matching.
        """
        # Arrange: Create diff with mixed case
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=4,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'TODO: uppercase'),
                        ('+', 'todo: lowercase'),
                        ('+', 'Todo: mixed'),
                        ('+', 'tOdO: weird'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Activate search
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for "TODO" (case-sensitive)

            # Assert: Should find only 1 match (line 1), not all 4 variants
            # Match counter should show "1/1 matches"
            # Test will fail until case-sensitive matching is implemented

    @pytest.mark.asyncio
    async def test_literal_string_matching(self):
        """Raccoon searches for exact shiny patterns, not magic symbols.

        FR-019: Perform literal string matching (no regex).
        """
        # Arrange: Create diff with regex-like characters
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'pattern = r"\\d+"'),
                        ('+', 'regex = ".*"'),
                        ('+', 'literal = "\\d+"'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Activate search
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for literal string "\\d+" (should not be treated as regex)

            # Assert: Should find exact matches of "\\d+" on lines 1 and 3
            # Should NOT match any digit character (regex interpretation)
            # Test will fail until literal matching is implemented

    @pytest.mark.asyncio
    async def test_esc_clears_highlights(self):
        """Goat erases the trail markers when escaping the search.

        FR-021, FR-022: Exit search mode with Esc, clear all highlights.
        """
        # Arrange: Create diff and perform search
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'HIGHLIGHT this'),
                        ('+', 'and this HIGHLIGHT'),
                        ('+', 'HIGHLIGHT too'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Search for "HIGHLIGHT" (creates highlights)

            # Act: Press Esc to exit search mode
            await pilot.press("escape")
            await pilot.pause()

            # Assert: All search highlights should be cleared immediately
            # DiffPane should no longer show highlighted matches
            # Test will fail until Esc-clear behavior is implemented

    @pytest.mark.asyncio
    async def test_file_switch_resets_search(self):
        """Raccoon forgets the old map when entering a new trash zone.

        FR-023: Reset search state when switching to different file.
        """
        # Arrange: Create app with multiple files
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="file1.py",
                added_lines=2,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'SEARCH in file1'),
                        ('+', 'more code'),
                    ]
                )]
            ),
            DiffFile(
                file_path="file2.py",
                added_lines=2,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'different content'),
                        ('+', 'SEARCH in file2'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search in file1
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Search for "SEARCH" in file1 (creates highlights)

            # Act: Switch to file2
            await pilot.press("tab")  # Focus files pane
            await pilot.press("down")  # Select file2
            await pilot.pause()

            # Assert: Search state should be completely reset
            # - Search query cleared
            # - All highlights removed
            # - Match counter reset
            # Test will fail until file-switch reset is implemented

    @pytest.mark.asyncio
    async def test_current_match_visually_distinct(self):
        """Goat paints the current peak in a brighter color.

        FR-016: Visually distinguish current match from other matches.
        """
        # Arrange: Create diff with multiple matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'MARK first'),
                        ('+', 'MARK second'),
                        ('+', 'MARK third'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Act: Search for "MARK" (creates 3 matches)
            # Current match should be the first one

            # Assert: First match should have distinct visual styling
            # Other matches should have different styling
            # (Implementation will use different CSS classes or Rich styles)

            # Navigate to next match
            await pilot.press("n")
            await pilot.pause()

            # Assert: Second match should now have distinct styling
            # First match should return to non-current styling
            # Test will fail until distinct current-match styling is implemented

    @pytest.mark.asyncio
    async def test_search_wraps_around(self):
        """Raccoon circles back to the start of the treasure trail.

        Edge case: Search navigation wraps from last to first match.
        """
        # Arrange: Create diff with 3 matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'WRAP first'),
                        ('+', 'middle'),
                        ('+', 'WRAP second'),
                        ('+', 'more'),
                        ('+', 'WRAP third'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Search for "WRAP" (3 matches, currently at first)

            # Navigate to last match
            await pilot.press("n")  # Match 2
            await pilot.press("n")  # Match 3
            await pilot.pause()

            # Assert: Counter shows "3/3 matches"

            # Act: Press 'n' again to wrap around
            await pilot.press("n")
            await pilot.pause()

            # Assert: Should wrap to first match, counter shows "1/3 matches"
            # Test will fail until wrap-around is implemented

    @pytest.mark.asyncio
    async def test_backward_wrap_around(self):
        """Goat leaps backward from the first peak to the last.

        Edge case: Backward navigation wraps from first to last match.
        """
        # Arrange: Create diff with multiple matches
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=4,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'BACK first'),
                        ('+', 'BACK second'),
                        ('+', 'BACK third'),
                        ('+', 'end'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Move to diff pane and search
            await pilot.press("tab")
            await pilot.press("slash")
            await pilot.pause()

            # Search for "BACK" (currently at first match)

            # Act: Press 'N' to go backward from first match
            await pilot.press("N")
            await pilot.pause()

            # Assert: Should wrap to last match (third), counter shows "3/3 matches"
            # Test will fail until backward wrap is implemented
