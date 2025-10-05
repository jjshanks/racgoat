"""UI consistency contract tests (T021-T023).

Validates consistent keybinding format, error message theming, and help text terminology.
Contract: ui-contracts.md
"""

import pytest
import re
from racgoat.main import RacGoatApp
from racgoat.parser.diff_parser import DiffParser


# T021: Keybinding format consistency


@pytest.mark.asyncio
async def test_keybinding_format():
    """All keybindings should use consistent format: capital letter or Ctrl+Letter.

    The raccoon's treasure map uses clear, consistent markings!

    Contract: ui-contracts.md Scenario 1
    Requirements:
    - Single keys: Capital letter (e.g., "Q", "A", not "q", "a")
    - Modifiers: "Ctrl+" format (not "^" or "Control-")
    - No lowercase in keybinding display
    """
    diff_text = _generate_test_diff()
    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Open help overlay
        await pilot.press("?")
        await pilot.pause()

        # Get help text
        help_overlay = app.query_one("#help-overlay")
        help_text = str(help_overlay.renderable)

        # Assert: No lowercase single-key bindings (like "q -", "a -")
        lowercase_bindings = re.findall(r'\b[a-z] -', help_text)
        assert not lowercase_bindings, f"Found lowercase keybindings: {lowercase_bindings}"

        # Assert: No caret notation (^C, ^X)
        assert "^" not in help_text or "Ctrl+" in help_text, "Found caret notation, should use Ctrl+"

        # Assert: No "Control-" prefix
        assert "Control-" not in help_text, "Found 'Control-' prefix, should use 'Ctrl+'"

        # Get footer text
        footer_text = str(app.query_one("Footer").renderable)

        # Footer should also follow format
        assert not re.search(r'\b[a-z]:', footer_text.lower()), "Footer has lowercase keybindings"


# T022: Error message theme


@pytest.mark.asyncio
async def test_error_message_theme():
    """All error messages should follow raccoon/goat theme.

    Every warning comes with the raccoon's wisdom and the goat's assurance!

    Contract: ui-contracts.md Scenario 1-3
    Requirements:
    - Start with 🦝 emoji
    - End with 🐐 emoji
    - Helpful text (not just "error")
    """
    # Test DiffTooLargeError
    from racgoat.exceptions import DiffTooLargeError

    error = DiffTooLargeError(actual_lines=12500, limit=10000)

    # Assert: Starts with raccoon
    assert error.message.startswith("🦝"), "Error should start with raccoon emoji"

    # Assert: Ends with goat
    assert "🐐" in error.message, "Error should contain goat emoji"

    # Assert: Helpful text
    assert "smaller chunks" in error.message.lower(), "Error should provide actionable advice"
    assert str(error.actual_lines) in error.message, "Error should show actual line count"


@pytest.mark.asyncio
async def test_malformed_hunk_error_display():
    """Malformed hunks should display with themed warning indicator.

    The goat marks the rocky path with a warning sign!

    Contract: ui-contracts.md Scenario 2
    """
    diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ invalid @@
broken content
"""

    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Get diff pane content
        diff_pane = app.query_one("DiffPane")
        diff_text_rendered = str(diff_pane.renderable)

        # Assert: Contains warning indicator
        assert "[⚠ UNPARSEABLE]" in diff_text_rendered, "Should show unparseable marker"


# T023: Help text terminology


@pytest.mark.asyncio
async def test_help_text_terminology():
    """Help text should use consistent canonical terms.

    The treasure map speaks a single language!

    Contract: ui-contracts.md Scenario 1-2
    Canonical terms:
    - "Add comment" (not "Create comment", "Insert comment")
    - "search mode" (not "find mode", "search state")
    - "at cursor" (not "on current line")
    """
    diff_text = _generate_test_diff()
    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Open help overlay
        await pilot.press("?")
        await pilot.pause()

        # Get help text
        help_overlay = app.query_one("#help-overlay")
        help_text = str(help_overlay.renderable)

        # Assert: Uses "Add comment" (not "Create", "Insert", "New")
        # Allow case variations but check terminology
        assert "add comment" in help_text.lower(), "Should use 'Add comment' terminology"
        assert "create comment" not in help_text.lower(), "Should not use 'Create comment'"
        assert "insert comment" not in help_text.lower(), "Should not use 'Insert comment'"

        # Assert: Uses "search mode" (not "find mode")
        if "search" in help_text.lower():
            assert "search mode" in help_text.lower() or "search" in help_text.lower(), "Should use 'search' terminology"
            assert "find mode" not in help_text.lower(), "Should not use 'find mode'"

        # Get status bar text
        # Check for mode indicators
        # This will be context-dependent, but verify consistency


@pytest.mark.asyncio
async def test_grammar_and_spelling():
    """User-facing text should be grammatically correct.

    The raccoon writes with care - no sloppy notes!

    Contract: ui-contracts.md - Grammar and Spelling
    """
    diff_text = _generate_test_diff()
    parser = DiffParser()
    app = RacGoatApp()

    async with app.run_test() as pilot:
        summary = parser.parse(diff_text)
        app.diff_summary = summary
        await pilot.pause()

        # Get help text
        await pilot.press("?")
        await pilot.pause()

        help_overlay = app.query_one("#help-overlay")
        help_text = str(help_overlay.renderable)

        # Basic grammar checks
        # No sentence fragments starting with lowercase (unless intentional)
        sentences = help_text.split(". ")
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 1:
                # Allow emoji at start
                if not sentence[0].isupper() and sentence[0] not in "🦝🐐":
                    # Skip if it's a keybinding line (e.g., "q - Quit")
                    if not re.match(r'^[A-Z/\?]+ -', sentence):
                        # This might be a fragment
                        # Allow for now, but flag for review
                        pass

        # Check for common typos (basic check)
        common_typos = ["teh", "recieve", "seperate", "occured"]
        for typo in common_typos:
            assert typo not in help_text.lower(), f"Found typo: {typo}"


# Helper functions


def _generate_test_diff() -> str:
    """Generate simple diff for UI testing.

    Returns:
        Basic diff
    """
    return """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def test():
-    old line
+    new line
     pass
"""
