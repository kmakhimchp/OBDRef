# Milestones: OBDII_WBZ451

## Project Overview

| Field                  | Value                                                        |
|------------------------|--------------------------------------------------------------|
| **Project Title**      | OBDII_WBZ451 — OBD-II Diagnostic Client on WBZ451            |
| **Objective**          | Build a UDS diagnostic client that sends OBD-II requests over CAN, with BLE bridge for wireless access |
| **Target Platform(s)** | Firmware — PIC32CX-BZ2 / WBZ45x (Curiosity board)           |
| **Repository**         | https://bitbucket.microchip.com/users/i41802/repos/aiworkflow |
| **JIRA Project Key**   | PC                                                           |
| **Default Branch**     | master                                                       |
| **Engineer**           | Shanmugasundaram Viswanathan                                 |
| **Created**            | 2026-05-08                                                   |
| **Last Updated**       | 2026-05-08                                                    |

## Dependencies

- CAN1 peripheral pre-configured via MCC (message RAM, TX FIFO, RX FIFO/buffers)
- BLE TRSPS (Transparent UART Profile Service) pre-configured via MCC
- FreeRTOS message queue infrastructure from base project
- SERCOM0 USART for debug console
- iso14229 reference implementation for UDS protocol patterns (`D:\CAN BLE\iso14229`)

## Risks / Unknowns

- ISO-TP multi-frame timing on FreeRTOS — may need tuning of STmin and block size parameters
- CAN bus timing at 500 kbps with real ECU — verified only with the base project's test messages so far
- BLE-to-CAN latency when bridging — diagnostic timeouts (P2/P2*) must account for BLE round-trip

## Completion Criteria

- WBZ451 can send OBD-II diagnostic requests (0x22 RDBI) over CAN and receive valid responses
- UART console allows manual entry of diagnostic commands and displays ECU responses
- BLE-connected device can send diagnostic requests wirelessly and receive responses
- All three milestones pass their six-gate completion process
- Application builds with zero errors and zero warnings

---

## Milestones

### Milestone 1: CAN Transport & ISO-TP Layer

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-353                                                     |
| **Branch**             | Application branch: `obdii_client`                         |
| **Objective**          | Implement ISO 15765-2 (ISO-TP) transport layer on top of the existing CAN1 peripheral, enabling multi-frame UDS message exchange |
| **Inputs**             | Base project CAN1 configuration, iso14229 isotp-c reference |
| **Deliverables**       | isotp_transport module with send/receive/poll API, MODULE.md |

**JIRA Description** _(copy this into the JIRA ticket description):_
> Implement the ISO-TP (ISO 15765-2) transport layer module for the OBD-II client. This provides segmentation and reassembly of UDS messages over CAN frames, supporting Single Frame, First Frame, Consecutive Frame, and Flow Control. Configured with standard OBD-II addressing (0x7E0 TX, 0x7E8 RX, 0x7DF functional). Deliverable: isotp_transport module with polling-based API.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | The module shall implement ISO 15765-2 Single Frame (SF) transmission for payloads up to 7 bytes |
| R2  | The module shall implement ISO 15765-2 First Frame (FF) and Consecutive Frame (CF) transmission for payloads 8–4095 bytes |
| R3  | The module shall implement Flow Control (FC) frame reception and respect Block Size (BS) and Separation Time (STmin) parameters |
| R4  | The module shall receive and reassemble multi-frame messages from the ECU (FF + CF inbound) |
| R5  | The module shall send Flow Control frames when receiving multi-frame messages |
| R6  | The module shall use CAN ID 0x7E0 for physical requests (tester to ECU) and 0x7DF for functional requests |
| R7  | The module shall listen on CAN ID 0x7E8 for ECU responses |
| R8  | The module shall provide a polling-based API: `isotp_send()`, `isotp_receive()`, `isotp_poll()` |
| R9  | The module shall integrate with the existing CAN1 RX FIFO callbacks for incoming frame notification |
| R10 | The module shall report timeout errors if a multi-frame transfer does not complete within 1000ms (N_Bs, N_Cr timeouts) |

**Definition of Ready** _(all must be checked before moving to In Progress):_
- [ ] Previous milestone is complete and merged to the application branch (or this is Milestone 1)
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description, and Epic Link field set to the application epic via `jira_update_issue`
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `isotp_transport` — new — MODULE.md stub location: `can_peripheral_trp_uart/firmware/src/app_modules/isotp_transport/MODULE.md`

**Acceptance Criteria** _(derived from requirements — reference requirement numbers):_
- [ ] R1: Single Frame messages (<=7 bytes) are correctly formatted and transmitted on CAN ID 0x7E0
- [ ] R2, R6: Multi-frame messages are segmented into FF+CF and transmitted with correct sequence numbering
- [ ] R3: Flow Control parameters from the receiver are respected (block size, separation time)
- [ ] R4, R5: Incoming multi-frame messages are reassembled and FC is sent back to the ECU
- [ ] R7: Module listens on 0x7E8 and passes received frames to the reassembly logic
- [ ] R8: Public API (`isotp_send`, `isotp_receive`, `isotp_poll`) is functional and callable from the app task
- [ ] R9: CAN1 RX callbacks feed frames into the ISO-TP layer without blocking
- [ ] R10: Timeout errors are reported when transfers exceed 1000ms

