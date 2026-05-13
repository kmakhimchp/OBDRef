# Module: obd_pids

## Purpose

OBD-II PID (Parameter Identifier) lookup table mapping standard Mode 01 PIDs to UDS DID values, with scaling formulas and unit definitions for human-readable display.

## Responsibility

**Owns:**
- PID-to-DID mapping table
- Raw value scaling formulas (bytes to engineering units)
- Unit string definitions
- PID name/description strings
- Response data parsing for known PIDs

**Does NOT own:**
- UDS request/response handling (handled by uds_client)
- CAN transport (handled by isotp_transport)
- Display formatting (handled by uds_console in uds_client module)

## Public Interface

```c
typedef struct {
    uint8_t     pid;
    uint16_t    did;
    const char *name;
    const char *unit;
    uint8_t     dataBytes;
    float       (*scale)(const uint8_t *data);
} OBD_PidEntry_t;

const OBD_PidEntry_t *OBD_GetPidByNumber(uint8_t pid);
const OBD_PidEntry_t *OBD_GetPidByName(const char *name);
uint16_t OBD_PidToDid(uint8_t pid);
float OBD_ScaleResponse(uint8_t pid, const uint8_t *data);
const char *OBD_GetPidName(uint8_t pid);
const char *OBD_GetPidUnit(uint8_t pid);
uint8_t OBD_GetPidCount(void);
```

## Internal Design

Pure data module with no state. Contains a static const table (`pidTable[]`) of `OBD_PidEntry_t` entries. Each entry maps a Mode 01 PID number to:
- UDS DID (0xF400 + PID for standard OBD-II)
- Human-readable name (used as command argument in console)
- Unit string
- Data byte count (1 or 2)
- Scaling function pointer

Lookup functions iterate the table linearly (5 entries, no performance concern). Scaling functions are static and implement the standard OBD-II formulas from SAE J1979.

## Dependencies

- None (pure data module, no hardware dependencies)

## Data Flow

```
UDS Client (after receiving 0x22 response)
    |
    v
OBD_ScaleResponse(pid, rawData)
    |
    v
[Apply formula: e.g., RPM = ((A*256)+B)/4]
    |
    v
Return float value in engineering units
```

## PID Table (Minimum Required)

| PID  | DID    | Name             | Unit | Formula |
|------|--------|------------------|------|---------|
| 0x04 | 0xF404 | Engine Load      | %    | A * 100 / 255 |
| 0x05 | 0xF405 | Coolant Temp     | C    | A - 40 |
| 0x0C | 0xF40C | Engine RPM       | rpm  | ((A*256)+B) / 4 |
| 0x0D | 0xF40D | Vehicle Speed    | km/h | A |
| 0x11 | 0xF411 | Throttle Position| %    | A * 100 / 255 |

## File Inventory

| File | Purpose |
|------|---------|
| `obd_pids.h` | Public API declarations and PID entry type |
| `obd_pids.c` | PID table data and lookup functions |
| `MODULE.md` | This file |
