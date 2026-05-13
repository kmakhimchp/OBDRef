# Milestones: DOSConsole_WBZ451

## Project Overview

| Field                  | Value                                                        |
|------------------------|--------------------------------------------------------------|
| **Project Title**      | DOSConsole_WBZ451                                            |
| **Objective**          | Build a DOS command console simulator that validates user input against common DOS commands and prints "valid DOS command" or "invalid DOS command" |
| **Target Platform(s)** | PIC32CX-BZ2 / WBZ451 Curiosity Board (Firmware)             |
| **Repository**         | https://bitbucket.microchip.com/users/i41802/repos/aiworkflow |
| **JIRA Project Key**   | PC                                                           |
| **Default Branch**     | master                                                       |
| **Engineer**           | Shanmugasundaram Viswanathan                                 |
| **Created**            | 2026-05-07                                                   |
| **Last Updated**       | 2026-05-07                                                   |

## Dependencies

- MPLAB Harmony 3 SERCOM USART ring buffer driver (pre-configured via MCC)
- XC32 compiler toolchain
- WBZ451 Curiosity board for hardware testing

## Risks / Unknowns

- USART ring buffer size may limit maximum command input length (to be confirmed during Milestone 1)

## Completion Criteria

- Console boots and displays `C:\>` prompt over UART
- User can type commands and press Enter to submit
- Recognized DOS commands print "valid DOS command"
- Unrecognized input prints "invalid DOS command"
- Console is responsive and handles edge cases (empty input, long input, mixed case)

---

## Milestones

### Milestone 1: Console Infrastructure

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-349                                                     |
| **Branch**             | `DOSConsole_module_PC-349` (merged)                        |
| **Objective**          | Establish USART-based console I/O with character echo, line buffering, and command prompt display |
| **Inputs**             | Working Harmony USART ring buffer project (baseline build passes) |
| **Deliverables**       | dos_console module (console I/O), modified main.c, MODULE.md, user.cmake |

**JIRA Description:**
> Console infrastructure module providing USART-based interactive console with character echo, backspace handling, line buffering, and C:\> prompt display. This is the foundation for all subsequent command processing.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | The console shall display `C:\>` as the command prompt after initialization and after each command is processed. |
| R2  | The console shall echo each received printable character back to the terminal. |
| R3  | The console shall support backspace (0x08 or 0x7F) to delete the last entered character with visual feedback. |
| R4  | The console shall accumulate received characters into a line buffer until Enter (CR, 0x0D) is received. |
| R5  | The line buffer shall support a maximum of 80 characters. Characters beyond this limit shall be silently ignored. |
| R6  | When Enter is pressed, the console shall pass the accumulated command string to a command processing callback and then redisplay the prompt. |
| R7  | The console shall print a welcome banner on startup identifying the application. |

**Definition of Ready:**
- [ ] Previous milestone is complete and merged to the application branch (or this is Milestone 1)
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] Branch created from the application branch: `DOSConsole_module_<JIRAID>`
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `dos_console` — new — `firmware/src/app_modules/dos_console/MODULE.md`

**Acceptance Criteria:**
- [ ] R1: After boot and after each command, `C:\>` prompt is displayed
- [ ] R2: Typing characters shows them on terminal in real-time
- [ ] R3: Backspace removes last character from display and buffer
- [ ] R4: Characters accumulate in buffer until Enter
- [ ] R5: Entering more than 80 characters does not overflow buffer
- [ ] R6: Enter key triggers command processing callback with the command string
- [ ] R7: Welcome banner prints on startup

**AI Tool Usage:**
Generate dos_console module with USART read/write abstraction, line buffer management, and character echo logic using the SERCOM1 ring buffer API.

**Code Review Checklist:** Not started

**Milestone Testing:** Not started

**Completion:**
- [ ] All acceptance criteria met
- [ ] Build succeeds (zero errors, zero warnings)
- [ ] Code review checklist passed
- [ ] Documentation updated (MODULE.md finalized, README.md updated)
- [ ] Milestone testing completed — all tests pass
- [ ] Test report saved to `docs/tests/TEST_M1.md`
- [ ] Committed on milestone branch
- [ ] Branch merged into the application branch
- [ ] JIRA ticket updated to Done

---

### Milestone 2: DOS Command Recognition

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-350                                                     |
| **Branch**             | `DOSConsole_module_PC-350` (merged)                        |
| **Objective**          | Implement command parser and DOS command lookup table to validate user input |
| **Inputs**             | Working console infrastructure from Milestone 1            |
| **Deliverables**       | cmd_parser module, dos_commands module, MODULE.md files, updated user.cmake |

