# Research: Core Commenting Engine

**Feature**: Core Commenting Engine (Milestone 3)
**Date**: 2025-10-02

## Research Questions

### 1. Modal Interaction in Textual (Normal vs Select Mode)

**Decision**: Use reactive property pattern with mode state managed at app level

**Rationale**:
- Textual's reactive system allows widgets to respond to mode changes automatically
- App-level mode state ensures consistent behavior across all widgets
- Existing codebase already uses reactive patterns (e.g., PaneFocusState in Milestone 2)
- Mode changes can trigger status bar updates and keybinding modifications

**Implementation Pattern**:
```python
# In RacGoatApp (main.py)
mode = reactive(ApplicationMode.NORMAL)

def watch_mode(self, new_mode: ApplicationMode) -> None:
    """React to mode changes - update status bar, keybindings"""
    self.query_one(StatusBar).update_keybindings(new_mode)
```

**Alternatives Considered**:
- Widget-level mode tracking: Rejected due to synchronization complexity
- Global state module: Rejected in favor of Textual's reactive system
- Event-based mode switching: Viable but less declarative than reactive properties

### 2. In-Memory Comment Storage Pattern

**Decision**: Centralized CommentStore service with dictionary-based lookup

**Rationale**:
- Fast O(1) lookups by file path + line number
- Supports all comment types (line, range, file-level) with unified interface
- Easy to query for visual marker rendering (e.g., "get all comments for current file")
- Aligns with 100-comment capacity requirement (minimal memory footprint)

**Data Structure**:
```python
# Key: (file_path, line_number) or (file_path, None) for file-level
# Value: Comment object
comments: dict[tuple[str, int | None], Comment] = {}

# For range comments: Store one entry per line in range
# Lookup efficiency: O(1) per line, marker rendering: O(visible_lines)
```

**Alternatives Considered**:
- List-based storage: O(n) lookups, rejected for performance
- Nested dict (file → line → comment): More complex, no clear benefit
- Separate stores per type: Would complicate overlap handling

### 3. Visual Gutter Rendering in Terminal

**Decision**: Prepend gutter column to diff content using Rich Text formatting

**Rationale**:
- Existing DiffPane uses Rich Text for syntax highlighting
- Gutter can be added as prefix to each line (e.g., "* | +42 | code here")
- Visual distinction via color/style (e.g., `[yellow]*[/yellow]` for markers)
- No changes to underlying diff parsing (line numbers already available)

**Rendering Approach**:
```python
# In DiffPane.update_content()
for hunk in file.hunks:
    for line in hunk.lines:
        marker = get_marker(line.post_line_num)  # "*" if commented
        gutter = f"{marker} | "
        content = f"{gutter}{line.prefix}{line.post_line_num} {line.content}"
```

**Alternatives Considered**:
- Separate gutter widget: Rejected due to synchronization complexity with scrolling
- Unicode box-drawing characters: Considered but kept simple for 80x24 compatibility
- Color-only indication (no `*`): Rejected for accessibility (colorblind users)

### 4. Context-Sensitive Status Bar Implementation

**Decision**: StatusBar widget with reactive keybinding templates per mode/focus

**Rationale**:
- Status bar already exists in Milestone 2 (Footer widget)
- Can watch both `mode` and `focus_state` reactive properties
- Keybinding templates defined as constants (e.g., NORMAL_DIFF_KEYS, SELECT_MODE_KEYS)
- Updates triggered automatically via Textual's reactive system

**Implementation Pattern**:
```python
# In StatusBar widget
def watch_app_mode(self, mode: ApplicationMode) -> None:
    self.render_keybindings(mode, self.app.focus_state)

KEYBINDING_TEMPLATES = {
    (ApplicationMode.NORMAL, PaneFocusState.DIFF): "a: Add Comment | s: Select Range | ...",
    (ApplicationMode.NORMAL, PaneFocusState.FILES): "c: Comment File | ...",
    (ApplicationMode.SELECT, PaneFocusState.DIFF): "↑/↓: Expand | Enter: Confirm | Esc: Cancel",
}
```

**Alternatives Considered**:
- Hardcoded strings in each widget: Rejected for maintainability
- Dynamic keybinding discovery: Overkill for well-defined set of actions
- Multiple status bar widgets: Rejected in favor of single reactive widget

## Key Architectural Decisions

### Comment Overlap Handling
**Decision**: Allow overlaps with visual distinction via marker styling

From spec clarifications:
> Q: When the user creates a range comment that overlaps with existing line or range comments, should the system allow this without restriction?
> A: Allow overlaps but visually distinguish overlapping regions

**Implementation**:
- Multiple comments per line stored as list in CommentStore
- Gutter marker changes style when >1 comment exists (e.g., `**` or different color)
- Comment editing (Milestone 5) will need to prompt user to choose which comment

### Comment Editing on Re-Comment
**Decision**: Display existing comment and allow in-place edit

From spec clarifications:
> Q: When a user tries to add a comment to a line that already has a comment, what should happen?
> A: The original comment should be shown and the user allowed to edit it

**Implementation**:
- Check CommentStore before prompting for new comment
- If exists: Pre-fill input with existing text
- Update comment in place (same timestamp, updated text)

### File Switching Lock in Select Mode
**Decision**: Prevent file navigation while Select Mode active

From spec clarifications:
> Q: When a user enters Select Mode (`s`) and then switches to a different file (e.g., via arrow keys in file list), what should happen to the selection?
> A: Prevent file switching while in Select Mode

**Implementation**:
- FilesPane checks app.mode before handling arrow key events
- Display message "Exit Select Mode first (Esc)" if file switch attempted
- Mode must be NORMAL for file list navigation to work

## Performance Considerations

- **Comment Capacity**: 100 comments @ ~200 bytes each = ~20KB memory (negligible)
- **Marker Rendering**: O(visible_lines) per frame (typically 20-50 lines in viewport)
- **Lookup Efficiency**: O(1) dictionary access per line for marker check
- **UI Response Time**: <10ms for comment operations (well within <50ms target)

## Testing Strategy

From Constitution Principle III (TDD):
1. Write contract tests for CommentStore API (add, get, update, delete)
2. Write integration tests for user scenarios (from spec acceptance scenarios)
3. Verify tests FAIL (no implementation yet)
4. Implement minimum code to pass
5. Refactor while keeping tests green

Test files to create:
- `tests/contract/test_milestone3/test_comment_store.py` (API contracts)
- `tests/integration/test_milestone3/test_single_line_comment.py` (FR-001)
- `tests/integration/test_milestone3/test_file_comment.py` (FR-002)
- `tests/integration/test_milestone3/test_range_comment.py` (FR-003, FR-010)
- `tests/integration/test_milestone3/test_visual_markers.py` (FR-006)
- `tests/integration/test_milestone3/test_status_bar.py` (FR-007)
- `tests/integration/test_milestone3/test_edge_cases.py` (FR-012, FR-015, FR-016)

## Dependencies & Tools

**Existing (from Milestone 2)**:
- Textual 6.2.0: Reactive properties, Rich Text, event system
- pytest 8.4.2: Test framework
- pytest-asyncio 1.2.0: Async test support

**No New Dependencies Required**: All functionality achievable with existing stack

## Next Steps

Phase 1 will:
1. Define Comment and CommentTarget models in `data-model.md`
2. Design CommentStore service API
3. Define UI interaction contracts (keybindings, mode transitions)
4. Generate contract tests from these designs
5. Create quickstart.md with user scenario walkthrough
