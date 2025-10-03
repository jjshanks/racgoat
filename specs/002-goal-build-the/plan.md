
# Implementation Plan: TUI Rendering & Navigation

**Branch**: `002-goal-build-the` | **Date**: 2025-10-01 | **Spec**: [/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/spec.md]
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/spec.md`

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
Build the read-only TUI visual interface for RacGoat, rendering a two-pane diff viewer (Files Pane + Diff Pane) with syntax highlighting, keyboard navigation, and support for up to 20 files / 2k diff lines. This consumes the parsed data structure from Milestone 1 and establishes the foundation for the commenting engine in Milestone 3.

## Technical Context
**Language/Version**: Python 3.13 (project uses >=3.12)
**Primary Dependencies**: Textual 6.2.0+ (TUI framework), pytest 8.4.2+ (testing)
**Storage**: In-memory Python data structures (DiffSummary, DiffFile from Milestone 1)
**Testing**: pytest with Textual's testing utilities
**Target Platform**: Linux/macOS/Windows terminals (80x24 minimum)
**Project Type**: Single project (TUI application)
**Performance Goals**: <100ms UI response time, support 20 files / 2k lines (Milestone 2 scale)
**Constraints**: Read-only view (no editing/commenting yet), keyboard-only navigation, ANSI color support
**Scale/Scope**: 6 functional requirements, 2 NFRs, 2 panes with focus management, ANSI syntax highlighting

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Fun Is a Feature ✅
- Widget names can embrace raccoon/goat theme (FilesPaw, DiffHooves)
- Test names must be punny AND descriptive
- Error messages for "No diff" should be whimsical but helpful
- Navigation keybindings are already fun (Tab = paw-switch!)

### Principle II: TUI-First Experience ✅
- Two-pane layout optimized for 80x24 minimum terminal
- Keyboard-only navigation (arrows, Tab, q)
- <100ms response time aligns with <50ms constitution target
- Textual framework patterns used consistently

### Principle III: Test-Driven Development ✅
- All features require tests first (contract tests for widgets, integration for navigation)
- Milestone 2 acceptance scenarios map to integration tests
- Tests must fail before implementation (TDD red-green-refactor)
- Punny test names encouraged (test_tab_switches_paws_like_a_nimble_goat)

### Principle IV: Performance Within Constraints ✅
- 20 files / 2k lines scale (conservative vs. final 100 files / 10k lines)
- Lazy loading NOT required for Milestone 2 (deferred to Milestone 6)
- File filtering from Milestone 1 already in place (binary/generated exclusion)
- No blocking operations during navigation (reactive UI)

### Principle V: Data Integrity Over Convenience ✅
- Consumes DiffSummary/DiffFile from Milestone 1 (post-change line numbers preserved)
- Read-only view ensures no data modification yet
- Comment state deferred to Milestone 3 (correct)
- Display "No diff" for empty input (graceful degradation)

### Principle VI: Graceful Degradation ✅
- Empty diffs display "No diff" message (app remains open)
- Single-file diffs maintain two-pane layout (consistency)
- File path truncation handles UI overflow gracefully
- Malformed diff handling deferred to Milestone 6 (acceptable for Milestone 2)

**GATE STATUS: PASS** ✅ - All constitutional principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
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
├── __init__.py
├── __main__.py              # Entry point (delegates to main())
├── main.py                  # RacGoatApp class (Textual App)
├── cli/
│   ├── __init__.py
│   ├── args.py              # Argument parsing
│   └── main.py              # CLI entry point
├── parser/
│   ├── __init__.py
│   ├── models.py            # DiffFile, DiffSummary (Milestone 1)
│   ├── diff_parser.py       # Git diff parsing logic (Milestone 1)
│   └── file_filter.py       # Binary/generated file filtering (Milestone 1)
├── ui/                      # NEW for Milestone 2
│   ├── __init__.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── files_pane.py    # Left pane file list widget
│   │   ├── diff_pane.py     # Right pane diff display widget
│   │   └── layout.py        # Two-pane layout container
│   ├── models.py            # UI-specific models (DiffHunk with ANSI colors)
│   └── theme.py             # ANSI color scheme, visual markers
└── utils.py                 # Raccoon/goat themed helpers

tests/
├── contract/
│   ├── test_milestone1/     # Existing Milestone 1 tests
│   └── test_milestone2/     # NEW contract tests for UI widgets
├── integration/
│   ├── test_milestone1/     # Existing Milestone 1 tests
│   └── test_milestone2/     # NEW integration tests for navigation
└── unit/
    ├── test_milestone1/     # Existing Milestone 1 tests
    └── test_milestone2/     # NEW unit tests for UI logic
```

