"""Unit tests for DiffNavigation.

Tests the goat's nimble movement through diff hunks!
"""

import pytest
from unittest.mock import Mock

from racgoat.parser.models import DiffFile, DiffHunk
from racgoat.ui.widgets.diff_navigation import DiffNavigation
from racgoat.ui.models import ApplicationMode


class TestMoveUpAcrossHunks:
    """Test cursor movement across hunk boundaries."""

    def test_move_up_from_second_hunk_to_first_hunk(self):
        """Cursor should move from second hunk's first line to first hunk's last line.

        This tests the fix for the bug where prev_line was reset for each hunk,
        preventing navigation across hunk boundaries.

        Scenario:
        - Hunk 1: lines 4-10
        - Hunk 2: lines 19-25 (gap from 11-18)
        - Cursor at line 19
        - Press up → should move to line 10
        """
        # Setup: Mock scroll widget
        mock_scroll = Mock()
        nav = DiffNavigation(mock_scroll)

        # Create file with two hunks with a gap
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=3,
            removed_lines=1,
            hunks=[
                # First hunk: lines 4-10 (7 lines)
                DiffHunk(
                    old_start=4,
                    new_start=4,
                    lines=[
                        (' ', 'context line 4'),
                        (' ', 'context line 5'),
                        (' ', 'context line 6'),
                        ('+', 'added line at 7'),
                        (' ', 'context line 8'),
                        (' ', 'context line 9'),
                        (' ', 'context line 10'),
                    ]
                ),
                # Second hunk: lines 19-25 (gap from 11-18)
                DiffHunk(
                    old_start=18,
                    new_start=19,
                    lines=[
                        (' ', 'context line 19'),
                        (' ', 'context line 20'),
                        ('-', 'removed line'),
                        ('+', 'replaced line at 21'),
                        (' ', 'context line 22'),
                        ('+', 'added line at 23'),
                        (' ', 'context line 24'),
                    ]
                ),
            ]
        )

        # Action: Move up from line 19 (first line of second hunk)
        current_line = 19
        new_current, new_select = nav.move_up(
            file=diff_file,
            current_line=current_line,
            app_mode=ApplicationMode.NORMAL,
            select_end_line=None
        )

        # Verify: Cursor moved to line 10 (last line of first hunk)
        assert new_current == 10
        assert new_select is None

    def test_move_up_within_same_hunk(self):
        """Cursor should move up within the same hunk normally."""
        # Setup
        mock_scroll = Mock()
        nav = DiffNavigation(mock_scroll)

        diff_file = DiffFile(
            file_path="test.py",
            added_lines=2,
            removed_lines=0,
            hunks=[
                DiffHunk(
                    old_start=10,
                    new_start=10,
                    lines=[
                        (' ', 'line 10'),
                        ('+', 'line 11'),
                        ('+', 'line 12'),
                        (' ', 'line 13'),
                    ]
                ),
            ]
        )

        # Action: Move up from line 12
        new_current, _ = nav.move_up(
            file=diff_file,
            current_line=12,
            app_mode=ApplicationMode.NORMAL,
            select_end_line=None
        )

        # Verify: Moved to line 11
        assert new_current == 11

    def test_move_up_at_first_line_stays_put(self):
        """Cursor should stay at first line when already at top."""
        # Setup
        mock_scroll = Mock()
        nav = DiffNavigation(mock_scroll)

        diff_file = DiffFile(
            file_path="test.py",
            added_lines=1,
            removed_lines=0,
            hunks=[
                DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        (' ', 'line 2'),
                    ]
                ),
            ]
        )

        # Action: Move up from line 1 (first line)
        new_current, _ = nav.move_up(
            file=diff_file,
            current_line=1,
            app_mode=ApplicationMode.NORMAL,
            select_end_line=None
        )

        # Verify: Still at line 1
        assert new_current == 1


class TestMoveDownAcrossHunks:
    """Test cursor movement down across hunk boundaries."""

    def test_move_down_from_first_hunk_to_second_hunk(self):
        """Cursor should move from first hunk's last line to second hunk's first line."""
        # Setup
        mock_scroll = Mock()
        nav = DiffNavigation(mock_scroll)

        # Same two-hunk file as above
        diff_file = DiffFile(
            file_path="test.py",
            added_lines=3,
            removed_lines=1,
            hunks=[
                DiffHunk(
                    old_start=4,
                    new_start=4,
                    lines=[
                        (' ', 'context line 4'),
                        (' ', 'line 5'),
                        ('+', 'line 6'),
                        (' ', 'line 7'),
                    ]
                ),
                DiffHunk(
                    old_start=18,
                    new_start=19,
                    lines=[
                        (' ', 'line 19'),
                        ('+', 'line 20'),
                    ]
                ),
            ]
        )

        # Action: Move down from line 7 (last line of first hunk)
        new_current, _ = nav.move_down(
            file=diff_file,
            current_line=7,
            app_mode=ApplicationMode.NORMAL,
            select_end_line=None
        )

        # Verify: Moved to line 19 (first line of second hunk)
        assert new_current == 19
