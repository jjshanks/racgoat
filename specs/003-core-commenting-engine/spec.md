# Feature Specification: Core Commenting Engine

**Feature Branch**: `003-core-commenting-engine`
**Created**: 2025-10-02
**Status**: Draft
**Input**: User description: "Core Commenting Engine
**Goal**: Implement the primary user action: creating and storing feedback. This milestone focuses on adding, selecting, and managing comments in memory.

**Tasks**:
    * Design and implement the in-memory data structures for storing comments.
    * Implement adding a **single-line comment** (`a`), a **file-level comment** (`c`), and **range-based comments** via **Select Mode** (`s`).
    * Display a visual marker (`*`) in the Diff Pane to indicate comments.
    * Update the status bar to show context-sensitive keybindings for commenting.

**Deliverable**: An interactive TUI where a user can fully annotate a diff in-memory."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Clarifications

### Session 2025-10-02
- Q: When a user tries to add a comment to a line that already has a comment, what should happen? → A: The original comment should be shown and the user allowed to edit it
- Q: When a user enters Select Mode (`s`) and then switches to a different file (e.g., via arrow keys in file list), what should happen to the selection? → A: Prevent file switching while in Select Mode
- Q: When the user creates a range comment that overlaps with existing line or range comments, should the system allow this without restriction? → A: Allow overlaps but visually distinguish overlapping regions
- Q: What is the maximum expected number of comments a user might create in a single review session? → A: 100
- Q: When displaying the visual marker (`*`) for comments, where exactly should it appear? → A: In a dedicated gutter column (left of line numbers)

## User Scenarios & Testing

### Primary User Story
A code reviewer navigates through a git diff in the TUI and wants to add feedback comments to specific lines, ranges of lines, or entire files. As they review the code, they can mark any line or section that needs attention with a comment. The comments are stored in memory and visible as markers in the diff view, helping the reviewer track what they've already annotated. The status bar dynamically shows which commenting actions are available based on the current context (e.g., which pane has focus, whether they're in selection mode).

### Acceptance Scenarios
1. **Given** the user is viewing a diff with focus on a specific line, **When** they press `a`, **Then** the system prompts for a comment and stores it associated with that line, displaying a visual marker in the diff pane.

2. **Given** the user is viewing a file in the file list, **When** they press `c`, **Then** the system prompts for a file-level comment and stores it associated with that file.

3. **Given** the user presses `s` to enter Select Mode, **When** they navigate to mark a range of lines and confirm the selection, **Then** the system prompts for a comment and stores it associated with all lines in the selected range, displaying markers for each line.

4. **Given** a line already has a comment, **When** the diff pane displays that line, **Then** a visual marker (asterisk `*`) appears next to the line to indicate a comment exists.

5. **Given** the user is in the files pane, **When** they look at the status bar, **Then** it shows keybindings relevant to file-level actions (e.g., `c` for file comment).

6. **Given** the user is in the diff pane, **When** they look at the status bar, **Then** it shows keybindings relevant to line-level actions (e.g., `a` for add comment, `s` for select mode).

7. **Given** the user is in Select Mode, **When** they look at the status bar, **Then** it shows keybindings relevant to selection actions (e.g., arrow keys to expand selection, Enter to confirm, Esc to cancel).

### Edge Cases
- What happens when the user tries to add a comment to an already-commented line? If exactly one comment exists, the system displays it and allows the user to edit it in place. If multiple comments exist (overlaps), the system prompts the user to select which comment to edit.
- What happens when the user tries to add a range comment that overlaps with existing comments? The system allows overlapping range comments but visually distinguishes overlapping regions in the diff pane display.
- What happens when the user cancels a comment prompt (e.g., provides empty input or exits the input dialog)? The system should abort the comment creation and return to the previous state without storing anything.
- What happens when the user enters Select Mode but cancels before confirming a range? The system should exit Select Mode and return to normal navigation without creating a comment.
- What happens when viewing an empty diff? File-level comments should still be possible, but line-level and range comments should be unavailable.
- What happens when the user switches files while in Select Mode? File switching is prevented while Select Mode is active; the user must confirm or cancel the selection first.

## Requirements

### Functional Requirements
- **FR-001**: System MUST allow users to add a single-line comment by pressing `a` when a line in the diff pane has focus.
- **FR-002**: System MUST allow users to add a file-level comment by pressing `c` when viewing any file.
- **FR-003**: System MUST allow users to enter Select Mode by pressing `s`, enabling them to mark a range of lines for commenting.
- **FR-004**: System MUST prompt users for comment text when they initiate any comment action (single-line, file-level, or range).
- **FR-005**: System MUST store all comments in memory with associations to their target (line number, line range, or file path).
- **FR-006**: System MUST display a visual marker (`*`) in a dedicated gutter column (left of line numbers) for any line that has a comment.
- **FR-007**: System MUST update the status bar to show context-sensitive keybindings based on the current pane focus and application mode (normal or Select Mode).
- **FR-008**: System MUST persist comments in memory throughout the user session until the application exits.
- **FR-009**: System MUST allow users to exit Select Mode by pressing Escape or by confirming a range selection.
- **FR-010**: System MUST visually indicate which lines are included in a range selection while in Select Mode.
- **FR-011**: System MUST prevent line-level and range comments when no diff content is available (e.g., empty diff, binary file).
- **FR-012**: System MUST handle comment cancellation gracefully (e.g., empty input, Escape key) without creating a comment or changing application state.
- **FR-013**: System MUST maintain comment marker visibility as users navigate between files and scroll through diff content.
- **FR-014**: System MUST distinguish between different comment types (line, range, file) when storing them in memory.
- **FR-015**: System MUST display the existing comment and allow in-place editing when the user attempts to add a comment to an already-commented line with exactly one comment. When multiple comments exist (overlaps), system MUST prompt the user to select which comment to edit.
- **FR-016**: System MUST prevent file switching while in Select Mode, requiring the user to confirm or cancel the selection first.
- **FR-017**: System MUST visually distinguish overlapping comment regions in the diff pane when range comments overlap.
- **FR-018**: System MUST support storing up to 100 comments in a single review session without performance degradation.

### Key Entities

- **Comment**: Represents a piece of user feedback. Contains the comment text, timestamp, and a reference to its target (line, range, or file). Each comment has a type indicator (single-line, range, or file-level).

- **CommentTarget**: Identifies what a comment is attached to. For single-line comments, includes file path and line number. For range comments, includes file path and start/end line numbers. For file-level comments, includes only file path.

- **ApplicationMode**: Represents the current interaction mode of the TUI. Can be Normal (standard navigation and commenting) or Select (range selection active). Affects which keybindings are available and how the status bar is rendered.

- **CommentMarker**: Visual indicator displayed in a dedicated gutter column (left of line numbers) to show that a line has one or more associated comments. When multiple comments overlap a region, the marker visually distinguishes the overlap.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
