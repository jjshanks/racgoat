# Feature Specification: CLI Git Diff Processor & Summary Generator

**Feature Branch**: `001-goal-create-a`
**Created**: 2025-09-30
**Status**: ✅ Implemented (100% test coverage, 124/124 tests passing)
**Input**: User description: "**Goal**: Create a non-visual command-line tool that successfully ingests, parses, and summarizes a `git diff`. This validates the entire data input and processing pipeline without any UI complexity.

**Tasks**:
    * Implement logic to read a `git diff` from `stdin`.
    * Parse the diff data to identify changed files and count their added/removed lines.
    * Filter and skip binary, non-text, and specified generated files (e.g., `.lock`, `.min.js`).
    * Implement command-line argument parsing for the `-o <filename>` flag.
    * For this milestone, the tool's output will be a **simple text summary written to a file** (e.g., `path/to/file.py: +10 -5`). The output filename should be controllable via the `-o` flag.
    * Handle the edge case of an empty diff.

**Deliverable**: A runnable CLI that processes a diff and writes a summary of changed files and line counts to an output file."

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

### Session 2025-09-30
- Q: Should the tool filter additional common generated file patterns beyond `.lock` and `.min.js`? → A: Comprehensive: All frontend patterns (`.lock`, `.min.js`, `.map`, `.bundle.js`) + package managers (`package-lock.json`, `yarn.lock`, `poetry.lock`) + `.min.css`, `*.generated.*`, `dist/`, `build/` directories
- Q: What should the default output filename be when the `-o` flag is not provided? → A: `review.md` (Markdown format, aligns with future review features)
- Q: What should the output be when the diff is empty (no changes)? → A: Skip file creation entirely (no output file)
- Q: What exit codes should the tool use for different outcomes? → A: 0 for success (including empty diff), 1 for all failures
- Q: How should the tool handle invalid command-line arguments? → A: Print error + usage help, exit code 1

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A developer wants to quickly understand the scope and impact of code changes in a git diff without manually reviewing each file. They pipe a git diff through the CLI tool, which reads the changes, filters out non-reviewable files (binary files, generated files like lockfiles and minified code), and produces a concise summary showing each changed file with line addition and deletion counts written to an output file.

### Acceptance Scenarios
1. **Given** a git diff with 5 modified text files on stdin, **When** the user runs the tool with `-o summary.txt`, **Then** the tool writes a summary file containing each file path with its line change counts (e.g., `src/main.py: +15 -3`)
2. **Given** a git diff containing both text files and binary files, **When** the tool processes the diff, **Then** the summary includes only text files and excludes binary files
3. **Given** a git diff with generated files (.lock, .min.js), **When** the tool processes the diff, **Then** the summary excludes these filtered files
4. **Given** an empty diff on stdin, **When** the tool runs, **Then** it handles the empty input gracefully and produces an appropriate output
5. **Given** no `-o` flag is provided, **When** the tool runs, **Then** it uses a default output filename for the summary

### Edge Cases
- What happens when stdin contains no data (empty diff)? → No output file is created, exits with code 0
- What happens when the specified output file path is invalid or unwritable? → Tool exits with code 1 (failure)
- What happens when a diff contains only binary or filtered files (resulting in no files to summarize)? → Treated as empty diff; no output file is created, exits with code 0
- What happens when the diff format is malformed or corrupted? → Tool exits with code 1 (failure)
- What happens when file paths in the diff contain special characters or spaces? → Paths are preserved as-is in output
- What happens when invalid command-line arguments are provided? → Tool prints error message + usage help to stderr, exits with code 1

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST read git diff data from stdin
- **FR-002**: System MUST parse diff data to identify all changed files
- **FR-003**: System MUST count added lines for each changed file
- **FR-004**: System MUST count removed lines for each changed file
- **FR-005**: System MUST identify and skip binary files in the diff
- **FR-006**: System MUST identify and skip generated files matching these patterns: `.lock`, `.min.js`, `.min.css`, `.map`, `.bundle.js`, `package-lock.json`, `yarn.lock`, `poetry.lock`, `*.generated.*`, and files within `dist/` or `build/` directories (all patterns are case-sensitive, matching git diff output exactly)
- **FR-007**: System MUST accept a `-o <filename>` command-line argument to specify the output file path
- **FR-007a**: System MUST validate command-line arguments and, when invalid arguments are detected (e.g., `-o` without filename, unknown flags), print an error message followed by usage help to stderr and exit with code 1
- **FR-008**: System MUST write summary output to the file specified by `-o` flag
- **FR-009**: System MUST use `review.md` as the default output filename when `-o` flag is not provided
- **FR-010**: System MUST format each summary line as `path/to/file: +X -Y` where X is added lines and Y is removed lines
- **FR-011**: System MUST handle empty diff input without error and skip output file creation when no changes are present
- **FR-012**: System MUST exit with status code 0 for successful processing (including empty diff handled gracefully) and status code 1 for any failure condition

### Key Entities *(include if feature involves data)*
- **Git Diff**: Raw text input from stdin containing unified diff format with file headers, hunks, and line changes
- **Changed File**: Represents a single file in the diff with its path, added line count, and removed line count
- **Summary Output**: Text file containing one line per changed file, showing file path and change statistics
- **File Filter Rule**: Pattern or criterion for excluding files (binary indicator, file extension patterns for generated files)

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
