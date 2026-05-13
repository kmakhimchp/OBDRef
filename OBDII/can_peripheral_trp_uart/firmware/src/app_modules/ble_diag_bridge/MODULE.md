# Module: ble_diag_bridge

## Purpose

BLE-to-CAN diagnostic bridge that receives UDS commands via BLE Transparent UART (TRSPS) and forwards them to the UDS client for CAN transmission. ECU responses are relayed back over BLE.

## Responsibility

**Owns:**
- BLE frame protocol parsing ([LEN_H][LEN_L][SERVICE_ID][DATA...])
- Request forwarding to UDS client
- Response relay back to BLE client
- BLE connection state tracking for graceful disconnect handling
- Mutual exclusion between BLE and UART console paths
- Activity indication (LED/UART status)
- Malformed frame rejection

**Does NOT own:**
- BLE stack or TRSPS service configuration (handled by MCC/app_ble)
- UDS protocol logic (handled by uds_client module)
- CAN transport (handled by isotp_transport module)

## Public Interface

```c
void BLE_DIAG_Init(void);
void BLE_DIAG_OnDataReceived(const uint8_t *data, uint16_t length);
void BLE_DIAG_OnConnected(uint16_t connHandle);
void BLE_DIAG_OnDisconnected(void);
void BLE_DIAG_OnUdsResponse(UDS_Status_t status, const uint8_t *data, uint16_t length);
bool BLE_DIAG_IsActive(void);
```

## Internal Design

The bridge uses a simple state model:
- `bleConnected` — tracks whether a BLE client is connected
- `transactionActive` — true while a UDS request is pending (prevents concurrent requests)
- `pendingSid` — stores the service ID for NRC response formatting

**Frame Protocol (BLE packets):**
```
Request:  [LEN_H][LEN_L][SID][SUB/DATA...]
Response: [LEN_H][LEN_L][RESPONSE_DATA...]
Error:    [LEN_H=0x00][LEN_L=0x02][0xFE][ERROR_CODE]
```

**Concurrency:** Mutual exclusion between UART console and BLE is achieved via `BLE_DIAG_IsActive()` — when a BLE transaction is active, the UDS response callback routes to the bridge instead of the console. Both paths share the single UDS client instance but never issue overlapping requests since the UDS state machine rejects requests when busy.

**Supported SIDs:** 0x10 (DiagSessionControl), 0x11 (ECU Reset), 0x22 (RDBI), 0x3E (TesterPresent).

## Dependencies

- `uds_client` module: UDS_DiagSessionControl, UDS_ReadDataByIdentifier, etc.
- BLE TRSPS: BLE_TRSPS_SendData() for response relay
- app_trsps_handler: hooks for data received events
- FreeRTOS: mutex for concurrent access protection

## Data Flow

```
BLE Client (Phone/PC)
    |
    v
BLE TRSPS RX -> app_trsps_handler -> BLE_DIAG_OnDataReceived()
    |
    v
[Parse frame: LEN_H, LEN_L, SID, DATA]
    |
    v
UDS service call (via uds_client)
    |
    v
ISO-TP -> CAN Bus -> ECU
    |
    v
ECU Response -> ISO-TP -> UDS_Poll -> BLE_DIAG_OnUdsResponse()
    |
    v
[Format response frame]
    |
    v
BLE_TRSPS_SendData() -> BLE Client
```

## File Inventory

| File | Purpose |
|------|---------|
| `ble_diag_bridge.h` | Public API declarations |
| `ble_diag_bridge.c` | Bridge logic, frame parsing, response relay |
| `MODULE.md` | This file |
