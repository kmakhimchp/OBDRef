#ifndef ISOTP_TRANSPORT_H
#define ISOTP_TRANSPORT_H

#include <stdint.h>
#include <stdbool.h>
#include "isotp_config.h"

typedef enum {
    ISOTP_STATUS_OK = 0,
    ISOTP_STATUS_BUSY,
    ISOTP_STATUS_NO_DATA,
    ISOTP_STATUS_OVERFLOW,
    ISOTP_STATUS_TIMEOUT,
    ISOTP_STATUS_ERROR
} ISOTP_Status_t;

typedef enum {
    ISOTP_TX_STATE_IDLE = 0,
    ISOTP_TX_STATE_WAIT_FC,
    ISOTP_TX_STATE_SEND_CF
} ISOTP_TxState_t;

typedef enum {
    ISOTP_RX_STATE_IDLE = 0,
    ISOTP_RX_STATE_RECEIVING
} ISOTP_RxState_t;

void ISOTP_Init(void);
ISOTP_Status_t ISOTP_Send(const uint8_t *data, uint16_t length, bool functional);
ISOTP_Status_t ISOTP_Receive(uint8_t *buffer, uint16_t *length);
void ISOTP_Poll(void);
void ISOTP_OnCanFrameReceived(uint32_t canId, const uint8_t *data, uint8_t dlc);
bool ISOTP_IsBusy(void);

#endif /* ISOTP_TRANSPORT_H */
