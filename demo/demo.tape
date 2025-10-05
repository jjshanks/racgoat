# VHS tape script for RacGoat demo
# Install VHS: https://github.com/charmbracelet/vhs
# Run: vhs demo/demo.tape

# Output settings
Output demo/racgoat-demo.gif
Set Shell bash
Set FontSize 14
Set Width 1400
Set Height 800
Set Padding 20
Set Theme "Catppuccin Mocha"

# Type speed settings
Set TypingSpeed 50ms

# Title card
Type "# RacGoat Demo: AI Code Review TUI"
Sleep 1.5s
Enter
Sleep 500ms

Type "# Built 100% with Claude Sonnet 4.5"
Sleep 1.5s
Enter
Sleep 500ms
Enter

Type "# Let's review an authentication diff..."
Sleep 1.5s
Enter
Sleep 500ms

# Show the command
Type "cat demo/sample.diff | uv run python -m racgoat -o demo/review.md"
Sleep 1s
Enter
# Wait for app to load
Sleep 1s

# Navigate down in file list
Down
Sleep 500ms
Down
Sleep 500ms

# Show navigation between panes
Sleep 1s
Tab
Sleep 800ms

# Scroll down in diff pane
Down
Sleep 500ms
Down
Sleep 500ms
Down
Sleep 500ms

# Add comment
Type "c"
Sleep 500ms
Type "Are you sure this is secure?"
Sleep 500ms
Enter

Tab
Sleep 500ms
Up
Sleep 500ms
Tab
Sleep 500ms
Down
Sleep 500ms
Down
Sleep 500ms
Type "s"
Sleep 500ms
Down
Sleep 500ms
Down
Sleep 500ms
Enter
Sleep 500ms
Type "Are these imports in the right order?"
Sleep 500ms
Enter
Sleep 500ms

Tab
Sleep 500ms
Up
Sleep 500ms
Tab
Sleep 500ms

Type "/"
Sleep 800ms
Type "rate"
Sleep 500ms
Enter
Sleep 1s
Type "n"
Sleep 500ms
Type "n"
Sleep 500ms
Escape
Sleep 1s

Type "C"
Sleep 500ms
Type "This looks good"
Sleep 500ms
Enter
Sleep 500ms

# Quit and save
Type "q"
Sleep 1s

# Show the output file
Type "cat demo/review.md"
Sleep 1s
Enter
Sleep 5s

# Final message
Sleep 500ms
Type "# Review complete! Paste @review.md back into Claude Code"
Sleep 3s
