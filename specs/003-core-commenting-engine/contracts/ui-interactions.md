# Contract: UI Interactions

**Components**: RacGoatApp, DiffPane, FilesPane, StatusBar
**Version**: 1.0.0

## Overview

This contract defines the UI interaction patterns for the commenting system, including keybindings, mode transitions, and visual feedback.

## Keybinding Contracts

### Single-Line Comment (`a` key)

**Trigger**: User presses `a` while DiffPane has focus and mode is NORMAL

**Preconditions**:
- App mode is NORMAL (not SELECT)
- DiffPane has focus
- Current line is a valid diff line (not header, not context marker)

**Flow**:
1. App captures current cursor line number
2. Check if comment exists at (current_file, line_number)
3. If exists: Display input with pre-filled text (FR-015)
4. If not exists: Display empty input prompt
5. User enters text or cancels (Esc/empty)
6. If text provided: Create comment, update display
7. If cancelled: Return to NORMAL with no changes

**Postconditions**:
- Comment stored in CommentStore (if text provided)
- Visual marker appears in gutter (if new comment)
- Marker updates to show overlap (if comment existed)
- Focus remains on DiffPane at same line

**Visual Feedback**:
- Input dialog appears with prompt "Comment on line {N}:"
- If editing: Input pre-filled with existing text
- On success: Marker appears/updates in gutter
- On cancel: No visual change

### File-Level Comment (`c` key)

**Trigger**: User presses `c` while viewing any file

**Preconditions**:
- App mode is NORMAL
- Current file is identified (from FilesPane or DiffPane)

**Flow**:
1. App captures current file path
2. Check if file-level comment exists
3. If exists: Display input with pre-filled text
4. If not exists: Display empty input prompt
5. User enters text or cancels
6. If text provided: Create file-level comment
7. If cancelled: Return to previous state

**Postconditions**:
- Comment stored with target (file_path, None, None)
- FilesPane shows file has comment (optional indicator)
- Focus remains on current widget

**Visual Feedback**:
- Input dialog with prompt "Comment on file {filename}:"
- If editing: Input pre-filled
- On success: File list item may show indicator (e.g., `[*] filename`)

### Range Selection Mode (`s` key)

**Trigger**: User presses `s` while DiffPane has focus and mode is NORMAL

**Preconditions**:
- App mode is NORMAL
- DiffPane has focus
- Current line is valid diff content

**Flow**:
1. App sets mode to SELECT
2. Record start_line = current cursor line
3. Status bar updates to show SELECT mode keys
4. User navigates with arrow keys:
   - Up: Decrease end_line (min: start_line)
   - Down: Increase end_line (max: last line in hunk)
5. DiffPane highlights selected range
6. User presses Enter to confirm or Esc to cancel
7. If Enter: Prompt for comment text
8. If text provided: Create range comment
9. Set mode back to NORMAL

**Postconditions**:
- If confirmed: Range comment stored, markers on all lines
- If cancelled: No comment created, mode back to NORMAL
- Focus remains on DiffPane

**Visual Feedback**:
- Selected lines have different background color
- Status bar shows: "↑/↓: Expand | Enter: Confirm | Esc: Cancel"
- Range indicator shows "Lines {start}-{end}"
- After confirm: Input dialog "Comment on lines {start}-{end}:"

### File Navigation Lock (SELECT mode)

**Trigger**: User presses arrow keys in FilesPane while mode is SELECT

**Preconditions**:
- App mode is SELECT
- FilesPane has focus (via Tab)

**Flow**:
1. FilesPane.on_key() receives arrow key event
2. Check app.mode
3. If mode == SELECT:
   - Display toast message: "Exit Select Mode first (Esc)"
   - Ignore navigation input
4. If mode == NORMAL:
   - Process navigation normally

**Postconditions**:
- File list selection unchanged (if mode was SELECT)
- User awareness of mode conflict (via toast message)

**Visual Feedback**:
- Toast/notification: "Exit Select Mode first (Esc)"
- No file list movement

### Quit (`q` key)

**Trigger**: User presses `q` in any mode

**Preconditions**: None (always available)

**Flow**:
1. Check if comments exist (CommentStore.count() > 0)
2. If comments exist: Save to Markdown (Milestone 4 - skip for Milestone 3)
3. Exit application

**Postconditions**:
- App exits cleanly
- Comments discarded (Milestone 3) or saved (Milestone 4+)

## Mode Transition Contract

