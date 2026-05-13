# Project: OBDII_WBZ451

## Initial Prompt
> Build an OBD-II diagnostic client application on the WBZ451 Curiosity board using CAN, with BLE transparent UART bridge for wireless diagnostic access. The application sends UDS requests (Read Data By Identifier, Diagnostic Session Control, Tester Present, ECU Reset) over CAN to vehicle ECUs, and bridges diagnostic commands received via BLE to the CAN bus.

## Description
OBD-II diagnostic client (tester) on WBZ451 Curiosity board, built on top
of the existing CAN peripheral transparent UART Harmony project.
The device acts as a UDS client sending diagnostic requests over CAN to
vehicle ECUs, supporting core OBD-II services. A BLE transparent UART
bridge allows a phone or PC to send diagnostic commands wirelessly.
The Harmony/MCC config is complete — CAN1 and BLE TRSPS are pre-configured.
This project modifies only application-owned files.
Target platform: PIC32CX-BZ2 / WBZ45x firmware.

## Repository Owner
- Name: `Shanmugasundaram Viswanathan`
- Email: `shanmugasundaram.viswanathan@microchip.com`

## JIRA Configuration
- JIRA Project Key: `PC`
- JIRA Project URL: `https://jira.microchip.com/projects/PC`
- JIRA Assignee Email: `shanmugasundaram.viswanathan@microchip.com`
- JIRA Epic ID: `PC-352`

## Active Milestone

See MILESTONES.md — currently working on **Milestone 3: BLE-CAN Diagnostic Bridge**.
- **JIRA ID:** PC-355 (Epic: PC-352)
- **Application Branch:** `obdii_client`
- **Previous:** Milestone 2 (PC-354) — Complete

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
1. This CLAUDE.md file is loaded and the Active Milestone section shows the current milestone's JIRA ID.
2. You are working on the application branch (`obdii_client`), not on the default branch.
3. The current milestone's details from MILESTONES.md have been provided.
4. MODULE.md files for every module the milestone will create or modify exist as stubs at minimum.
5. The project's current folder structure has been shared.
6. `Workflow.html` has been regenerated via `python generate_workflow.py`.

### JIRA & Commit Rules
- Every milestone JIRA ticket must have its Epic Link field set to the application Epic immediately after creation using `jira_update_issue(issue_key, {"customfield_11220": "<EPIC_KEY>"})`. Do NOT use `jira_link_to_epic` — it creates a link relationship but does not set the Epic Link field. An unlinked ticket is an incomplete Definition of Ready.
- All milestone work is committed directly to the application branch (`obdii_client`). Do not commit to the default branch.
- The application branch is pushed and a PR is created only at project completion — after all milestones pass their testing gates.

### Folder Structure
- Follow the folder structure already established in this repository. Do not create new top-level directories without explicit approval.
- Application modules go in `can_peripheral_trp_uart/firmware/src/app_modules/`.

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

### Build & Commit Rules
- Do not commit code that does not build.
- Build validation is automated when possible. The AI tool runs `cmake --build` from the project's build directory after code changes.
- Incremental commits are permitted on the application branch.
- Commit messages must reference both the milestone and JIRA ID: `Milestone N [JIRAID]: [Title]`.

### Code Review
- Before creating a PR, complete the code review checklist (CODE_REVIEW_CHECKLIST.md).
- All checklist items must pass. No exceptions.

### Testing
- Every milestone must be tested before merge.
- Tests must cover five dimensions: requirements verification, module functionality, use cases, data flow, and AI code verification.
- Use TEMPLATE_TESTING.md to create the test report: `docs/tests/TEST_MN.md`.
- Zero failed tests is required for milestone completion.

### Milestone Lifecycle (Automated via MCP)
The AI tool automates lifecycle operations when MCP servers for JIRA and Bitbucket are configured.

**At Definition of Ready (start of milestone):**
1. Verify previous milestone is Done via `jira_get_issue` (skip for Milestone 1)
2. Create JIRA ticket via `jira_create_issue` and set Epic Link via `jira_update_issue(issue_key, {"customfield_11220": "<EPIC_KEY>"})`
3. Record returned JIRA ID in MILESTONES.md and CLAUDE.md Active Milestone
4. **[HUMAN GATE]** Wait for engineer to sign off requirements on the JIRA ticket
5. Update CLAUDE.md Active Milestone section
6. Transition JIRA to In Progress via `jira_transition_issue`
7. Run `python generate_workflow.py` to update the workflow guide

**At Milestone Completion (after build + review + testing pass):**
1. Commit test report to application branch
2. Transition JIRA to Done via `jira_transition_issue`
3. Add completion comment to JIRA ticket via `jira_add_comment`
4. Run `python generate_workflow.py` to update the workflow guide

**At Project Completion (after all milestones pass):**
1. Push application branch to remote via `git push -u origin obdii_client`
2. Create Pull Request on Bitbucket via `create_pull_request` (obdii_client -> master)
3. Post code review findings as inline PR comments via `add_comment`
4. **[HUMAN GATE]** Engineer reviews and approves the PR
5. Merge PR via `merge_pull_request` after engineer approval
6. Transition JIRA Epic to Done via `jira_transition_issue`
7. Run `python generate_workflow.py` to update the workflow guide

**Session Resume Protocol:**
When resuming in a new AI session, the AI tool must:
1. Read CLAUDE.md to identify the active milestone, JIRA ID, and branch
2. Query the JIRA ticket status via `jira_get_issue`
3. Check local artifacts (test reports, review reports, git log) to determine which gates have passed
4. Do not re-do completed work or skip incomplete gates

**Build System — Adding New Source Files:**
Register new source files in `can_peripheral_trp_uart/cmake/user.cmake`. Do not modify MCC-generated build files directly.

## Build Validation

**Build validation is automated [AUTO].** The AI tool runs the build commands below via CLI after code changes. If the AI tool cannot access the XC32 toolchain, builds fall back to [MANUAL].

### Build Commands

| Platform | Build Command | Working Directory | Expected Result |
|----------|--------------|-------------------|-----------------|
| Firmware | VS Code: **CMake: Build** using preset `can_peripheral_trp_uart_wbz451_curiosity_conf` | `can_peripheral_trp_uart/cmake/` | Zero errors, zero warnings, `.elf`/`.hex` output |

## Dependencies

- iso14229 reference library (at `D:\CAN BLE\iso14229`) — UDS protocol reference implementation
- isotp-c (embedded in iso14229) — ISO 15765-2 transport protocol for CAN
- Microchip Harmony 3 — framework (pre-configured via MCC)
- XC32 Compiler 4.60 — build toolchain
- FreeRTOS 11.1.0 — RTOS kernel (pre-configured)

## Restrictions / Guardrails

- Do not modify MCC-generated files in `can_peripheral_trp_uart/firmware/src/config/` or `packs/`
- All new application code goes in `can_peripheral_trp_uart/firmware/src/` or `can_peripheral_trp_uart/firmware/src/app_modules/`
- The iso14229 library is reference only — adapt and rewrite for this platform, do not copy wholesale
- No third-party libraries without explicit approval
- CAN communication uses standard OBD-II addressing (0x7E0/0x7E8/0x7DF)
