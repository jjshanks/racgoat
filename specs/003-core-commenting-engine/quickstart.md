# Quickstart: Core Commenting Engine

**Feature**: Core Commenting Engine (Milestone 3)
**Date**: 2025-10-02

## Overview

This quickstart demonstrates the core commenting functionality through realistic user scenarios. Each scenario maps to acceptance criteria from the feature spec.

## Prerequisites

- RacGoat installed with Milestone 2 complete (TUI navigation functional)
- Sample diff file available (see "Preparing Test Data" below)
- Python 3.12+ and UV installed

## Preparing Test Data

Create a sample diff file for testing:

```bash
# Generate a diff with multiple files and changes
git diff HEAD~1 > test.diff

# Or use RacGoat's test diff generator
uv run python scripts/generate_large_diff.py --preset small -o test.diff
```

## Scenario 1: Adding a Single-Line Comment

**Maps to**: Acceptance Scenario 1 (FR-001)

**Steps**:
1. Launch RacGoat with the test diff:
   ```bash
   uv run python -m racgoat < test.diff
   ```

2. Navigate to a file using arrow keys in the file list (left pane)

3. Press `Enter` to view the diff in the right pane

4. Use arrow keys to navigate to a specific line in the diff (e.g., a line with `+` prefix)

5. Press `a` (add comment)

6. **Observe**: Input dialog appears with prompt "Comment on line {N}:"

7. Type a comment (e.g., "This needs error handling")

8. Press `Enter` to confirm

9. **Verify**:
   - Input dialog closes
   - Yellow `*` marker appears in gutter next to the commented line
   - You can navigate away and back - marker persists

**Expected Result**: Comment is stored and visual marker displays correctly

## Scenario 2: Adding a File-Level Comment

**Maps to**: Acceptance Scenario 2 (FR-002)

**Steps**:
1. With RacGoat running (from Scenario 1 or fresh start)

2. Ensure focus is on the file list (left pane) - if not, press `Tab` to switch focus

3. Select a file using arrow keys

4. Press `c` (comment on file)

5. **Observe**: Input dialog appears with prompt "Comment on file {filename}:"

6. Type a file-level comment (e.g., "This entire module needs refactoring")

7. Press `Enter` to confirm

8. **Verify**:
   - Input dialog closes
   - (Optional in Milestone 3) File list shows indicator like `[*] filename`
   - File-level comment is independent of line-level comments

**Expected Result**: File-level comment is stored separately from line comments

## Scenario 3: Adding a Range Comment via Select Mode

**Maps to**: Acceptance Scenarios 3, 7 (FR-003, FR-007, FR-010)

**Steps**:
1. Navigate to the diff pane (right pane)

2. Use arrow keys to position cursor on the first line of a block you want to comment on

3. Press `s` (enter Select Mode)

4. **Observe**:
   - Status bar changes to: "↑/↓: Expand Selection | Enter: Confirm | Esc: Cancel"
   - Current line is highlighted (selection start)
   - App mode indicator shows "SELECT" (if visible)

5. Press `Down` arrow 3 times to expand selection to cover 4 lines

6. **Observe**:
   - Selection highlight expands to cover all 4 lines
   - Lines are visually distinct (e.g., different background color)

7. Press `Enter` to confirm selection

8. **Observe**: Input dialog appears with prompt "Comment on lines {start}-{end}:"

9. Type a comment (e.g., "Refactor this logic - too complex")

10. Press `Enter` to confirm

11. **Verify**:
    - Input dialog closes
    - Yellow `*` markers appear on ALL 4 lines in the gutter
    - Mode returns to NORMAL
    - Status bar shows normal keybindings again

**Expected Result**: Range comment is stored, all lines in range show markers

## Scenario 4: Visual Markers for Existing Comments

**Maps to**: Acceptance Scenario 4 (FR-006, FR-013)

**Steps**:
1. Add comments using Scenarios 1-3 above (if not already done)

2. Navigate to a different file in the file list

3. Navigate back to a file with comments

4. **Verify**:
   - Yellow `*` markers appear next to previously commented lines
   - Markers are in a dedicated gutter column (left of line numbers)
   - Format: `* | +42 code content here`
   - Markers persist across navigation

5. Scroll through the diff using arrow keys

6. **Verify**:
   - Markers scroll with the content
   - Only visible lines are checked for markers (performance optimization)

**Expected Result**: Visual markers persist and display correctly during navigation

## Scenario 5: Context-Sensitive Status Bar

**Maps to**: Acceptance Scenarios 5-7 (FR-007)

**Steps**:
1. With RacGoat running, observe the status bar (bottom of screen)

2. When focus is on **file list (left pane)**:
   - **Verify**: Status bar shows `c: Comment File | ↑/↓: Navigate | Enter: Select | q: Quit`

3. Press `Tab` to switch focus to **diff pane (right pane)**:
   - **Verify**: Status bar shows `a: Add Comment | s: Select Range | c: Comment File | q: Quit`

4. Press `s` to enter **Select Mode**:
   - **Verify**: Status bar shows `↑/↓: Expand Selection | Enter: Confirm | Esc: Cancel`

5. Press `Esc` to exit Select Mode:
   - **Verify**: Status bar returns to diff pane keybindings

**Expected Result**: Status bar updates automatically based on mode and focus

## Scenario 6: Editing an Existing Comment

**Maps to**: Edge Case (FR-015)

