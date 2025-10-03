# Quickstart Guide: TUI Rendering & Navigation

**Feature**: Milestone 2 - TUI Rendering & Navigation
**Date**: 2025-10-01
**Purpose**: Validate Milestone 2 acceptance scenarios via manual/automated quickstart tests.

## Prerequisites
- RacGoat installed via `uv sync`
- Git repository with uncommitted changes OR sample diff file

## Test Scenarios

### Scenario 1: Two-Pane Layout with Multiple Files
**Acceptance Criteria**: FR-001, FR-002, FR-013 (spec.md lines 64-65)

**Given**: A git diff with 3 changed files

**Setup**:
```bash
# Create test diff with 3 files
cat > /tmp/test_diff.txt <<'EOF'
diff --git a/src/main.py b/src/main.py
index abc123..def456 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,4 @@
+# New comment
 def main():
     print("hello")
     return 0
diff --git a/src/utils.py b/src/utils.py
index 111222..333444 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -10,5 +10,6 @@ def helper():
     pass
+    # Added helper comment

 def old_function():
-    return False
+    return True
diff --git a/tests/test_main.py b/tests/test_main.py
new file mode 100644
index 0000000..999888
--- /dev/null
+++ b/tests/test_main.py
@@ -0,0 +1,2 @@
+def test_main():
+    assert True
EOF
```

**When**: Run RacGoat with test diff
```bash
cat /tmp/test_diff.txt | uv run python -m racgoat
```

**Then**: Verify the following (manual or automated):
1. ✅ Two-pane layout visible (Files Pane left, Diff Pane right)
2. ✅ Files Pane shows 3 files:
   - `src/main.py (+1 -0)`
   - `src/utils.py (+1 -1)`
   - `tests/test_main.py (+2 -0)`
3. ✅ First file (`src/main.py`) is auto-selected
4. ✅ Diff Pane shows `src/main.py` diff content with:
   - Green `+# New comment` line
   - Context lines in dim/white
   - Post-change line numbers (1, 2, 3, 4)
5. ✅ Diff Pane has initial focus (border color = $primary)

**Automated Test**: `tests/integration/test_milestone2/test_two_pane_layout.py::test_multi_file_diff_shows_two_panes()`

---

### Scenario 2: File List Navigation with Arrow Keys
**Acceptance Criteria**: FR-005, FR-007 (spec.md lines 66-67)

**Given**: Same 3-file diff from Scenario 1

**When**: User navigates Files Pane with arrow keys
1. Press `Tab` to focus Files Pane (border changes to $primary)
2. Press `down` arrow twice

**Then**: Verify:
1. ✅ First press: Selection moves to `src/utils.py`
   - Diff Pane updates to show `src/utils.py` diff
2. ✅ Second press: Selection moves to `tests/test_main.py`
   - Diff Pane updates to show `tests/test_main.py` diff
3. ✅ Each file's diff hunks displayed correctly with:
   - Green for `+` lines
   - Red for `-` lines
   - Dim for context lines
   - Post-change line numbers

**Automated Test**: `tests/integration/test_milestone2/test_navigation.py::test_arrow_keys_navigate_files_and_update_diff()`

---

### Scenario 3: Focus Switching with Tab Key
**Acceptance Criteria**: FR-006 (spec.md line 68)

**Given**: Same 3-file diff from Scenario 1

**When**: User presses Tab multiple times
1. Initial state: Diff Pane focused
2. Press `Tab` → Files Pane focused
3. Press `Tab` → Diff Pane focused
4. Press `Tab` → Files Pane focused (cycles)

**Then**: Verify:
1. ✅ Visual focus indicator updates on each press (border color toggles)
2. ✅ Arrow keys control the focused pane:
   - When Files Pane focused: arrow keys navigate file list
   - When Diff Pane focused: arrow keys scroll diff content
3. ✅ Focus cycles between two panes indefinitely

**Automated Test**: `tests/integration/test_milestone2/test_navigation.py::test_tab_switches_focus_between_panes()`

---

### Scenario 4: Empty Diff Handling
**Acceptance Criteria**: FR-009 (spec.md line 69)

**Given**: An empty git diff (no changes)

