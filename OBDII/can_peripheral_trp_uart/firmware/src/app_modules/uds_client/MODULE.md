# Module: uds_client

## Purpose

UDS (Unified Diagnostic Services) client state machine implementing core OBD-II diagnostic services over ISO-TP transport.

## Responsibility

**Owns:**
- UDS request/response state machine (IDLE, SENDING, AWAITING_RESPONSE, ERROR)
- Diagnostic Session Control (SID 0x10)
- Tester Present (SID 0x3E)
- ECU Reset (SID 0x11)
- Read Data By Identifier (SID 0x22)
- Negative Response Code (NRC) handling
- P2/P2* timeout management
- UART command console for manual diagnostic interaction

**Does NOT own:**
- CAN frame transport (handled by isotp_transport module)
- OBD-II PID definitions and scaling (handled by obd_pids module)
- BLE communication (handled by ble_diag_bridge module in M3)

## Public Interface

```c
typedef enum {
    UDS_STATE_IDLE,
    UDS_STATE_SENDING,
    UDS_STATE_AWAITING_RESPONSE,
    UDS_STATE_ERROR
} UDS_State_t;

typedef struct {
    UDS_State_t state;
    uint8_t     lastNrc;
    uint8_t     currentSession;
} UDS_Client_t;

void UDS_Init(void);
void UDS_Poll(void);

UDS_Status_t UDS_DiagSessionControl(uint8_t sessionType);
UDS_Status_t UDS_TesterPresent(bool suppressResponse);
UDS_Status_t UDS_EcuReset(uint8_t resetType);
UDS_Status_t UDS_ReadDataByIdentifier(const uint16_t *dids, uint8_t count);

UDS_Status_t UDS_GetResponse(uint8_t *buffer, uint16_t *length);
UDS_State_t  UDS_GetState(void);
uint8_t      UDS_GetLastNrc(void);

void UDS_ConsoleProcessCommand(const char *cmdLine);
```

## Internal Design

**uds_client.c** — Core UDS state machine:
- Single static context (`UDS_Context_t`) tracks state, pending SID, timers, response buffer
- `UDS_SendRequest()` internal helper: validates idle state, sends via ISO-TP, starts P2 timer
- `UDS_Poll()` checks for ISO-TP responses and handles:
  - Positive response (SID + 0x40): stores in buffer, fires callback, returns to IDLE
  - NRC 0x78 (Response Pending): extends timeout to P2* (5000ms)
  - Other NRC: stores NRC, fires callback with NEGATIVE status
  - P2/P2* timeout: fires callback with TIMEOUT status
- Suppress-positive-response: for TesterPresent 0x80 sub-function, skips wait state

**uds_console.c** — UART command line interface:
- Character-by-character input with local echo and backspace support
- Command parser: `read <pid>`, `session <type>`, `reset <type>`, `tester [suppress]`, `help`
- Response callback (`UDS_ConsoleOnResponse`) formats and displays results
- PID responses are parsed using obd_pids module for human-readable display

**State machine:** IDLE -> (send request) -> AWAITING_RESPONSE -> (response/timeout) -> IDLE or ERROR

## Dependencies

- `isotp_transport` module: ISOTP_Send(), ISOTP_Receive(), ISOTP_Poll(), ISOTP_IsBusy()
- `obd_pids` module: PID lookup for RDBI formatting and response parsing
- FreeRTOS tick for P2/P2* timeout tracking
- SERCOM0 USART for console output

## Data Flow

```
UART Console / BLE Bridge
    |
    v
UDS_ConsoleProcessCommand("read rpm")
    |
    v
UDS_ReadDataByIdentifier([0xF40C], 1)
    |
    v
[Format UDS request: 22 F4 0C]
    |
    v
ISOTP_Send(request, len, physical)
    |
    v
[State -> AWAITING_RESPONSE, start P2 timer]
    |
    v
UDS_Poll() checks ISOTP_Receive()
    |-- Positive response: parse, return to IDLE
    |-- NRC 0x78: extend to P2*, continue waiting
    |-- Other NRC: report error, return to IDLE
    |-- P2/P2* timeout: set ERROR state
```

## File Inventory

| File | Purpose |
|------|---------|
| `uds_client.h` | Public API declarations, types, and status codes |
| `uds_client.c` | UDS state machine and service request formatting |
| `uds_console.h` | Console public interface (init, char input, response callback) |
| `uds_console.c` | UART command parser and response display |
| `MODULE.md` | This file |
