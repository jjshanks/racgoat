# Quickstart: End-to-End Workflow & Markdown Output

**Feature**: End-to-End Workflow & Markdown Output
**Branch**: 004-end-to-end
**Date**: 2025-10-02
**Prerequisites**: Milestone 3 (Commenting Engine) complete

---

## Purpose

This quickstart validates the complete user journey from adding comments during diff review to generating a Markdown output file. It serves as both user documentation and an integration test scenario.

---

## Quick Test (2 minutes)

### 1. Setup

```bash
# Ensure you're on the feature branch
git checkout 004-end-to-end

# Create a sample diff for testing
git diff HEAD~1 > sample.diff

# Verify the diff has content
cat sample.diff  # Should show actual changes
```

### 2. Launch RacGoat with Output File Specified

```bash
# Run with custom output filename
uv run python -m racgoat -o my-review.md < sample.diff
```

**Expected**: TUI opens with diff displayed

### 3. Add Comments During Review

**Actions**:
1. Navigate to first file (arrow keys)
2. Navigate to a specific line in the diff pane
3. Press `a` to add line comment
   - Type: "This looks good"
   - Press Enter to confirm
4. Navigate to another line
5. Press `s` to start range selection
   - Arrow to select 3-4 lines
   - Press `a` to add range comment
   - Type: "Consider refactoring this block"
   - Press Enter to confirm
6. Press `c` to add file-level comment
   - Type: "Overall well-structured"
   - Press Enter to confirm

**Expected**: Visual markers (`*`) appear next to commented lines in diff pane

### 4. Quit and Save

```bash
# Press 'q' to quit
```

**Expected**:
- App exits cleanly
- File `my-review.md` created in current directory

### 5. Verify Output

```bash
# View the generated Markdown
cat my-review.md
```

**Expected Output Structure**:
```markdown
# Code Review

**Branch**: 004-end-to-end
**Commit**: <actual-commit-sha>

## File: <file-path>

### Line <N>
This looks good

### Lines <M>-<P>
Consider refactoring this block

### File-level comment
Overall well-structured
```

**Validation Checks**:
- ✅ File exists
- ✅ Header includes correct branch name
- ✅ Header includes actual commit SHA (40 hex chars)
- ✅ All 3 comments present with correct text
- ✅ Line numbers match where comments were added
- ✅ Markdown renders correctly (test with `mdcat my-review.md` or VS Code preview)

---

## Scenario: No Comments Made

### Test Steps

```bash
# Launch app
uv run python -m racgoat < sample.diff

# Navigate around (don't add any comments)
# Press 'q' to quit
```

**Expected**:
- App exits cleanly
- **No file created** (per FR-004)

**Validation**:
```bash
ls review.md  # Should not exist
echo $?       # Exit code: 2 (file not found)
```

---

## Scenario: Default Output Filename

### Test Steps

```bash
# Launch WITHOUT -o flag
uv run python -m racgoat < sample.diff

# Add one comment
# Press 'q' to quit
```

**Expected**:
- File `review.md` created (default name per FR-003)

**Validation**:
```bash
ls review.md        # Should exist
cat review.md       # Contains the comment
```

---

## Scenario: File Already Exists (Error Handling)

### Test Steps

```bash
# Create existing file
echo "old content" > existing-review.md

# Launch with same filename
uv run python -m racgoat -o existing-review.md < sample.diff

# Add comments
# Press 'q' to quit
```

**Expected**:
- Modal dialog appears: "Error: Output file already exists: existing-review.md"
- Options shown:
  - "Specify new path" (keyboard shortcut: `n`)
  - "Cancel" (keyboard shortcut: `Escape`)
- User presses `n`:
  - Text input appears: "Enter new output path:"
  - User types: "review-v2.md"
  - File saved to `review-v2.md`
- Original file unchanged: `cat existing-review.md` shows "old content"

**Validation**:
```bash
cat existing-review.md   # Still "old content"
cat review-v2.md         # New review content
```

---

## Scenario: Invalid Output Path (Error Handling)

### Test Steps

```bash
# Launch with invalid path (directory doesn't exist)
uv run python -m racgoat -o /nonexistent/dir/review.md < sample.diff

# Add comments
# Press 'q' to quit
```

**Expected**:
- Modal dialog appears: "Error: Cannot write to /nonexistent/dir/review.md (No such file or directory)"
- Options shown:
  - "Specify new path" (keyboard shortcut: `n`)
  - "Save to /tmp" (keyboard shortcut: `t`)
  - "Cancel" (keyboard shortcut: `Escape`)
- User presses `t`:
  - File saved to `/tmp/review.md`
  - Success message: "Review saved to /tmp/review.md"

