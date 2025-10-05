"""Theme Controller - Handles easter egg theme modes.

Because every good app needs trash panda and GOAT modes! 🦝🐐
"""

from typing import TYPE_CHECKING

from textual.theme import Theme

if TYPE_CHECKING:
    from racgoat.main import RacGoatApp


class ThemeController:
    """Controller for theme and easter egg operations."""

    def __init__(self, app: "RacGoatApp"):
        """Initialize the theme controller.

        Args:
            app: Reference to the main RacGoatApp instance
        """
        self.app = app

    def create_and_register_themes(self) -> None:
        """Create and register both raccoon and goat themes."""
        self._create_and_register_raccoon_theme()
        self._create_and_register_goat_theme()

    def _create_and_register_raccoon_theme(self) -> None:
        """Create and register the trash panda theme! 🦝"""
        raccoon_theme = Theme(
            name="raccoon",
            primary="#A8A8A8",  # Raccoon gray
            secondary="#4A4A4A",  # Dark gray/black
            warning="#FFB84D",  # Amber "shiny" color
            error="#FF6B6B",  # Soft red
            success="#88C999",  # Muted green
            accent="#D4AF37",  # Golden "treasure" color
            foreground="#E0E0E0",  # Light gray text
            background="#2D2D2D",  # Dark background
            surface="#3A3A3A",  # Slightly lighter surface
            panel="#333333",  # Panel color
        )
        self.app.register_theme(raccoon_theme)

    def _create_and_register_goat_theme(self) -> None:
        """Create and register the mountain goat theme! 🐐"""
        goat_theme = Theme(
            name="mountain_goat",
            primary="#8B7355",  # Mountain brown
            secondary="#5D4E37",  # Dark earth
            warning="#FFD700",  # Golden yellow (summit shine)
            error="#CD5C5C",  # Indian red
            success="#6B8E23",  # Mountain green
            accent="#87CEEB",  # Sky blue
            foreground="#F5F5DC",  # Beige text (like a goat's coat)
            background="#2F4F4F",  # Dark slate gray (rocky)
            surface="#696969",  # Dim gray (stone)
            panel="#556B2F",  # Dark olive green
        )
        self.app.register_theme(goat_theme)

    def action_toggle_raccoon_mode(self) -> None:
        """Toggle raccoon mode! 🦝

        Because every good app needs a trash panda easter egg!
        Triggered by Ctrl+T.
        """
        if not self.app.raccoon_mode_active:
            # Deactivate goat mode if active (mutual exclusion)
            if self.app.goat_mode_active:
                self.app.goat_mode_active = False

            # Activate raccoon mode
            self.app.raccoon_mode_active = True
            self.app._original_theme = self.app.theme
            self.app.theme = "raccoon"
            self.app.title = "🦝 RacGoat - TRASH PANDA MODE 🦝"

            # Show ASCII art notification
            from racgoat.utils import generate_ascii_art
            self.app.notify(
                "Raccoon mode activated! Time to raid the code bins! 🦝\n" +
                generate_ascii_art(),
                severity="information",
                timeout=8
            )
        else:
            # Deactivate raccoon mode
            self.app.raccoon_mode_active = False
            if self.app._original_theme:
                self.app.theme = self.app._original_theme
            self.app.title = "RacGoat - TUI Diff Viewer"
            self.app.notify("Back to normal mode. The raccoons have left the building! 🦝",
                           severity="information", timeout=3)

        # Refresh diff pane to update comment markers
        self._refresh_ui()

    def action_toggle_goat_mode(self) -> None:
        """Toggle GOAT mode! 🐐

        Because the Greatest Of All Time deserves its own mode!
        Triggered by Ctrl+G.
        """
        if not self.app.goat_mode_active:
            # Deactivate raccoon mode if active (mutual exclusion)
            if self.app.raccoon_mode_active:
                self.app.raccoon_mode_active = False

            # Activate goat mode
            self.app.goat_mode_active = True
            self.app._original_theme = self.app.theme
            self.app.theme = "mountain_goat"
            self.app.title = "🐐 RacGoat - GREATEST OF ALL TIME MODE 🐐"

            # Show ASCII art notification
            from racgoat.utils import generate_goat_ascii_art
            self.app.notify(
                "GOAT mode activated! Time to climb to the top! 🐐\n" +
                generate_goat_ascii_art(),
                severity="information",
                timeout=8
            )
        else:
            # Deactivate goat mode
            self.app.goat_mode_active = False
            if self.app._original_theme:
                self.app.theme = self.app._original_theme
            self.app.title = "RacGoat - TUI Diff Viewer"
            self.app.notify("Back to normal mode. The GOAT has left the mountain! 🐐",
                           severity="information", timeout=3)

        # Refresh diff pane to update comment markers
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        """Refresh UI components after theme change."""
        try:
            from racgoat.ui.widgets import TwoPaneLayout
            from racgoat.ui.widgets.status_bar import StatusBar

            two_pane = self.app.query_one(TwoPaneLayout, expect_type=TwoPaneLayout)
            diff_pane = two_pane._diff_pane
            if diff_pane and diff_pane.current_file:
                diff_pane.display_file(diff_pane.current_file, refresh_only=True)
        except Exception:
            pass  # Layout not yet mounted

        # Refresh status bar to update keybinding messages
        try:
            from racgoat.ui.widgets.status_bar import StatusBar
            status_bar = self.app.query_one(StatusBar, expect_type=StatusBar)
            if status_bar:
                status_bar.refresh_keybindings()
        except Exception:
            pass  # Status bar not yet mounted
