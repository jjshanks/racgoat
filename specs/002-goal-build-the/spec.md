# Feature Specification: TUI Rendering & Navigation

**Feature Branch**: `002-goal-build-the`
**Created**: 2025-10-01
**Status**: Draft
**Input**: User description: "**Goal**: Build the read-only visual interface. This milestone takes the parsed data structure from Milestone 1 and renders it in an interactive TUI.

**Tasks**:
    * Build the basic two-pane TUI layout: a **Files Pane** on the left and a **Diff Pane** on the right.
    * Populate the file list using the parsed diff data.
    * Render the selected file's diff hunks in the Diff Pane with correct **ANSI color highlighting** and post-change line numbers.
    * Implement navigation: `arrow keys` to move within a pane and `Tab` to switch focus.
    * Implement the `q` key to quit the application.
    * Display a "No diff" message if the input was empty.

**Deliverable**: A read-only TUI diff viewer. Invoking the tool now opens the visual interface instead of writing a summary file."

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

---

## Clarifications

### Session 2025-10-01
- Q: When the application launches with a valid diff, which pane should receive initial focus? → A: Diff Pane (right) - shows content of first file immediately
- Q: What is the maximum number of files and total diff lines this milestone must handle without performance degradation? → A: 20 files / 2k lines (reasonable for Milestone 2)
- Q: When a very long file name exceeds the Files Pane width, how should it be displayed? → A: Truncate middle (e.g., "src/.../path/file.py")
- Q: What data format does Milestone 1's parser output for consumption by this TUI? → A: Python data structure (dict/list) in memory
- Q: When the git diff contains only one file, should the Files Pane still be displayed? → A: Yes - maintain two-pane layout consistently

---

## User Scenarios & Testing

### Primary User Story
As a code reviewer, I want to visually navigate through a git diff in a terminal interface so that I can view changed files and their diff hunks without leaving the command line. The interface should provide a split-pane view where I can select files from a list on the left and see the corresponding diff content with syntax highlighting on the right.

### Acceptance Scenarios
1. **Given** a git diff with multiple changed files, **When** the application launches, **Then** the user sees a two-pane layout with a file list on the left and diff content on the right, with the first file auto-selected, its diff displayed, and focus on the Diff Pane
2. **Given** the file list is populated, **When** the user navigates with arrow keys, **Then** the selection moves between files and the diff pane updates to show the selected file's changes
3. **Given** a file is selected, **When** the diff is displayed, **Then** line numbers reflect the post-change state with appropriate +/- prefixes and syntax highlighting
4. **Given** the user is in one pane, **When** they press Tab, **Then** focus switches to the other pane
5. **Given** the user is viewing the diff, **When** they press 'q', **Then** the application exits cleanly
6. **Given** an empty git diff is provided, **When** the application launches, **Then** a "No diff" message is displayed instead of empty panes

### Edge Cases
- When the git diff contains only one file, the two-pane layout must be maintained consistently (Files Pane shows the single file, Diff Pane shows its content)
- File names that exceed the Files Pane width must be truncated in the middle, preserving the beginning and end of the path (e.g., "src/.../path/file.py")
- How does navigation behave when there are no files in the list?

## Requirements

### Functional Requirements
- **FR-001**: System MUST display a two-pane layout with a Files Pane on the left and a Diff Pane on the right
- **FR-002**: System MUST populate the Files Pane with the list of changed files from the parsed git diff data
- **FR-003**: System MUST display the selected file's diff hunks in the Diff Pane with ANSI color highlighting
- **FR-004**: System MUST show post-change line numbers in the diff display with +/- prefixes indicating additions and deletions
- **FR-005**: Users MUST be able to navigate within a pane using arrow keys (up/down for file list, up/down for scrolling diff content)
- **FR-006**: Users MUST be able to switch focus between panes using the Tab key
- **FR-007**: System MUST update the Diff Pane content when a different file is selected in the Files Pane
- **FR-008**: Users MUST be able to quit the application by pressing the 'q' key
- **FR-009**: System MUST display a "No diff" message when the input git diff is empty
- **FR-010**: System MUST maintain a read-only view (no editing or commenting in this milestone)
- **FR-011**: System MUST filter out binary and generated files from the file list (as established in Milestone 1: .lock files, .min.js files, etc.)
- **FR-012**: System MUST indicate which pane currently has focus through visual feedback
- **FR-013**: On launch with valid diff data, system MUST auto-select the first file, display its diff content, and set initial focus to the Diff Pane
- **FR-014**: System MUST truncate file paths that exceed the Files Pane width by removing middle path segments and replacing with "...", preserving the beginning and end of the path
- **FR-015**: System MUST maintain the two-pane layout regardless of the number of files (including when only one file is present in the diff)

### Non-Functional Requirements
- **NFR-001**: System MUST render the UI and respond to navigation input without noticeable lag for diffs containing up to 20 files and 2,000 total diff lines
- **NFR-002**: UI updates (pane switching, file selection, scrolling) MUST feel instantaneous to the user (≤100ms response time)

### Dependencies & Assumptions
- **DEP-001**: This milestone depends on Milestone 1's parser, which provides parsed diff data as Python data structures (dictionaries and lists) in memory
- **ASSUME-001**: The parser provides a list of file entries, where each entry contains the file path and a list of diff hunks with line numbers and content

### Key Entities
- **File Entry**: Represents a single changed file in the diff, containing the file path, change summary (lines added/removed), and associated diff hunks
- **Diff Hunk**: Represents a contiguous block of changes within a file, containing line numbers, change type (addition/deletion/context), and the actual line content
- **Pane Focus State**: Indicates which pane (Files or Diff) is currently active and receiving keyboard input

---

## Review & Acceptance Checklist

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

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