**Setup**:
```bash
# Create empty diff
echo "" | uv run python -m racgoat
```

**When**: Run RacGoat with empty input

**Then**: Verify:
1. ✅ Two-pane layout is NOT displayed
2. ✅ Centered message displayed: "No changes to review 🦝🐐" (or similar whimsical message)
3. ✅ App remains running (does not auto-exit)
4. ✅ Press `q` to quit successfully

**Automated Test**: `tests/integration/test_milestone2/test_empty_diff.py::test_empty_diff_shows_no_changes_message()`

---

### Scenario 5: Diff Rendering with ANSI Colors
**Acceptance Criteria**: FR-003, FR-004 (spec.md lines 66-67)

**Given**: A diff with additions, deletions, and context lines

**Setup**:
```bash
cat > /tmp/color_test_diff.txt <<'EOF'
diff --git a/example.py b/example.py
index aaa111..bbb222 100644
--- a/example.py
+++ b/example.py
@@ -5,8 +5,9 @@ def func():
     # Context line 1
     x = 10
-    y = 20  # Removed line
+    y = 30  # Modified line (shown as remove + add)
     z = 40
+    # New comment added
     return x + y + z
EOF

cat /tmp/color_test_diff.txt | uv run python -m racgoat
```

**Then**: Verify Diff Pane rendering:
1. ✅ Context lines (lines 5-6): Dim/white color, post-change line numbers
   ```
   [dim]  5[/]  # Context line 1
   [dim]  6[/]  x = 10
   ```
2. ✅ Removed line: Red, no line number
   ```
   [red]-y = 20  # Removed line[/]
   ```
3. ✅ Added lines: Green, post-change line numbers
   ```
   [dim]  7[/] [green]+y = 30  # Modified line[/]
   [dim]  9[/] [green]+# New comment added[/]
   ```
4. ✅ Line numbers increment correctly (5, 6, 7, 8, 9, 10)

**Automated Test**: `tests/integration/test_milestone2/test_rendering.py::test_diff_pane_ansi_colors_and_line_numbers()`

---

### Scenario 6: Single File Diff
**Acceptance Criteria**: FR-015 (spec.md line 72)

**Given**: A diff with only one changed file

**Setup**:
```bash
cat > /tmp/single_file_diff.txt <<'EOF'
diff --git a/README.md b/README.md
index fff888..ggg999 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,3 @@
 # Project Title
+## New Section
 Description here.
EOF

cat /tmp/single_file_diff.txt | uv run python -m racgoat
```

**Then**: Verify:
1. ✅ Two-pane layout is STILL displayed (not single-pane)
2. ✅ Files Pane shows 1 file: `README.md (+1 -0)`
3. ✅ Diff Pane shows `README.md` diff content
4. ✅ Layout consistency maintained (same UI as multi-file case)

**Automated Test**: `tests/integration/test_milestone2/test_edge_cases.py::test_single_file_maintains_two_pane_layout()`

---

### Scenario 7: Long File Path Truncation
**Acceptance Criteria**: FR-014 (spec.md line 73)

**Given**: A diff with a very long file path

**Setup**:
```bash
cat > /tmp/long_path_diff.txt <<'EOF'
diff --git a/src/deeply/nested/directory/structure/with/many/levels/and/a/very/long/filename.py b/src/deeply/nested/directory/structure/with/many/levels/and/a/very/long/filename.py
index 123456..789abc 100644
--- a/src/deeply/nested/directory/structure/with/many/levels/and/a/very/long/filename.py
+++ b/src/deeply/nested/directory/structure/with/many/levels/and/a/very/long/filename.py
@@ -1 +1,2 @@
 # Original line
+# Added line
EOF

cat /tmp/long_path_diff.txt | uv run python -m racgoat
```

**Then**: Verify Files Pane display:
1. ✅ File path is truncated to fit pane width (assume 30% of 80-char screen = 24 chars)
2. ✅ Truncation format: `src/deeply...filename.py` (preserves start and end)
3. ✅ Full path NOT visible (no overflow, no wrapping)
4. ✅ Line count stats appended: `(+1 -0)` after truncated path

