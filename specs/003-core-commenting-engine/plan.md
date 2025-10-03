
# Implementation Plan: Core Commenting Engine

**Branch**: `003-core-commenting-engine` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/003-core-commenting-engine/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implement the core commenting engine for RacGoat, enabling users to add single-line, file-level, and range-based comments to git diffs in the TUI. The system stores comments in memory, displays visual markers in the diff pane, and provides context-sensitive keybindings through an updated status bar.

## Technical Context
**Language/Version**: Python 3.12+
**Primary Dependencies**: Textual >=6.2.0 (TUI framework)
**Storage**: In-memory data structures (no persistence in this milestone)
**Testing**: pytest >=8.4.2 with pytest-asyncio >=1.2.0
**Target Platform**: Terminal/CLI (Linux, macOS, Windows with WSL)
**Project Type**: Single (TUI application)
**Performance Goals**: <50ms UI response time, support up to 100 comments per session
**Constraints**: Keyboard-only navigation, 80x24 terminal minimum, no mouse required
**Scale/Scope**: Up to 100 files, 10k diff lines, 100 comments per review session

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fun Is a Feature (NON-NEGOTIABLE)
✅ **PASS** - Comment-related functions will follow raccoon/goat theme (e.g., `stash_thought()`, `bleats_opinion()`). Visual markers and status bar updates provide delightful interaction feedback. Test names will be punny (e.g., `test_goat_chews_on_comment_overlaps()`).

### II. TUI-First Experience
✅ **PASS** - All commenting interactions are keyboard-driven (`a`, `c`, `s` keys). Select Mode provides visual feedback within terminal constraints. Status bar updates maintain context awareness. UI response <50ms aligns with <50ms constitutional requirement.

### III. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - Phase 1 will generate contract tests for comment operations before implementation. Each user scenario from spec maps to integration tests. TDD cycle enforced: tests → fail → implement → pass → refactor.

### IV. Performance Within Constraints
✅ **PASS** - 100 comment capacity meets PRD scale. In-memory storage ensures fast access. Visual marker rendering optimized for viewport. No blocking operations during comment creation.

### V. Data Integrity Over Convenience
✅ **PASS** - Comments store exact line numbers and ranges. Overlap handling allows multiple comments per line (as specified in clarifications). File-level comments maintain file path references. No data loss on navigation.

### VI. Graceful Degradation
✅ **PASS** - Empty input cancellation handled gracefully (FR-012). Select Mode escapable without creating comment (FR-009). File switching prevented during Select Mode (FR-016). Invalid states return to previous mode without data corruption.

## Project Structure

### Documentation (this feature)
```
specs/003-core-commenting-engine/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
racgoat/
├── models/              # Existing: DiffHunk, DiffFile, DiffSummary
│   └── comments.py      # NEW: Comment, CommentTarget models
├── services/
│   └── comment_store.py # NEW: In-memory comment management
├── ui/
│   ├── models.py        # Existing: FilesListItem, PaneFocusState
│   │                    # NEW: ApplicationMode enum
│   └── widgets/
│       ├── files_pane.py    # MODIFY: Add file-level comment keybinding
│       ├── diff_pane.py     # MODIFY: Add gutter, visual markers, Select Mode
│       └── status_bar.py    # NEW: Context-sensitive keybinding display
├── parser/              # Existing: diff parsing (no changes)
└── main.py             # MODIFY: Wire comment system, mode management

tests/
├── contract/
│   └── test_milestone3/      # NEW: Contract tests for commenting
├── integration/
│   └── test_milestone3/      # NEW: Integration tests for user scenarios
└── unit/
    └── test_comment_store.py # NEW: Unit tests for comment storage
```

**Structure Decision**: Single project structure (Option 1). RacGoat is a TUI application with existing `racgoat/` source directory and `tests/` hierarchy. New comment functionality extends existing `models/`, `services/`, and `ui/` packages. Milestone 3 tests follow established `contract/`, `integration/`, `unit/` pattern with dedicated `test_milestone3/` subdirectories.

## Phase 0: Outline & Research

**Status**: All technical context is clear from existing codebase and spec clarifications. No NEEDS CLARIFICATION markers found.

**Research Focus Areas**:
1. Textual best practices for modal interaction (Normal vs Select Mode)
2. In-memory comment storage patterns for TUI applications
3. Visual gutter rendering techniques in terminal UIs
4. Context-sensitive status bar implementation patterns

Research findings will be documented in `research.md`.

**Output**: research.md with best practices and design decisions

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

**Completed Deliverables**:

1. ✅ **data-model.md** created with:
   - Comment, CommentTarget, ApplicationMode, CommentMarker entities
   - Validation rules from functional requirements
   - State transitions for ApplicationMode
   - Data flow diagrams for all comment types

