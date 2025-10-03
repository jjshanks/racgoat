"""Comment Input Modal - where raccoons stash their thoughts!

This modal screen provides an input dialog for adding/editing comments.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.binding import Binding


class CommentInput(ModalScreen[str | None]):
    """Modal screen for comment input.

    The raccoon's favorite place to scribble thoughts!

    Attributes:
        prompt: The prompt text to display
        prefill: Pre-filled text for editing existing comments
    """

    DEFAULT_CSS = """
    CommentInput {
        align: center middle;
    }

    #comment-dialog {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #comment-prompt {
        width: 100%;
        content-align: center middle;
        color: $accent;
        margin-bottom: 1;
        text-style: bold;
    }

    #comment-input {
        width: 100%;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        layout: horizontal;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("enter", "submit", "Submit", show=False),  # Input handles Enter
    ]

    def __init__(
        self,
        prompt: str = "Enter comment:",
        prefill: str = "",
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize comment input modal.

        Args:
            prompt: Prompt text to display
            prefill: Pre-filled text (for editing existing comments)
            name: Widget name (optional)
            id: Widget ID (optional)
        """
        super().__init__(name=name, id=id)
        self.prompt = prompt
        self.prefill = prefill
        self._input_widget: Input | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal dialog."""
        with Container(id="comment-dialog"):
            yield Label(self.prompt, id="comment-prompt")
            self._input_widget = Input(
                value=self.prefill,
                placeholder="Type your comment here...",
                id="comment-input"
            )
            yield self._input_widget
            with Vertical(id="button-container"):
                yield Button("Submit [Enter]", variant="primary", id="submit-btn")
                yield Button("Cancel [Esc]", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        """Focus input when mounted."""
        if self._input_widget:
            self._input_widget.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "submit-btn":
            self.action_submit()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        self.action_submit()

    def action_submit(self) -> None:
        """Submit the comment text."""
        if self._input_widget:
            text = self._input_widget.value.strip()
            if text:  # Only submit non-empty text
                self.dismiss(text)
            else:
                # Empty text = cancel
                self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel the input (Esc key or Cancel button)."""
        self.dismiss(None)
