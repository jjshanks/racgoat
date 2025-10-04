# Feature Specification: End-to-End Workflow & Markdown Output

**Feature Branch**: `004-end-to-end`
**Created**: 2025-10-02
**Status**: Draft
**Input**: User description: "End-to-End Workflow & Markdown Output
**Goal**: Close the primary user loop by persisting the in-memory comments to the specified Markdown file upon exit.

**Tasks**:
    * On quit, implement the logic to serialize the stored comments into the specified Markdown format.
    * Write the formatted output to the file specified with the `-o` flag (or `review.md`).
    * Ensure no output file is generated if no comments were made.
    * Attempt to extract and include the current `branch name` and `commit sha` in the output header.

**Deliverable**: A complete, functional tool that produces the specified `review.md` artifact."

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
- Q: When the user specifies an output file that already exists, what should the system do? → A: Display a modal dialog with the error and require a different filename via path input
- Q: When file write errors occur (invalid path, no permissions, etc.), how should the system inform the user? → A: Modal dialog within the TUI before exiting, allowing user to specify a new path
- Q: When git metadata (branch name, commit SHA) cannot be extracted, what should the system do? → A: Include placeholder values like "Unknown Branch" and "Unknown SHA"
- Q: When user comments contain special Markdown characters (like *, #, [, etc.), how should the system handle them in the output file? → A: Preserve as-is - allow users' Markdown to render (intentional formatting)
- Q: What is the maximum comment volume the system should handle before implementing pagination or limits? → A: 100

---

## User Scenarios & Testing

### Primary User Story
A developer reviews an AI-generated git diff using the TUI application. After examining the code changes and adding inline comments throughout the review process, they quit the application. The system automatically persists all their comments to a Markdown file (specified via `-o` flag or defaulting to `review.md`), including contextual metadata about the branch and commit being reviewed. If no comments were made during the session, no output file is created.

### Acceptance Scenarios
1. **Given** a user has added comments during their review session and specified `-o custom-review.md`, **When** they quit the application, **Then** the system creates `custom-review.md` containing all comments in Markdown format with branch name and commit SHA in the header
2. **Given** a user has added comments during their review session without specifying an output file, **When** they quit the application, **Then** the system creates `review.md` (default filename) containing all comments with branch and commit metadata
3. **Given** a user has not added any comments during their review session, **When** they quit the application, **Then** no output file is created
4. **Given** a user has added multiple comments on different files and lines, **When** they quit the application, **Then** the output file organizes comments by file with proper line number references
5. **Given** the system successfully extracts git metadata, **When** generating the output file, **Then** the header includes the current branch name and commit SHA
6. **Given** a user has added comments and the specified output file already exists, **When** they quit the application, **Then** the system displays a modal dialog with the error and prompts for a different filename
7. **Given** a file write error occurs (invalid path or no permissions), **When** the system attempts to save, **Then** a modal dialog appears prompting the user to specify a new path
8. **Given** git metadata cannot be extracted, **When** generating the output file, **Then** the header includes placeholder values ("Unknown Branch" and "Unknown SHA") instead of failing

### Edge Cases
- When the output file path is invalid or unwritable (e.g., no permissions, invalid directory), the system displays a modal dialog showing the error and prompts the user to specify a new output path
- When git metadata (branch name or commit SHA) cannot be extracted, the system includes placeholder values ("Unknown Branch" / "Unknown SHA") in the output header rather than failing or omitting the metadata section
- When a comment contains special Markdown characters (*, #, [, etc.), the system preserves them as-is in the output, allowing them to render as intentional Markdown formatting rather than escaping them
- The system supports up to 100 comments without pagination or imposed limits; beyond this threshold is out of scope for this feature
- When the user specifies an output file that already exists, the system displays a modal dialog with the error and prompts for a different filename (does not overwrite)

## Requirements

### Functional Requirements
- **FR-001**: System MUST serialize all in-memory comments to Markdown format when the user quits the application
- **FR-002**: System MUST write the serialized output to the file specified by the `-o` command-line flag
- **FR-002a**: System MUST display a modal dialog per FR-009 if the specified output file already exists, preventing accidental overwrites
- **FR-003**: System MUST default to filename `review.md` when no `-o` flag is provided
- **FR-004**: System MUST NOT create any output file when zero comments have been made during the review session
- **FR-005**: System MUST attempt to extract the current git branch name and include it in the output file header, using "Unknown Branch" as a placeholder if extraction fails
- **FR-006**: System MUST attempt to extract the current git commit SHA and include it in the output file header, using "Unknown SHA" as a placeholder if extraction fails
- **FR-007**: Output file MUST organize comments by file path, with each file section clearly delineated
- **FR-008**: Output file MUST include line number references for each comment to indicate the exact location in the diff
- **FR-009**: System MUST display a modal dialog when file write errors occur (invalid path, permissions, existing file), showing the specific error and prompting for an alternative output path
- **FR-009a**: When a write error occurs, the modal dialog MUST allow the user to specify an alternative output path via text input
- **FR-010**: System MUST preserve comment content exactly as entered by the user, including multi-line comments and special characters
- **FR-010a**: System MUST NOT escape Markdown special characters (*, #, [, etc.) in user comments, allowing them to render as intentional formatting in the output file
- **FR-011**: System MUST use valid Markdown syntax in the output file to ensure proper rendering by Markdown viewers
- **FR-012**: System MUST complete the file write operation before fully exiting the application to prevent data loss

### Non-Functional Requirements

- **NFR-001**: System MUST support serialization and output of up to 100 comments without performance degradation
- **NFR-002**: File write operations MUST complete within 5 seconds for the maximum supported comment volume (100 comments)

### Key Entities

- **Comment**: A user-provided annotation associated with a specific location in the diff (file path, line number, or range), containing the comment text and metadata about its position. See data-model.md for the Comment class hierarchy (LineComment, RangeComment, FileComment)
- **Output Document**: The final Markdown file containing all review comments, organized by file with metadata header including branch name and commit SHA
- **Git Metadata**: Information about the current repository state, specifically the branch name and commit SHA being reviewed

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---