2. ✅ **contracts/** directory created with:
   - `comment-store-api.md`: CommentStore service API specification
   - `ui-interactions.md`: Keybinding and UI behavior contracts
   - Performance requirements and error handling specs

3. ✅ **Contract tests** generated:
   - `tests/contract/test_milestone3/test_comment_store.py` (13 tests)
   - Tests validate: add, get, update, delete, overlaps, capacity, edge cases
   - Tests are currently FAILING (no implementation yet - TDD red phase)

4. ✅ **quickstart.md** created with:
   - 10 user scenarios mapping to acceptance criteria
   - Step-by-step walkthroughs for all comment types
   - Performance validation steps
   - Testing commands and troubleshooting guide

5. ✅ **CLAUDE.md** updated:
   - Added Milestone 3 technical context (Python 3.12+, Textual, in-memory storage)
   - Preserved existing manual content
   - Added new dependencies and project context

**Output**: All Phase 1 artifacts complete, ready for Constitution re-evaluation

### Post-Design Constitution Review

**Re-evaluation after Phase 1 design**:

✅ **I. Fun Is a Feature**: Contract tests use raccoon/goat theme consistently (e.g., `test_raccoon_stashes_single_line_comment`, `test_goat_bleats_file_level_wisdom`). Data model follows playful naming (CommentStore as "treasure cache"). Status bar provides delightful interaction feedback.

✅ **II. TUI-First Experience**: All interactions keyboard-driven per contracts. Gutter rendering uses Rich Text (existing pattern). Select Mode provides terminal-appropriate visual feedback. <50ms response maintained through O(1) lookups.

✅ **III. Test-Driven Development**: 13 contract tests created BEFORE implementation. Tests currently fail (verified TDD red phase). Each functional requirement has corresponding test. User scenarios map to integration tests in quickstart.md.

✅ **IV. Performance Within Constraints**: Dictionary-based storage ensures O(1) lookups. 100 comment capacity enforced. Viewport-only marker rendering (O(visible_lines)). All operations <50ms based on research findings.

✅ **V. Data Integrity Over Convenience**: CommentTarget model ensures exact line/range preservation. Overlaps allowed per spec clarifications. Timestamp preservation on edit. No data loss on navigation.

✅ **VI. Graceful Degradation**: All edge cases have contracts (empty input, cancel, capacity limit). Select Mode exits cleanly. File navigation lock prevents invalid states. Error messages clear and actionable.

**Complexity Tracking**: No constitutional violations. No deviations to document.

**Verdict**: ✅ PASS - Design adheres to all constitutional principles

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

The `/tasks` command will load `.specify/templates/tasks-template.md` and generate tasks from Phase 1 artifacts:

1. **From data-model.md** → Model creation tasks:
   - Task: Create Comment, CommentTarget, CommentType models [P]
   - Task: Create ApplicationMode enum in ui/models.py [P]
   - Task: Create CommentMarker UI model [P]

2. **From contracts/comment-store-api.md** → Service tasks:
   - Task: Create CommentStore service skeleton [P]
   - Task: Implement add() method (TDD: make test_raccoon_stashes_single_line_comment pass)
   - Task: Implement get() method (TDD: make test_empty_cache_returns_no_treasures pass)
   - Task: Implement range comment storage (TDD: make test_raccoon_marks_trash_range pass)
   - Task: Implement overlap support (TDD: make test_goat_and_raccoon_both_claim_same_line pass)
   - Task: Implement capacity limit (TDD: make test_trash_hoard_capacity_limit pass)
   - Task: Implement update() and delete() methods [P]
   - Task: Implement has_comment() and get_file_comments() utility methods [P]

3. **From contracts/ui-interactions.md** → UI tasks:
   - Task: Create StatusBar widget with reactive mode/focus watching
   - Task: Modify DiffPane to add gutter column rendering
   - Task: Modify DiffPane to implement Select Mode highlighting
   - Task: Wire `a` keybinding for single-line comments
   - Task: Wire `s` keybinding for Select Mode entry/exit
   - Task: Wire `c` keybinding for file-level comments
   - Task: Implement file navigation lock in FilesPane (SELECT mode check)
   - Task: Integrate CommentStore into RacGoatApp

4. **From quickstart.md scenarios** → Integration tests:
   - Task: Write test_single_line_comment.py (Scenario 1)
   - Task: Write test_file_level_comment.py (Scenario 2)
   - Task: Write test_range_selection.py (Scenario 3)
   - Task: Write test_visual_markers.py (Scenario 4)
   - Task: Write test_status_bar.py (Scenario 5)
   - Task: Write test_edit_existing.py (Scenario 6)
   - Task: Write test_overlapping_comments.py (Scenario 7)
   - Task: Write test_cancel_scenarios.py (Scenarios 8-9)
   - Task: Write test_select_mode_lock.py (Scenario 10)
   - Task: Write test_performance.py (100 comments)

**Ordering Strategy**:
- **Phase A (Foundation)**: Models first [P] - all can run in parallel
- **Phase B (Service Layer)**: CommentStore implementation following TDD (tests already exist from Phase 1)
- **Phase C (UI Layer)**: Widget modifications and new widgets
- **Phase D (Integration)**: Wire everything together in RacGoatApp
- **Phase E (Validation)**: Integration tests to validate user scenarios

**Parallel Execution Markers**:
- [P] = Can run in parallel (independent files)
- Sequential tasks depend on previous completion

**Estimated Task Count**: ~30-35 tasks total

**Deliverable**: tasks.md with numbered, dependency-ordered tasks ready for execution

**IMPORTANT**: This phase is executed by the `/tasks` command, NOT by `/plan`

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅ (clarifications present in spec)
- [x] Complexity deviations documented ✅ (none - no violations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
