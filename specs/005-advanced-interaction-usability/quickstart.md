# Quickstart Guide: Milestone 5 - Advanced Interaction & Usability

## Overview

Milestone 5 introduces three major enhancements to the RacGoat review workflow:

1. **Comment Edit/Delete** (`e` key) - Modify or remove existing comments without recreating them
2. **Search Functionality** (`/` key) - Quickly find code patterns within diffs
3. **Help Overlay** (`?` key) - View all available keybindings without leaving the application

This guide maps each acceptance scenario from the spec to concrete test scenarios and integration test references.

---

## Prerequisites

Before validating Milestone 5 features, ensure the following from previous milestones are complete:

### From Milestone 3 (Core Commenting Engine):
- ✅ Line-level comments (`a` key)
- ✅ Range comments (Select Mode via `s` key)
- ✅ File-level comments (`c` key)
- ✅ Visual markers (`*`) displaying in Diff Pane
- ✅ Context-sensitive status bar showing available keybindings
- ✅ In-memory comment storage (CommentStore)

### From Milestone 4 (Markdown Output):
- ✅ Markdown serialization of comments
- ✅ File output via `-o` flag
- ✅ Git metadata extraction (branch name, commit SHA)
- ✅ Atomic file write with error recovery

---

## Quick Test Scenarios

### Scenario 1: Edit Existing Line Comment

**Acceptance Criteria:** AS-001 from spec.md

**User Action:**
1. Launch RacGoat with a diff: `uv run python -m racgoat < sample.diff`
2. Navigate to a file in the Files Pane using arrow keys
3. Press `Tab` to focus the Diff Pane
4. Navigate to line 42 using arrow keys
5. Press `a` to create a line comment: "This needs refactoring"
6. Navigate back to line 42
7. Press `e` to edit the comment
8. Modify text to: "This needs refactoring - extract to helper method"
9. Press Enter to confirm

**Expected Outcome:**
- Edit dialog appears pre-populated with "This needs refactoring"
- Input field shows cursor ready for editing
- Modified comment "This needs refactoring - extract to helper method" is saved
- Visual marker `*` remains on line 42
- Status bar shows "e - Edit comment" when on line 42

**Verification:**
- Check status bar displays `e - Edit comment` when cursor on line 42
- Verify dialog input pre-populated with original text
- Confirm comment_store reflects updated text
- After quitting with `q`, verify `review.md` contains updated comment text

**Integration Test:** `tests/integration/test_milestone5/test_edit_scenarios.py::test_edit_line_comment_updates_text`

---

### Scenario 2: Delete Comment by Clearing Text

**Acceptance Criteria:** AS-002 from spec.md

**User Action:**
1. Navigate to a line with an existing comment (e.g., line 15)
2. Press `e` to edit the comment
3. Delete all text in the edit dialog (Ctrl+U or backspace)
4. Press Enter to confirm

**Expected Outcome:**
- Edit dialog appears with original text
- Clearing text and confirming deletes the comment
- Visual marker `*` disappears from line 15
- Status bar no longer shows "e - Edit comment" when on line 15

**Verification:**
- Comment removed from comment_store
- No visual marker displayed on line 15
- `review.md` does not contain the deleted comment after quit
- Status bar updates to show only default keybindings

**Integration Test:** `tests/integration/test_milestone5/test_edit_scenarios.py::test_delete_comment_by_clearing_text`

---

### Scenario 3: Initiate Search Mode

**Acceptance Criteria:** AS-003 from spec.md

**User Action:**
1. Navigate to the Diff Pane (press `Tab` if needed)
2. Press `/` to initiate search

**Expected Outcome:**
- Search input field appears at bottom of Diff Pane or status bar area
- Cursor positioned in search input field
- Status bar shows search-related keybindings (Enter to search, Esc to cancel)

**Verification:**
- Search input widget is visible and has focus
- User can type search query
- Status bar reflects search mode context

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_initiate_search_mode`

---

### Scenario 4: Execute Search and Highlight Matches

**Acceptance Criteria:** AS-004 from spec.md

**User Action:**
1. Press `/` to enter search mode
2. Type search query: "TODO"
3. Press Enter to execute search

**Expected Outcome:**
- All instances of "TODO" in the current file are highlighted
- Cursor jumps to the first match
- Status bar shows match counter: "1/5 matches" (if 5 matches found)
- Current match is visually distinguished from other matches

**Verification:**
- All matches are highlighted in the Diff Pane
- First match is scrolled into view
- Match counter displays correct format: `current/total`
- Search is case-sensitive (only exact "TODO" matches, not "todo")

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_search_highlights_all_matches`