**Steps**:
1. Navigate to a line that already has a comment (from Scenario 1)

2. Press `a` (add comment)

3. **Observe**: Input dialog appears with EXISTING comment text pre-filled

4. Edit the text (e.g., change "error handling" to "better error handling")

5. Press `Enter` to confirm

6. **Verify**:
   - Input dialog closes
   - Visual marker remains (same position)
   - Comment is updated (can verify in Milestone 4 when output is implemented)

**Expected Result**: Existing comment is edited in place, not duplicated

## Scenario 7: Overlapping Comments

**Maps to**: Edge Case (FR-017)

**Steps**:
1. Add a single-line comment to line 50 (using Scenario 1 steps)
   - **Verify**: Yellow `*` marker appears

2. Add a range comment covering lines 45-55 (using Scenario 3 steps)
   - **Verify**: Range comment is created

3. Navigate to line 50

4. **Observe**:
   - Marker changes from yellow `*` to red `**`
   - Indicates overlap (line has 2 comments: single-line + part of range)

5. Try to add a third comment to line 50 (press `a`)

6. **Observe**: Input shows existing comment (first one added)
   - Note: Milestone 3 allows editing first comment; Milestone 5 will add UI to choose which comment to edit

**Expected Result**: Overlapping comments are allowed, visually distinguished

## Scenario 8: Canceling Comment Input

**Maps to**: Edge Case (FR-012)

**Steps**:
1. Navigate to any diff line

2. Press `a` to start adding a comment

3. Input dialog appears

4. Press `Esc` (or leave text empty and press Enter)

5. **Verify**:
   - Input dialog closes
   - No marker appears
   - No comment created
   - App returns to NORMAL state, same line position

**Expected Result**: Cancel gracefully, no side effects

## Scenario 9: Canceling Range Selection

**Maps to**: Edge Case (FR-009)

**Steps**:
1. Navigate to diff pane

2. Press `s` to enter Select Mode

3. Use arrow keys to expand selection

4. Press `Esc` (instead of Enter)

5. **Verify**:
   - Selection highlight disappears
   - Mode returns to NORMAL
   - Status bar shows normal keybindings
   - No input dialog appears
   - No comment created

**Expected Result**: Select Mode exits cleanly without creating comment

## Scenario 10: File Navigation Lock in Select Mode

**Maps to**: Edge Case (FR-016)

**Steps**:
1. In diff pane, press `s` to enter Select Mode

2. Press `Tab` to attempt switching focus to file list

3. **Observe**: Focus may switch (Tab is global), but...

4. Try to navigate files with arrow keys

5. **Observe**:
   - Toast/message appears: "Exit Select Mode first (Esc)"
   - File list selection does NOT change
   - Arrow keys are ignored

6. Press `Tab` to return to diff pane

7. Press `Esc` to exit Select Mode

8. Press `Tab` again to go to file list

9. Use arrow keys to navigate files

10. **Verify**: File navigation works normally now

**Expected Result**: File switching blocked during Select Mode, prevented gracefully

## Performance Validation

**Maps to**: FR-018 (100 comment capacity)

**Steps**:
1. Add comments until reaching ~100 comments:
   - Mix of line, range, and file-level comments
   - Use different files

2. **Verify**:
   - All operations remain responsive (<50ms feel)
   - Markers render quickly during scroll
   - No lag when switching files
   - Memory usage remains low (~20KB for comment storage)

3. Attempt to add 101st comment:
   - **Verify**: Error message "Comment limit reached (100 max)"
   - No comment created

**Expected Result**: System handles capacity limit gracefully

## Testing Commands

Run automated tests to validate these scenarios:

```bash
# All Milestone 3 integration tests
uv run pytest tests/integration/test_milestone3/ -v

# Specific test suites
uv run pytest tests/integration/test_milestone3/test_single_line_comment.py -v
uv run pytest tests/integration/test_milestone3/test_range_comment.py -v
uv run pytest tests/integration/test_milestone3/test_visual_markers.py -v
uv run pytest tests/integration/test_milestone3/test_status_bar.py -v

# Contract tests (API validation)
uv run pytest tests/contract/test_milestone3/ -v
```

## Expected Outputs

At the end of Milestone 3:
- Comments are stored in memory (verified via tests)
- Visual markers display correctly
- Status bar updates based on context
- All keybindings work as specified
- Edge cases handled gracefully

**Note**: Comments are NOT persisted to disk in Milestone 3. Markdown output is added in Milestone 4.

## Troubleshooting

**Issue**: Marker not appearing after adding comment
- **Check**: Ensure you're on a valid diff line (not a header or separator)
- **Check**: Verify comment text was not empty

**Issue**: Status bar not updating
- **Check**: Ensure mode transitions are working (watch for SELECT mode indicator)
- **Check**: Verify focus state changes (Tab key cycles focus)

**Issue**: Select Mode not highlighting
- **Check**: Press `s` while in diff pane (not file pane)
- **Check**: Ensure mode is NORMAL before entering Select Mode

**Issue**: File navigation not blocked in Select Mode
- **Check**: Verify FilesPane is checking `app.mode` before processing arrow keys
- **Check**: Look for toast message indicating lock

## Next Steps

After completing this quickstart:
1. Run all integration tests to validate scenarios
2. Run contract tests to validate API behavior
3. Check performance with large diffs (scripts/generate_large_diff.py --preset max)
4. Proceed to Milestone 4: Markdown output generation