**AI Tool Usage:**
Generate ISO-TP implementation adapted from iso14229's isotp-c reference. Rewrite for PIC32CX-BZ2 CAN1 HAL integration. Generate MODULE.md documentation.

**Code Review Checklist:** Passed — see `docs/reviews/REVIEW_M1.md`

**Milestone Testing:** Passed — see `docs/tests/TEST_M1.md`

**Completion:**
- [x] All acceptance criteria met
- [x] Build succeeds (zero errors, zero warnings)
- [x] Code review checklist passed
- [x] Documentation updated (MODULE.md finalized, README.md updated)
- [x] Milestone testing completed — all tests pass
- [x] Test report saved to `docs/tests/TEST_M1.md`
- [x] Committed on application branch with message: `Milestone 1 [PC-353]: CAN Transport & ISO-TP Layer`
- [x] JIRA ticket updated to Done

---

### Milestone 2: UDS Client Core

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-354                                                     |
| **Branch**             | Application branch: `obdii_client`                         |
| **Objective**          | Implement the UDS client state machine with four core diagnostic services and a UART console interface |
| **Inputs**             | Milestone 1 (isotp_transport module), iso14229 client reference |
| **Deliverables**       | uds_client module, obd_pids module, UART command console, MODULE.md files |

**JIRA Description** _(copy this into the JIRA ticket description):_
> Implement the UDS client state machine supporting Diagnostic Session Control (0x10), Tester Present (0x3E), ECU Reset (0x11), and Read Data By Identifier (0x22). Includes a DID table for common OBD-II parameters (RPM, speed, coolant temp, throttle position) and a UART command console for manual diagnostic interaction. Uses the ISO-TP transport from Milestone 1.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | The UDS client shall maintain a state machine with states: IDLE, SENDING, AWAITING_RESPONSE, ERROR |
| R2  | The client shall implement Diagnostic Session Control (SID 0x10) to enter Default, Extended, and Programming sessions |
| R3  | The client shall implement Tester Present (SID 0x3E) with suppress-positive-response option |
| R4  | The client shall implement ECU Reset (SID 0x11) for Hard Reset, Key-Off-On, and Soft Reset sub-functions |
| R5  | The client shall implement Read Data By Identifier (SID 0x22) supporting multiple DIDs in a single request |
| R6  | The client shall handle Negative Response Codes (NRC) and report the specific NRC to the caller |
| R7  | The client shall implement P2 timeout (150ms default) and P2* timeout (5000ms after NRC 0x78 — Response Pending) |
| R8  | The obd_pids module shall define a lookup table mapping standard OBD-II PIDs to DID values, names, units, and scaling formulas |
| R9  | The obd_pids module shall include at minimum: Engine RPM (0x0C), Vehicle Speed (0x0D), Coolant Temperature (0x05), Throttle Position (0x11), Engine Load (0x04) |
| R10 | The UART console shall accept text commands (e.g., `read rpm`, `session extended`, `reset hard`) and display formatted responses |

**Definition of Ready** _(all must be checked before moving to In Progress):_
- [ ] Previous milestone is complete and merged to the application branch
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description, and Epic Link field set to the application epic via `jira_update_issue`
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `uds_client` — new — MODULE.md stub location: `can_peripheral_trp_uart/firmware/src/app_modules/uds_client/MODULE.md`
- `obd_pids` — new — MODULE.md stub location: `can_peripheral_trp_uart/firmware/src/app_modules/obd_pids/MODULE.md`

**Acceptance Criteria** _(derived from requirements — reference requirement numbers):_
- [ ] R1: State machine transitions correctly between IDLE -> SENDING -> AWAITING_RESPONSE -> IDLE (or ERROR)
- [ ] R2: DiagSessionControl request is correctly formatted and session type is tracked
- [ ] R3: TesterPresent keepalive works with and without suppress-positive-response
- [ ] R4: ECU Reset requests are correctly formatted for all three sub-functions
- [ ] R5: RDBI requests encode multiple DIDs and responses are correctly parsed
- [ ] R6: Negative responses are decoded and the NRC value is reported
- [ ] R7: P2 timeout triggers error state; NRC 0x78 extends wait to P2*
- [ ] R8, R9: OBD-II PID table contains at least 5 entries with correct DID mapping and scaling
- [ ] R10: UART console accepts commands and displays human-readable diagnostic results

**AI Tool Usage:**
Generate UDS client implementation adapted from iso14229 client.c/client.h reference. Generate OBD-II PID table with standard Mode 01 PIDs mapped to UDS DIDs. Generate UART command parser.

**Code Review Checklist:** Passed — see `docs/reviews/REVIEW_M2.md`

**Milestone Testing:** Passed — see `docs/tests/TEST_M2.md`

