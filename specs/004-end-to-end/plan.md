
# Implementation Plan: End-to-End Workflow & Markdown Output

**Branch**: `004-end-to-end` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/004-end-to-end/spec.md`

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
Implement the end-to-end workflow for RacGoat's comment persistence system. When users quit the application after adding comments during diff review, serialize all in-memory comments to Markdown format and write to the specified output file (via `-o` flag or default `review.md`). Include git metadata (branch name, commit SHA) in the output header. Skip file creation if no comments exist. Handle edge cases including file write errors, existing files, missing git metadata, and special Markdown characters in comments.

## Technical Context
**Language/Version**: Python 3.12+
**Primary Dependencies**: Textual >=6.2.0 (TUI framework), pytest >=8.4.2 (testing)
**Storage**: File system (Markdown output files), in-memory comment store (existing from Milestone 3)
**Testing**: pytest with pytest-asyncio >=1.2.0 for async TUI testing
**Target Platform**: Linux/macOS/Windows terminal environments (cross-platform TUI)
**Project Type**: single (TUI application with parser, services, UI layers)
**Performance Goals**: File write operations must complete within 5 seconds for up to 100 comments
**Constraints**: Support up to 100 comments without performance degradation; preserve comment content exactly (including special Markdown characters)
**Scale/Scope**: Single-user TUI application, up to 100 files and 10k diff lines per review session, up to 100 comments per session

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fun Is a Feature (NON-NEGOTIABLE)
✅ **PASS** - Output generation will use playful messaging ("No trash to dump!" when no comments exist, "Climbing the git tree..." for metadata extraction). Error modals will maintain raccoon/goat theme while remaining helpful.

### II. TUI-First Experience
✅ **PASS** - File write operations are non-blocking (asynchronous). Modal dialogs for error handling integrate seamlessly with Textual framework. Performance target (<5s for 100 comments) ensures responsive exit flow.

### III. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - All output serialization, file writing, git metadata extraction, and error handling will be implemented with contract tests first, followed by integration tests for the full quit workflow.

### IV. Performance Within Constraints
✅ **PASS** - 100 comment maximum aligns with PRD scale (100 files, 10k lines). File I/O operations are async to avoid blocking TUI. Performance target (5s write time) validated via performance tests.

### V. Data Integrity Over Convenience
✅ **PASS** - Comments preserved exactly as entered (special Markdown characters not escaped per FR-010a). Git metadata uses placeholders when unavailable rather than failing. File overwrite protection prevents accidental data loss (FR-002a).

### VI. Graceful Degradation
✅ **PASS** - Multiple error handling paths defined: existing file → modal with retry option; write errors → modal with /tmp fallback; missing git metadata → placeholders. No crashes on edge cases.

**Initial Constitution Check: PASS** - All principles satisfied, no violations to track.

---

### Post-Design Constitution Re-Check

After completing Phase 1 design (data model, contracts, quickstart):

#### I. Fun Is a Feature (NON-NEGOTIABLE)
✅ **PASS** - Quickstart includes playful test names ("Raccoon reviews diff, stashes treasures to Markdown", "Goat leaves no droppings when pasture is empty"). Error modal messages maintain theme.

#### II. TUI-First Experience
✅ **PASS** - Modal dialogs use Textual's `ModalScreen` pattern. File I/O uses `pathlib` for cross-platform compatibility. No blocking operations in TUI event loop (research.md confirms async pattern).

#### III. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - Contracts define expected behavior (markdown-output-schema.md, git-metadata-contract.md). Quickstart provides 7 test scenarios. Integration tests written before implementation.

#### IV. Performance Within Constraints
✅ **PASS** - Data model caps at 100 comments (NFR-001). Research validates <5s write time. No lazy loading needed for this scale.

#### V. Data Integrity Over Convenience
✅ **PASS** - Data model enforces immutability (frozen dataclasses). Comments preserved exactly (no escaping). Git metadata uses placeholders, never fails.

#### VI. Graceful Degradation
✅ **PASS** - Error modals provide recovery paths (retry, /tmp fallback). Missing git metadata → placeholders. Invalid paths → user-friendly errors.

**Post-Design Constitution Check: PASS** - Design maintains constitutional compliance.

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
│   └── comments.py          # Comment data classes (from Milestone 3)
├── services/
│   ├── comment_store.py     # In-memory comment storage (from Milestone 3)
│   ├── markdown_writer.py   # NEW: Comment → Markdown conversion
│   └── git_metadata.py      # NEW: Git branch/SHA extraction
├── cli/
│   ├── args.py              # Existing: CLI argument parsing (-o flag)
│   └── main.py              # Existing: Entry point (Milestone 1)
├── parser/
│   ├── models.py            # DiffFile, DiffHunk models (Milestone 1-2)
│   └── diff_parser.py       # Diff parsing logic (Milestone 1)
├── ui/
│   ├── widgets/
│   │   ├── files_pane.py    # Left pane file list (Milestone 2)
│   │   ├── diff_pane.py     # Right pane diff view (Milestone 2)
│   │   ├── comment_input.py # Comment input modal (Milestone 3)
│   │   └── error_modal.py   # NEW: File write error handling
│   └── models.py            # UI data models (Milestone 2)
├── main.py                  # RacGoatApp TUI application (Milestone 2)
└── __main__.py              # Module entry point

tests/
├── contract/
│   ├── test_milestone3/     # Existing: Comment store contracts
│   └── test_milestone4/     # NEW: Output serialization contracts
├── integration/
│   ├── test_milestone2/     # Existing: TUI navigation tests
│   ├── test_milestone3/     # Existing: Comment workflow tests
│   └── test_milestone4/     # NEW: End-to-end quit workflow tests
└── unit/
    ├── test_diff_parser.py  # Existing: Parser unit tests
    └── test_markdown_serializer.py  # NEW: Serialization unit tests
```

