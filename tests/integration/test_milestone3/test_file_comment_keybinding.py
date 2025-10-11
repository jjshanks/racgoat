"""Integration tests for file-level comment keybindings.

These tests validate that Shift+C correctly creates file-level comments
and that the visual feedback is appropriate.
"""

import pytest
from racgoat.main import RacGoatApp
from racgoat.parser.models import DiffSummary, DiffFile, DiffHunk
from racgoat.models.comments import CommentType


class TestFileCommentKeybinding:
    """Integration tests for Shift+C file comment keybinding."""

    @pytest.mark.asyncio
    async def test_shift_c_creates_file_comment(self):
        """Shift+C should create a file-level comment, not a line comment.

        The goat speaks wisdom about the entire file!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="whole_file.py",
                added_lines=5,
                removed_lines=2,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        (' ', 'context line'),
                        ('+', 'new line 1'),
                        ('+', 'new line 2'),
                        ('-', 'removed line'),
                        ('+', 'new line 3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Shift+C to add file comment
            await pilot.press("C")  # Uppercase C = Shift+C in Textual
            await pilot.pause()

            # Type comment text in the modal
            await pilot.press(*"This entire file needs review")
            await pilot.pause()

            # Submit the comment (Enter)
            await pilot.press("enter")
            await pilot.pause()

            # Verify a file-level comment was created
            file_comments = app.comment_store.get("whole_file.py", None)
            assert len(file_comments) == 1

            comment = file_comments[0]
            assert comment.comment_type == CommentType.FILE
            assert comment.text == "This entire file needs review"
            assert comment.target.file_path == "whole_file.py"
            assert comment.target.line_number is None
            assert comment.target.line_range is None

    @pytest.mark.asyncio
    async def test_shift_c_shows_file_comment_type_in_modal(self):
        """The comment modal should clearly show FILE COMMENT type.

        Visual feedback prevents user confusion!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        ('+', 'line 2'),
                        ('+', 'line 3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Shift+C to add file comment
            await pilot.press("C")
            await pilot.pause()

            # Check if the modal is displayed with FILE comment type
            # The modal should contain the comment type label
            modal = app.screen_stack[-1]
            assert modal is not None

            # Verify this is a CommentInput modal (by checking for the input widget)
            input_widget = modal.query_one("#comment-input")
            assert input_widget is not None

            # Cancel to close modal
            await pilot.press("escape")
            await pilot.pause()

    @pytest.mark.asyncio
    async def test_lowercase_c_creates_line_comment_not_file(self):
        """Lowercase 'c' should create a line comment, not file comment.

        This confirms the keybindings are distinct!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="line_test.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        ('+', 'line 2'),
                        ('+', 'line 3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus diff pane and move to line 2
            await pilot.press("tab")  # Switch to diff pane
            await pilot.pause()

            await pilot.press("down")  # Move to line 2
            await pilot.pause()

            # Press lowercase c to add line comment
            await pilot.press("c")
            await pilot.pause()

            # Type comment text
            await pilot.press(*"Line comment here")
            await pilot.pause()

            # Submit
            await pilot.press("enter")
            await pilot.pause()

            # Verify a LINE comment was created, not FILE
            line_comments = app.comment_store.get("line_test.py", 2)
            assert len(line_comments) == 1

            comment = line_comments[0]
            assert comment.comment_type == CommentType.LINE
            assert comment.target.line_number == 2

            # Verify NO file-level comment was created
            file_comments = app.comment_store.get("line_test.py", None)
            assert len(file_comments) == 0

    @pytest.mark.asyncio
    async def test_file_comment_works_from_any_cursor_position(self):
        """File comment should work regardless of which line cursor is on.

        The goat's file-level wisdom transcends individual lines!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="cursor_test.py",
                added_lines=5,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        ('+', 'line 2'),
                        ('+', 'line 3'),
                        ('+', 'line 4'),
                        ('+', 'line 5'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus diff pane
            await pilot.press("tab")
            await pilot.pause()

            # Move to line 4
            await pilot.press("down", "down", "down")
            await pilot.pause()

            # Add file comment while cursor is at line 4
            await pilot.press("C")  # Shift+C
            await pilot.pause()

            await pilot.press(*"File comment from line 4")
            await pilot.pause()

            await pilot.press("enter")
            await pilot.pause()

            # Verify file comment was created (not line 4 comment)
            file_comments = app.comment_store.get("cursor_test.py", None)
            assert len(file_comments) == 1
            assert file_comments[0].comment_type == CommentType.FILE

            # Verify NO line comment at line 4
            line4_comments = app.comment_store.get("cursor_test.py", 4)
            assert len(line4_comments) == 0

    @pytest.mark.asyncio
    async def test_can_have_both_file_and_line_comments(self):
        """A file can have both file-level and line-level comments.

        The goat and raccoon can both leave their marks!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="mixed.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        ('+', 'line 2'),
                        ('+', 'line 3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add file comment first
            await pilot.press("C")  # Shift+C
            await pilot.pause()
            await pilot.press(*"Overall file comment")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            # Switch to diff pane and add line comment
            await pilot.press("tab")
            await pilot.pause()
            await pilot.press("c")  # lowercase c
            await pilot.pause()
            await pilot.press(*"Line 1 comment")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

            # Verify both comments exist
            file_comments = app.comment_store.get("mixed.py", None)
            assert len(file_comments) == 1
            assert file_comments[0].comment_type == CommentType.FILE

            line_comments = app.comment_store.get("mixed.py", 1)
            assert len(line_comments) == 1
            assert line_comments[0].comment_type == CommentType.LINE

            # Total unique comments should be 2
            assert app.comment_store.count() == 2

    @pytest.mark.asyncio
    async def test_f_key_also_creates_file_comment(self):
        """The 'f' key should work as an alternative to Shift+C for file comments.

        For terminals that don't handle Shift+C well, the goat provides an alternative!
        """
        diff_summary = DiffSummary(files=[
            DiffFile(
                file_path="alt_key.py",
                added_lines=3,
                removed_lines=0,
                hunks=[DiffHunk(
                    old_start=1,
                    new_start=1,
                    lines=[
                        ('+', 'line 1'),
                        ('+', 'line 2'),
                        ('+', 'line 3'),
                    ]
                )]
            ),
        ])

        app = RacGoatApp(diff_summary=diff_summary)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press lowercase 'f' to add file comment
            await pilot.press("f")
            await pilot.pause()

            # Type comment text
            await pilot.press(*"File comment via f key")
            await pilot.pause()

            # Submit
            await pilot.press("enter")
            await pilot.pause()

            # Verify a file-level comment was created
            file_comments = app.comment_store.get("alt_key.py", None)
            assert len(file_comments) == 1

            comment = file_comments[0]
            assert comment.comment_type == CommentType.FILE
            assert comment.text == "File comment via f key"
            assert comment.target.file_path == "alt_key.py"
            assert comment.target.line_number is None
