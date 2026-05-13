# OBD-II Message Testing Guide

This guide explains how to test OBD-II diagnostic messages with the WBZ451 board, covering the request/response format, supported PIDs, and step-by-step testing procedures using both UART and BLE interfaces.

## OBD-II Message Format (over UDS)

OBD-II PIDs are accessed using UDS service **Read Data By Identifier (SID 0x22)**. The standard OBD-II Mode 01 PIDs are mapped to UDS DIDs using the format `0xF4XX` where `XX` is the PID number.

### CAN Frame Structure

```
Request (ID 0x7E0):
+------+------+------+------+------+------+------+------+
| PCI  | SID  | DID  | DID  |  00  |  00  |  00  |  00  |
| Len  | 0x22 | High | Low  | pad  | pad  | pad  | pad  |
+------+------+------+------+------+------+------+------+

Positive Response (ID 0x7E8):
+------+------+------+------+------+------+------+------+
| PCI  | SID  | DID  | DID  | Data | Data |      |      |
| Len  |+0x40 | High | Low  |  A   |  B   |      |      |
+------+------+------+------+------+------+------+------+

Negative Response (ID 0x7E8):
+------+------+------+------+------+------+------+------+
| PCI  | 0x7F | SID  | NRC  |  00  |  00  |  00  |  00  |
| 0x03 |      | 0x22 |      | pad  | pad  | pad  | pad  |
+------+------+------+------+------+------+------+------+
```

- **PCI Length**: Number of remaining significant bytes in the frame (ISO-TP Single Frame)
- **SID 0x22**: Read Data By Identifier request
- **SID 0x62**: Positive response (request SID + 0x40)
- **DID**: Data Identifier — `0xF4XX` for OBD-II PID `XX`

## Supported OBD-II PIDs

| PID | DID | Name | Unit | Data Bytes | Scaling Formula |
|-----|-----|------|------|-----------|-----------------|
| 0x04 | 0xF404 | Engine Load | % | 1 (A) | A * 100 / 255 |
| 0x05 | 0xF405 | Coolant Temperature | C | 1 (A) | A - 40 |
| 0x0C | 0xF40C | Engine RPM | rpm | 2 (A, B) | ((A * 256) + B) / 4 |
| 0x0D | 0xF40D | Vehicle Speed | km/h | 1 (A) | A |
| 0x11 | 0xF411 | Throttle Position | % | 1 (A) | A * 100 / 255 |

## Testing via UART Console

### Setup

1. Connect WBZ451 board to PC via USB (debug connector)
2. Open serial terminal at **115200 baud, 8N1**
3. Connect CAN transceiver to a vehicle OBD-II port or ECU simulator

### Reading OBD-II PIDs

Type the command and press Enter:

```
read rpm
```

**What happens on the CAN bus:**
```
TX (0x7E0): 03 22 F4 0C 00 00 00 00
             |  |  |  |
             |  |  +--+-- DID 0xF40C (RPM)
             |  +-------- SID 0x22 (RDBI)
             +----------- PCI: 3 bytes follow
```

**If ECU responds with RPM = 3000:**
```
RX (0x7E8): 05 62 F4 0C 2E E0 00 00
             |  |  |  |  |  |
             |  |  +--+  +--+-- Data: A=0x2E, B=0xE0
             |  |  DID 0xF40C
             |  +-- Positive response SID (0x22 + 0x40)
             +-- PCI: 5 bytes follow

Calculation: ((0x2E * 256) + 0xE0) / 4 = (11776 + 224) / 4 = 3000 rpm
```

**Terminal displays:** `RPM: 3000.00 rpm`

### All UART Read Commands

| Command | CAN TX (0x7E0) | Notes |
|---------|---------------|-------|
| `read rpm` | `03 22 F4 0C 00 00 00 00` | Engine speed |
| `read speed` | `03 22 F4 0D 00 00 00 00` | Vehicle speed |
| `read coolant` | `03 22 F4 05 00 00 00 00` | Coolant temperature |
| `read throttle` | `03 22 F4 11 00 00 00 00` | Throttle position |
| `read load` | `03 22 F4 04 00 00 00 00` | Calculated engine load |

### Other UDS Commands

| Command | CAN TX (0x7E0) | Purpose |
|---------|---------------|---------|
| `session default` | `02 10 01 00 00 00 00 00` | Enter default diagnostic session |
| `session extended` | `02 10 03 00 00 00 00 00` | Enter extended session (required by some ECUs before reading PIDs) |
| `tester` | `02 3E 00 00 00 00 00 00` | Keep session alive |
| `tester suppress` | `02 3E 80 00 00 00 00 00` | Keep session alive (no ECU response) |
| `reset hard` | `02 11 01 00 00 00 00 00` | Hard reset ECU |
| `reset soft` | `02 11 03 00 00 00 00 00` | Soft reset ECU |