**Structure Decision**: Single project structure (Option 1). This is a TUI application with parser, UI, and CLI layers. Milestone 2 adds the `ui/` module with widgets for Files Pane and Diff Pane, consuming DiffSummary from Milestone 1's `parser/` module.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

### Task Generation Strategy

**Input Artifacts** (from Phase 1):
1. `data-model.md` → Entity implementation tasks (DiffHunk, FilesListItem, PaneFocusState)
2. `contracts/widget_contracts.md` → 15 contract test tasks + widget implementation tasks
3. `quickstart.md` → 9 integration test tasks
4. `research.md` → Implementation guidance (Textual patterns, ANSI formatting)

**Task Categories** (TDD order):

1. **Data Model Tasks** (Foundation)
   - Extend DiffFile with `hunks: list[DiffHunk]` attribute
   - Create DiffHunk dataclass with validation
   - Create FilesListItem model for UI
   - Create PaneFocusState enum
   - Update parser to populate DiffHunk objects

2. **Contract Test Tasks** (Test First)
   - 15 contract tests from widget_contracts.md
   - Each test MUST fail initially (verify red state)
   - Examples:
     * `test_files_pane_select_file_emits_event()`
     * `test_diff_pane_format_hunk_applies_ansi_colors()`
     * `test_two_pane_layout_tab_cycles_focus()`

3. **Widget Implementation Tasks** (Make Tests Pass)
   - Implement FilesPane widget (ListView subclass)
   - Implement DiffPane widget (Static subclass)
   - Implement TwoPaneLayout container (Horizontal subclass)
   - Add CSS styling for focus indicators and layout
   - Wire up event handlers (FileSelected, Tab focus switch)

4. **Integration Test Tasks** (Scenario Validation)
   - 9 integration tests from quickstart.md scenarios
   - Examples:
     * `test_multi_file_diff_shows_two_panes()`
     * `test_arrow_keys_navigate_files_and_update_diff()`
     * `test_empty_diff_shows_no_changes_message()`

5. **App Integration Tasks** (End-to-End)
   - Update RacGoatApp.compose() to use TwoPaneLayout
   - Add empty diff conditional logic
   - Wire up `q` key quit action
   - Set initial focus to Diff Pane

6. **Performance & Validation Tasks**
   - Generate large test diff (20 files / 2k lines)
   - Run performance test (verify <100ms render)
   - Execute all quickstart scenarios manually
   - Update documentation (CLAUDE.md recent changes)

### Dependency Ordering Strategy

**Phase Ordering** (sequential):
1. Data models (DiffHunk, etc.) → No dependencies
2. Contract tests → Depend on models
3. Widget implementations → Depend on contract tests (TDD)
4. Integration tests → Depend on widgets
5. App integration → Depend on all widgets
6. Performance validation → Depend on complete app

**Parallel Execution Opportunities** [P]:
- All 15 contract test files can be written in parallel
- All 3 widget implementations can proceed once contract tests exist
- All 9 integration test files can be written in parallel
- Data model tasks (DiffHunk, FilesListItem, PaneFocusState) are independent

### Estimated Task Breakdown

**Total Tasks**: ~35 tasks