**Validation**:
```bash
cat /tmp/review.md  # Contains review content
```

---

## Scenario: Git Metadata Unavailable

### Test Steps

```bash
# Create temp directory (not a git repo)
mkdir /tmp/racgoat-test
cd /tmp/racgoat-test

# Create fake diff
echo "--- a/file.txt
+++ b/file.txt
@@ -1 +1 @@
-old
+new" > test.diff

# Run RacGoat
uv run python -m racgoat < test.diff

# Add comment, quit
```

**Expected Output** (`cat review.md`):
```markdown
# Code Review

**Branch**: Unknown Branch
**Commit**: Unknown SHA

## File: file.txt

### Line 1
<your-comment>
```

**Validation**:
- ✅ Placeholders used (per FR-005, FR-006)
- ✅ App doesn't crash or abort

---

## Scenario: Special Markdown Characters in Comments

### Test Steps

```bash
uv run python -m racgoat < sample.diff

# Add comment with Markdown syntax
# Text: "Use `*args` and `**kwargs` instead of #TODO"
# Press 'q' to quit
```

**Expected Output** (`cat review.md`):
```markdown
### Line <N>
Use `*args` and `**kwargs` instead of #TODO
```

**Validation**:
- ✅ Backticks preserved (code formatting works)
- ✅ Asterisks preserved (bold `**kwargs**` renders correctly)
- ✅ Hash preserved (`#TODO` shows as heading in some renderers - expected per FR-010a)
- ✅ No escaping characters added (no `\*` or `\#`)

**Render Test**:
```bash
# View in terminal Markdown viewer
mdcat review.md  # or: glow review.md

# Expected: `*args` and `**kwargs` formatted as inline code
```

---

## Scenario: Maximum Comment Volume (100 comments)

### Test Steps

```bash
# Generate large diff with many files
git diff HEAD~5 > large.diff

# Launch app
uv run python -m racgoat < large.diff

# Add 100 line comments across files (scripted or manual)
# Press 'q' to quit
```

**Expected**:
- File write completes in <5 seconds (per NFR-002)
- Output file contains all 100 comments
- No performance degradation or truncation

**Validation**:
```bash
# Count comments in output
grep "^### Line" review.md | wc -l  # Should be 100
```

---

## Integration Test Script

**File**: `tests/integration/test_end_to_end.py`

```python
import pytest
from pathlib import Path
from racgoat.test_helpers import launch_app_with_diff, add_comment, quit_app

def test_happy_path_with_comments(tmp_path):
    """Raccoon reviews diff, stashes treasures to Markdown"""
    # Arrange
    diff_file = tmp_path / "test.diff"
    output_file = tmp_path / "review.md"
    diff_file.write_text("--- a/test.py\n+++ b/test.py\n...")

    # Act
    app = launch_app_with_diff(diff_file, output_file)
    add_comment(app, comment_type="line", line=5, text="Fix this")
    quit_app(app)

    # Assert
    assert output_file.exists()
    content = output_file.read_text()
    assert "# Code Review" in content
    assert "### Line 5" in content
    assert "Fix this" in content

def test_no_comments_no_file(tmp_path):
    """Goat leaves no droppings when pasture is empty"""
    # Arrange
    output_file = tmp_path / "review.md"

    # Act
    app = launch_app_with_diff(tmp_path / "test.diff", output_file)
    quit_app(app)  # No comments added

    # Assert
    assert not output_file.exists()  # File NOT created
```

---

## Success Criteria

**This quickstart is complete when**:
1. ✅ All 7 scenarios pass (happy path, no comments, default name, errors, git, special chars, volume)
2. ✅ Integration tests execute scenarios programmatically
3. ✅ Manual test of each scenario takes <2 minutes
4. ✅ Generated Markdown renders correctly in 3+ viewers (GitHub, VS Code, terminal)

---

## Troubleshooting

### File Not Created After Quitting

**Check**:
- Did you add at least one comment? (No comments = no file per FR-004)
- Check for error dialog (may have been dismissed too quickly)

### Git Metadata Shows "Unknown"

**Check**:
- Are you in a git repository? (`git status`)
- Does `git rev-parse HEAD` work in terminal?

### Markdown Rendering Looks Wrong

**Check**:
- View raw file: `cat review.md` (verify structure)
- Try different viewer: `mdcat review.md` or `glow review.md`
- Check for user comments with conflicting Markdown (expected per FR-010a)

---

## References

- Feature Spec: `specs/004-end-to-end/spec.md`
- Data Model: `specs/004-end-to-end/data-model.md`
- Markdown Contract: `specs/004-end-to-end/contracts/markdown-output-schema.md`

---

**Status**: Quickstart Complete ✅
**Next**: Run integration tests to validate all scenarios
