# UI Contracts: Consistency & Error Display

## Contract: Keybinding Consistency (FR-016)

**Standard**: All keybindings displayed as capital letter or Ctrl+Letter format

### Scenario 1: Help Overlay Keybinding Format
**Given**: User presses `?` to view help overlay

**Then**: All keybindings displayed consistently:
```
✅ CORRECT:
  Q - Quit and save review
  A - Add line comment
  / - Search in diff
  Ctrl+C - Cancel action

❌ INCORRECT (must fix):
  ^C - Cancel      # Wrong: use "Ctrl+C"
  Control-X - Cut  # Wrong: use "Ctrl+X"
  q - quit         # Wrong: use "Q -" (capital)
```

### Scenario 2: Status Bar Keybinding Display
**Given**: User in normal mode (no active operation)

**Then**: Footer status bar shows:
```
Q: Quit | A: Add comment | S: Select range | C: File comment | /: Search | ?: Help
```

**Format Rules**:
- Single key: Capital letter followed by colon (e.g., `Q:`)
- Modifier key: `Ctrl+` prefix (e.g., `Ctrl+C:`)
- Separator: Pipe with spaces (` | `)
- Action: Title case, concise (e.g., "Add comment" not "add a comment")

---

## Contract: Error Message Consistency (FR-019)

**Theme**: All errors follow raccoon/goat personality while remaining helpful

### Scenario 1: Malformed Diff Error
**Given**: Diff with completely invalid format (no git headers)

**Then**: Error modal displays:
```
🦝 Oops! This doesn't look like a git diff!

RacGoat expected to see 'diff --git' headers,
but found something else entirely.

Try: git diff HEAD~1 | uv run python -m racgoat

[Press any key to exit] 🐐
```

**Tone Rules**:
- Start with emoji + friendly exclamation
- Explain what's wrong (not just "error")
- Provide actionable next step ("Try: ...")
- End with goat emoji for closure

### Scenario 2: File I/O Error (Permission Denied)
**Given**: Cannot write to review.md (permission denied)

**Then**: Error recovery modal (same as M4 file exists modal):
```
🦝 Can't write to review.md!

Permission denied. This raccoon needs write access!

Options:
  1. Fix permissions: chmod +w review.md
  2. Try different path: -o ~/reviews/my-review.md
  3. Cancel and copy to clipboard

[R]etry | [C]hange path | [Q]uit 🐐
```

**Pattern**: Same modal structure as existing file conflict recovery (FR-010 clarification)

### Scenario 3: Size Limit Error
**Already specified in parser-contracts.md**:
```
🦝 This diff is too large!

RacGoat can handle up to 10,000 lines,
but this diff has 12,345.

Consider reviewing in smaller chunks. 🐐

[Press any key to exit]
```

---

## Contract: Help Text Consistency (FR-015)

**Standard**: Help overlay, tooltips, and docs use identical terminology

### Scenario 1: Comment Action Descriptions
**Given**: Multiple places describe comment actions

**Then**: Use identical phrasing:

| Location | Text |
|----------|------|
| Help overlay | `A - Add line comment at cursor` |
| Status bar | `A: Add comment` (abbreviated) |
| CLAUDE.md | "Add line comment (a key)" |
| User error | "Use 'A' to add a comment" |

**Consistency Rules**:
- Action verb: "Add" (not "Create", "Insert", "New")
- Object: "line comment" (not "comment on line", "single-line comment")
- Location: "at cursor" (not "on current line", "here")

### Scenario 2: Search Terminology
**Given**: Search feature described in multiple places

**Then**:
- Help: `/ - Enter search mode`
- Status: `/: Search`
- Error (no matches): "No matches found. Press Esc to exit search mode."
- NOT: "search in diff", "find text", "pattern matching"

**Canonical Terms**:
- "search mode" (not "find mode", "search state")
- "pattern" or "search term" (not "query", "text", "string")
- "match" (not "result", "hit", "occurrence")

---

## Contract: Visual Indicator Consistency (FR-018)

