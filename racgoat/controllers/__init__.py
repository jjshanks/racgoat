"""Controllers for RacGoat application.

Controllers handle action logic extracted from the main application class.
"""

from racgoat.controllers.comment_controller import CommentController
from racgoat.controllers.search_controller import SearchController
from racgoat.controllers.quit_controller import QuitController
from racgoat.controllers.theme_controller import ThemeController

__all__ = [
    "CommentController",
    "SearchController",
    "QuitController",
    "ThemeController",
]
