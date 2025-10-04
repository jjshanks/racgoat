"""Error Recovery Modal - when the raccoon's treasure stash gets stuck!

This modal screen handles file write errors and provides recovery options
including retrying with a new path or falling back to /tmp.
"""

from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.binding import Binding


class ErrorRecoveryScreen(ModalScreen[str | None]):
    """Modal dialog for file write error recovery.

    When the raccoon can't stash its treasures, this goat shows the way!

    Attributes:
        error_message: The error message to display
        show_tmp_fallback: Whether to show /tmp fallback option
        original_path: The original path that failed (for context)
    """

    DEFAULT_CSS = """
    ErrorRecoveryScreen {
        align: center middle;
    }

    #error-dialog {
        width: 70;
        height: auto;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }

    #error-title {
        width: 100%;
        content-align: center middle;
        color: $error;
        margin-bottom: 1;
        text-style: bold;
    }

    #error-message {
        width: 100%;
        margin-bottom: 1;
        color: $text;
    }

    #path-prompt {
        width: 100%;
        margin-bottom: 1;
        color: $accent;
    }

    #path-input {
        width: 100%;
        margin-bottom: 1;
    }

    #path-error {
        width: 100%;
        margin-bottom: 1;
        color: $error;
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
        Binding("enter", "retry", "Retry", show=True),
    ]

    def __init__(
        self,
        error_message: str,
        show_tmp_fallback: bool = True,
        original_path: str | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize error recovery modal.

        Args:
            error_message: Error message to display
            show_tmp_fallback: Whether to show /tmp fallback button
            original_path: Original path that failed (for context)
            name: Widget name (optional)
            id: Widget ID (optional)
        """
        super().__init__(name=name, id=id)
        self.error_message = error_message
        self.show_tmp_fallback = show_tmp_fallback
        self.original_path = original_path
        self._input_widget: Input | None = None
        self._path_error_widget: Static | None = None

    def compose(self) -> ComposeResult:
        """Compose the error recovery dialog."""
        with Container(id="error-dialog"):
            yield Static("⚠️  File Write Error", id="error-title")
            yield Static(self.error_message, id="error-message")
            yield Static("Enter new output path:", id="path-prompt")

            self._input_widget = Input(
                value=self.original_path or "",
                placeholder="/path/to/review.md",
                id="path-input"
            )
            yield self._input_widget

            # Path validation error (hidden initially)
            self._path_error_widget = Static("", id="path-error")
            yield self._path_error_widget

            with Horizontal(id="button-container"):
                yield Button("Retry [Enter]", variant="primary", id="retry-btn")
                if self.show_tmp_fallback:
                    yield Button("Save to /tmp [t]", variant="default", id="tmp-btn")
                yield Button("Cancel [Esc]", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        """Focus input when mounted."""
        if self._input_widget:
            self._input_widget.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "retry-btn":
            self.action_retry()
        elif event.button.id == "tmp-btn":
            self.action_save_to_tmp()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        self.action_retry()

    def action_retry(self) -> None:
        """Retry with new path from input field."""
        if not self._input_widget:
            return

        new_path = self._input_widget.value.strip()

        if not new_path:
            # Show validation error
            if self._path_error_widget:
                self._path_error_widget.update("⚠️ Path cannot be empty")
            return

        # Validate path (basic check)
        path = Path(new_path)
        if not path.parent.exists():
            # Parent directory doesn't exist
            if self._path_error_widget:
                self._path_error_widget.update(
                    f"⚠️ Directory does not exist: {path.parent}"
                )
            return

        # Path looks valid, return it
        self.dismiss(new_path)

    def action_save_to_tmp(self) -> None:
        """Save to /tmp directory as fallback."""
        # Generate filename from original path if available
        if self.original_path:
            filename = Path(self.original_path).name
        else:
            filename = "review.md"

        tmp_path = f"/tmp/{filename}"
        self.dismiss(tmp_path)

    def action_cancel(self) -> None:
        """Cancel the operation (Esc key or Cancel button)."""
        self.dismiss(None)