## Testing via BLE

### Setup

1. Install a BLE terminal app (nRF Connect, LightBlue, or BLE Terminal)
2. Scan and connect to the WBZ451 device
3. Locate the Transparent UART Service (TRSPS)
4. Use the RX characteristic to send commands (write bytes)
5. Subscribe to the TX characteristic to receive responses (notifications)

### BLE Frame Protocol

```
Request:  [LEN_H] [LEN_L] [SID] [DATA...]
Response: [LEN_H] [LEN_L] [RESPONSE_DATA...]
```

- `LEN_H`, `LEN_L`: Big-endian 16-bit length of everything after the length field (SID + DATA)

### BLE OBD-II Read Commands

| Read | Hex Bytes to Send | Breakdown |
|------|-------------------|-----------|
| RPM | `00 03 22 F4 0C` | LEN=3, SID=0x22, DID=0xF40C |
| Speed | `00 03 22 F4 0D` | LEN=3, SID=0x22, DID=0xF40D |
| Coolant | `00 03 22 F4 05` | LEN=3, SID=0x22, DID=0xF405 |
| Throttle | `00 03 22 F4 11` | LEN=3, SID=0x22, DID=0xF411 |
| Load | `00 03 22 F4 04` | LEN=3, SID=0x22, DID=0xF404 |
| RPM + Speed | `00 05 22 F4 0C F4 0D` | LEN=5, SID=0x22, two DIDs |

### BLE Response Interpretation

**Positive response (RPM = 3000):**
```
Received: 00 05 62 F4 0C 2E E0
          |  |  |  |  |  |  |
          +--+  |  +--+  +--+-- Data bytes A=0x2E, B=0xE0
          LEN=5 |  DID 0xF40C
                +-- Positive SID 0x62
```

**Negative response (service not supported):**
```
Received: 00 03 7F 22 11
          |  |  |  |  |
          +--+  |  |  +-- NRC 0x11 (serviceNotSupported)
          LEN=3 |  +-- Requested SID
                +-- Negative response indicator
```

**Error responses from bridge:**
```
00 02 FE 01  -> Malformed frame (bad length or too short)
00 02 FE 02  -> UDS client busy (another request pending)
00 02 FE 03  -> Invalid/unsupported SID
00 02 FF 04  -> UDS timeout (ECU did not respond within 150ms)
```

## Simulating ECU Responses (Without a Vehicle)

If you do not have access to a real vehicle, use a CAN analyzer or second CAN node to inject responses on ID `0x7E8`.

### Step-by-Step: Simulate RPM Reading

1. On the WBZ451 terminal, type: `read rpm`
2. Observe CAN TX: `03 22 F4 0C 00 00 00 00` on ID `0x7E0`
3. Within 150ms, inject on ID `0x7E8`: `05 62 F4 0C 2E E0 00 00`
4. Terminal displays: `RPM: 3000.00 rpm`

### ECU Response Examples to Inject

| PID | Simulated Value | Inject on 0x7E8 | Terminal Output |
|-----|----------------|-----------------|-----------------|
| RPM = 800 (idle) | A=0x0C, B=0x80 | `05 62 F4 0C 0C 80 00 00` | `RPM: 800.00 rpm` |
| RPM = 3000 | A=0x2E, B=0xE0 | `05 62 F4 0C 2E E0 00 00` | `RPM: 3000.00 rpm` |
| RPM = 6000 | A=0x5D, B=0xC0 | `05 62 F4 0C 5D C0 00 00` | `RPM: 6000.00 rpm` |
| Speed = 0 km/h | A=0x00 | `04 62 F4 0D 00 00 00 00` | `Speed: 0.00 km/h` |
| Speed = 60 km/h | A=0x3C | `04 62 F4 0D 3C 00 00 00` | `Speed: 60.00 km/h` |
| Speed = 120 km/h | A=0x78 | `04 62 F4 0D 78 00 00 00` | `Speed: 120.00 km/h` |
| Coolant = -40C (min) | A=0x00 | `04 62 F4 05 00 00 00 00` | `Coolant Temp: -40.00 C` |
| Coolant = 90C | A=0x82 | `04 62 F4 05 82 00 00 00` | `Coolant Temp: 90.00 C` |
| Coolant = 105C (hot) | A=0x91 | `04 62 F4 05 91 00 00 00` | `Coolant Temp: 105.00 C` |
| Throttle = 0% | A=0x00 | `04 62 F4 11 00 00 00 00` | `Throttle: 0.00 %` |
| Throttle = 50% | A=0x80 | `04 62 F4 11 80 00 00 00` | `Throttle: 50.20 %` |
| Throttle = 100% | A=0xFF | `04 62 F4 11 FF 00 00 00` | `Throttle: 100.00 %` |
| Load = 0% | A=0x00 | `04 62 F4 04 00 00 00 00` | `Load: 0.00 %` |
| Load = 75% | A=0xBF | `04 62 F4 04 BF 00 00 00` | `Load: 74.90 %` |

