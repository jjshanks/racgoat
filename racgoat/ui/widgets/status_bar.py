"""StatusBar widget - context-sensitive keybinding display.

This widget shows the appropriate keybindings based on current mode and focus state.
Like a raccoon's treasure map legend - always showing the way to the shinies!
"""

from textual.reactive import reactive
from textual.widgets import Static

from racgoat.ui.models import ApplicationMode, PaneFocusState


# Keybinding templates for each (mode, focus) combination
KEYBINDING_TEMPLATES = {
    (ApplicationMode.NORMAL, PaneFocusState.DIFF): "a: Add Comment | s: Select Range | c: Comment File | Tab: Switch | q: Quit",
    (ApplicationMode.NORMAL, PaneFocusState.FILES): "c: Comment File | ↑/↓: Navigate | Enter: Select | Tab: Switch | q: Quit",
    (ApplicationMode.SELECT, PaneFocusState.DIFF): "↑/↓: Expand Selection | Enter: Confirm | Esc: Cancel",
    (ApplicationMode.SELECT, PaneFocusState.FILES): "Exit Select Mode first (Esc) | q: Quit",  # Navigation blocked
}


class StatusBar(Static):
    """Status bar widget for displaying context-sensitive keybindings.

    The raccoon's cheat sheet - always reminding you which keys unlock
    which treasures in the current situation!

    This widget reactively watches the app's mode and focus state, updating
    the displayed keybindings automatically.

    Attributes:
        app_mode: Current application mode (NORMAL or SELECT)
        focus_state: Current pane focus (DIFF or FILES)
    """

    # Reactive properties - will trigger watch_* methods on change
    app_mode = reactive(ApplicationMode.NORMAL)
    focus_state = reactive(PaneFocusState.DIFF)

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, *, name: str | None = None, id: str | None = None) -> None:
        """Initialize status bar.

        Args:
            name: Widget name (optional)
            id: Widget ID (optional, default: "status-bar")
        """
        super().__init__("", name=name, id=id or "status-bar")
        self._render_keybindings()

    def watch_app_mode(self, new_mode: ApplicationMode) -> None:
        """React to mode changes.

        Args:
            new_mode: New application mode
        """
        self._render_keybindings()

    def watch_focus_state(self, new_focus: PaneFocusState) -> None:
        """React to focus changes.

        Args:
            new_focus: New focus state
        """
        self._render_keybindings()

    def _render_keybindings(self) -> None:
        """Render keybindings based on current mode and focus."""
        key = (self.app_mode, self.focus_state)
        keybindings = KEYBINDING_TEMPLATES.get(
            key,
            "Unknown state - press q to quit"
        )
        self.update(keybindings)
