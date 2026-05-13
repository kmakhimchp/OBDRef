#include "isotp_internal.h"
#include "definitions.h"
#include "../debug_log/debug_log.h"
#include "FreeRTOS.h"
#include "task.h"
#include <string.h>

#define WRITE_ID(id) ((id) << 18)

static uint8_t canTxFrame[CAN1_TX_FIFO_BUFFER_ELEMENT_SIZE]
    __attribute__((aligned(4)));

uint32_t ISOTP_GetTickMs(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

bool ISOTP_TransmitFrame(uint32_t canId, const uint8_t *data, uint8_t len)
{
    DBG_LOG("ISOTP", "CAN TX id=0x%03X [%02X %02X %02X %02X %02X %02X %02X %02X]",
            (unsigned int)canId,
            len > 0 ? data[0] : 0, len > 1 ? data[1] : 0,
            len > 2 ? data[2] : 0, len > 3 ? data[3] : 0,
            len > 4 ? data[4] : 0, len > 5 ? data[5] : 0,
            len > 6 ? data[6] : 0, len > 7 ? data[7] : 0);

    CAN_TX_BUFFER *txBuf = (CAN_TX_BUFFER *)canTxFrame;
    memset(canTxFrame, 0, CAN1_TX_FIFO_BUFFER_ELEMENT_SIZE);

    txBuf->id  = WRITE_ID(canId);
    txBuf->dlc = len;
    txBuf->fdf = 0;
    txBuf->brs = 0;
    txBuf->xtd = 0;

    memcpy(txBuf->data, data, len);
    return CAN1_MessageTransmitFifo(1, txBuf);
}

void ISOTP_SendFlowControl(void)
{
    uint8_t frame[ISOTP_CAN_DL];
    memset(frame, 0xCC, ISOTP_CAN_DL);

    frame[0] = PCI_FC | FC_FLOW_STATUS_CTS;
    frame[1] = ISOTP_DEFAULT_BS;
    frame[2] = ISOTP_DEFAULT_STMIN;

    ISOTP_TransmitFrame(ISOTP_TX_ID_PHYSICAL, frame, ISOTP_CAN_DL);
}

void ISOTP_SendNextCF(void)
{
    uint8_t frame[ISOTP_CAN_DL];
    uint16_t remaining = txCtx.totalLen - txCtx.offset;
    uint8_t copyLen = (remaining > 7u) ? 7u : (uint8_t)remaining;

    memset(frame, 0xCC, ISOTP_CAN_DL);
    frame[0] = PCI_CF | (txCtx.seqNum & 0x0Fu);
    memcpy(&frame[1], &txCtx.buffer[txCtx.offset], copyLen);

    uint32_t id = txCtx.functional ? ISOTP_TX_ID_FUNCTIONAL : ISOTP_TX_ID_PHYSICAL;
    ISOTP_TransmitFrame(id, frame, ISOTP_CAN_DL);

    txCtx.offset += copyLen;
    txCtx.seqNum = (txCtx.seqNum + 1u) & 0x0Fu;

    if (txCtx.blockSize != 0u) {
        txCtx.blockCount++;
    }
}

void ISOTP_HandleSF(const uint8_t *data, uint8_t dlc)
{
    uint8_t sfLen = data[0] & 0x0Fu;
    if (sfLen == 0u || sfLen > 7u || sfLen > (dlc - 1u)) {
        return;
    }

    DBG_LOG("ISOTP", "RX SF len=%d", sfLen);
    rxResult.length = sfLen;
    memcpy(rxResult.buffer, &data[1], sfLen);
    rxResult.complete = true;
}

void ISOTP_HandleFF(const uint8_t *data, uint8_t dlc)
{
    uint16_t ffLen = (uint16_t)((data[0] & 0x0Fu) << 8) | data[1];
    if (ffLen == 0u || ffLen > ISOTP_RX_BUFFER_SIZE) {
        return;
    }

    DBG_LOG("ISOTP", "RX FF total=%d bytes", (int)ffLen);
    rxCtx.state       = ISOTP_RX_STATE_RECEIVING;
    rxCtx.totalLen    = ffLen;
    rxCtx.offset      = 0;
    rxCtx.expectedSeq = 1u;
    rxCtx.timerStart  = ISOTP_GetTickMs();

    uint8_t copyLen = (dlc - 2u < ffLen) ? (dlc - 2u) : (uint8_t)ffLen;
    memcpy(rxCtx.buffer, &data[2], copyLen);
    rxCtx.offset = copyLen;

    ISOTP_SendFlowControl();
}

void ISOTP_HandleCF(const uint8_t *data, uint8_t dlc)
{
    if (rxCtx.state != ISOTP_RX_STATE_RECEIVING) {
        return;
    }

    uint8_t seq = data[0] & 0x0Fu;
    if (seq != rxCtx.expectedSeq) {
        rxCtx.state = ISOTP_RX_STATE_IDLE;
        return;
    }

    uint16_t remaining = rxCtx.totalLen - rxCtx.offset;
    uint8_t copyLen = (remaining > 7u) ? 7u : (uint8_t)remaining;
    memcpy(&rxCtx.buffer[rxCtx.offset], &data[1], copyLen);
    rxCtx.offset += copyLen;

    rxCtx.expectedSeq = (rxCtx.expectedSeq + 1u) & 0x0Fu;
    rxCtx.timerStart  = ISOTP_GetTickMs();

    if (rxCtx.offset >= rxCtx.totalLen) {
        DBG_LOG("ISOTP", "RX complete (%d bytes)", (int)rxCtx.totalLen);
        rxResult.length   = rxCtx.totalLen;
        memcpy(rxResult.buffer, rxCtx.buffer, rxCtx.totalLen);
        rxResult.complete = true;
        rxCtx.state       = ISOTP_RX_STATE_IDLE;
    }
}

void ISOTP_HandleFC(const uint8_t *data, uint8_t dlc)
{
    if (txCtx.state != ISOTP_TX_STATE_WAIT_FC) {
        return;
    }

    uint8_t flowStatus = data[0] & 0x0Fu;
    if (flowStatus == FC_FLOW_STATUS_OVFL) {
        DBG_LOG("ISOTP", "RX FC overflow, aborting TX");
        txCtx.state = ISOTP_TX_STATE_IDLE;
        return;
    }
    if (flowStatus == FC_FLOW_STATUS_WAIT) {
        DBG_LOG("ISOTP", "RX FC wait, resetting timer");
        txCtx.timerStart = ISOTP_GetTickMs();
        return;
    }

    DBG_LOG("ISOTP", "RX FC CTS bs=%d stmin=%d", data[1], data[2]);
    txCtx.blockSize  = data[1];
    txCtx.stMin      = data[2];
    txCtx.blockCount = 0;
    txCtx.state      = ISOTP_TX_STATE_SEND_CF;
    txCtx.cfTimerStart = ISOTP_GetTickMs();
}