---

### Scenario 5: Navigate to Next Match

**Acceptance Criteria:** AS-005 from spec.md

**User Action:**
1. Execute a search with multiple matches (e.g., "return" in a function-heavy file)
2. Press `n` to jump to next match
3. Press `n` again to jump to third match

**Expected Outcome:**
- Cursor moves to next match in sequence
- Match counter updates: "2/7 matches", then "3/7 matches"
- Current match is visually distinguished
- Viewport scrolls to keep current match visible

**Verification:**
- Match counter increments correctly
- Cursor position changes to next match line
- At last match, pressing `n` wraps to first match
- All match highlights remain visible

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_navigate_next_match`

---

### Scenario 6: Navigate to Previous Match

**Acceptance Criteria:** AS-006 from spec.md

**User Action:**
1. Execute a search with multiple matches
2. Navigate to third match using `n` twice
3. Press `N` (Shift+n) to jump to previous match

**Expected Outcome:**
- Cursor moves to previous match in sequence
- Match counter updates: "2/7 matches"
- Current match is visually distinguished
- Viewport scrolls to keep current match visible

**Verification:**
- Match counter decrements correctly
- Cursor position changes to previous match line
- At first match, pressing `N` wraps to last match
- All match highlights remain visible

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_navigate_previous_match`

---

### Scenario 7: Display Help Overlay

**Acceptance Criteria:** AS-007 from spec.md

**User Action:**
1. From any screen in the application, press `?`

**Expected Outcome:**
- Help overlay appears centered on screen
- All keybindings are displayed organized by category:
  - **Navigation**: Arrow keys, Tab, PgUp/PgDown
  - **Commenting**: a (line comment), c (file comment), s (range select), e (edit)
  - **Search**: / (search), n (next), N (previous), Esc (exit search)
  - **General**: q (quit), ? (help)
- Each keybinding shows: key, action name, description

**Verification:**
- Help overlay is visible and readable
- All 15+ keybindings are listed
- Categories are clearly labeled
- Help overlay is scrollable if taller than terminal

**Integration Test:** `tests/integration/test_milestone5/test_help_overlay.py::test_display_help_overlay`

---

### Scenario 8: Dismiss Help Overlay

**Acceptance Criteria:** AS-008 from spec.md

**User Action:**
1. Press `?` to open help overlay
2. Press `?` again (or `Esc`) to close it

**Expected Outcome:**
- Help overlay disappears
- User returns to previous context (Files Pane or Diff Pane focus unchanged)
- Application state is preserved (search state, selected file, comments intact)

**Verification:**
- Help overlay is no longer visible
- Focus returns to previously focused widget
- No state changes occurred during help display

**Integration Test:** `tests/integration/test_milestone5/test_help_overlay.py::test_dismiss_help_overlay`

---

### Scenario 9: Edit Range Comment

**Acceptance Criteria:** AS-009 from spec.md

**User Action:**
1. Navigate to the Diff Pane
2. Press `s` to enter Select Mode
3. Use arrow keys to select lines 10-15
4. Press Enter and add comment: "This block handles error cases"
5. Navigate to any line in range 10-15
6. Press `e` to edit the range comment
7. Modify text to: "This block handles error cases - consider extracting"
8. Press Enter to confirm

**Expected Outcome:**
- Edit dialog appears with original range comment text
- Modified comment is saved
- Visual markers remain on lines 10-15
- Comment type remains RANGE (not converted to LINE)

**Verification:**
- Pressing `e` on any line in range 10-15 edits the same comment
- comment_store shows RANGE comment type unchanged
- `review.md` shows updated comment under range section
- Visual markers remain consistent across range

**Integration Test:** `tests/integration/test_milestone5/test_edit_scenarios.py::test_edit_range_comment_preserves_type`

---

### Scenario 10: Edit File-Level Comment

**Acceptance Criteria:** AS-010 from spec.md

**User Action:**
1. Navigate to a file in the Files Pane
2. Press `c` to add file-level comment: "Review security implications"
3. Ensure the file is still selected
4. Press `e` to edit the file-level comment
5. Modify text to: "Review security implications - check auth flow"
6. Press Enter to confirm