**Completion:**
- [x] All acceptance criteria met
- [x] Build succeeds (zero errors, zero warnings)
- [x] Code review checklist passed
- [x] Documentation updated (MODULE.md finalized, README.md updated)
- [x] Milestone testing completed — all tests pass
- [x] Test report saved to `docs/tests/TEST_M2.md`
- [x] Committed on application branch with message: `Milestone 2 [PC-354]: UDS Client Core`
- [x] JIRA ticket updated to Done

---

### Milestone 3: BLE-CAN Diagnostic Bridge

| Field                  | Details                                                    |
|------------------------|------------------------------------------------------------|
| **Status**             | Complete                                                   |
| **JIRA ID**            | PC-355                                                     |
| **Branch**             | Application branch: `obdii_client`                         |
| **Objective**          | Bridge BLE transparent UART service to the UDS client, enabling wireless OBD-II diagnostics from a phone or PC |
| **Inputs**             | Milestone 2 (uds_client, obd_pids), existing BLE TRSPS service |
| **Deliverables**       | ble_diag_bridge module, updated app.c integration, MODULE.md |

**JIRA Description** _(copy this into the JIRA ticket description):_
> Implement the BLE-CAN diagnostic bridge module that receives UDS diagnostic commands via BLE Transparent UART and forwards them through the UDS client to the CAN bus. ECU responses are relayed back to the BLE-connected device. Includes a simple framing protocol for request/response demarcation over BLE.

**Requirements:**

| #   | Requirement                                                                     |
|-----|---------------------------------------------------------------------------------|
| R1  | The module shall receive diagnostic command frames from BLE TRSPS and parse them into UDS service requests |
| R2  | The module shall forward parsed UDS requests to the uds_client module for transmission over CAN |
| R3  | The module shall relay UDS responses (positive and negative) back to the BLE-connected device via TRSPS |
| R4  | The module shall define a simple frame protocol: [LEN_H][LEN_L][SERVICE_ID][DATA...] for BLE packets |
| R5  | The module shall handle BLE disconnection gracefully — cancel any pending UDS transaction |
| R6  | The module shall support concurrent UART console and BLE access with proper mutual exclusion |
| R7  | The module shall indicate diagnostic activity via an LED or status message on the UART console |
| R8  | The module shall reject malformed BLE frames with an error response code |

**Definition of Ready** _(all must be checked before moving to In Progress):_
- [ ] Previous milestone is complete and merged to the application branch
- [ ] Requirements written (numbered, specific, verifiable) in MILESTONES.md
- [ ] JIRA ticket created with module summary and requirements as description, and Epic Link field set to the application epic via `jira_update_issue`
- [ ] Requirements signed off by the engineer on the JIRA ticket
- [ ] MODULE.md stubs created for all modules this milestone will create or modify
- [ ] CLAUDE.md Active Milestone updated with milestone, JIRA ID, and branch name
- [ ] AI tool loaded with context: CLAUDE.md, this milestone's details, relevant MODULE.md files, folder structure

**Modules Involved:**
- `ble_diag_bridge` — new — MODULE.md stub location: `can_peripheral_trp_uart/firmware/src/app_modules/ble_diag_bridge/MODULE.md`

**Acceptance Criteria** _(derived from requirements — reference requirement numbers):_
- [ ] R1: BLE frames are correctly parsed into UDS service ID + data
- [ ] R2: Parsed requests trigger UDS client operations over CAN
- [ ] R3: ECU responses are packaged and sent back over BLE TRSPS
- [ ] R4: Frame protocol is documented and correctly implemented (length prefix + service ID + data)
- [ ] R5: BLE disconnect cancels pending transaction without crashing
- [ ] R6: Simultaneous UART and BLE diagnostic requests are handled without data corruption
- [ ] R7: Activity indication works (LED toggle or UART status print)
- [ ] R8: Malformed frames return an error code to the BLE client

**AI Tool Usage:**
Generate BLE bridge module integrating existing app_trsps_handler with the UDS client. Define BLE frame protocol. Handle concurrency between UART console and BLE paths.

**Code Review Checklist:** Passed — see `docs/reviews/REVIEW_M3.md`

**Milestone Testing:** Passed — see `docs/tests/TEST_M3.md`

**Completion:**
- [x] All acceptance criteria met
- [x] Build succeeds (zero errors, zero warnings)
- [x] Code review checklist passed
- [x] Documentation updated (MODULE.md finalized, README.md updated)
- [x] Milestone testing completed — all tests pass
- [x] Test report saved to `docs/tests/TEST_M3.md`
- [x] Committed on application branch with message: `Milestone 3 [PC-355]: BLE-CAN Diagnostic Bridge`
- [x] JIRA ticket updated to Done

---

## Change Log

| Date       | Change Description                                  |
|------------|-----------------------------------------------------|
| 2026-05-08 | Initial milestone document created                  |
| 2026-05-08 | Milestone 1 completed — ISO-TP module implemented   |
| 2026-05-08 | Milestone 2 completed — UDS client + OBD PIDs + console |
| 2026-05-08 | Milestone 3 completed — BLE-CAN diagnostic bridge |