**Structure Decision**: Single project structure (Option 1). RacGoat is a standalone TUI application with clear separation: `models/` for data, `services/` for business logic (comment storage, serialization, git metadata), `cli/` for argument parsing, `parser/` for diff processing, and `ui/` for Textual widgets. Tests mirror source structure with contract/integration/unit layers following TDD principles from the constitution.

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
1. **Load template**: `.specify/templates/tasks-template.md` as base structure
2. **Extract from contracts**:
   - `markdown-output-schema.md` → contract test for serialization format
   - `git-metadata-contract.md` → contract test for git extraction
3. **Extract from data model** (`data-model.md`):
   - Comment model classes (LineComment, RangeComment, FileComment)
   - ReviewSession container class
4. **Extract from quickstart** (`quickstart.md`):
   - 7 integration test scenarios (happy path, no comments, default name, file exists error, invalid path error, missing git, special chars)
   - Performance test (100 comments in <5s)

**Task Categories** (TDD order):
1. **Contract Tests** [P] - Define API expectations:
   - Test: Markdown serialization format validation
   - Test: Git metadata extraction with fallback

2. **Model Implementation** [P] - Data structures:
   - Create: Comment dataclass hierarchy (models/comments.py)
   - Create: ReviewSession container

3. **Service Implementation**:
   - Create: MarkdownSerializer service (services/markdown_serializer.py)
   - Create: GitMetadata extractor (services/git_metadata.py)
   - Tests: Unit tests for serialization logic
   - Tests: Unit tests for git extraction

4. **UI Components**:
   - Create: ErrorModal base widget (ui/widgets/error_modal.py)
   - Create: FileExistsModal variant
   - Create: WriteErrorModal variant
   - Tests: Modal interaction tests

5. **Integration Layer**:
   - Update: RacGoatApp.action_quit() to orchestrate save workflow
   - Integration: Wire comment store → serializer → file writer
   - Tests: 7 end-to-end scenarios from quickstart

6. **Performance Validation**:
   - Test: 100 comments write time <5s

**Ordering Strategy**:
- **TDD order**: All tests before corresponding implementation
- **Dependency order**:
  - Models → Services → UI → Integration
  - Independent components marked [P] for parallel execution
- **Constitutional order**: Fun test names required for all test tasks

**Estimated Task Count**: 28-32 tasks
- Contract tests: 2
- Model implementation: 4 (2 tests + 2 impl)
- Service layer: 8 (4 tests + 4 impl)
- UI widgets: 6 (3 tests + 3 impl)
- Integration: 10 (7 scenario tests + performance test + 2 impl)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

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
- [ ] Phase 3: Tasks generated (/tasks command) - **NEXT STEP**
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented (N/A - no violations) ✅

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
