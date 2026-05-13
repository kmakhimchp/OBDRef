# OBDII_WBZ451 — OBD-II Diagnostic Client

## Overview

OBD-II diagnostic client (tester) running on the WBZ451 Curiosity board. The device sends UDS (Unified Diagnostic Services) requests over CAN to vehicle ECUs and provides a BLE transparent UART bridge for wireless diagnostic access from a phone or PC.

## Architecture

```
+------------------+       BLE        +------------------+       CAN Bus
|  Phone / PC App  | <-- TRSPS -->    |   WBZ451 Board   | <-- 500kbps -->  [ ECU ]
|  (BLE Client)    |                  |                  |
+------------------+                  |  +-----------+   |
                                      |  | BLE Diag  |   |
     +----------+                     |  | Bridge    |   |
     | UART     | <-- SERCOM0 ----->  |  +-----------+   |
     | Terminal  |                     |       |          |
     +----------+                     |  +-----------+   |
                                      |  | UDS Client|   |
                                      |  | (0x10,3E, |   |
                                      |  |  11, 22)  |   |
                                      |  +-----------+   |
                                      |       |          |
                                      |  +-----------+   |
                                      |  | ISO-TP    |   |
                                      |  | Transport |   |
                                      |  +-----------+   |
                                      |       |          |
                                      |  +-----------+   |
                                      |  | CAN1 HAL  |   |
                                      |  | (MCC)     |   |
                                      |  +-----------+   |
                                      +------------------+
```

## Data Flow

1. **UART Path:** User types command on terminal -> UART RX -> Command Parser -> UDS Client -> ISO-TP -> CAN TX -> ECU -> CAN RX -> ISO-TP -> UDS Client -> Display on terminal
2. **BLE Path:** Phone sends BLE frame -> TRSPS RX -> BLE Diag Bridge -> UDS Client -> ISO-TP -> CAN TX -> ECU -> CAN RX -> ISO-TP -> UDS Client -> BLE Diag Bridge -> TRSPS TX -> Phone

## Supported OBD-II Services

| Service | SID | Description |
|---------|-----|-------------|
| Diagnostic Session Control | 0x10 | Switch between Default, Extended, Programming sessions |
| ECU Reset | 0x11 | Hard Reset, Key-Off-On, Soft Reset |
| Read Data By Identifier | 0x22 | Read OBD-II PIDs (RPM, speed, temperature, etc.) |
| Tester Present | 0x3E | Keep diagnostic session alive |

## CAN Configuration

| Parameter | Value |
|-----------|-------|
| Baud Rate | 500 kbps |
| Tester TX ID (Physical) | 0x7E0 |
| Tester TX ID (Functional) | 0x7DF |
| ECU Response ID | 0x7E8 |
| Max Payload (ISO-TP) | 4095 bytes |

## Module Map

| Module | Location | Purpose | Status |
|--------|----------|---------|--------|
| `isotp_transport` | `firmware/src/app_modules/isotp_transport/` | ISO 15765-2 segmentation & reassembly | Implemented |
| `uds_client` | `firmware/src/app_modules/uds_client/` | UDS client state machine & service handlers | Implemented |
| `obd_pids` | `firmware/src/app_modules/obd_pids/` | OBD-II PID table, scaling, formatting | Implemented |
| `ble_diag_bridge` | `firmware/src/app_modules/ble_diag_bridge/` | BLE-to-CAN diagnostic bridge | Implemented |

## Build

Built via CMake with XC32 toolchain:

1. Open the project folder in VS Code
2. Install the CMake Tools extension if not already installed
3. Select the CMake preset: `can_peripheral_trp_uart_wbz451_curiosity_conf`
4. Run **CMake: Build** from the command palette (Ctrl+Shift+P)
5. Output: `.elf` / `.hex` in the `_build/` directory

**Toolchain:** XC32 v4.60 or later, Ninja build system.

## Hardware Requirements

| Component | Details |
|-----------|---------|
| **Board** | WBZ451 Curiosity Board (PIC32CX-BZ2) |
| **CAN Transceiver** | External CAN transceiver (e.g., ATA6563 click board) connected to CAN1 TX/RX pins |
| **CAN Bus** | Vehicle OBD-II port or ECU simulator connected at 500 kbps |
| **BLE** | On-chip BLE 5.0 (no external hardware needed) |
| **UART** | SERCOM0 — use the on-board USB-UART (CDC) via the debug USB connector |
| **Terminal** | Any serial terminal (TeraTerm, PuTTY, minicom) at 115200 8N1 |

