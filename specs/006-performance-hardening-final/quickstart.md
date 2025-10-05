# Quickstart: Performance Hardening & Final Polish

**Status (2025-01-04)**: ✅ Core implementation complete. All scenarios below can be manually validated.

## Prerequisites
```bash
uv sync
uv run pytest tests/contract/test_error_handling.py -v  # Verify error handling
uv run pytest tests/contract/test_binary_filtering.py -v  # Verify binary filtering
```

## Scenario 1: Large Diff Performance (FR-001, FR-002)

**Goal**: Verify 100 files / 10k lines loads within 2 seconds

```bash
# Generate max-size test diff
uv run python scripts/generate_large_diff.py --preset max -o /tmp/large.diff

# Launch with timing
time uv run python -m racgoat < /tmp/large.diff
```

**Expected**:
- Real time: < 2s (from launch to TUI render)
- Files pane: Shows 100 files
- Diff pane: First file rendered, scrollable
- Quit with `q`: review.md NOT created (no comments)

**Validation**:
```bash
# Automated test
uv run pytest tests/integration/test_performance/test_initial_load.py -v

# Expected output:
# test_large_diff_load_under_2s PASSED (1.85s)
```

---

## Scenario 2: Viewport Rendering (FR-003)

**Goal**: Scroll through 1000+ line file smoothly (< 100ms per scroll)

```bash
# Generate single large file diff
uv run python scripts/generate_large_diff.py --files 1 --lines 2000 -o /tmp/scroll-test.diff

# Launch and test scrolling
uv run python -m racgoat < /tmp/scroll-test.diff
```

**Actions**:
1. Press `PgDn` repeatedly → should be instant (< 100ms visual delay)
2. Press `End` → jumps to bottom instantly
3. Press `Home` → jumps to top instantly
4. Hold `Down` arrow → smooth continuous scroll

**Expected**:
- No lag or stuttering
- Line numbers update correctly
- Only ~50 lines visible at once (viewport)

**Validation**:
```bash
uv run pytest tests/integration/test_performance/test_scroll_responsiveness.py -v

# Expected output:
# test_rapid_scroll_under_100ms PASSED
# test_viewport_only_renders_visible_lines PASSED
```

---

## Scenario 3: Malformed Diff Handling (FR-006 to FR-011)

**Goal**: Application continues functioning with malformed hunks

```bash
# Create diff with intentional errors
cat > /tmp/malformed.diff << 'EOF'
diff --git a/file1.py b/file1.py
@@ -1,2 +1,2 @@
-old line
+new line

diff --git a/file2.py b/file2.py
@@ invalid header @@
this is malformed content
no proper diff syntax

diff --git a/file3.py b/file3.py
@@ -10,3 +10,3 @@
-valid
+hunk
 here
EOF

uv run python -m racgoat < /tmp/malformed.diff
```

**Expected**:
- Files pane: Shows 3 files (file1.py, file2.py, file3.py)
- Select file2.py → Diff pane shows:
  ```
  [⚠ UNPARSEABLE]
  @@ invalid header @@
  this is malformed content
  no proper diff syntax
  ```
- Can add comments to file1.py and file3.py (valid files)
- Can add file-level comment to file2.py (despite malformed hunks)
- Quit saves review with all comments intact

**Validation**:
```bash
uv run pytest tests/contract/test_error_handling.py::test_malformed_hunk_display -v

# Expected: PASSED
```

---

## Scenario 4: Size Limit Enforcement (FR-002a)

**Goal**: Reject diffs > 10k lines with clear error

```bash
# Generate oversized diff
uv run python scripts/generate_large_diff.py --lines 12000 -o /tmp/oversized.diff

# Attempt to load
uv run python -m racgoat < /tmp/oversized.diff
```

**Expected**:
- Error modal appears immediately:
  ```
  🦝 This diff is too large!

  RacGoat can handle up to 10,000 lines,
  but this diff has 12,000.

  Consider reviewing in smaller chunks. 🐐

  [Press any key to exit]
  ```
- Press any key → application exits cleanly
- Exit code: 1

**Validation**:
```bash
uv run pytest tests/contract/test_error_handling.py::test_size_limit_enforcement -v

# Expected: PASSED
```

---

## Scenario 5: Binary File Handling (FR-020, FR-021)

**Goal**: Binary files excluded from TUI file list

```bash
# Create diff with mixed binary and text files
cat > /tmp/binary-test.diff << 'EOF'
diff --git a/image.png b/image.png
Binary files differ

diff --git a/package-lock.json b/package-lock.json
index 1234..5678
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,2 +1,2 @@
-old lock
+new lock

diff --git a/main.py b/main.py
@@ -1,1 +1,1 @@
-print("old")
+print("new")
EOF

uv run python -m racgoat < /tmp/binary-test.diff
```

**Expected**:
- Files pane: Shows only `main.py` (1 file)
- Footer: "1 file (2 binary/generated skipped)"
- Diff pane: Shows main.py content
- No image.png or package-lock.json in list

**Validation**:
```bash
uv run pytest tests/contract/test_binary_filtering.py -v

# Expected:
# test_binary_files_excluded_from_tui_list PASSED  # REWRITTEN test
# test_all_binary_shows_placeholder PASSED
```

