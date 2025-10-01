
# Implementation Plan: CLI Git Diff Processor & Summary Generator

**Branch**: `001-goal-create-a` | **Date**: 2025-09-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/jjshanks/workspace/racgoat/specs/001-goal-create-a/spec.md`

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
Create a CLI tool that reads git diff from stdin, parses changed files, counts added/removed lines, filters out binary files and generated files (`.lock`, `.min.js`, `.min.css`, `.map`, `.bundle.js`, package manager lockfiles, `*.generated.*`, `dist/`, `build/`), and writes a text summary to a file specified by `-o` flag (default: `review.md`). Handle empty diffs gracefully by skipping file creation. Exit with code 0 for success, 1 for failures.

## Technical Context
**Language/Version**: Python 3.12+ (configured in pyproject.toml and .python-version)
**Primary Dependencies**: Standard library (argparse for CLI, sys for stdin/stdout)
**Storage**: File system only (write output to specified filename)
**Testing**: pytest (existing dev dependency)
**Target Platform**: Cross-platform CLI (Linux/macOS/Windows with Python 3.12+)
**Project Type**: Single project (CLI-only tool, no frontend/backend split)
**Performance Goals**: Process up to 100 files and 10k diff lines (per PRD constraints)
**Constraints**: Stdin-based input, single output file, exit codes (0=success, 1=failure)
**Scale/Scope**: CLI parser milestone only - TUI features deferred to future milestones

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fun Is a Feature (NON-NEGOTIABLE)
- **Status**: ⚠️ DEFERRED - This milestone focuses on CLI data processing logic
- **Rationale**: Milestone 1 (CLI parser) intentionally omits TUI/humor elements. The raccoon/goat theme applies to future TUI milestones (2-6). Function names will remain descriptive but professional for this foundation.
- **Compliance Plan**: Milestone 2+ will introduce themed UI elements, keybindings, and playful error messages per constitution

### II. TUI-First Experience
- **Status**: ⚠️ DEFERRED - CLI-only milestone (no TUI components)
- **Rationale**: PRD roadmap explicitly sequences CLI parser (M1) before TUI (M2). This milestone validates data pipeline without UI complexity.
- **Compliance Plan**: Milestone 2 introduces Textual framework, two-pane layout, keyboard navigation per constitution

### III. Test-Driven Development (NON-NEGOTIABLE)
- **Status**: ✅ PASS - TDD mandatory for all implementation
- **Implementation**: All tasks will follow red-green-refactor cycle. Contract tests written before implementation. Integration tests derived from acceptance scenarios in spec.

### IV. Performance Within Constraints
- **Status**: ✅ PASS - Meets PRD scale requirements
- **Implementation**: CLI parser designed to handle 100 files / 10k lines. File filtering happens at parse time (binary/generated file detection). No blocking operations during stdin read.

### V. Data Integrity Over Convenience
- **Status**: ✅ PASS - Accurate line counting and file path preservation
- **Implementation**: Parser extracts exact added/removed line counts from diff hunks. File paths preserved as-is (including special characters). Empty diff handled without creating output file.

### VI. Graceful Degradation
- **Status**: ✅ PASS - Comprehensive error handling
- **Implementation**: Empty diff → skip file creation, exit 0. Malformed diff → error message, exit 1. Invalid CLI args → usage help + exit 1. Per FR-007a, FR-011, FR-012 in spec.

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
├── __init__.py          # Package initialization
├── __main__.py          # Entry point (python -m racgoat)
├── main.py              # Current TUI app (will become diff parser CLI)
├── utils.py             # Utilities (theme-based helpers)
├── parser/              # NEW: Diff parsing logic
│   ├── __init__.py
│   ├── diff_parser.py   # Core diff parsing
│   └── file_filter.py   # Binary/generated file filtering
└── cli/                 # NEW: CLI argument handling
    ├── __init__.py
    └── args.py          # argparse configuration

tests/
├── test_goat.py         # Existing TUI tests
├── unit/                # NEW: Unit tests
│   ├── test_diff_parser.py
│   └── test_file_filter.py
├── integration/         # NEW: Integration tests
│   └── test_cli_workflow.py
└── contract/            # NEW: Contract tests
    └── test_output_format.py
```

