# Project: DOSConsole_WBZ451

## Initial Prompt
> Build a DOS command console simulator on the WBZ451 Curiosity board that recognizes common DOS commands, prints "valid DOS command" for recognized commands, and "invalid DOS command" for unrecognized input.

## Description
DOS command console simulator on WBZ451 Curiosity board, built on top
of the existing USART ring buffer interrupt Harmony project.
The Harmony/MCC config is complete — SERCOM1 USART ring buffer mode is
pre-configured. This project modifies only application-owned files.
Target platform: PIC32CX-BZ2 / WBZ45 firmware.

## Repository Owner
- Name: `Shanmugasundaram Viswanathan`
- Email: `shanmugasundaram.viswanathan@microchip.com`

## JIRA Configuration
- JIRA Project Key: `PC`
- JIRA Project URL: `https://jira.microchip.com/projects/PC`
- JIRA Assignee Email: `shanmugasundaram.viswanathan@microchip.com`
- JIRA Epic ID: `PC-348`

## Active Milestone
All milestones complete. See MILESTONES.md for the full history.
- **Application Branch:** `dos_console`
- **JIRA Epic:** PC-348 (all children Done)

## Rules for AI Tools

### Workflow Guide (MANDATORY)
Run `python generate_workflow.py` to regenerate `Workflow.html` after **every** significant workflow step:
- Definition of Ready completion (JIRA ticket created, branch created)
- Each six-gate milestone completion (all gates passed)
- Each milestone merge into the application branch
- Any milestone status change in MILESTONES.md

This is non-optional. The AI tool must run this script at each of these points. Failure to do so means the workflow guide is stale and does not reflect actual project state.

### Definition of Ready (Before Starting Any Milestone)
Before generating code for a milestone, you (the AI tool) must confirm:
1. This CLAUDE.md file is loaded and the Active Milestone section shows the current milestone's JIRA ID and branch name.
2. You are working on the correct milestone branch, not on `dos_console` or the default branch.
3. The current milestone's details from MILESTONES.md have been provided.
4. MODULE.md files for every module the milestone will create or modify exist as stubs at minimum.
5. The project's current folder structure has been shared.
6. `Workflow.html` has been regenerated via `python generate_workflow.py`.

### Folder Structure
- Follow the folder structure already established in this repository. Do not create new top-level directories without explicit approval.
- Application modules go under `firmware/src/app_modules/`.
- Existing structure must be preserved.

### File Constraints
- Every file must have a single, clear purpose. If a file does two unrelated things, split it.
- No file may exceed **300 lines**. If approaching this limit, refactor into smaller, focused files.
- File and folder names must be descriptive. Do not use generic names like `utils`, `helpers`, `misc`, or `temp`.

### Module Rules
- Group related files (3+) into a subfolder recognized as a module.
- Every module folder **must** contain a MODULE.md describing the module's purpose, interfaces, and design.
- Module boundaries must be respected — do not reach into another module's internal files.

### Documentation Standards
- Update MODULE.md for any module that is created or modified.
- Update the project README.md to reflect the current module map, data flow, and architecture.
- Documentation is part of every milestone — not an afterthought.

### Branching & JIRA Rules
- Every milestone has a JIRA ticket and a dedicated branch: `DOSConsole_module_<JIRAID>`.
- **Every milestone JIRA ticket must be linked to the application Epic (`PC-348`) immediately after creation** using `jira_link_to_epic(issue_key, "PC-348")`. An unlinked ticket is an incomplete Definition of Ready.
- All work for a milestone must happen on its dedicated branch. Do not commit directly to `dos_console` or the default branch.

### Build & Commit Rules
- **Do not commit code that does not build.** A milestone is only complete when the build succeeds.
- The AI tool runs `cmake --build .` from the build directory to validate the build automatically. If the build fails, the AI tool fixes errors and rebuilds before committing.
- Commit messages must reference both the milestone and JIRA ID: `Milestone N [JIRAID]: [Title]`.

### Code Review
- Before any milestone commit, complete the code review checklist (CODE_REVIEW_CHECKLIST.md).
- All checklist items must pass. No exceptions.

### Testing
- Every milestone must be tested before merge.
- Tests must cover five dimensions: requirements verification, module functionality, use cases, data flow, and AI code verification.
- Use TEMPLATE_TESTING.md to create the test report: `docs/tests/TEST_MN.md`.
- Zero failed tests is required for milestone completion.

## Build Validation

| Platform | Build Method | Working Directory | Expected Result |
|----------|-------------|-------------------|-----------------|
| Firmware | `cmake --build .` (automated by AI tool) | `_build/usart_ring_buffer_interrupt_wbz451_curiosity/wbz451_curiosity/` | Zero errors, `.elf`/`.hex` output in `out/usart_ring_buffer_interrupt_wbz451_curiosity/` |

**Adding new source files:** Create or update `user.cmake` in `cmake/usart_ring_buffer_interrupt_wbz451_curiosity/wbz451_curiosity/` to append new source files to the compile list variable. Do not modify `.generated/file.cmake`.

**Build is automated [AUTO]:** The AI tool runs `cmake --build .` from the build directory after code changes. If the build fails, the AI tool fixes the errors and rebuilds. Only hardware testing (flashing and UART verification) remains manual.

## Restrictions / Guardrails
- Do not modify any MCC-generated or Harmony framework source files (files under `firmware/src/config/` or `firmware/src/packs/`).
- Do not reconfigure peripherals outside of MCC.
- Application code goes in `firmware/src/app_modules/` and `firmware/src/main.c`.
