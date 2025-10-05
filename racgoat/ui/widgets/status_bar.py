"""StatusBar widget - context-sensitive keybinding display.

This widget shows the appropriate keybindings based on current mode and focus state.
Like a raccoon's treasure map legend - always showing the way to the shinies!
"""

from textual.reactive import reactive
from textual.widgets import Static

from racgoat.ui.models import ApplicationMode, PaneFocusState
from racgoat.constants import STATUS_BAR_HEIGHT


# Keybinding templates for each (mode, focus) combination
KEYBINDING_TEMPLATES = {
    (ApplicationMode.NORMAL, PaneFocusState.DIFF): "c: Add Comment | s: Select Range | Shift+C: Comment File | Tab: Switch | q: Quit",
    (ApplicationMode.NORMAL, PaneFocusState.FILES): "Shift+C: Comment File | ↑/↓: Navigate | Enter: Select | Tab: Switch | q: Quit",
    (ApplicationMode.SELECT, PaneFocusState.DIFF): "↑/↓: Expand Selection | Enter: Confirm | Esc: Cancel",
    (ApplicationMode.SELECT, PaneFocusState.FILES): "Exit Select Mode first (Esc) | q: Quit",  # Navigation blocked
}

# Raccoon-themed keybinding templates 🦝
RACCOON_KEYBINDING_TEMPLATES = {
    (ApplicationMode.NORMAL, PaneFocusState.DIFF): "c: Cache in Trash Bin 🦝 | s: Scope Shinies | Shift+C: File Cache | Tab: Scout Territory | q: Return to Den",
    (ApplicationMode.NORMAL, PaneFocusState.FILES): "Shift+C: File Cache | ↑/↓: Sniff Around | Enter: Investigate | Tab: Scout Territory | q: Return to Den",
    (ApplicationMode.SELECT, PaneFocusState.DIFF): "↑/↓: Expand Loot | Enter: Grab It! | Esc: Drop It",
    (ApplicationMode.SELECT, PaneFocusState.FILES): "Drop your shinies first (Esc) 🦝 | q: Return to Den",
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

    DEFAULT_CSS = f"""
    StatusBar {{
        dock: bottom;
        height: {STATUS_BAR_HEIGHT};
        background: $surface;
        color: $text;
        padding: 0 1;
    }}
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

        # Check if raccoon mode is active
        raccoon_mode = getattr(self.app, 'raccoon_mode_active', False) if self.app else False
        templates = RACCOON_KEYBINDING_TEMPLATES if raccoon_mode else KEYBINDING_TEMPLATES

        keybindings = templates.get(
            key,
            "🦝 Unknown state - return to den (q)" if raccoon_mode else "Unknown state - press q to quit"
        )
        self.update(keybindings)

    def refresh_keybindings(self) -> None:
        """Force refresh of keybindings display (e.g., when raccoon mode toggles)."""
        self._render_keybindings()
