# Phase 0: Research & Best Practices

**Feature**: TUI Rendering & Navigation (Milestone 2)
**Date**: 2025-10-01

## Overview
This research consolidates best practices for building a two-pane TUI diff viewer in Textual framework with ANSI color highlighting, keyboard navigation, and focus management.

## Technology Decisions

### 1. Textual Framework Widget Composition
**Decision**: Use Textual's `Horizontal` container for two-pane layout, custom `ListView`-based widget for Files Pane, and `RichLog` or custom `Static` for Diff Pane.

**Rationale**:
- Textual's `Horizontal` container provides automatic flex layout for side-by-side panes
- `ListView` provides built-in keyboard navigation (up/down arrows) and selection state
- `RichLog` or `Static` with Rich markup handles ANSI color codes and scrollable content
- Textual's focus system automatically manages Tab navigation between focusable widgets

**Alternatives Considered**:
- **Manual grid layout**: More complex, Horizontal container is idiomatic for 2-pane splits
- **DataTable widget**: Overkill for simple file list, ListView is lighter
- **ScrollableContainer**: Requires manual scroll handling, RichLog/Static is simpler

**References**:
- Textual docs: [Layout](https://textual.textualize.io/guide/layout/), [ListView](https://textual.textualize.io/widgets/list_view/), [RichLog](https://textual.textualize.io/widgets/rich_log/)
- Existing RacGoat code: `main.py` uses `Container` + `compose()` pattern

### 2. ANSI Color Highlighting for Diffs
**Decision**: Use Rich's ANSI markup with color codes: `[green]+added lines[/]`, `[red]-removed lines[/]`, `[dim] context lines[/]`.

**Rationale**:
- Rich (Textual's rendering engine) natively supports ANSI color codes
- Standard git diff colors: green for additions (+), red for deletions (-), dim/white for context
- No external syntax highlighting library needed for basic diff display (defer to Milestone 5+ for language-specific highlighting)

**Alternatives Considered**:
- **Pygments syntax highlighting**: Too heavy for Milestone 2, deferred to future milestones
- **Manual ANSI escape codes**: Rich markup is cleaner and more maintainable
- **Textual's built-in styles**: Less granular than Rich markup for inline color changes

**References**:
- Rich docs: [Console Markup](https://rich.readthedocs.io/en/stable/markup.html)
- Git diff color conventions: `git config --get-color color.diff.new` (green), `color.diff.old` (red)

### 3. Focus Management Between Panes
**Decision**: Use Textual's `can_focus` property + `focus()` method, bind Tab key to custom action that cycles focus.

**Rationale**:
- Textual's built-in focus system tracks focused widget via `App.focused` property
- Tab key automatically moves focus between `can_focus=True` widgets (default behavior)
- Custom `action_focus_next()` can override Tab to explicitly cycle between Files Pane and Diff Pane

**Alternatives Considered**:
- **Manual focus state tracking**: Reinvents the wheel, Textual's focus system is robust
- **Screen-based focus switching**: Overkill for single-screen two-pane layout

**References**:
- Textual docs: [Input](https://textual.textualize.io/guide/input/#focus), [Actions](https://textual.textualize.io/guide/actions/)
- Constitution Principle II: Keyboard-only navigation required

### 4. Data Flow: Parser → UI
**Decision**: Extend `DiffFile` model with `hunks: list[DiffHunk]` attribute, where `DiffHunk` contains line numbers, change type, and Rich-formatted content.

**Rationale**:
- Milestone 1's `DiffFile` only has file path and line counts (summary-level)
- Milestone 2 needs actual diff content (hunks) for rendering in Diff Pane
- `DiffHunk` model bridges parser output and UI rendering needs
- Parser creates `DiffHunk` objects during diff parsing, UI widgets consume them directly

**Alternatives Considered**:
- **Parse hunks on-demand in UI**: Violates separation of concerns, parser should provide complete data
- **Store raw diff text**: Requires re-parsing in UI, inefficient
- **Modify Milestone 1's DiffFile**: Extends cleanly without breaking existing code

**Data Model**:
```python
@dataclass
class DiffHunk:
    """Represents a contiguous diff hunk with line-level detail."""
    old_start: int  # Line number in old file
    new_start: int  # Line number in new file (post-change)
    lines: list[tuple[str, str]]  # (change_type, content) where type = '+', '-', ' '

@dataclass
class DiffFile:
    # Existing fields from Milestone 1
    file_path: str
    added_lines: int
    removed_lines: int
    is_binary: bool
    # NEW for Milestone 2
    hunks: list[DiffHunk] = field(default_factory=list)
```

**References**:
- Git diff format: [Unified Diff Format](https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html)
- Milestone 1 code: `racgoat/parser/models.py`

### 5. File Path Truncation for UI
**Decision**: Use Python's path manipulation to truncate middle segments, preserving start and end: `src/.../ui/widgets/files_pane.py`.

**Rationale**:
- Start of path shows module/directory context (e.g., `src/`)
- End of path shows filename (most important for identification)
- Middle segments are least critical and safely truncated
- Calculate max width based on Files Pane available columns

**Algorithm**:
```python
def truncate_path(path: str, max_width: int) -> str:
    """Truncate path if longer than max_width, preserving start and end."""
    if len(path) <= max_width:
        return path

    # Reserve 3 chars for "..."
    available = max_width - 3
    start_chars = available // 2
    end_chars = available - start_chars

    return f"{path[:start_chars]}...{path[-end_chars:]}"
```

**Alternatives Considered**:
- **Truncate end**: Loses filename (unacceptable)
- **Truncate start**: Loses directory context (less useful)
- **Ellipsize library**: Overkill for simple string manipulation

**References**:
- Feature spec FR-014: "Truncate file paths that exceed Files Pane width"
- Textual widget sizing: `self.size.width` provides available columns

### 6. Post-Change Line Numbers with +/- Prefixes
**Decision**: Render line numbers in Diff Pane as `[dim]{line_num}[/] {prefix}{content}` where prefix is `+` for added, `-` for removed, ` ` for context.

**Rationale**:
- Post-change line numbers are already computed by Milestone 1 parser (DiffHunk.new_start)
- Prefixes visually indicate change type (aligns with git diff conventions)
- Dim style for line numbers reduces visual clutter, keeps focus on content

**Rendering Format**:
```
  123  context line
+ 124  added line (green)
- (removed line, no line number shown)
  125  context line
```

**Alternatives Considered**:
- **Side-by-side old/new line numbers**: Too complex for Milestone 2, deferred to future
- **No line numbers**: Required by FR-004, unacceptable

**References**:
- Feature spec FR-004: "Post-change line numbers with +/- prefixes"
- Git diff hunk header format: `@@ -old_start,old_count +new_start,new_count @@`

### 7. Performance Optimization for 20 Files / 2k Lines
**Decision**: Render all content immediately (no lazy loading), rely on Textual's viewport rendering for scrolling performance.

**Rationale**:
- 20 files / 2k lines is well within Textual's rendering capacity (<100ms)
- Lazy loading adds complexity without measurable benefit at this scale
- Textual's `ScrollView` automatically renders only visible viewport (built-in optimization)
- Milestone 6 will add lazy loading for 100 files / 10k lines (deferred intentionally)

**Measurement Plan**:
- Integration test with 20 files / 2k lines sample diff
- Assert UI render time <100ms (NFR-002)
- Use Textual's `--dev` mode for performance profiling

**Alternatives Considered**:
- **Virtual scrolling**: Premature optimization, adds bugs
- **Pagination**: Poor UX for diff review, rejected

**References**:
- Feature spec NFR-001: "Render without noticeable lag for 20 files / 2k lines"
- Constitution Principle IV: "Performance Within Constraints"

### 8. Empty Diff Handling
**Decision**: Display centered `Static` widget with message "No changes to review 🦝🐐" when `DiffSummary.is_empty` is True.

**Rationale**:
- `DiffSummary.is_empty` property already exists from Milestone 1
- Replace two-pane layout with single centered message widget
- Whimsical message aligns with Constitution Principle I (Fun Is a Feature)
- Keep app running (don't exit), allow user to quit with `q` key

**Implementation**:
```python
def compose(self) -> ComposeResult:
    if self.diff_summary.is_empty:
        yield Static("No changes to review 🦝🐐", id="empty-message")
    else:
        yield Horizontal(
            FilesPane(self.diff_summary),
            DiffPane(),
        )
```

**Alternatives Considered**:
- **Auto-exit on empty diff**: Poor UX, user may want to check app is working
- **Error message instead of friendly message**: Violates Constitution Principle I

**References**:
- Feature spec FR-009: "Display 'No diff' message when input is empty"
- Milestone 1 code: `DiffSummary.is_empty` property in `parser/models.py`

## Best Practices Summary

### Textual Framework
- Use composition over inheritance for widget hierarchies
- Leverage built-in widgets (ListView, RichLog) before custom implementations
- CSS styling via class variables for visual consistency
- Keybindings via BINDINGS class variable for discoverability

### TDD Approach
1. Write contract tests for widget APIs (FilesPane.select_file(), DiffPane.render_hunks())
2. Write integration tests for user scenarios (navigation, focus switching, empty diff)
3. Implement minimum code to pass tests
4. Refactor while keeping tests green

### Performance
- Profile with Textual's `--dev` mode and `Elapsed` widget
- Rely on Textual's viewport rendering for scroll performance
- Defer optimization until measurements prove bottleneck

### Theme & Fun
- Widget class names embrace theme: `FilesPane` (raccoon's organized paws), `DiffPane` (goat's stubborn comparison)
- Test names must be punny: `test_arrow_keys_climb_file_list_like_a_mountain_goat()`
- Error messages stay helpful but whimsical: "No changes to review 🦝🐐"

## Unresolved Questions (for /tasks)
- Should Files Pane show line count summary next to each file name? (e.g., `file.py (+10 -5)`)
- Should Diff Pane render hunk headers (`@@ ... @@`) or hide them for cleaner display?
- Visual indicator for focused pane (border color change, highlight, or status bar text)?

These questions will be answered during task generation based on PRD constraints and UI mockups.

---
**Phase 0 Complete**: All technologies researched, best practices documented. Ready for Phase 1 design.
