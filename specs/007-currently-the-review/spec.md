# Feature Specification: Include Diff Segments in Review Output

**Feature Branch**: `007-currently-the-review`
**Created**: 2025-10-10
**Status**: Draft
**Input**: User description: "Currently the review.md output only capture the current file which loses the context when asking question about why something was done. The output should include the actual diff segment being commented on so the relevant context is available."

## Clarifications

### Session 2025-10-10

- Q: When a diff segment would exceed a reasonable size (e.g., a 100+ line hunk), what should happen? → A: Show the entire diff segment regardless of size (no truncation)
- Q: For file-level comments (Priority P3), what should be displayed in the output? → A: Show only statistical summary (e.g., "5 hunks, +120 -45 lines")
- Q: How should diff segments format and display line numbers? → A: Use standard unified diff format without explicit line numbers (just +/- markers and context spaces)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Actual Changes in Review (Priority: P1)

As a code reviewer or AI agent analyzing review feedback, I want to see the actual diff segment (with +/- markers showing before/after changes) in the review.md output, so that I can understand what was changed without needing to reference the original diff file.

**Why this priority**: This is the core value proposition - the current implementation shows plain code context, but reviewers and AI agents need to see the actual changes (additions, deletions, modifications) to understand why a comment was made. Without this, the review loses critical context about what changed and why it might be problematic.

**Independent Test**: Can be fully tested by creating a comment on a modified line, saving the review, and verifying that the output includes the diff segment showing both the removed and added lines with -/+ markers.

**Acceptance Scenarios**:

1. **Given** a diff with line modifications (deletions + additions), **When** I add a line comment on a modified line and save the review, **Then** the review.md shows the diff segment with both - and + lines in context
2. **Given** a diff with pure additions, **When** I add a line comment on an added line, **Then** the review.md shows the diff segment with + markers
3. **Given** a diff with deletions, **When** I add a range comment spanning deleted lines, **Then** the review.md shows the diff segment with - markers

---

### User Story 2 - Range Comments with Full Diff Context (Priority: P2)

As a code reviewer commenting on a range of lines, I want the diff segment to show all changes within that range (including both before/after states), so that the context captures the full scope of modifications I'm commenting on.

**Why this priority**: Range comments often span multiple related changes. Showing the full diff segment (not just post-change code) provides essential context about what was removed and what was added across the entire range.

**Independent Test**: Can be tested by creating a range comment spanning 5 lines with mixed additions/deletions, then verifying the output shows all relevant diff lines with proper markers.

**Acceptance Scenarios**:

1. **Given** a diff with interleaved additions/deletions in a hunk, **When** I create a range comment spanning lines 10-15 (post-change), **Then** the review.md shows the complete diff segment including all - and + lines within that range with proper context
2. **Given** a range comment at the beginning of a hunk, **When** I save the review, **Then** the diff segment respects file boundaries and doesn't attempt to show context before the hunk start

---

### User Story 3 - File-level Comments with Statistical Summary (Priority: P3)

As a code reviewer adding file-level comments (e.g., "needs more tests"), I want to see a statistical summary of the file changes in the output, so that readers understand the scope of changes to the entire file without overwhelming detail.

**Why this priority**: File-level comments don't target specific lines, so detailed diff context is less critical. A statistical summary (hunk count and line changes) provides sufficient context for understanding the file's overall modifications. This is lower priority than line/range comments.

**Independent Test**: Can be tested by adding a file-level comment and verifying that the output includes a statistical summary in the format "N hunks, +X -Y lines".

**Acceptance Scenarios**:

1. **Given** a file with multiple hunks, **When** I add a file-level comment, **Then** the review.md shows a statistical summary (e.g., "5 hunks, +120 -45 lines")
2. **Given** a file-level comment, **When** no diff context is available, **Then** the review.md gracefully omits the statistical summary without errors

---

### Edge Cases

- What happens when a comment targets a line at the very start or end of a hunk (boundary conditions)?
- ✅ ANSWERED (FR-008, data-model.md:L157): Malformed hunks return None gracefully (no error, no segment displayed)
- ✅ ANSWERED (L12-13): Large diff segments (100+ line hunks) are displayed in full without truncation
- ✅ ANSWERED (FR-012): Removed-only lines (deletions with no additions) are displayed with '-' markers
- ✅ ANSWERED (data-model.md:L156): When target line not found in any hunk, return None (fallback to no context)
- ❓ OPEN: Binary files or files with no hunks - Current behavior: skip diff segment display (implicit in FR-010 backward compatibility)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extract and include the actual diff segment (with +/- markers) in the **Context** code block for line and range comments
- **FR-002**: Diff segments MUST show the before state (- lines) and after state (+ lines) with proper diff syntax
- **FR-003**: Diff segments MUST include surrounding context lines (prefix with space, matching standard diff format) to show unchanged code around the target
- **FR-004**: For line comments, the diff segment MUST include ±2 lines of context (2 lines before + 2 lines after = DEFAULT_CONTEXT_LINES=2 from constants.py) around the target line in the diff hunk
- **FR-005**: For range comments, the diff segment MUST include the entire range plus ±2 lines of context (2 before + 2 after), showing all diff markers within that range
- **FR-006**: For file-level comments, system MUST display statistical summary showing hunk count and line changes (format: "N hunks, +X -Y lines") instead of diff segments
- **FR-007**: Diff segments MUST respect hunk boundaries (do not attempt to show context outside available hunk lines)
- **FR-008**: System MUST gracefully handle malformed hunks by skipping diff segment display (fallback to no context)
- **FR-009**: System MUST format diff segments as fenced code blocks with diff syntax highlighting (```diff)
- **FR-010**: System MUST maintain backward compatibility - when diff_summary is not provided, skip diff segment display
- **FR-011**: Diff segments MUST use standard unified diff format with +/- markers and context spaces, without explicit line numbers
- **FR-012**: System MUST handle edge cases: boundary lines, removed-only hunks, added-only hunks, empty hunks
- **FR-013**: System MUST display diff segments in full without truncation, regardless of hunk size

### Key Entities *(include if feature involves data)*

- **DiffSegment**: Represents an extracted portion of a DiffHunk with before/after changes and context
  - Contains: list of diff lines (marker + content), formatting metadata
  - Extracted from DiffHunk based on comment target (line or range)
  - Formatted as standard unified diff syntax (space/+/- prefix + content, no line numbers)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Review output for line/range comments includes diff segments showing actual changes (with +/- markers) in 100% of cases where diff_summary is available
- **SC-002**: Diff segment extraction handles all edge cases (boundaries, malformed hunks, removed-only/added-only changes) without errors
- **SC-003**: AI agents can parse diff segments from review output to understand what changed and why it was commented on
- **SC-004**: Performance impact is minimal - extracting and formatting diff segments adds <100ms to serialization time for 100 comments
- **SC-005**: Existing tests continue to pass (backward compatibility maintained)
- **SC-006**: New contract tests validate diff segment accuracy for line comments, range comments, and edge cases (minimum 10 new tests)
- **SC-007**: Human reviewers report improved context clarity in review output (subjective - validate via example outputs)