### Normal → Select
**Trigger**: Press `s` in DiffPane
**Validation**:
- Mode must be NORMAL before transition
- Focus must be on DiffPane
- Current line must be valid diff content

### Select → Normal (Cancel)
**Trigger**: Press Esc in SELECT mode
**Validation**:
- Mode must be SELECT
- No comment created
- Selection cleared

### Select → Normal (Confirm)
**Trigger**: Press Enter in SELECT mode, then provide text
**Validation**:
- Mode must be SELECT
- Range must be valid (start ≤ end)
- Comment created only if text provided

## Status Bar Update Contract

### Context-Sensitive Display

**State 1: NORMAL mode, DiffPane focus**
Display: `a: Add Comment | s: Select Range | c: Comment File | q: Quit`

**State 2: NORMAL mode, FilesPane focus**
Display: `c: Comment File | ↑/↓: Navigate | Enter: Select | q: Quit`

**State 3: SELECT mode (any focus)**
Display: `↑/↓: Expand Selection | Enter: Confirm | Esc: Cancel`

**Reactive Updates**:
- StatusBar watches `app.mode` reactive property
- StatusBar watches `app.focus_state` reactive property (from Milestone 2)
- Updates triggered automatically on property change
- No manual calls to update() required

## Visual Marker Contract

### Gutter Rendering

**Format**: `{marker} | {line_num} {content}`

**Marker Rules**:
- No comment: Empty space (e.g., "  | +42 code")
- Single comment: Yellow `*` (e.g., "[yellow]*[/yellow] | +42 code")
- Multiple comments (overlap): Red `**` (e.g., "[red]**[/red] | +42 code")

**Update Triggers**:
- DiffPane re-renders when CommentStore notifies of changes
- Query CommentStore for visible line range only (viewport optimization)
- Markers update on file switch, scroll, or new comment addition

**Performance**:
- O(visible_lines) marker lookups per render (typically 20-50)
- Render time <10ms (well within <50ms UI response target)

## Error Handling Contract

### Invalid Key in Wrong Mode
**Scenario**: User presses `a` while in SELECT mode
**Behavior**: Ignore input, no error message (mode-specific bindings enforced)

### Empty Comment Text
**Scenario**: User provides empty string in comment prompt
**Behavior**: Treat as cancel, no comment created, return to previous state

### Navigation in SELECT Mode
**Scenario**: User tries to switch files via arrow keys in FilesPane while SELECT active
**Behavior**: Display toast "Exit Select Mode first (Esc)", ignore input

### Capacity Exceeded
**Scenario**: User tries to add 101st comment
**Behavior**: Display error toast "Comment limit reached (100 max)", don't create comment

## Contract Test Scenarios

UI interaction tests (Textual-based):

1. **test_add_comment_key_triggers_prompt**: Press `a`, verify input appears
2. **test_cancel_comment_returns_to_normal**: Esc in prompt, verify no comment
3. **test_select_mode_changes_status_bar**: Press `s`, verify status bar updates
4. **test_select_mode_prevents_file_nav**: SELECT active, arrow in files, verify blocked
5. **test_range_selection_visual_highlight**: SELECT mode, navigate, verify highlight
6. **test_marker_appears_after_comment**: Add comment, verify `*` in gutter
7. **test_overlap_marker_changes**: Add 2nd comment to same line, verify `**`
8. **test_edit_existing_prefills_input**: Comment on existing line, verify pre-filled
9. **test_file_comment_from_any_pane**: Press `c` in files/diff, verify prompt
10. **test_quit_exits_cleanly**: Press `q`, verify app exits

## Integration with Existing Components

### DiffPane (existing widget)
**Modifications**:
- Add gutter column rendering in `render()` method
- Query CommentStore for current file's markers
- Handle SELECT mode highlighting (background color for selected lines)
- Wire `a` and `s` keybindings

### FilesPane (existing widget)
**Modifications**:
- Wire `c` keybinding for file-level comments
- Check `app.mode` before processing arrow keys (SELECT lock)
- Optional: Show indicator for files with comments

### StatusBar (new widget)
**Creation**:
- Reactive widget watching `app.mode` and `app.focus_state`
- Keybinding template lookup based on (mode, focus) tuple
- Rich Text rendering for styled keybinding hints

### RacGoatApp (existing app class)
**Modifications**:
- Add `mode` reactive property (default: ApplicationMode.NORMAL)
- Instantiate CommentStore service
- Wire comment creation actions to store operations
- Handle input prompts (Textual Input widget)