1. Data Model: 5 tasks (extend DiffFile, create DiffHunk, FilesListItem, PaneFocusState, update parser)
2. Contract Tests: 15 tasks (one per contract from widget_contracts.md)
3. Widget Implementation: 6 tasks (3 widgets + CSS + events + focus)
4. Integration Tests: 9 tasks (one per quickstart scenario)
5. App Integration: 3 tasks (compose(), empty diff logic, quit action)
6. Validation: 3 tasks (large diff generation, performance test, manual quickstart)

**Milestone Completion Gate**: All 35 tasks complete AND all tests passing (contract + integration)

### Special Instructions for /tasks

- **TDD Enforcement**: Every implementation task MUST be preceded by its test task
- **Test Naming**: Contract test names must be punny (Constitution Principle I)
- **Parallelization**: Mark independent tasks with [P] tag
- **Focus Preservation**: Initial focus = Diff Pane (per clarification in spec.md)
- **Empty Diff Message**: Use exact text "No changes to review 🦝🐐"

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Post-Phase 1 Constitution Re-Check

### Re-evaluation After Design (Phase 1)

**Principle I: Fun Is a Feature** ✅
- Widget names confirmed: FilesPane (raccoon paws), DiffPane (goat comparison)
- Empty diff message: "No changes to review 🦝🐐" (whimsical + helpful)
- Test names in quickstart.md embrace puns (examples ready for /tasks)
- Contract tests will have punny names (deferred to /tasks phase)

**Principle II: TUI-First Experience** ✅
- Two-pane layout uses Textual's Horizontal container (idiomatic)
- Focus management via built-in Textual focus system (no reinvention)
- Visual focus indicators via CSS border changes (Textual best practice)
- 30%/70% pane split accommodates 80x24 minimum terminal

**Principle III: Test-Driven Development** ✅
- 15 contract tests defined in widget_contracts.md (tests written before implementation)
- 9 integration tests defined in quickstart.md (scenario validation)
- TDD workflow documented: contract tests → integration tests → implementation
- All tests must fail before implementation begins (enforced by /tasks order)

**Principle IV: Performance Within Constraints** ✅
- Design avoids lazy loading (correct for 20 files / 2k lines scale)
- Textual's viewport rendering leveraged (no manual optimization)
- Performance scenario documented (Scenario 9: measure <100ms render time)
- No blocking operations in design (reactive UI via Textual events)

**Principle V: Data Integrity Over Convenience** ✅
- DiffHunk model preserves exact line numbers from parser (old_start, new_start)
- Validation rules ensure hunk line counts match DiffFile totals (data integrity check)
- File path truncation algorithm preserves start+end (accuracy over convenience)
- No data modification in UI layer (read-only view)

**Principle VI: Graceful Degradation** ✅
- Empty diff displays friendly message (app doesn't crash or exit)
- Single-file diff maintains two-pane layout (consistency)
- Missing hunks edge case documented (display "File metadata only")
- File path truncation handles UI overflow (min 10 char validation prevents breakage)

**GATE STATUS: PASS** ✅ - Post-design check confirms no new violations. Design aligns with all constitutional principles.

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No violations.** All design decisions align with constitutional principles. No complexity justifications required.


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (Technical Context fully populated)
- [x] Complexity deviations documented (None - no violations)

**Artifacts Generated** (Phase 0-1):
- [x] `/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/research.md`
- [x] `/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/data-model.md`
- [x] `/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/contracts/widget_contracts.md`
- [x] `/home/jjshanks/workspace/racgoat/specs/002-goal-build-the/quickstart.md`
- [x] `/home/jjshanks/workspace/racgoat/CLAUDE.md` (updated with Milestone 2 context)

**Next Steps**:
1. Run `/tasks` command to generate `tasks.md` from Phase 1 design artifacts
2. Execute tasks in TDD order (contract tests → implementation → integration tests)
3. Validate with quickstart scenarios (manual + automated)
4. Measure performance (NFR-001, NFR-002: <100ms response time)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
