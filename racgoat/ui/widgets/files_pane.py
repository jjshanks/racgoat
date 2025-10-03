"""FilesPane widget - the raccoon's organized file list.

This pane shows all the changed files, letting the user navigate
through them like a goat hopping from rock to rock!
"""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import ListItem, ListView, Label

from racgoat.parser.models import DiffFile, DiffSummary
from racgoat.ui.models import FilesListItem


class FilesPane(VerticalScroll):
    """Files pane widget for displaying changed files list.

    This widget displays a scrollable list of changed files with their
    line count statistics. Like a raccoon sorting through treasures!

    Attributes:
        diff_summary: The parsed diff data containing all files
    """

    can_focus = False
    DEFAULT_CSS = """
    FilesPane {
        width: 30%;
        border: solid $accent;
    }

    FilesPane:focus-within {
        border: solid $primary;
    }

    FilesPane ListView {
        height: 100%;
    }

    FilesPane .file-item {
        height: 1;
    }

    FilesPane .file-item.-selected {
        background: $boost;
    }
    """

    class FileSelected(Message):
        """Message emitted when a file is selected.

        The raccoon has chosen a treasure to examine!

        Attributes:
            file: The DiffFile that was selected
        """

        def __init__(self, file: DiffFile) -> None:
            super().__init__()
            self.file = file

    def __init__(
        self,
        diff_summary: DiffSummary,
        *,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize files pane with diff data.

        Args:
            diff_summary: Parsed diff data containing file list
            name: Widget name (optional)
            id: Widget ID (optional, default: "files-pane")

        Raises:
            ValueError: If diff_summary is None
        """
        super().__init__(name=name, id=id or "files-pane")
        if diff_summary is None:
            raise ValueError("diff_summary cannot be None")

        self.diff_summary = diff_summary
        self._list_view: ListView | None = None
        self._file_items: list[FilesListItem] = []

    def compose(self) -> ComposeResult:
        """Compose the files list view.

        Creates a ListView with one item per file, formatted with stats.
        """
        # Create FilesListItem for each file
        # For now, don't truncate (will be handled by ListView width)
        self._file_items = [
            FilesListItem.from_file(f, max_width=None)
            for f in self.diff_summary.files
        ]

        # Create ListView and immediately populate it with items
        self._list_view = ListView(*[
            ListItem(Label(item.display_text), id=f"file-{idx}", classes="file-item")
            for idx, item in enumerate(self._file_items)
        ], id="files-list")

        yield self._list_view

    def on_mount(self) -> None:
        """Select first file after mounting.

        The raccoon picks the first treasure!
        """
        if self._list_view and self._file_items:
            # Select first item
            self._list_view.index = 0
            # Emit FileSelected for first file
            self.post_message(self.FileSelected(self._file_items[0].file))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle file selection changes.

        When the raccoon picks a new treasure, tell everyone!

        Args:
            event: ListView highlight event
        """
        if self._list_view and self._file_items:
            index = self._list_view.index
            if 0 <= index < len(self._file_items):
                selected_file = self._file_items[index].file
                self.post_message(self.FileSelected(selected_file))

    def select_file(self, index: int) -> None:
        """Programmatically select a file by index.

        Args:
            index: Zero-based file index

        Raises:
            IndexError: If index out of bounds
            ValueError: If index < 0
        """
        if index < 0:
            raise ValueError(f"Index must be >= 0, got {index}")

        if index >= len(self._file_items):
            raise IndexError(f"Index {index} out of bounds (total files: {len(self._file_items)})")

        if self._list_view:
            self._list_view.index = index

    def get_selected_file(self) -> DiffFile | None:
        """Get currently selected file.

        Returns:
            DiffFile if a file is selected, None if no selection

        """
        if not self._list_view:
            return None
        if not self._file_items:
            return None

        index = self._list_view.index
        if index is None or index < 0 or index >= len(self._file_items):
            return None

        return self._file_items[index].file

    @property
    def file_count(self) -> int:
        """Get count of files in pane.

        Returns:
            Number of files in diff_summary
        """
        return len(self._file_items)

    def focus(self, scroll_visible: bool = True) -> None:
        """Focus the files pane by focusing the ListView.

        Args:
            scroll_visible: Whether to scroll the widget into view
        """
        if self._list_view:
            self._list_view.focus(scroll_visible=scroll_visible)
        else:
            super().focus(scroll_visible=scroll_visible)

    @property
    def has_focus(self) -> bool:
        """Check if this pane or its ListView has focus.

        Returns:
            True if pane or ListView is focused
        """
        if self._list_view:
            return self._list_view.has_focus
        return super().has_focus