**Standard**: Colors, symbols, spacing follow established patterns

### Scenario 1: Comment Markers
**Given**: Line has comment

**Then**: Display format in DiffPane:
```
  123 * +  new line with comment
```

**Format**:
- Line number: Right-aligned, 6 chars, dim white
- Comment marker: `*` in bright yellow
- Diff prefix: `+`/`-`/` ` in green/red/white
- Content: Default white or syntax highlighted

### Scenario 2: Malformed Hunk Indicator
**Given**: Hunk failed parsing

**Then**: Display in DiffPane:
```
[⚠ UNPARSEABLE]
@@ invalid header @@
  raw hunk content preserved
  ...
```

**Format**:
- Indicator: `[⚠ UNPARSEABLE]` in dim red, before raw text
- Raw text: Shown verbatim, no syntax highlighting
- Separator: Blank line before next valid hunk

### Scenario 3: Binary File Placeholder
**Given**: All files are binary

**Then**: DiffPane shows:
```
┌─ Diff View ───────────────────┐
│                               │
│   🦝 No reviewable files      │
│                               │
│   All files are binary or     │
│   generated.                  │
│                               │
│   🐐 Nothing to review here!  │
│                               │
└───────────────────────────────┘
```

**Format**:
- Centered text, vertically and horizontally
- Emoji bookends (raccoon top, goat bottom)
- 2 line spacing between message and emoji

---

## Contract: Grammar and Spelling (FR-019)

**Standard**: All user-facing text is grammatically correct with proper punctuation

### Checklist (Applied to All Text):
- [ ] No sentence fragments (unless stylistic, e.g., "Amazing!")
- [ ] Consistent punctuation (all status messages end with period OR no period, not mixed)
- [ ] Proper capitalization (sentences, proper nouns)
- [ ] No typos (spell-check required)
- [ ] Raccoon/goat references grammatically integrated

### Scenario 1: Status Message Punctuation
**Given**: Status bar shows mode indicators

**Then**:
```
✅ CORRECT (no periods for short labels):
  Normal mode | 10 files | 250 lines

✅ CORRECT (periods for full sentences):
  Searching for "TODO". Press N for next match.

❌ INCORRECT (mixed):
  Normal mode. | 10 files | 250 lines  # Don't mix styles
```

### Scenario 2: Modal Dialog Text
**Given**: Confirmation modal for comment deletion

**Then**:
```
✅ CORRECT:
  Delete this comment?

  "This looks wrong"

  This action cannot be undone.

  [Y]es | [N]o

❌ INCORRECT:
  delete this comment  # Missing capital
  "This looks wrong."  # No period in quoted text
  this action cannot be undone  # Missing capital
```

---

## UI Consistency Audit Checklist

**Automated Checks**:
- [ ] Grep for `Ctrl\|Control\|^` → Standardize to `Ctrl+`
- [ ] Grep for `comment` → Ensure "Add comment", "Edit comment", "Delete comment" (not "create", "remove")
- [ ] Grep for `search|find` → Ensure "search mode", "search term" (not "find")

**Manual Review**:
- [ ] Help overlay vs status bar: Same action names
- [ ] Error messages: All have emoji bookends (🦝 ... 🐐)
- [ ] Visual markers: `*` for comments, `[⚠ UNPARSEABLE]` for malformed
- [ ] Color scheme: No new colors introduced, use existing palette
- [ ] Spacing: Consistent padding (modals, panes, borders)

**Test Assertions**:
```python
def test_keybinding_format_consistency():
    help_text = app.query_one(HelpOverlay).text
    # No lowercase single-key bindings
    assert not re.search(r'\b[a-z] -', help_text)
    # No caret notation
    assert '^' not in help_text or 'Ctrl+' in help_text
    # No "Control-" prefix
    assert 'Control-' not in help_text

def test_error_message_theme():
    error_modal = app.query_one(ErrorModal)
    text = error_modal.text
    # Must start with raccoon emoji
    assert text.startswith('🦝')
    # Must end with goat emoji
    assert '🐐' in text
```
