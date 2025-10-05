"""
RacGoat Main Application
A TUI that's part raccoon mischief, part goat stubbornness!
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Label, Input
from textual.binding import Binding
from textual.design import ColorSystem
from textual.theme import Theme

from racgoat.parser.diff_parser import DiffParser
from racgoat.parser.models import DiffSummary
from racgoat.exceptions import DiffTooLargeError
from racgoat.ui.widgets import TwoPaneLayout
from racgoat.ui.models import ApplicationMode, PaneFocusState
from racgoat.di import ServiceContainer
from racgoat.models.comments import Comment, CommentTarget, CommentType
from racgoat.controllers import (
    CommentController,
    SearchController,
    QuitController,
    ThemeController,
)
from racgoat.constants import (
    MODAL_WIDTH_LARGE,
    MODAL_HEIGHT,
    BUTTON_WIDTH,
)


class RacGoatApp(App):
    """
    The main RacGoat TUI application.

    Don't be a scapegoat - let's code!
    """

    # Reactive properties for Milestone 3
    mode = reactive(ApplicationMode.NORMAL)
    focus_state = reactive(PaneFocusState.DIFF)

    CSS = f"""
    Screen {{
        layout: vertical;
    }}

    #two-pane-layout {{
        height: 1fr;
    }}

    #empty-message {{
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }}

    #main-container {{
        width: {MODAL_WIDTH_LARGE};
        height: {MODAL_HEIGHT};
        border: heavy $primary;
        padding: 2 4;
        align: center middle;
    }}

    #title {{
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }}

    #message {{
        width: 100%;
        content-align: center middle;
        margin-bottom: 2;
    }}

    #easter-egg {{
        width: 100%;
        content-align: center middle;
        color: $warning;
        margin-bottom: 1;
    }}

    Button {{
        width: {BUTTON_WIDTH};
        margin: 1 0;
    }}
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("tab", "cycle_focus", "Switch", show=True),
        Binding("c", "add_line_comment", "Add Comment", show=True),
        Binding("C", "add_file_comment", "File Comment", show=True),
        Binding("s", "enter_select_mode", "Select", show=True),
        Binding("e", "edit_comment", "Edit", show=True),
        Binding("escape", "cancel_select_mode", "Cancel/Exit", show=False),
        Binding("enter", "confirm_select_mode", "Confirm", show=False),
        # Milestone 5: Search functionality
        Binding("slash", "initiate_search", "Search", show=True),
        Binding("n", "next_item", "Next", show=True),
        Binding("p", "previous_item", "Prev", show=True),
        # Milestone 5: Help overlay
        Binding("question_mark", "show_help", "Help", show=True),
        # Easter eggs
        Binding("ctrl+t", "toggle_raccoon_mode", "🦝 Raccoon", show=False),
        Binding("ctrl+g", "toggle_goat_mode", "🐐 GOAT", show=False),
    ]

    # Hidden easter egg flags - shhh, they're secrets! 🦝🐐
    raccoon_mode_active = False
    goat_mode_active = False

    def __init__(
        self,
        diff_summary: DiffSummary | None = None,
        diff_file: str | None = None,
        output_file: str = "review.md",
        services: ServiceContainer | None = None,
    ):
        """Initialize the RacGoat app.

        Args:
            diff_summary: Parsed diff data (preferred for Milestone 2+)
            diff_file: Path to file containing git diff (legacy Milestone 1)
            output_file: Path for output review file (default: review.md)
            services: Service container for dependency injection (optional)
        """
        super().__init__()
        self.diff_file = diff_file
        self.output_file = output_file
        self.diff_input = None

        # Dependency injection: Use provided container or create new one
        self.services = services or ServiceContainer()

        # Initialize controllers
        self.comment_controller = CommentController(self)
        self.search_controller = SearchController(self)
        self.quit_controller = QuitController(self)
        self.theme_controller = ThemeController(self)

        # Easter egg themes setup
        self._original_theme = None
        self.theme_controller.create_and_register_themes()

        # Use provided diff_summary if available
        if diff_summary is not None:
            self.diff_summary = diff_summary
        elif diff_file:
            # Legacy: Load diff from file (Milestone 1 mode)
            try:
                with open(diff_file, "r") as f:
                    self.diff_input = f.read()
                # Parse the diff input
                parser = DiffParser()
                self.diff_summary = parser.parse(self.diff_input)
            except DiffTooLargeError:
                # Re-raise to be handled at entry point
                raise
            except (OSError, IOError) as e:
                # File read error - will show error in UI
                self.diff_input = ""
                self.diff_summary = None
        else:
            # No diff provided - empty state
            self.diff_summary = None

    @property
    def comment_store(self):
        """Access comment store through service container.

        This property provides backward compatibility for existing code
        that accesses app.comment_store directly.

        Returns:
            CommentStore: The application's comment store instance
        """
        return self.services.comment_store

    def compose(self) -> ComposeResult:
        """Compose the UI layout.

        For Milestone 3: Show TwoPaneLayout with StatusBar or empty message.
        """
        from racgoat.ui.widgets.status_bar import StatusBar

        yield Header()

        # Check if we have a valid diff
        if self.diff_summary and not self.diff_summary.is_empty:
            # Milestone 3: Show two-pane layout with services
            two_pane = TwoPaneLayout(
                self.diff_summary,
                services=self.services,
                id="two-pane-layout"
            )
            yield two_pane
            # Milestone 3: Add status bar
            yield StatusBar(id="status-bar")
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

    def watch_mode(self, new_mode: ApplicationMode) -> None:
        """Propagate mode changes to child widgets."""
        if self.diff_summary and not self.diff_summary.is_empty:
            try:
                two_pane = self.query_one(TwoPaneLayout)
                if two_pane._diff_pane:
                    two_pane._diff_pane.app_mode = new_mode
                status_bar = self.query_one("#status-bar")
                if status_bar:
                    status_bar.app_mode = new_mode
            except:
                # Widgets not mounted yet
                pass

    def action_cycle_focus(self) -> None:
        """Cycle focus between panes (Tab key)."""
        # This is handled by TwoPaneLayout in Milestone 2
        pass

    def action_quit(self) -> None:
        """Quit the application and save review if comments exist."""
        self.quit_controller.action_quit()

    def action_add_line_comment(self) -> None:
        """Add a comment to the current line (c key)."""
        self.comment_controller.action_add_line_comment()

    def action_add_file_comment(self) -> None:
        """Add a comment to the current file (Shift+C key)."""
        self.comment_controller.action_add_file_comment()

    def action_enter_select_mode(self) -> None:
        """Enter SELECT mode for range comments (s key)."""
        self.comment_controller.action_enter_select_mode()

    def action_cancel_select_mode(self) -> None:
        """Cancel SELECT mode or search (Esc key)."""
        # Check if search is active first
        if self.search_controller._is_search_active():
            self.search_controller.action_cancel_search()
            return

        # Otherwise, handle SELECT mode
        self.comment_controller.action_cancel_select_mode()

    def action_confirm_select_mode(self) -> None:
        """Confirm SELECT mode and prompt for range comment (Enter key)."""
        self.comment_controller.action_confirm_select_mode()

    # Milestone 5: New actions

    def action_show_help(self) -> None:
        """Show help overlay with all keybindings (? key)."""
        self.search_controller.action_show_help()

    def action_initiate_search(self) -> None:
        """Initiate search mode (/ key)."""
        self.search_controller.action_initiate_search()

    def action_next_item(self) -> None:
        """Navigate to next item (search match or file) (n key)."""
        self.search_controller.action_next_item()

    def action_previous_item(self) -> None:
        """Navigate to previous item (search match or file) (p key)."""
        self.search_controller.action_previous_item()

    def action_edit_comment(self) -> None:
        """Edit or delete comment at cursor (e key)."""
        self.comment_controller.action_edit_comment()

    def action_toggle_raccoon_mode(self) -> None:
        """Toggle raccoon mode! 🦝"""
        self.theme_controller.action_toggle_raccoon_mode()

    def action_toggle_goat_mode(self) -> None:
        """Toggle GOAT mode! 🐐"""
        self.theme_controller.action_toggle_goat_mode()


def run_tui(diff_summary: DiffSummary, output_file: str = "review.md") -> None:
    """Launch TUI with diff data (Milestone 2+).

    Args:
        diff_summary: Parsed diff to display
        output_file: Path for output review file (default: review.md)
    """
    app = RacGoatApp(diff_summary=diff_summary, output_file=output_file)
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
