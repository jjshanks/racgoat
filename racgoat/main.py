"""
RacGoat Main Application
A TUI that's part raccoon mischief, part goat stubbornness!
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding


class RacGoatApp(App):
    """
    The main RacGoat TUI application.

    Don't be a scapegoat - let's code!
    """

    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        width: 80;
        height: 20;
        border: heavy $primary;
        padding: 2 4;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #message {
        width: 100%;
        content-align: center middle;
        margin-bottom: 2;
    }

    #easter-egg {
        width: 100%;
        content-align: center middle;
        color: $warning;
        margin-bottom: 1;
    }

    Button {
        width: 20;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        ("ctrl+c", "quit", "Quit"),
    ]

    # Hidden easter egg flag - shhh, it's a secret! 🦝
    raccoon_mode_active = False

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        with Container(id="main-container"):
            yield Static("🦝 RacGoat Adventures 🐐", id="title")
            yield Label("Don't be a 'scapegoat' – let's code!", id="message")
            yield Static("", id="easter-egg")  # Hidden easter egg area
            yield Button("Quit", variant="error", id="quit-btn")
        yield Footer()

    def on_mount(self) -> None:
        """Set the app title when mounted."""
        self.title = "RacGoat - Trash Panda meets Mountain Climber"
        self.sub_title = "Press 'q' to quit | Type 'trash' for a surprise 🦝"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "quit-btn":
            self.exit()

    def on_key(self, event) -> None:
        """
        Handle keyboard input for easter eggs.

        This is where the raccoon magic happens! 🦝✨
        """
        # Build up a string from key presses to detect "trash"
        if not hasattr(self, '_key_buffer'):
            self._key_buffer = ""

        # Add character to buffer (only letters)
        if len(event.key) == 1 and event.key.isalpha():
            self._key_buffer += event.key.lower()

            # Keep buffer reasonable size (goats don't hoard like raccoons!)
            if len(self._key_buffer) > 10:
                self._key_buffer = self._key_buffer[-10:]

            # Check for easter egg trigger
            if "trash" in self._key_buffer:
                self.activate_raccoon_mode()
                self._key_buffer = ""  # Reset buffer after activation

    def activate_raccoon_mode(self) -> None:
        """
        Activate secret raccoon mode! 🦝

        Because every good app needs a trash panda easter egg!
        """
        if not self.raccoon_mode_active:
            self.raccoon_mode_active = True
            easter_egg_widget = self.query_one("#easter-egg", Static)
            easter_egg_widget.update(
                "🦝 RACCOON MODE ACTIVATED! 🦝\n"
                "Digging through code bins for treasures!\n"
                "🗑️ Found: bugs, features, and leftover pizza! 🍕"
            )
            # Flash the background - raccoons love shiny things!
            self.notify("Raccoon mode activated! Time to raid the code bins! 🦝",
                       severity="information", timeout=5)


def main():
    """
    Entry point for the RacGoat application.

    Let's get this goat on the road! 🐐
    """
    app = RacGoatApp()
    app.run()


if __name__ == "__main__":
    main()
