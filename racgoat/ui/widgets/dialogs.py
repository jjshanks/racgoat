"""Dialog widgets for user confirmation and input (Milestone 5).

Simple modal dialogs for yes/no decisions. The goat asks before deleting treasure!
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from racgoat.constants import MODAL_WIDTH_XSMALL


class ConfirmDialog(ModalScreen[bool]):
    """Simple Yes/No confirmation dialog.

    The goat double-checks before tossing treasure into the abyss!

    Attributes:
        message: Confirmation question to display

    Returns:
        True if user confirms (Yes button), False if user cancels (No button or Esc)

    Usage:
        app.push_screen(
            ConfirmDialog("Delete this comment?"),
            callback=lambda confirmed: handle_delete(confirmed)
        )
    """

    DEFAULT_CSS = f"""
    ConfirmDialog {{
        align: center middle;
    }}

    #confirm-dialog {{
        width: {MODAL_WIDTH_XSMALL};
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }}

    .confirm-message {{
        text-align: center;
        margin-bottom: 2;
        color: $text;
    }}

    .confirm-buttons {{
        align: center middle;
        height: auto;
    }}

    .confirm-buttons Button {{
        margin: 0 1;
    }}
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel (No)", show=True),
        Binding("enter", "confirm", "Confirm (Yes)", show=True),
    ]

    def __init__(self, message: str):
        """Initialize confirmation dialog.

        Args:
            message: Question to ask user (e.g., "Delete this comment?")
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        with Container(id="confirm-dialog"):
            yield Static(self.message, classes="confirm-message")
            with Horizontal(classes="confirm-buttons"):
                yield Button("Yes", variant="error", id="yes")
                yield Button("No", variant="primary", id="no")

    def on_mount(self) -> None:
        """Focus Yes button when mounted so Enter confirms deletion."""
        yes_button = self.query_one("#yes", Button)
        yes_button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button press event
        """
        # Return True for Yes, False for No
        self.dismiss(event.button.id == "yes")

    def action_confirm(self) -> None:
        """Handle Enter key - confirm deletion (Yes)."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Handle Esc key - cancel deletion (No)."""
        self.dismiss(False)
