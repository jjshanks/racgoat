
# Implementation Plan: Advanced Interaction & Usability

**Branch**: `005-advanced-interaction-usability` | **Date**: 2025-10-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/005-advanced-interaction-usability/spec.md`

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
Enhance RacGoat with advanced interaction features: comment edit/delete functionality (`e` key), search within diff view (`/` key), and help overlay (`?` key). These features build on the existing M3/M4 commenting system and TUI navigation to make code review workflows more efficient.

## Technical Context
**Language/Version**: Python 3.12+
**Primary Dependencies**: Textual >=6.2.0 (TUI framework)
**Storage**: In-memory comment storage (racgoat/services/comment_store.py)
**Testing**: pytest with pytest-asyncio for Textual event testing
**Target Platform**: Linux/macOS/Windows terminals (80x24 minimum, keyboard-only navigation)
**Project Type**: Single project (TUI application)
**Performance Goals**: <50ms input response, <200ms search across 10k diff lines
**Constraints**: Must work with existing comment models (Comment, CommentTarget, CommentType), maintain keyboard-only navigation, preserve TUI-first experience
**Scale/Scope**: Up to 100 files, 10k diff lines, support all comment types (line/range/file-level)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fun Is a Feature ✅
- Edit dialog can use playful prompts ("Polish your thoughts?" for edit)
- Search not found state: "No trash matching that description" message
- Help overlay organized with raccoon/goat themed section headers
- Test names will follow punny convention (e.g., `test_edit_erases_errors_elegantly`)

### II. TUI-First Experience ✅
- All features keyboard-driven (e, /, ?, n, N, Esc)
- Help overlay uses Textual ModalScreen for overlay pattern
- Search highlights use Textual Text markup for efficiency
- Edit dialog reuses existing InputDialog pattern from M3
- <50ms keybinding response ensures immediate feedback

### III. Test-Driven Development ✅
- Contract tests define edit/search/help interfaces BEFORE implementation
- Integration tests validate user scenarios from spec (8 acceptance scenarios)
- Unit tests cover edge cases (empty edits, no matches, overlapping comments)
- Performance tests ensure <200ms search on 10k lines

### IV. Performance Within Constraints ✅
- Search uses incremental highlighting (not full reparse)
- Help overlay lazy-rendered (build on demand, cache result)
- Edit operations O(1) on comment_store (dict lookup by key)
- No blocking: all UI updates via Textual's reactive system

### V. Data Integrity Over Convenience ✅
- Edits preserve comment type (line/range/file) and target integrity
- Empty edit text = delete (explicit user confirmation, no silent data loss)
- Search state isolated per file (switch file = reset search completely)
- Comment markers stay synchronized with comment_store updates

### VI. Graceful Degradation ✅
- `e` on non-commented line: silent no-op (keybinding only shown when applicable)
- Search no matches: "0/0 matches" counter, no error modal
- Help overlay taller than terminal: scrollable via Textual VerticalScroll
- Search wrap-around: cycle through matches naturally (n at last → first)

**Initial Assessment**: ✅ PASS - All principles satisfied, no violations to justify

**Post-Design Assessment**: ✅ PASS - Design maintains constitutional compliance:
- TDD approach followed: 35 contract + 63 integration tests created before implementation
- Fun theme maintained: Punny test names, playful UI messages in design
- TUI-first: All interactions keyboard-driven, Textual patterns used correctly
- Performance targets met: Design uses incremental updates, O(1) operations
- Data integrity preserved: Edit operations maintain comment type/target consistency
- Graceful degradation: All edge cases handled (silent no-ops, friendly messages)

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
├── models/
│   └── comments.py         # Comment, CommentTarget, CommentType (M3/M4)
├── services/
│   ├── comment_store.py    # In-memory storage (M3)
│   ├── markdown_writer.py  # Serialization (M4)
│   └── git_metadata.py     # Branch/SHA extraction (M4)
├── ui/
│   ├── widgets/
│   │   ├── diff_pane.py    # Diff display (M2, extend for search highlights)
│   │   ├── files_pane.py   # File list (M2)
│   │   └── dialogs.py      # InputDialog (M3, reuse for edit)
│   └── models.py           # FilesListItem, PaneFocusState
├── parser/
│   └── models.py           # DiffHunk, DiffFile, DiffSummary (M1)
└── main.py                 # RacGoatApp entry point

tests/
├── contract/               # API contract tests (Phase 1 output)
│   ├── test_edit_contract.py
│   ├── test_search_contract.py
│   └── test_help_contract.py
├── integration/            # User scenario tests (Phase 1 output)
│   └── test_milestone5/
│       ├── test_edit_scenarios.py
│       ├── test_search_scenarios.py
│       └── test_help_scenarios.py
├── unit/                   # Component tests
│   └── test_search_state.py
└── performance/            # Performance validation
    └── test_search_performance.py
```

