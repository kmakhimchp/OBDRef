# Module: isotp_transport

## Purpose

ISO 15765-2 (ISO-TP) transport layer for segmentation and reassembly of UDS messages over CAN frames.

## Responsibility

**Owns:**
- CAN frame segmentation (Single Frame, First Frame, Consecutive Frame)
- CAN frame reassembly (incoming multi-frame messages)
- Flow Control frame generation and processing
- ISO-TP timing (N_Bs, N_Cr, STmin)
- CAN ID management (0x7E0 TX physical, 0x7DF TX functional, 0x7E8 RX)

**Does NOT own:**
- CAN peripheral initialization (handled by MCC-generated CAN1 driver)
- UDS protocol parsing (handled by uds_client module)
- Application-level message routing

## Public Interface

```c
// Initialization
void ISOTP_Init(void);

// Send a complete ISO-TP message (handles segmentation internally)
ISOTP_Status_t ISOTP_Send(const uint8_t *data, uint16_t length, bool functional);

// Check if a complete message has been received
ISOTP_Status_t ISOTP_Receive(uint8_t *buffer, uint16_t *length);

// Must be called periodically from the main loop (handles CF timing, timeouts)
void ISOTP_Poll(void);

// Called from CAN1 RX callback to feed incoming frames
void ISOTP_OnCanFrameReceived(uint32_t canId, const uint8_t *data, uint8_t dlc);
```

## Internal Design

The module is split into two compilation units for maintainability:

**isotp_transport.c** — Public API and polling state machine:
- `ISOTP_Init()` zeroes all state contexts
- `ISOTP_Send()` handles SF directly or starts FF+CF multi-frame transmission
- `ISOTP_Receive()` returns completed messages from the receive result buffer
- `ISOTP_Poll()` drives CF transmission timing (STmin), block size FC waits, and timeout detection
- `ISOTP_OnCanFrameReceived()` dispatches incoming CAN frames by PCI type

**isotp_frames.c** — Frame-level operations:
- `ISOTP_TransmitFrame()` formats CAN_TX_BUFFER and calls `CAN1_MessageTransmitFifo()`
- `ISOTP_SendFlowControl()` sends FC with CTS status and configured BS/STmin
- `ISOTP_SendNextCF()` sends the next consecutive frame and manages sequence number
- `ISOTP_HandleSF/FF/CF/FC()` process each incoming frame type

**State machines:**
- TX: IDLE -> WAIT_FC (after FF sent) -> SEND_CF (after FC received) -> IDLE (all CF sent or timeout)
- RX: IDLE -> RECEIVING (after FF received, FC sent) -> IDLE (all CF received or timeout)

**Timeout handling:**
- N_Bs (1000ms): waiting for FC after sending FF
- N_Cr (1000ms): waiting for next CF during multi-frame reception
- STmin: minimum separation time between consecutive frames (from receiver's FC)

**Padding:** Unused bytes in CAN frames are padded with 0xCC (common diagnostic fill byte).

## Dependencies

- CAN1 PLIB (MCC-generated): `CAN1_MessageTransmitFifo()`, RX callbacks
- System tick for timeout tracking

## Data Flow

```
Application (UDS Client)
    |
    v
ISOTP_Send(data, len)
    |
    v
[Segmentation Logic]
    |-- len <= 7:  Single Frame -> CAN1_MessageTransmitFifo()
    |-- len > 7:   First Frame  -> CAN1_MessageTransmitFifo()
    |               (wait for FC)
    |               Consecutive Frames -> CAN1_MessageTransmitFifo()
    v
CAN Bus TX (ID: 0x7E0 or 0x7DF)


CAN Bus RX (ID: 0x7E8)
    |
    v
CAN1 RX Callback -> ISOTP_OnCanFrameReceived()
    |
    v
[Reassembly Logic]
    |-- SF:  Complete message -> receive buffer
    |-- FF:  Start reassembly, send FC
    |-- CF:  Append to buffer, check complete
    |-- FC:  Update TX flow parameters
    v
ISOTP_Receive(buffer, &len) -> returns complete message
```

## File Inventory

| File | Purpose |
|------|---------|
| `isotp_transport.h` | Public API declarations and types |
| `isotp_transport.c` | Public API implementation and polling state machine |
| `isotp_frames.c` | Frame-level TX/RX handlers (SF, FF, CF, FC) |
| `isotp_internal.h` | Internal shared types, contexts, and frame handler declarations |
| `isotp_config.h` | Configuration constants (timeouts, buffer sizes, CAN IDs) |
| `MODULE.md` | This file |