### Wiring Diagram

```
WBZ451 Curiosity Board
+-------------------------+
|  USB (Debug/UART)       |----> PC Serial Terminal (115200 baud)
|                         |
|  CAN1_TX (pin PA12)     |----> CAN Transceiver TX
|  CAN1_RX (pin PA13)     |<---- CAN Transceiver RX
|  CAN Transceiver CANH   |----> OBD-II Pin 6 (CAN High)
|  CAN Transceiver CANL   |----> OBD-II Pin 14 (CAN Low)
|  GND                    |----> OBD-II Pin 4/5 (Chassis/Signal GND)
|                         |
|  BLE Antenna (on-board) |~~~~ Phone / PC (wireless)
+-------------------------+
```

## Testing the Project

### Prerequisites

1. Flash the `.hex` file to the WBZ451 board using MPLAB IPE or the on-board debugger
2. Connect the CAN transceiver to the board and to a CAN bus (vehicle or simulator)
3. Open a serial terminal on the USB-UART port at **115200 baud, 8N1**
4. The board prints `Advertising` on boot — it is ready

### Test 1: UART Console — Basic Commands

After flashing and connecting the terminal, type the following commands:

| Command | Expected CAN Frame (ID 0x7E0) | Description |
|---------|-------------------------------|-------------|
| `help` | (none — prints available commands) | Show command list |
| `read rpm` | `02 22 F4 0C 00 00 00 00` | Read engine RPM DID |
| `read speed` | `02 22 F4 0D 00 00 00 00` | Read vehicle speed DID |
| `read coolant` | `02 22 F4 05 00 00 00 00` | Read coolant temperature DID |
| `read throttle` | `02 22 F4 11 00 00 00 00` | Read throttle position DID |
| `read load` | `02 22 F4 04 00 00 00 00` | Read engine load DID |
| `session extended` | `02 10 03 00 00 00 00 00` | Enter extended diagnostic session |
| `session default` | `02 10 01 00 00 00 00 00` | Return to default session |
| `reset hard` | `02 11 01 00 00 00 00 00` | Request ECU hard reset |
| `reset soft` | `02 11 03 00 00 00 00 00` | Request ECU soft reset |
| `tester` | `02 3E 00 00 00 00 00 00` | TesterPresent (expects response) |
| `tester suppress` | `02 3E 80 00 00 00 00 00` | TesterPresent (no response expected) |

**Verification:** Use a CAN bus analyzer (e.g., PCAN-View, Vector CANalyzer, or a second CAN device) to confirm the frames appear on the bus with ID `0x7E0`.

### Test 2: UART Console — ECU Response Handling

To verify response processing, simulate an ECU response by injecting a CAN frame on ID `0x7E8`:

| Scenario | Inject on 0x7E8 | Expected Terminal Output |
|----------|-----------------|--------------------------|
| RPM = 3000 | `04 62 F4 0C 2E E0` | `RPM: 3000.00 rpm` |
| Speed = 60 km/h | `04 62 F4 0D 00 3C` | `Speed: 60.00 km/h` |
| Coolant = 90C | `04 62 F4 05 00 82` | `Coolant Temp: 90.00 C` |
| Negative response (service not supported) | `03 7F 22 11` | `NRC: 0x11 (serviceNotSupported)` |
| No response (timeout) | (send nothing) | `Timeout` after 150ms |
| Response pending then positive | `03 7F 22 78` then `04 62 F4 0C 2E E0` | Waits up to 5s, then shows RPM |

**RPM scaling formula:** value = ((A * 256) + B) / 4. So for 3000 RPM: (0x2E * 256 + 0xE0) / 4 = (46 * 256 + 224) / 4 = 12000 / 4 = 3000.

### Test 3: BLE Diagnostic Bridge

**Setup:**
1. Use a BLE terminal app on your phone (e.g., nRF Connect, LightBlue, or BLE Terminal)
2. Scan for and connect to the device (advertises as the WBZ451 BLE name)
3. Find the Transparent UART Service (TRSPS) and its TX/RX characteristics
4. Write data to the TRSPS RX characteristic to send commands

