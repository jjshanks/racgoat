"""RacGoat Application Constants

Centralized configuration values for the TUI application.
Because even raccoons and goats need to agree on some numbers!
"""

# ===========================
# UI Layout Constants
# ===========================

# Modal Widths (in columns)
MODAL_WIDTH_LARGE = 80  # Main container, large modals
MODAL_WIDTH_MEDIUM = 70  # Help screen, error dialog
MODAL_WIDTH_SMALL = 60  # Comment input dialog
MODAL_WIDTH_XSMALL = 50  # Confirmation dialogs

# Modal Heights (in rows)
MODAL_HEIGHT = 20  # Standard modal height
MODAL_MAX_HEIGHT_PERCENT = 90  # Maximum modal height as percentage

# Pane Widths (as percentages)
FILES_PANE_WIDTH_PERCENT = 30  # Left pane (file list)
DIFF_PANE_WIDTH_PERCENT = 70  # Right pane (diff viewer)

# Widget Dimensions
BUTTON_WIDTH = 20  # Standard button width
STATUS_BAR_HEIGHT = 1  # Status bar height (rows)

# ===========================
# Performance Limits
# ===========================

# Diff Processing Limits
MAX_DIFF_LINES = 10_000  # Maximum total diff lines supported
MAX_FILES = 100  # Maximum number of files in a diff

# Comment Limits
MAX_COMMENT_LENGTH = 10_000  # Maximum characters per comment

# ===========================
# Content Display
# ===========================

# Code Context
DEFAULT_CONTEXT_LINES = 2  # Lines of context before/after target line in Markdown output