**Structure Decision**: Single project (Python package). This milestone adds `parser/` and `cli/` modules to the existing `racgoat/` package. TUI code in `main.py` remains unchanged (used in future milestones). Tests organized by type (unit/integration/contract) to support TDD workflow.

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
1. Load `.specify/templates/tasks-template.md` as base template
2. Generate tasks from Phase 1 artifacts:
   - **From contracts/cli-interface.md**: Contract test tasks for CLI args, stdin/stdout, exit codes
   - **From contracts/output-format.md**: Contract test tasks for output format validation
   - **From data-model.md**: Unit test + implementation tasks for DiffFile, DiffSummary, FileFilter, CLIArguments
   - **From quickstart.md**: Integration test tasks mapping to 9 scenarios (basic, custom output, empty diff, binary filter, generated filter, multiple files, special chars, invalid args, all filtered)
   - **From research.md**: Implementation tasks for diff parser, file filter, CLI args

**Task Categories**:
- **Contract Tests** (implement first, per TDD): 10 contract test tasks from CLI + output contracts
- **Unit Tests + Implementation** (TDD pairs): 8 tasks (4 entities × 2 tasks each: test + impl)
- **Integration Tests** (end-to-end scenarios): 9 tasks from quickstart scenarios
- **Parser Implementation**: 3 tasks (diff parsing, hunk parsing, line counting)
- **Filter Implementation**: 2 tasks (pattern matching, directory filtering)
- **CLI Integration**: 2 tasks (argparse setup, main entry point)
- **Validation**: 1 task (run all tests, verify quickstart)

**Ordering Strategy**:
1. **Contract tests first** (define interface boundaries) - all [P] parallel
2. **Unit tests + models** (TDD red-green cycle) - [P] within each entity
3. **Parser implementation** (make unit tests pass) - sequential (parser → filter)
4. **CLI integration** (wire components together)
5. **Integration tests** (validate end-to-end) - [P] parallel
6. **Final validation** (run quickstart scenarios)

**Dependency Chain**:
```
Contract Tests [P]
  ↓
Unit Tests (DiffFile, FileFilter) [P]
  ↓
Parser Implementation (diff_parser.py)
  ↓
Unit Tests (DiffSummary, CLIArguments) [P]
  ↓
Summary + CLI Implementation
  ↓
Integration Tests [P]
  ↓
Validation
```

**Estimated Output**: 35 numbered, dependency-ordered tasks in tasks.md

**TDD Compliance**: Every implementation task preceded by corresponding test task (Constitution Principle III)

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
| I. Fun Is a Feature (deferred) | Milestone 1 focuses on data pipeline validation without UI | PRD explicitly sequences CLI parser (M1) before TUI (M2). Adding theme now would complicate testing of core parsing logic. Fun elements added in M2+ when TUI framework introduced. |
| II. TUI-First Experience (deferred) | CLI-only milestone, no Textual components | PRD roadmap design decision: validate stdin→parse→output pipeline before adding UI complexity. TUI introduced in M2 with full keyboard navigation and rendering. |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, CLAUDE.md updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - approach documented above
- [x] Phase 3: Tasks generated (/tasks command) - tasks.md created with 37 tasks
- [x] Phase 4: Implementation complete - All 37 tasks completed, 100% test pass rate (124/124 tests)
- [x] Phase 5: Validation passed - Performance validated (0.127s, ~30MB), all features working

**Gate Status**:
- [x] Initial Constitution Check: PASS (2 deferred violations justified in Complexity Tracking)
- [x] Post-Design Constitution Check: PASS (no new violations introduced)
- [x] All NEEDS CLARIFICATION resolved (Technical Context complete, research.md covers all unknowns)
- [x] Complexity deviations documented (see Complexity Tracking table above)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