**BLE Frame Protocol:**
```
[LEN_H] [LEN_L] [SID] [DATA...]
```
- `LEN_H`, `LEN_L`: 16-bit big-endian length of the payload (SID + DATA), NOT including the 2 length bytes
- `SID`: UDS Service ID
- `DATA`: Service-specific sub-function and data bytes

**BLE Test Commands (hex bytes to send):**

| Command | Hex Bytes to Send | Description |
|---------|-------------------|-------------|
| Read RPM | `00 03 22 F4 0C` | RDBI for DID 0xF40C |
| Read Speed | `00 03 22 F4 0D` | RDBI for DID 0xF40D |
| Session Extended | `00 02 10 03` | DiagSessionControl Extended |
| ECU Hard Reset | `00 02 11 01` | ECU Reset — Hard |
| TesterPresent | `00 01 3E` | TesterPresent (wait for response) |
| TesterPresent Suppress | `00 02 3E 80` | TesterPresent (suppress positive response) |
| Multi-DID Read | `00 05 22 F4 0C F4 0D` | Read RPM + Speed in one request |

**Expected BLE Responses (received on TRSPS TX characteristic):**

| Scenario | Response Hex | Meaning |
|----------|-------------|---------|
| Positive response (RPM=3000) | `00 05 62 F4 0C 2E E0` | LEN=5, positive SID 0x62, DID, data |
| Negative response | `00 03 7F 22 11` | LEN=3, NRC frame |
| Timeout/error | `00 02 FF 04` | LEN=2, 0xFF=error indicator, 0x04=timeout |
| Malformed frame error | `00 02 FE 01` | LEN=2, 0xFE=frame error, 0x01=malformed |
| Busy error | `00 02 FE 02` | LEN=2, 0xFE=frame error, 0x02=UDS busy |

### Test 4: Concurrent Access (UART + BLE)

1. Connect both UART terminal and BLE client simultaneously
2. Send `read rpm` on UART — verify CAN frame sent and response displayed on UART
3. Send `00 03 22 F4 0D` on BLE — verify CAN frame sent and response returned to BLE
4. Try sending a BLE command while UART command is pending — should receive `FE 02` (busy) on BLE
5. Disconnect BLE mid-transaction — verify UART console still works normally

### Test 5: Error Handling

| Test | Action | Expected Result |
|------|--------|-----------------|
| Unknown UART command | Type `foo` and press Enter | `Unknown command` error message |
| Unknown PID | Type `read foo` | `Unknown PID` error message |
| BLE frame too short | Send `00 01` (only 2 bytes) | BLE receives `00 02 FE 01` (malformed) |
| BLE length mismatch | Send `00 05 22 F4 0C` (says 5, only 3 payload) | BLE receives `00 02 FE 01` |
| BLE unknown SID | Send `00 01 99` | BLE receives `00 02 FE 03` (invalid SID) |
| BLE disconnect during wait | Disconnect phone while waiting for ECU | No crash, UART shows `BLE: Client disconnected` |

### Test 6: ISO-TP Multi-Frame (Long Messages)

If you need to test multi-frame transfer (messages > 7 bytes):

1. Send a RDBI request for multiple DIDs: `read rpm` followed by simulating an ECU response longer than 7 bytes
2. Inject a First Frame on 0x7E8: `10 0A 62 F4 0C 2E E0 F4` (FF, total length 10)
3. Board should send a Flow Control frame on 0x7E0: `30 00 00 00 00 00 00 00`
4. Inject a Consecutive Frame on 0x7E8: `21 0D 00 3C 00 00 00 00` (CF, seq=1)
5. Full response reassembled and displayed

### Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No output on terminal | Wrong COM port or baud rate | Verify 115200, 8N1; try other COM ports |
| `Advertising` but phone can't find device | BLE range or scan filter | Move closer; disable name filters in BLE app |
| CAN frame not seen on analyzer | Transceiver wiring or termination | Check TX/RX connections; add 120-ohm termination |
| `Timeout` on every command | No ECU connected or wrong baud | Verify CAN bus at 500 kbps; check ECU power |
| Board resets after `reset hard` | Expected behavior | ECU Reset (0x11) causes board reset if connected to its own CAN response |

## Project Status

| Milestone | Description | Status |
|-----------|-------------|--------|
| M1 | CAN Transport & ISO-TP Layer | Complete |
| M2 | UDS Client Core | Complete |
| M3 | BLE-CAN Diagnostic Bridge | Complete |

See `Workflow.html` for current workflow status dashboard.
