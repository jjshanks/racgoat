"""
RacGoat Main Application
A TUI that's part raccoon mischief, part goat stubbornness!
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding

from racgoat.parser.diff_parser import parse_diff
from racgoat.parser.models import DiffSummary
from racgoat.ui.widgets import TwoPaneLayout


class RacGoatApp(App):
    """
    The main RacGoat TUI application.

    Don't be a scapegoat - let's code!
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    #two-pane-layout {
        height: 1fr;
    }

    #empty-message {
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }

    #main-container {
        width: 80;
        height: 20;
        border: heavy $primary;
        padding: 2 4;
        align: center middle;
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

    def __init__(
        self,
        diff_summary: DiffSummary | None = None,
        diff_file: str | None = None,
        output_file: str = "review.md",
    ):
        """Initialize the RacGoat app.

        Args:
            diff_summary: Parsed diff data (preferred for Milestone 2+)
            diff_file: Path to file containing git diff (legacy Milestone 1)
            output_file: Path for output review file (default: review.md)
        """
        super().__init__()
        self.diff_file = diff_file
        self.output_file = output_file
        self.diff_input = None

        # Use provided diff_summary if available
        if diff_summary is not None:
            self.diff_summary = diff_summary
        elif diff_file:
            # Legacy: Load diff from file (Milestone 1 mode)
            try:
                with open(diff_file, "r") as f:
                    self.diff_input = f.read()
                # Parse the diff input
                self.diff_summary = parse_diff(
                    self.diff_input.splitlines(keepends=True)
                )
            except (OSError, IOError) as e:
                # File read error - will show error in UI
                self.diff_input = ""
                self.diff_summary = None
        else:
            # No diff provided - empty state
            self.diff_summary = None

    def compose(self) -> ComposeResult:
        """Compose the UI layout.

        For Milestone 2: Show TwoPaneLayout or empty message.
        """
        yield Header()

        # Check if we have a valid diff
        if self.diff_summary and not self.diff_summary.is_empty:
            # Milestone 2: Show two-pane layout
            yield TwoPaneLayout(self.diff_summary, id="two-pane-layout")
        else:
            # Empty diff: Show friendly message
            yield Static(
                "No changes to review 🦝🐐\n\n"
                "The raccoon found no treasures today!\n"
                "The goat climbed an empty cliff!",
                id="empty-message",
            )

        yield Footer()

    def on_mount(self) -> None:
        """Set the app title when mounted."""
        self.title = "RacGoat - TUI Diff Viewer"
        if self.diff_summary and not self.diff_summary.is_empty:
            self.sub_title = (
                f"Viewing {len(self.diff_summary.files)} file(s) | "
                "Tab: Switch pane | q: Quit"
            )
        else:
            self.sub_title = "No changes to review | Press q to quit"

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


def run_tui(diff_summary: DiffSummary) -> None:
    """Launch TUI with diff data (Milestone 2+).

    Args:
        diff_summary: Parsed diff to display
    """
    app = RacGoatApp(diff_summary=diff_summary)
    app.run(mouse=False)


def main(diff_file: str | None = None, output_file: str = "review.md"):
    """
    Entry point for the RacGoat application (legacy Milestone 1).

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
