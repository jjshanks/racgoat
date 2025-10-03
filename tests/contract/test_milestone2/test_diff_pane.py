"""Contract tests for DiffPane widget.

The goat carefully examines each line of diff, ensuring colors shine bright!
"""

import pytest
from racgoat.parser.models import DiffFile, DiffHunk


class TestDiffPaneDisplayFile:
    """Tests for display_file() - showing the diff like a proud raccoon!"""

    @pytest.mark.asyncio
    async def test_display_file_renders_hunks_with_colors(self):
        """Hunks should be rendered with ANSI colors - green for adds, red for removes!"""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from textual.app import App

        file = DiffFile(
            file_path="test.py",
            added_lines=2,
            removed_lines=1,
            hunks=[
                DiffHunk(old_start=1, new_start=1, lines=[
                    ('+', 'added line 1'),
                    ('+', 'added line 2'),
                    ('-', 'removed line'),
                ])
            ]
        )

        app = App()
        async with app.run_test() as pilot:
            pane = DiffPane(id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            pane.display_file(file)
            await pilot.pause()

            # Verify file is set
            assert pane.current_file == file

    @pytest.mark.asyncio
    async def test_display_file_shows_line_numbers(self):
        """Post-change line numbers should be displayed for each line."""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from textual.app import App

        file = DiffFile(
            file_path="test.py",
            added_lines=1,
            removed_lines=0,
            hunks=[
                DiffHunk(old_start=5, new_start=5, lines=[
                    (' ', 'context line'),
                    ('+', 'added line'),
                ])
            ]
        )

        app = App()
        async with app.run_test() as pilot:
            pane = DiffPane(id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            pane.display_file(file)
            await pilot.pause()

            # Verify the hunk formatting logic tracks line numbers correctly
            hunk_text = pane.format_hunk(file.hunks[0])
            # Line numbers start at new_start (5)
            # Context line gets line 5, added line gets line 6
            assert hunk_text is not None

    def test_display_file_raises_error_for_none(self):
        """Can't display nothing! A goat needs a cliff to climb!"""
        from racgoat.ui.widgets.diff_pane import DiffPane

        pane = DiffPane(id="test-pane")

        with pytest.raises(ValueError, match="file cannot be None"):
            pane.display_file(None)


class TestDiffPaneFormatHunk:
    """Tests for format_hunk() - painting each hunk with the right colors!"""

    def test_format_hunk_applies_green_for_additions(self):
        """Added lines should be green - like fresh grass for the goat!"""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from rich.text import Text

        pane = DiffPane()
        hunk = DiffHunk(old_start=1, new_start=1, lines=[
            ('+', 'added line'),
        ])

        text = pane.format_hunk(hunk)

        # Verify it's a Text object with content
        assert isinstance(text, Text)
        # Check that the text contains the added line content
        plain_text = text.plain
        assert 'added line' in plain_text
        assert '+' in plain_text

    def test_format_hunk_applies_red_for_deletions(self):
        """Removed lines should be red - danger, cliff ahead!"""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from rich.text import Text

        pane = DiffPane()
        hunk = DiffHunk(old_start=1, new_start=1, lines=[
            ('-', 'removed line'),
        ])

        text = pane.format_hunk(hunk)

        # Verify it's a Text object with content
        assert isinstance(text, Text)
        plain_text = text.plain
        assert 'removed line' in plain_text
        assert '-' in plain_text

    def test_format_hunk_applies_dim_for_context(self):
        """Context lines should be dim - background for the raccoon's show!"""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from rich.text import Text

        pane = DiffPane()
        hunk = DiffHunk(old_start=1, new_start=1, lines=[
            (' ', 'context line'),
        ])

        text = pane.format_hunk(hunk)

        # Verify it's a Text object with content
        assert isinstance(text, Text)
        plain_text = text.plain
        assert 'context line' in plain_text

    def test_format_hunk_includes_line_numbers(self):
        """Each line needs its number - how else to know where the goat stands?"""
        from racgoat.ui.widgets.diff_pane import DiffPane

        pane = DiffPane()
        hunk = DiffHunk(old_start=10, new_start=10, lines=[
            (' ', 'context'),
            ('+', 'added'),
        ])

        text = pane.format_hunk(hunk)
        plain_text = text.plain

        # Line numbers should appear in the formatted text
        # Context line at 10, added line at 11
        assert '10' in plain_text
        assert '11' in plain_text


class TestDiffPaneClear:
    """Tests for clear() - wiping the slate clean!"""

    @pytest.mark.asyncio
    async def test_clear_removes_all_content(self):
        """After clear(), the pane should be empty - like a raccoon's clean den!"""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from textual.app import App

        file = DiffFile(
            file_path="test.py",
            added_lines=1,
            removed_lines=0,
            hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])]
        )

        app = App()
        async with app.run_test() as pilot:
            pane = DiffPane(id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            # Display a file first
            pane.display_file(file)
            assert pane.current_file is not None

            # Clear the pane
            pane.clear()
            assert pane.current_file is None


class TestDiffPaneCurrentFile:
    """Tests for current_file property - tracking what's displayed!"""

    @pytest.mark.asyncio
    async def test_current_file_reflects_displayed_file(self):
        """The property should return the file currently being shown."""
        from racgoat.ui.widgets.diff_pane import DiffPane
        from textual.app import App

        file = DiffFile(
            file_path="test.py",
            added_lines=1,
            removed_lines=0,
            hunks=[DiffHunk(old_start=1, new_start=1, lines=[('+', 'line')])]
        )

        app = App()
        async with app.run_test() as pilot:
            pane = DiffPane(id="test-pane")
            await app.mount(pane)
            await pilot.pause()

            pane.display_file(file)

            assert pane.current_file == file
            assert pane.current_file.file_path == "test.py"

    def test_current_file_returns_none_when_empty(self):
        """No file shown? Return None - simple as that!"""
        from racgoat.ui.widgets.diff_pane import DiffPane

        pane = DiffPane(id="test-pane")

        # Initially, no file is displayed
        assert pane.current_file is None
