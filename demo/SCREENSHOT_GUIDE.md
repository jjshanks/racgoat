# Screenshot Guide for Contest Submission

If you can't create a GIF right now, screenshots work too! Here's how to capture the essential views.

## Required Screenshots

You need **4-5 key screenshots** to show RacGoat's features:

### 1. Main TUI View (Two-Pane Layout)
**Command:**
```bash
cat demo/sample.diff | uv run python -m racgoat -o demo/review.md
```

**What to capture:**
- Files pane on left showing 3 files
- Diff pane on right with syntax highlighting
- Status bar at bottom
- Header showing "RacGoat"

**Screenshot name:** `01-main-view.png`

---

### 2. Comment Added (Visual Marker)
**Actions:**
1. Navigate to a line in diff
2. Press `c` to add comment
3. Type a comment (e.g., "This should use bcrypt")
4. Press Enter
5. Take screenshot showing the `*` marker

**What to capture:**
- The `*` marker next to commented line
- The diff content around it
- Status bar showing available actions

**Screenshot name:** `02-comment-marker.png`

---

### 3. Help Overlay
**Actions:**
1. While in the app, press `?`
2. Take screenshot of help overlay

**What to capture:**
- Full help overlay with keybindings
- Navigation, Commenting, Search, Help sections
- "Press ? to close" message

**Screenshot name:** `03-help-overlay.png`

---

### 4. Search Feature
**Actions:**
1. Press `/` to enter search
2. Type "session"
3. Press Enter
4. Take screenshot showing highlighted matches

**What to capture:**
- Search input at bottom
- Highlighted search matches in diff
- Current match highlighted differently

**Screenshot name:** `04-search-highlight.png`

---

### 5. Markdown Output
**Command (after quitting app):**
```bash
cat demo/review.md
```

**What to capture:**
- YAML frontmatter with metadata
- File path header
- Comments with line numbers
- Code context blocks

**Screenshot name:** `05-markdown-output.png`

---

## How to Take Screenshots

### macOS
- **Cmd+Shift+4** - Select area
- **Cmd+Shift+3** - Full screen

### Linux
- **Print Screen** - Full screen
- **Shift+Print Screen** - Select area
- Or use `gnome-screenshot` or `spectacle`

### Windows (WSL)
- **Win+Shift+S** - Select area
- **Win+Print Screen** - Full screen

---

## Tips for Good Screenshots

1. **Use a readable terminal theme**
   - Dark background with good contrast
   - Try: Dracula, Nord, Monokai, Solarized Dark

2. **Increase font size**
   - Terminal should be readable in screenshot
   - 14-16pt font recommended

3. **Full window, no desktop**
   - Capture just the terminal window
   - No desktop/taskbar clutter

4. **Terminal size**
   - Make window large enough: 120x40 or bigger
   - App should fit without scrolling

5. **Clean environment**
   - Close unnecessary terminal tabs
   - Clear prompt if it's long/messy

---

## Quick Checklist

Before screenshots:
- [ ] Terminal font size is 14pt or larger
- [ ] Using a readable dark theme
- [ ] Terminal window is clean (no clutter)
- [ ] App fits in window without scrolling

Screenshots needed:
- [ ] Main TUI view with two panes
- [ ] Comment marker (`*`) visible
- [ ] Help overlay open
- [ ] Search with highlights
- [ ] Markdown output in terminal

---

## Using Screenshots in Submission

### For GitHub README
Add at top of README.md:

```markdown
## 🎬 Demo

### Main Interface
![RacGoat TUI](demo/01-main-view.png)

### Help Overlay
![Help](demo/03-help-overlay.png)

### Markdown Output
![Output](demo/05-markdown-output.png)
```

### For Contest Post
Upload all 5 screenshots and caption them:
- "Two-pane TUI with file list and diff viewer"
- "Visual markers show commented lines"
- "Built-in help overlay"
- "Search with highlighting"
- "AI-parseable Markdown output"

---

## Alternative: Quick Video

Can't do screenshots either? Record a quick phone video:

1. Point phone at screen
2. Run the demo (see demo/README.md for script)
3. Narrate: "This is RacGoat, a TUI for reviewing AI diffs..."
4. Show key features (30-60 seconds)
5. Upload to YouTube/Vimeo as unlisted
6. Share link in contest post

---

Need help? See `demo/README.md` for full demo instructions.
