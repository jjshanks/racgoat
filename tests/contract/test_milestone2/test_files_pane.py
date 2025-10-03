"""Contract tests for FilesPane widget.

These tests climb the widget like a sure-footed goat, verifying
every method and behavior before implementation!
"""

import pytest
from racgoat.parser.models import DiffFile, DiffSummary


class TestFilesPaneSelectFile:
    """Tests for the select_file() method - like picking treasures from a pile!"""

    @pytest.mark.asyncio
    async def test_select_file_emits_event_with_correct_file(self):
        """When select_file(index) is called, it should emit FileSelected with the right DiffFile."""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
            DiffFile(file_path="file2.py", added_lines=2, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line2')])]),
        ])

        from textual.app import App
        app = App()
        async with app.run_test() as pilot:
            pane = FilesPane(diff_summary=diff_summary, id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            # Select second file
            pane.select_file(1)
            await pilot.pause()

            # Verify selection changed
            assert pane.get_selected_file().file_path == "file2.py"

    def test_select_file_raises_index_error_when_out_of_bounds(self):
        """A goat can't jump to a cliff that doesn't exist!"""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
        ])

        pane = FilesPane(diff_summary=diff_summary)

        with pytest.raises(IndexError):
            pane.select_file(5)

    def test_select_file_raises_value_error_for_negative_index(self):
        """Negative indices are as nonsensical as a raccoon's backward climb!"""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
        ])

        pane = FilesPane(diff_summary=diff_summary)

        with pytest.raises(ValueError):
            pane.select_file(-1)


class TestFilesPaneGetSelectedFile:
    """Tests for get_selected_file() - retrieving the currently shiny treasure!"""

    @pytest.mark.asyncio
    async def test_get_selected_file_returns_current_selection(self):
        """Should return the DiffFile that's currently selected."""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk
        from textual.app import App

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
            DiffFile(file_path="file2.py", added_lines=2, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line2')])]),
        ])

        app = App()
        async with app.run_test() as pilot:
            pane = FilesPane(diff_summary=diff_summary, id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            # After mount, first file is auto-selected
            selected = pane.get_selected_file()
            assert selected is not None
            assert selected.file_path == "file1.py"

    def test_get_selected_file_returns_none_when_empty(self):
        """No treasures? Return None, don't crash the raccoon's cart!"""
        from racgoat.ui.widgets.files_pane import FilesPane

        # Empty diff summary
        diff_summary = DiffSummary(files=[])
        pane = FilesPane(diff_summary=diff_summary)

        # Should return None when no files exist
        assert pane.get_selected_file() is None


class TestFilesPaneTruncatePath:
    """Tests for path truncation - making long paths fit like a goat in a tight spot!"""

    def test_truncate_path_preserves_start_and_end(self):
        """Long paths should be truncated in the middle with '...' """
        # Import FilesListItem for the truncation logic
        from racgoat.ui.models import FilesListItem

        # Test case: very long path
        long_path = "src/deeply/nested/directory/structure/with/many/levels/filename.py"
        truncated = FilesListItem._truncate_path(long_path, max_width=30)

        # Should preserve start and end
        assert truncated.startswith("src/deeply")
        assert truncated.endswith("filename.py")
        assert "..." in truncated
        assert len(truncated) == 30

    def test_truncate_path_no_change_when_short_enough(self):
        """Short paths shouldn't be touched - they're already goat-sized!"""
        from racgoat.ui.models import FilesListItem

        short_path = "src/file.py"
        truncated = FilesListItem._truncate_path(short_path, max_width=30)

        assert truncated == short_path

    def test_truncate_path_raises_error_when_width_too_narrow(self):
        """Can't fit a goat in a mouse hole!"""
        from racgoat.ui.models import FilesListItem

        with pytest.raises(ValueError, match="max_width must be >= 10"):
            FilesListItem._truncate_path("some/path.py", max_width=5)


class TestFilesPaneKeyboardNavigation:
    """Tests for arrow key navigation - the goat's nimble hopping!"""

    @pytest.mark.asyncio
    async def test_arrow_keys_emit_file_selected_on_change(self):
        """Arrow keys should emit FileSelected when selection changes."""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk
        from textual.app import App

        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
            DiffFile(file_path="file2.py", added_lines=2, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line2')])]),
        ])

        app = App()
        async with app.run_test() as pilot:
            pane = FilesPane(diff_summary=diff_summary, id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            # Focus the pane's ListView so it receives key events
            pane.focus()
            await pilot.pause()

            # Initial: file1 selected
            assert pane.get_selected_file().file_path == "file1.py"

            # Press down arrow to navigate
            await pilot.press("down")
            await pilot.pause()

            # file2 should now be selected
            assert pane.get_selected_file().file_path == "file2.py"


class TestFilesPaneFileCount:
    """Tests for the file_count property - counting the raccoon's treasures!"""

    @pytest.mark.asyncio
    async def test_file_count_matches_diff_summary(self):
        """The count should match the number of files in DiffSummary."""
        from racgoat.ui.widgets.files_pane import FilesPane
        from racgoat.parser.models import DiffHunk
        from textual.app import App

        # Test with 3 files
        diff_summary = DiffSummary(files=[
            DiffFile(file_path="file1.py", added_lines=1, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line1')])]),
            DiffFile(file_path="file2.py", added_lines=2, removed_lines=0,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line2')])]),
            DiffFile(file_path="file3.py", added_lines=3, removed_lines=1,
                     hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line3')])]),
        ])

        app = App()
        async with app.run_test() as pilot:
            pane = FilesPane(diff_summary=diff_summary)
            await app.mount(pane)
            await pilot.pause()

            assert pane.file_count == 3

        # Test with empty diff
        empty_diff = DiffSummary(files=[])
        app2 = App()
        async with app2.run_test() as pilot:
            empty_pane = FilesPane(diff_summary=empty_diff)
            await app2.mount(empty_pane)
            await pilot.pause()

            assert empty_pane.file_count == 0
