"""TwoPaneLayout widget - the container holding both panes.

Like a raccoon's den with two rooms - one for organizing, one for examining!
"""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.binding import Binding

from racgoat.parser.models import DiffSummary
from racgoat.ui.widgets.files_pane import FilesPane
from racgoat.ui.widgets.diff_pane import DiffPane

if TYPE_CHECKING:
    from racgoat.di import ServiceContainer


class TwoPaneLayout(Horizontal):
    """Container for two-pane diff viewer layout.

    Manages the side-by-side Files Pane and Diff Pane, with focus cycling
    and event forwarding. The raccoon's organized workspace!

    Attributes:
        diff_summary: The parsed diff data to display
        services: Optional service container for dependency injection
    """

    BINDINGS = [
        Binding("tab", "focus_next", "Switch pane", show=True),
    ]

    DEFAULT_CSS = """
    TwoPaneLayout {
        height: 100%;
        layout: horizontal;
    }
    """

    def __init__(
        self,
        diff_summary: DiffSummary,
        *,
        services: "ServiceContainer | None" = None,
        comment_store: "ServiceContainer | None" = None,  # Deprecated: backward compatibility
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize two-pane layout.

        Args:
            diff_summary: Parsed diff data
            services: Optional service container for dependency injection
            comment_store: Deprecated - use services instead (backward compatibility only)
            name: Widget name (optional)
            id: Widget ID (optional, default: "two-pane-layout")
        """
        super().__init__(name=name, id=id or "two-pane-layout")
        self.diff_summary = diff_summary
        self.services = services
        # Backward compatibility: support old comment_store parameter
        self._comment_store_legacy = comment_store if comment_store is not None else None
        self._files_pane: FilesPane | None = None
        self._diff_pane: DiffPane | None = None

    def compose(self) -> ComposeResult:
        """Compose the two-pane layout.

        Creates Files Pane on left, Diff Pane on right.
        """
        self._files_pane = FilesPane(self.diff_summary, id="files-pane")

        # Get comment_store from services or legacy parameter
        comment_store = (
            self.services.comment_store if self.services
            else self._comment_store_legacy
        )
        self._diff_pane = DiffPane(comment_store=comment_store, id="diff-pane")

        yield self._files_pane
        yield self._diff_pane

    def on_mount(self) -> None:
        """Set initial focus to Files Pane.

        The raccoon starts by looking at the file list!
        """
        if self._files_pane:
            self._files_pane.focus()

    def on_files_pane_file_selected(self, message: FilesPane.FileSelected) -> None:
        """Handle FileSelected event from Files Pane.

        When the raccoon picks a treasure, show it in the Diff Pane!

        Args:
            message: FileSelected message with the selected file
        """
        if self._diff_pane:
            self._diff_pane.display_file(message.file)

    def action_focus_next(self) -> None:
        """Cycle focus between panes (Tab key handler).

        The goat hops from one pane to the other!
        """
        if not self._files_pane or not self._diff_pane:
            return

        # Check which pane currently has focus
        # Note: FilesPane delegates focus to its ListView, so we check focus-within
        focused = self.app.focused

        # Check if focus is within files pane (ListView child)
        if focused and self._files_pane in focused.ancestors:
            # Files pane has focus -> switch to Diff pane
            self._diff_pane.focus()
        elif self._diff_pane.has_focus:
            # Diff pane has focus -> switch to Files pane
            self._files_pane.focus()
        else:
            # Default to Files Pane if neither focused
            self._files_pane.focus()

    @property
    def focused_pane(self) -> str:
        """Get ID of currently focused pane.

        Returns:
            "files-pane" or "diff-pane"
        """
        focused = self.app.focused
        if focused == self._files_pane:
            return "files-pane"
        elif focused == self._diff_pane:
            return "diff-pane"
        else:
            # Default if neither focused (shouldn't happen)
            return "diff-pane"