---

## Scenario 6: Performance Benchmarking (FR-013)

**Goal**: Automated performance tests validate all latency requirements

```bash
# Run full performance suite
uv run pytest tests/integration/test_performance/ -v --benchmark-only

# Expected output (example):
# test_initial_load_small_diff .................. PASSED (mean: 0.32s)
# test_initial_load_large_diff .................. PASSED (mean: 1.85s)
# test_file_switch_latency ...................... PASSED (mean: 0.15s)
# test_scroll_responsiveness .................... PASSED (mean: 0.08s)
# test_comment_addition_latency ................. PASSED (mean: 0.12s)
```

**Assertions**:
- All `mean` values under thresholds (500ms, 2s, 200ms, 100ms, 200ms respectively)
- If any test fails → performance regression detected
- CI/CD integration: Fail build if thresholds exceeded

---

## Scenario 7: UI Consistency Check (FR-015 to FR-019)

**Goal**: Manual verification of text consistency and theme

```bash
# Launch app with any diff
uv run python -m racgoat < /tmp/large.diff

# In TUI:
# 1. Press ? → Check help overlay
#    - All keybindings capital: "Q - Quit", "A - Add comment"
#    - No "^C" or "Control-X", only "Ctrl+C"
#
# 2. Check status bar
#    - Format: "Q: Quit | A: Add comment | ..."
#    - Separator: " | " (spaces around pipe)
#
# 3. Trigger error (load malformed diff)
#    - Error starts with 🦝 emoji
#    - Error ends with 🐐 emoji
#    - Message is helpful (not just "error")
#
# 4. Check grammar
#    - No typos in help text
#    - Consistent punctuation (all periods or no periods)
```

**Validation**:
```bash
uv run pytest tests/integration/test_ui_consistency.py -v

# Expected:
# test_keybinding_format_consistency PASSED
# test_error_message_theme PASSED
# test_help_text_terminology PASSED
# test_grammar_and_spelling PASSED
```

---

## Scenario 8: File I/O Error Recovery (FR-010)

**Goal**: Verify error modal when output write fails

```bash
# Create read-only directory
mkdir -p /tmp/readonly
echo "test diff" | git diff --no-index /dev/null - > /tmp/test.diff
chmod 444 /tmp/readonly  # Read-only

# Attempt to save review
uv run python -m racgoat -o /tmp/readonly/review.md < /tmp/test.diff

# In TUI:
# 1. Add a comment (press 'a', enter text)
# 2. Quit (press 'q')
```

**Expected**:
- Error modal appears (same design as M4 file exists modal):
  ```
  🦝 Can't write to /tmp/readonly/review.md!

  Permission denied. This raccoon needs write access!

  [R]etry | [C]hange path | [Q]uit 🐐
  ```
- Press `C` → prompt for new path → saves successfully
- Press `R` (after fixing perms) → saves successfully
- Press `Q` → exits without saving

**Validation**:
```bash
uv run pytest tests/integration/test_io_error_recovery.py -v

# Expected: PASSED
```

---

## Scenario 9: End-to-End Workflow

**Goal**: Complete review workflow with all features

```bash
# Generate realistic diff
git diff HEAD~3 > /tmp/review.diff  # Or use test fixture

# Full workflow
uv run python -m racgoat -o /tmp/my-review.md < /tmp/review.diff
```

**Actions**:
1. Launch → observe <2s load (if <100 files, <10k lines)
2. Navigate files → observe <200ms switches
3. Scroll large file → observe <100ms scrolls
4. Add line comment on line 50 (`a` key) → observe <200ms
5. Add range comment (select mode: `s`, move, `enter`)
6. Add file comment (`c` key)
7. Search for "TODO" (`/` key, type pattern, `enter`)
8. Press `n` to jump to next match
9. Quit (`q`) → saves to /tmp/my-review.md

**Expected review.md**:
```markdown
# Code Review: [branch name]

**Commit**: [SHA]
**Reviewed**: [timestamp]

---

## 📁 path/to/file.py

### Line 50
> This looks wrong

### Lines 100-105
> This range needs refactoring

### File-level
> Overall structure is good

---

[... more files ...]
```

**Validation**:
```bash
# Check review created
cat /tmp/my-review.md

# Run all integration tests
uv run pytest tests/integration/test_milestone6/ -v

# Expected: All scenarios PASSED
```

---

## Success Criteria

All quickstart scenarios pass ✅:
- [ ] Large diff loads <2s (Scenario 1)
- [ ] Scrolling <100ms (Scenario 2)
- [ ] Malformed hunks handled gracefully (Scenario 3)
- [ ] >10k lines rejected with error (Scenario 4)
- [ ] Binary files excluded from list (Scenario 5)
- [ ] Performance benchmarks pass (Scenario 6)
- [ ] UI text consistent and correct (Scenario 7)
- [ ] I/O errors show recovery modal (Scenario 8)
- [ ] End-to-end workflow smooth (Scenario 9)

**Ready for v1 release when**:
- All automated tests pass (`uv run pytest`)
- All quickstart scenarios validated
- No performance regressions vs baseline
