"""Help overlay screen for displaying keybindings (Milestone 5).

The raccoon's treasure map - showing where all the shiny buttons are!
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from racgoat.constants import MODAL_WIDTH_MEDIUM, MODAL_MAX_HEIGHT_PERCENT

from racgoat.ui.models import HelpEntry


# Define all help entries organized by context
HELP_ENTRIES = [
    # Navigation
    HelpEntry(
        key="↑ / ↓",
        action="Navigate",
        description="Move cursor up/down in file list or scroll diff",
        context="Navigation"
    ),
    HelpEntry(
        key="PgUp / PgDn",
        action="Scroll page",
        description="Scroll diff pane by full page",
        context="Navigation"
    ),
    HelpEntry(
        key="Tab",
        action="Switch pane",
        description="Cycle focus between Files and Diff pane",
        context="Navigation"
    ),

    # Commenting
    HelpEntry(
        key="c",
        action="Add line comment",
        description="Create comment for current line",
        context="Commenting"
    ),
    HelpEntry(
        key="Shift+C",
        action="Add file comment",
        description="Create file-level comment",
        context="Commenting"
    ),
    HelpEntry(
        key="s",
        action="Select range",
        description="Enter Select Mode to mark range for comment",
        context="Commenting"
    ),
    HelpEntry(
        key="e",
        action="Edit comment",
        description="Edit or delete existing comment at cursor",
        context="Commenting"
    ),

    # Search
    HelpEntry(
        key="/",
        action="Search",
        description="Enter search mode to find text in diff",
        context="Search"
    ),
    HelpEntry(
        key="n",
        action="Next match",
        description="Jump to next search result",
        context="Search"
    ),
    HelpEntry(
        key="N",
        action="Previous match",
        description="Jump to previous search result",
        context="Search"
    ),
    HelpEntry(
        key="Esc",
        action="Exit mode",
        description="Exit search or select mode",
        context="General"
    ),

    # General
    HelpEntry(
        key="?",
        action="Help",
        description="Show/hide this help overlay",
        context="General"
    ),
    HelpEntry(
        key="q",
        action="Quit",
        description="Exit application and save review",
        context="General"
    ),
]


class HelpScreen(ModalScreen[None]):
    """Modal screen displaying all keybindings.

    The raccoon's complete treasure map - every shiny button explained!

    Features:
        - Organized by context (Navigation, Commenting, Search, General)
        - Scrollable if content exceeds terminal height
        - Dismissible with ? or Esc
        - Centered modal with border

    Usage:
        app.push_screen(HelpScreen())
    """

    DEFAULT_CSS = f"""
    HelpScreen {{
        align: center middle;
    }}

    #help-dialog {{
        width: {MODAL_WIDTH_MEDIUM};
        height: auto;
        max-height: {MODAL_MAX_HEIGHT_PERCENT}%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }}

    .help-title {{
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }}

    .help-section-title {{
        text-style: bold;
        color: $primary;
        margin-top: 1;
        margin-bottom: 1;
    }}

    .help-entry {{
        margin-bottom: 1;
    }}

    .help-key {{
        text-style: bold;
        color: $warning;
    }}

    .help-action {{
        color: $accent;
    }}

    .help-description {{
        color: $text;
        margin-left: 4;
    }}
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("question_mark", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help overlay with all keybindings."""
        with Container(id="help-dialog"):
            with VerticalScroll():
                yield Static("🦝 RacGoat Keybindings 🐐", classes="help-title")

                # Group entries by context
                contexts = ["Navigation", "Commenting", "Search", "General"]
                for context in contexts:
                    yield Static(f"📍 {context}", classes="help-section-title")

                    # Filter entries for this context
                    context_entries = [e for e in HELP_ENTRIES if e.context == context]

                    for entry in context_entries:
                        # Format: [key] action - description
                        text = f"[bold yellow]{entry.key}[/] {entry.action}\n"
                        text += f"    {entry.description}"
                        yield Static(text, classes="help-entry", markup=True)

    def action_dismiss(self) -> None:
        """Dismiss help overlay."""
        self.dismiss(None)