### Simulating Negative Responses

| NRC | Meaning | Inject on 0x7E8 |
|-----|---------|-----------------|
| 0x10 | General reject | `03 7F 22 10 00 00 00 00` |
| 0x11 | Service not supported | `03 7F 22 11 00 00 00 00` |
| 0x12 | Sub-function not supported | `03 7F 22 12 00 00 00 00` |
| 0x22 | Conditions not correct | `03 7F 22 22 00 00 00 00` |
| 0x31 | Request out of range | `03 7F 22 31 00 00 00 00` |
| 0x78 | Response pending (extends timeout to 5s) | `03 7F 22 78 00 00 00 00` |

### Simulating Response Pending (NRC 0x78)

This tests the P2* extended timeout:

1. Type: `read rpm`
2. Within 150ms, inject: `03 7F 22 78 00 00 00 00` (Response Pending)
3. The board now waits up to 5000ms for the real response
4. Within 5000ms, inject: `05 62 F4 0C 2E E0 00 00` (actual RPM data)
5. Terminal displays the RPM value

## Testing ISO-TP Multi-Frame Messages

For responses larger than 7 bytes (e.g., reading multiple PIDs), ISO-TP splits the response into multiple CAN frames.

### Example: Multi-DID Response (RPM + Speed)

1. Request (type on terminal or send via BLE `00 05 22 F4 0C F4 0D`):
   ```
   TX (0x7E0): 05 22 F4 0C F4 0D 00 00  (Single Frame, 5 bytes payload)
   ```

2. ECU response is 8 bytes: `62 F4 0C 2E E0 F4 0D 3C` (too large for Single Frame)

3. ECU sends a First Frame:
   ```
   RX (0x7E8): 10 08 62 F4 0C 2E E0 F4  (FF: total=8 bytes, first 6 data bytes)
               |  |  |
               |  |  +-- Start of response data
               |  +-- Total payload length = 8
               +-- PCI type 1 = First Frame
   ```

4. Board automatically sends Flow Control:
   ```
   TX (0x7E0): 30 00 00 00 00 00 00 00  (FC: BS=0, STmin=0 — send all)
   ```

5. ECU sends Consecutive Frame:
   ```
   RX (0x7E8): 21 0D 3C 00 00 00 00 00  (CF: seq=1, remaining data)
               |  |
               |  +-- Remaining bytes: 0x0D, 0x3C
               +-- PCI type 2, sequence number 1
   ```

6. Full response reassembled: `62 F4 0C 2E E0 F4 0D 3C`
   - RPM DID 0xF40C: A=0x2E, B=0xE0 -> 3000 rpm
   - Speed DID 0xF40D: A=0x3C -> 60 km/h

## Timing Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| P2 (response timeout) | 150 ms | Time to wait for ECU response after request |
| P2* (extended timeout) | 5000 ms | Extended wait after receiving NRC 0x78 |
| N_Bs (FC timeout) | 1000 ms | Time to wait for Flow Control during multi-frame TX |
| N_Cr (CF timeout) | 1000 ms | Time to wait for next Consecutive Frame during RX |
| STmin | 0 ms | Minimum separation time between Consecutive Frames |
| Block Size | 0 | No limit — send all CFs without waiting for another FC |

## Quick Verification Checklist

- [ ] Board boots and prints `Advertising` on UART
- [ ] `help` command lists available commands
- [ ] `read rpm` produces CAN frame `03 22 F4 0C` on ID 0x7E0
- [ ] Injected response on 0x7E8 is displayed with correct scaling
- [ ] No response within 150ms triggers `Timeout` message
- [ ] BLE connection shows `BLE: Client connected` on UART
- [ ] BLE frame `00 03 22 F4 0C` produces same CAN frame as UART command
- [ ] BLE receives response frame with length prefix
- [ ] BLE disconnect shows `BLE: Client disconnected` on UART
- [ ] Malformed BLE frame returns error code `FE 01`