**Structure Decision**: Single project layout. All new features extend existing widgets (DiffPane for search, dialogs.py for edit) and leverage existing services (comment_store.py for edit operations). Tests follow established M3/M4 pattern with contract, integration, and unit test separation.

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

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (data-model.md, contracts/, quickstart.md)
- Contract tests already created (35 tests across 3 files) → verify they fail [P]
- Integration tests already created (63 tests across 6 files) → verify they fail [P]
- Each entity in data-model.md → implementation task:
  - SearchState model (new)
  - EditContext helper (new)
  - HelpEntry model (new)
- Each functional area → implementation task:
  - Edit/delete functionality in DiffPane (extend existing)
  - Search functionality in DiffPane (extend existing)
  - Help overlay widget (new HelpScreen modal)
  - Status bar updates for context-sensitive keybindings
- Integration with existing systems:
  - CommentStore edit/delete methods
  - DiffPane event handlers for e, /, ?, n, N keys
  - Main app screen stack management

**Ordering Strategy**:
- TDD order: Verify tests fail → implement → verify tests pass
- Dependency order:
  1. Models (SearchState, EditContext, HelpEntry) [P]
  2. Service extensions (CommentStore edit/delete) [P]
  3. UI widgets (SearchInput, HelpScreen, ConfirmDialog) [P]
  4. Event handlers in DiffPane/RacGoatApp (sequential, depends on models/services)
  5. Status bar context updates (depends on all above)
- Mark [P] for parallel execution (independent files/modules)
- Group by feature (Edit, Search, Help) for clarity

**Estimated Task Count**: ~35-40 tasks
- 2 verification tasks (contract + integration tests fail)
- 6 model/entity tasks
- 8 service method tasks
- 12 UI widget tasks
- 10 event handler tasks
- 4 integration tasks (status bar, keybindings, Markdown output)
- 2 performance validation tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No violations detected.** All design decisions align with constitutional principles. The implementation extends existing patterns (DiffPane, CommentStore, modal screens) without introducing unnecessary complexity.


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, integration tests, CLAUDE.md updated
- [x] Phase 2: Task planning complete (/plan command - approach described above)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (all 6 principles satisfied)
- [x] Post-Design Constitution Check: PASS (no new violations, TDD approach maintained)
- [x] All NEEDS CLARIFICATION resolved (Technical Context has no unknowns)
- [x] Complexity deviations documented (none - no violations to justify)

**Artifacts Generated**:
- `/specs/005-advanced-interaction-usability/research.md` - Textual patterns research
- `/specs/005-advanced-interaction-usability/data-model.md` - 6 entities documented
- `/specs/005-advanced-interaction-usability/quickstart.md` - 18 test scenarios mapped
- `/tests/contract/test_edit_contract.py` - 9 contract tests
- `/tests/contract/test_search_contract.py` - 14 contract tests
- `/tests/contract/test_help_contract.py` - 12 contract tests
- `/tests/integration/test_milestone5/` - 63 integration tests across 6 files
- `/CLAUDE.md` - Updated with M5 context

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