**Expected Outcome:**
- Edit dialog appears with original file-level comment text
- Modified comment is saved
- File-level comment marker remains visible (if implemented)
- Comment type remains FILE

**Verification:**
- comment_store shows FILE comment type unchanged
- `review.md` shows updated comment under file-level section
- Pressing `e` while viewing the file edits the file comment (not line comments)

**Integration Test:** `tests/integration/test_milestone5/test_edit_scenarios.py::test_edit_file_comment_preserves_type`

---

## Edge Case Scenarios

### Edge Case 1: Edit on Non-Commented Line

**Spec Reference:** Edge Cases section, FR-034

**User Action:**
1. Navigate to a line with no comment (e.g., line 5)
2. Press `e`

**Expected Outcome:**
- Nothing happens (silent ignore)
- No error message displayed
- No dialog appears

**Verification:**
- Status bar does not show "e - Edit comment" on uncommented lines
- Pressing `e` has no effect
- Application remains in normal state

**Integration Test:** `tests/integration/test_milestone5/test_edge_cases.py::test_edit_on_uncommented_line_does_nothing`

---

### Edge Case 2: Search with No Matches

**Spec Reference:** Edge Cases section, FR-018

**User Action:**
1. Press `/` to enter search mode
2. Type search query: "XYZABC123" (pattern that doesn't exist)
3. Press Enter to execute search

**Expected Outcome:**
- Status bar displays: "0/0 matches"
- No highlights appear in Diff Pane
- Cursor position unchanged

**Verification:**
- Match counter shows "0/0 matches"
- No visual highlights in diff text
- Search mode remains active (can type new query)

**Integration Test:** `tests/integration/test_milestone5/test_edge_cases.py::test_search_no_matches_shows_zero_counter`

---

### Edge Case 3: Search State Reset on File Switch

**Spec Reference:** Edge Cases section, FR-023

**User Action:**
1. Execute a search in file1.py with matches highlighted
2. Press `Tab` to focus Files Pane
3. Press arrow key to select file2.py
4. Press `Tab` to return to Diff Pane

**Expected Outcome:**
- All search highlights are cleared when switching to file2.py
- Search query is cleared
- Status bar no longer shows match counter
- Search mode is exited

**Verification:**
- No highlights visible in file2.py
- Pressing `n` or `N` has no effect (search not active)
- Must press `/` again to initiate new search

**Integration Test:** `tests/integration/test_milestone5/test_edge_cases.py::test_search_state_resets_on_file_switch`

---

### Edge Case 4: Exit Search Mode with Esc

**Spec Reference:** FR-021, FR-022

**User Action:**
1. Execute a search with multiple matches highlighted
2. Press `Esc` to exit search mode

**Expected Outcome:**
- All search highlights are cleared immediately
- Search query is cleared
- Status bar returns to normal mode keybindings
- Cursor position unchanged

**Verification:**
- No highlights visible in Diff Pane
- Search input field is hidden
- Status bar shows normal mode keys (a, c, s, q, ?)

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_exit_search_clears_highlights`

---

### Edge Case 5: Edit Comment Then Cancel

**Spec Reference:** FR-009

**User Action:**
1. Navigate to a line with comment: "Original comment"
2. Press `e` to edit
3. Change text to: "Modified comment"
4. Press `Esc` to cancel (instead of Enter to confirm)

**Expected Outcome:**
- Edit dialog closes
- Original comment text "Original comment" is preserved
- No changes saved to comment_store

**Verification:**
- comment_store still contains "Original comment"
- Visual marker unchanged
- Pressing `e` again shows original text

**Integration Test:** `tests/integration/test_milestone5/test_edit_scenarios.py::test_cancel_edit_preserves_original`

---

### Edge Case 6: Help Overlay Taller Than Terminal

**Spec Reference:** Edge Cases section, FR-030

**User Action:**
1. Resize terminal to very small height (e.g., 10 lines)
2. Press `?` to open help overlay

**Expected Outcome:**
- Help overlay appears scrollable
- User can scroll through all keybindings using arrow keys or PgUp/PgDown
- Scroll indicator visible (if implemented)

**Verification:**
- All keybindings are accessible via scrolling
- No content is cut off or hidden
- Overlay remains usable in small terminals

**Integration Test:** `tests/integration/test_milestone5/test_edge_cases.py::test_help_overlay_scrollable_in_small_terminal`

---

### Edge Case 7: Search Wraps Around

**Spec Reference:** Edge Cases section

**User Action:**
1. Execute search with 3 matches
2. Navigate to third match (match 3/3)
3. Press `n` to go forward

**Expected Outcome:**
- Cursor wraps to first match
- Match counter shows "1/3 matches"

**Verification:**
- Cursor position jumps to first match line
- No error or indication of end-of-matches
- Similarly, pressing `N` at first match wraps to last match

**Integration Test:** `tests/integration/test_milestone5/test_search_scenarios.py::test_search_navigation_wraps_around`

---

### Edge Case 8: Edit During Select Mode

**Spec Reference:** Edge Cases section

**User Action:**
1. Press `s` to enter Select Mode
2. Begin selecting a range
3. Press `e` while in Select Mode

**Expected Outcome:**
- If current line has a comment, edit dialog appears
- Select Mode is exited
- OR: `e` is ignored while in Select Mode (implementation choice)

**Verification:**
- Behavior is consistent and documented
- No crashes or undefined states
- User can complete edit or return to Select Mode

**Integration Test:** `tests/integration/test_milestone5/test_edge_cases.py::test_edit_during_select_mode`

---

## Performance Validation

### Performance Test 1: Search in Large Diff

**Requirement:** Search operation must complete in <200ms for files up to 2000 lines

**User Action:**
1. Generate large diff: `uv run python scripts/generate_large_diff.py --preset max -o large.diff`
2. Launch RacGoat: `uv run python -m racgoat < large.diff`
3. Navigate to largest file
4. Press `/` and search for common pattern (e.g., "def")
5. Press Enter

**Expected Outcome:**
- Search completes in <200ms
- All matches are highlighted
- UI remains responsive

**Verification:**
- Use pytest timing assertions in integration test
- Verify no UI lag or freezing
- Match counter displays promptly

**Integration Test:** `tests/integration/test_milestone5/test_performance.py::test_search_large_file_performance`

---

### Performance Test 2: Edit Comment with Large Comment Store

**Requirement:** Edit operation must complete in <100ms even with 100+ comments

**User Action:**
1. Create 100+ comments across multiple files
2. Navigate to a line with a comment
3. Press `e` to edit
4. Modify text and confirm

**Expected Outcome:**
- Edit dialog appears instantly (<100ms)
- Comment update saves instantly
- No performance degradation

**Verification:**
- Use pytest timing assertions
- Verify comment_store lookup is O(1) or O(log n)

**Integration Test:** `tests/integration/test_milestone5/test_performance.py::test_edit_comment_performance_with_large_store`

---

## Markdown Output Validation

### Validation 1: Edited Comments in Output

**User Action:**
1. Create line comment: "Original text"
2. Edit to: "Updated text"
3. Quit with `q`

**Expected Outcome:**
- `review.md` contains "Updated text"
- Original text is not present in output

**Verification:**
- Read `review.md` file
- Search for "Updated text" in line comment section
- Confirm "Original text" does not appear

**Integration Test:** `tests/integration/test_milestone5/test_markdown_output.py::test_edited_comments_appear_in_output`

---

### Validation 2: Deleted Comments Not in Output

**User Action:**
1. Create line comment: "To be deleted"
2. Edit and clear all text to delete comment
3. Quit with `q`

**Expected Outcome:**
- `review.md` does not contain "To be deleted"
- Line is not listed in output

**Verification:**
- Read `review.md` file
- Confirm deleted comment is absent
- Verify line number is not referenced

**Integration Test:** `tests/integration/test_milestone5/test_markdown_output.py::test_deleted_comments_not_in_output`

---

## Integration Test Mapping

### Test File Structure

```
tests/integration/test_milestone5/
├── __init__.py
├── test_edit_scenarios.py          # AS-001, AS-002, AS-009, AS-010, Edge Case 5
├── test_search_scenarios.py        # AS-003, AS-004, AS-005, AS-006, Edge Case 4, Edge Case 7
├── test_help_overlay.py            # AS-007, AS-008, Edge Case 6
├── test_edge_cases.py              # Edge Cases 1, 2, 3, 8
├── test_performance.py             # Performance Tests 1-2
└── test_markdown_output.py         # Markdown Validation 1-2
```

### Test Coverage Matrix

| Acceptance Scenario | Integration Test File | Test Function |
|---------------------|----------------------|---------------|
| AS-001: Edit line comment | `test_edit_scenarios.py` | `test_edit_line_comment_updates_text` |
| AS-002: Delete by clearing | `test_edit_scenarios.py` | `test_delete_comment_by_clearing_text` |
| AS-003: Initiate search | `test_search_scenarios.py` | `test_initiate_search_mode` |
| AS-004: Search highlights | `test_search_scenarios.py` | `test_search_highlights_all_matches` |
| AS-005: Next match | `test_search_scenarios.py` | `test_navigate_next_match` |
| AS-006: Previous match | `test_search_scenarios.py` | `test_navigate_previous_match` |
| AS-007: Show help | `test_help_overlay.py` | `test_display_help_overlay` |
| AS-008: Dismiss help | `test_help_overlay.py` | `test_dismiss_help_overlay` |
| AS-009: Edit range comment | `test_edit_scenarios.py` | `test_edit_range_comment_preserves_type` |
| AS-010: Edit file comment | `test_edit_scenarios.py` | `test_edit_file_comment_preserves_type` |

| Edge Case | Integration Test File | Test Function |
|-----------|----------------------|---------------|
| Edit on uncommented line | `test_edge_cases.py` | `test_edit_on_uncommented_line_does_nothing` |
| Search no matches | `test_edge_cases.py` | `test_search_no_matches_shows_zero_counter` |
| File switch resets search | `test_edge_cases.py` | `test_search_state_resets_on_file_switch` |
| Exit search clears highlights | `test_search_scenarios.py` | `test_exit_search_clears_highlights` |
| Cancel edit preserves original | `test_edit_scenarios.py` | `test_cancel_edit_preserves_original` |
| Help scrollable in small terminal | `test_edge_cases.py` | `test_help_overlay_scrollable_in_small_terminal` |
| Search wraps around | `test_search_scenarios.py` | `test_search_navigation_wraps_around` |
| Edit during Select Mode | `test_edge_cases.py` | `test_edit_during_select_mode` |

---

## Running the Tests

### Run All Milestone 5 Tests
```bash
uv run pytest tests/integration/test_milestone5/ -v
```

### Run Specific Test Categories
```bash
# Edit/Delete functionality
uv run pytest tests/integration/test_milestone5/test_edit_scenarios.py -v

# Search functionality
uv run pytest tests/integration/test_milestone5/test_search_scenarios.py -v

# Help overlay
uv run pytest tests/integration/test_milestone5/test_help_overlay.py -v

# Edge cases
uv run pytest tests/integration/test_milestone5/test_edge_cases.py -v

# Performance tests
uv run pytest tests/integration/test_milestone5/test_performance.py -v

# Markdown output validation
uv run pytest tests/integration/test_milestone5/test_markdown_output.py -v
```

### Run with Coverage
```bash
uv run pytest tests/integration/test_milestone5/ --cov=racgoat --cov-report=html -v
```

---

## Manual Testing Workflow

For hands-on validation beyond automated tests:

1. **Generate sample diff:**
   ```bash
   git diff HEAD~1 > sample.diff
   ```

2. **Launch RacGoat:**
   ```bash
   uv run python -m racgoat -o review.md < sample.diff
   ```

3. **Test edit workflow:**
   - Add comments with `a`, `c`, `s`
   - Edit comments with `e`
   - Verify visual markers and status bar

4. **Test search workflow:**
   - Press `/` to search
   - Try patterns like "def", "import", "TODO"
   - Navigate with `n` and `N`
   - Exit with `Esc`

5. **Test help overlay:**
   - Press `?` to view help
   - Scroll if needed
   - Dismiss with `?` or `Esc`

6. **Verify output:**
   ```bash
   cat review.md
   ```
   - Check edited comments appear
   - Confirm deleted comments absent

---

## Success Criteria

Milestone 5 is complete when:

- ✅ All 10 acceptance scenarios pass integration tests
- ✅ All 8 edge cases handled correctly
- ✅ Performance tests meet <200ms targets
- ✅ Markdown output reflects all edits/deletes
- ✅ Status bar updates correctly for all modes
- ✅ Help overlay displays all keybindings
- ✅ No regressions in Milestone 3-4 functionality

---

## Next Steps

After validating Milestone 5:

1. **User Acceptance Testing:** Have team members perform manual testing with real diffs
2. **Performance Benchmarking:** Test with 100-file, 10k-line diffs (Milestone 6 prep)
3. **Documentation:** Update main README.md with new keybindings
4. **PRD Compliance:** Verify all Milestone 5 requirements from docs/prd.md are met
