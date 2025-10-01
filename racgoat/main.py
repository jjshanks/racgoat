"""
RacGoat Main Application
A TUI that's part raccoon mischief, part goat stubbornness!
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding

from racgoat.parser.diff_parser import parse_diff


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
        Binding("ctrl+t", "toggle_raccoon_mode", "🦝 Raccoon", show=True),
    ]

    # Hidden easter egg flag - shhh, it's a secret! 🦝
    raccoon_mode_active = False

    def __init__(self, diff_file: str | None = None, output_file: str = "review.md"):
        """Initialize the RacGoat app with optional diff file.

        Args:
            diff_file: Path to file containing git diff, or None for demo mode
            output_file: Path for output review file (default: review.md)
        """
        super().__init__()
        self.diff_file = diff_file
        self.output_file = output_file
        self.diff_input = None
        self.diff_summary = None

        if diff_file:
            # Load diff from file
            try:
                with open(diff_file, 'r') as f:
                    self.diff_input = f.read()
                # Parse the diff input
                self.diff_summary = parse_diff(self.diff_input.splitlines(keepends=True))
            except (OSError, IOError) as e:
                # File read error - will show error in UI
                self.diff_input = ""
                self.diff_summary = None

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        with Container(id="main-container"):
            yield Static("🦝 RacGoat Adventures 🐐", id="title")
            yield Label("", id="message")
            yield Static("", id="diff-display")
            yield Static("", id="easter-egg")  # Hidden easter egg area
        yield Footer()

    def on_mount(self) -> None:
        """Set the app title when mounted."""
        self.title = "RacGoat - Trash Panda meets Mountain Climber"
        self.sub_title = "Press 'q' to quit | Ctrl+T for raccoon mode 🦝"

        # Update the display based on whether we have diff data
        if self.diff_summary and not self.diff_summary.is_empty:
            message_widget = self.query_one("#message", Label)
            message_widget.update(f"Found {len(self.diff_summary.files)} file(s) in diff:")

            diff_widget = self.query_one("#diff-display", Static)
            diff_widget.update(self.diff_summary.format_output())
        else:
            message_widget = self.query_one("#message", Label)
            if self.diff_input is not None:
                message_widget.update("No changes found in diff (all filtered or empty)")
            else:
                message_widget.update("Don't be a 'scapegoat' – let's code!")

    def action_toggle_raccoon_mode(self) -> None:
        """
        Toggle raccoon mode! 🦝

        Because every good app needs a trash panda easter egg!
        Triggered by Ctrl+T.
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


def main(diff_file: str | None = None, output_file: str = "review.md"):
    """
    Entry point for the RacGoat application.

    Args:
        diff_file: Optional path to file containing git diff
        output_file: Path for output review file

    Let's get this goat on the road! 🐐
    """
    app = RacGoatApp(diff_file=diff_file, output_file=output_file)
    app.run(mouse=False)


if __name__ == "__main__":
    import sys
    from racgoat.cli.args import parse_arguments

    # Parse CLI arguments
    args = parse_arguments()

    # Determine diff source
    diff_path = getattr(args, 'diff_file', None)

    main(diff_file=diff_path, output_file=args.output)