**JIRA Description:**
> Command parser and DOS command recognition modules. Parses user input to extract the command name, looks it up against a table of common DOS commands, and prints "valid DOS command" or "invalid DOS command" accordingly.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | The system shall extract the command name from user input (first whitespace-delimited token). |
| R2  | The system shall maintain a lookup table of at least 20 common DOS commands: DIR, CD, CLS, COPY, DEL, MKDIR, RMDIR, TYPE, REN, ECHO, DATE, TIME, VER, VOL, PATH, MOVE, ATTRIB, FIND, MORE, TREE. |
| R3  | If the extracted command matches a table entry, the system shall print `'<command>' is a valid DOS command`. |
| R4  | If the extracted command does not match any table entry, the system shall print `'<input>' is not a valid DOS command`. |
| R5  | Command matching shall be case-insensitive (e.g., `dir`, `DIR`, `Dir` all match). |

**Definition of Ready:**
- [ ] Previous milestone is complete and merged to the application branch
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] Branch created from the application branch: `DOSConsole_module_<JIRAID>`
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `cmd_parser` — new — `firmware/src/app_modules/cmd_parser/MODULE.md`
- `dos_commands` — new — `firmware/src/app_modules/dos_commands/MODULE.md`

**Acceptance Criteria:**
- [ ] R1: Input "DIR /w" extracts command "DIR"
- [ ] R2: All 20 listed commands are present in the lookup table
- [ ] R3: Typing a valid command prints "'DIR' is a valid DOS command"
- [ ] R4: Typing "FOOBAR" prints "'FOOBAR' is not a valid DOS command"
- [ ] R5: "dir", "DIR", "Dir" all recognized as valid

**AI Tool Usage:**
Generate cmd_parser module for token extraction and dos_commands module for the lookup table and validation logic.

**Code Review Checklist:** Not started

**Milestone Testing:** Not started

**Completion:**
- [ ] All acceptance criteria met
- [ ] Build succeeds (zero errors, zero warnings)
- [ ] Code review checklist passed
- [ ] Documentation updated (MODULE.md finalized, README.md updated)
- [ ] Milestone testing completed — all tests pass
- [ ] Test report saved to `docs/tests/TEST_M2.md`
- [ ] Committed on milestone branch
- [ ] Branch merged into the application branch
- [ ] JIRA ticket updated to Done

---

### Milestone 3: Polish and Edge Cases

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-351                                                     |
| **Branch**             | `DOSConsole_module_PC-351` (merged)                        |
| **Objective**          | Add help command, handle edge cases, and polish the user experience |
| **Inputs**             | Working command recognition from Milestone 2               |
| **Deliverables**       | Updated dos_commands module, updated dos_console module, test reports |

**JIRA Description:**
> Polish milestone adding HELP command, empty input handling, whitespace trimming, and overall robustness improvements to the DOS console simulator.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | Typing `HELP` (case-insensitive) shall print a list of all recognized DOS commands. |
| R2  | Empty input (pressing Enter with no characters) shall redisplay the prompt without printing any error message. |
| R3  | Input consisting only of whitespace shall be treated as empty input. |
| R4  | Leading and trailing whitespace in the input shall be trimmed before command extraction. |

**Definition of Ready:**
- [ ] Previous milestone is complete and merged to the application branch
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] Branch created from the application branch: `DOSConsole_module_<JIRAID>`
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `dos_commands` — existing — `firmware/src/app_modules/dos_commands/MODULE.md`
- `dos_console` — existing — `firmware/src/app_modules/dos_console/MODULE.md`

**Acceptance Criteria:**
- [ ] R1: Typing "HELP" displays the full list of recognized commands
- [ ] R2: Pressing Enter on empty line just shows new prompt
- [ ] R3: Entering only spaces/tabs shows new prompt without error
- [ ] R4: "  DIR  " is recognized the same as "DIR"

**AI Tool Usage:**
Extend existing modules with help command handler, whitespace trimming utility, and empty input guard.

**Code Review Checklist:** Not started

**Milestone Testing:** Not started

**Completion:**
- [ ] All acceptance criteria met
- [ ] Build succeeds (zero errors, zero warnings)
- [ ] Code review checklist passed
- [ ] Documentation updated (MODULE.md finalized, README.md updated)
- [ ] Milestone testing completed — all tests pass
- [ ] Test report saved to `docs/tests/TEST_M3.md`
- [ ] Committed on milestone branch
- [ ] Branch merged into the application branch
- [ ] JIRA ticket updated to Done

---

## Change Log

| Date       | Change Description                                  |
|------------|-----------------------------------------------------|
| 2026-05-07 | Initial milestone document created                  |