**Automated Test**: `tests/integration/test_milestone2/test_edge_cases.py::test_long_file_path_truncation()`

---

### Scenario 8: Quit Application
**Acceptance Criteria**: FR-008 (spec.md line 68)

**Given**: Any valid diff displayed in two-pane layout

**When**: User presses `q` key

**Then**: Verify:
1. ✅ Application exits immediately
2. ✅ Exit code is 0 (success)
3. ✅ No error messages or warnings
4. ✅ Terminal state restored (no leftover UI artifacts)

**Automated Test**: `tests/integration/test_milestone2/test_quit.py::test_q_key_quits_application()`

---

## Performance Validation

### Scenario 9: Render 20 Files / 2k Lines
**Acceptance Criteria**: NFR-001, NFR-002 (spec.md lines 96-97)

**Given**: A diff with 20 files and ~2000 total diff lines

**Setup**:
```bash
# Generate large test diff (20 files, 100 lines each = 2000 total)
python scripts/generate_large_diff.py --files 20 --lines-per-file 100 > /tmp/large_diff.txt
cat /tmp/large_diff.txt | uv run python -m racgoat --profile
```

**Then**: Measure and verify:
1. ✅ Initial render time: ≤100ms (from stdin read to UI display)
2. ✅ File selection response: ≤100ms (arrow key → diff update)
3. ✅ Tab focus switch: ≤100ms (Tab key → border update)
4. ✅ Scroll responsiveness: ≤100ms per scroll event (arrow up/down in Diff Pane)

**Measurement Method**:
- Use Textual's `--dev` mode with `Elapsed` widget
- Or programmatic timing in integration test: `start = time.perf_counter(); ...; assert (time.perf_counter() - start) < 0.1`

**Automated Test**: `tests/integration/test_milestone2/test_performance.py::test_large_diff_renders_within_100ms()`

---

## Test Execution Checklist

### Manual Quickstart (Human Validation)
Run all scenarios 1-9 manually to validate UX:
- [ ] Scenario 1: Two-pane layout ✅
- [ ] Scenario 2: Arrow key navigation ✅
- [ ] Scenario 3: Tab focus switching ✅
- [ ] Scenario 4: Empty diff message ✅
- [ ] Scenario 5: ANSI color rendering ✅
- [ ] Scenario 6: Single file layout ✅
- [ ] Scenario 7: Long path truncation ✅
- [ ] Scenario 8: Quit with `q` ✅
- [ ] Scenario 9: Performance (20 files / 2k lines) ✅

### Automated Integration Tests
Run all automated tests to validate contracts:
```bash
uv run pytest tests/integration/test_milestone2/ -v
```

Expected output:
```
tests/integration/test_milestone2/test_two_pane_layout.py::test_multi_file_diff_shows_two_panes PASSED
tests/integration/test_milestone2/test_navigation.py::test_arrow_keys_navigate_files_and_update_diff PASSED
tests/integration/test_milestone2/test_navigation.py::test_tab_switches_focus_between_panes PASSED
tests/integration/test_milestone2/test_empty_diff.py::test_empty_diff_shows_no_changes_message PASSED
tests/integration/test_milestone2/test_rendering.py::test_diff_pane_ansi_colors_and_line_numbers PASSED
tests/integration/test_milestone2/test_edge_cases.py::test_single_file_maintains_two_pane_layout PASSED
tests/integration/test_milestone2/test_edge_cases.py::test_long_file_path_truncation PASSED
tests/integration/test_milestone2/test_quit.py::test_q_key_quits_application PASSED
tests/integration/test_milestone2/test_performance.py::test_large_diff_renders_within_100ms PASSED
======================= 9 passed in 2.5s =======================
```

---

## Success Criteria
Milestone 2 is complete when:
1. ✅ All 9 quickstart scenarios pass (manual or automated)
2. ✅ All contract tests pass (15 widget contract tests)
3. ✅ All integration tests pass (9 scenario tests)
4. ✅ Performance NFRs validated (<100ms response time)
5. ✅ Constitution Principle III satisfied (TDD: tests written first, all passing)

---
**Quickstart Complete**: 9 acceptance scenarios documented, 9 integration tests defined. Ready for task generation.
