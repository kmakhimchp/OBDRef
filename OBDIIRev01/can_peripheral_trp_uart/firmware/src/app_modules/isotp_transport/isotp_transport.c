#include "isotp_internal.h"
#include "../debug_log/debug_log.h"
#include <string.h>

ISOTP_TxContext_t txCtx;
ISOTP_RxContext_t rxCtx;
ISOTP_RxResult_t  rxResult;

void ISOTP_Init(void)
{
    memset(&txCtx, 0, sizeof(txCtx));
    memset(&rxCtx, 0, sizeof(rxCtx));
    memset(&rxResult, 0, sizeof(rxResult));
    DBG_LOG("ISOTP", "Init (TX:0x%X RX:0x%X)", ISOTP_TX_ID_PHYSICAL, ISOTP_RX_ID);
}

ISOTP_Status_t ISOTP_Send(const uint8_t *data, uint16_t length, bool functional)
{
    if (txCtx.state != ISOTP_TX_STATE_IDLE) {
        return ISOTP_STATUS_BUSY;
    }
    if (length == 0u || length > ISOTP_TX_BUFFER_SIZE) {
        return ISOTP_STATUS_OVERFLOW;
    }

    if (length <= 7u) {
        uint8_t frame[ISOTP_CAN_DL];
        memset(frame, 0x00, ISOTP_CAN_DL);
        frame[0] = PCI_SF | (uint8_t)length;
        memcpy(&frame[1], data, length);

        uint32_t id = functional ? ISOTP_TX_ID_FUNCTIONAL : ISOTP_TX_ID_PHYSICAL;
        DBG_LOG("ISOTP", "TX SF len=%d id=0x%X", (int)length, (unsigned int)id);
        if (!ISOTP_TransmitFrame(id, frame, ISOTP_CAN_DL)) {
            DBG_LOG("ISOTP", "TX SF failed");
            return ISOTP_STATUS_ERROR;
        }
        return ISOTP_STATUS_OK;
    }

    memcpy(txCtx.buffer, data, length);
    txCtx.totalLen   = length;
    txCtx.functional = functional;
    txCtx.seqNum     = 1u;
    txCtx.blockCount = 0;

    uint8_t frame[ISOTP_CAN_DL];
    memset(frame, 0x00, ISOTP_CAN_DL);
    frame[0] = PCI_FF | (uint8_t)((length >> 8) & 0x0Fu);
    frame[1] = (uint8_t)(length & 0xFFu);
    memcpy(&frame[2], data, 6u);
    txCtx.offset = 6u;

    uint32_t id = functional ? ISOTP_TX_ID_FUNCTIONAL : ISOTP_TX_ID_PHYSICAL;
    if (!ISOTP_TransmitFrame(id, frame, ISOTP_CAN_DL)) {
        return ISOTP_STATUS_ERROR;
    }

    txCtx.state      = ISOTP_TX_STATE_WAIT_FC;
    txCtx.timerStart = ISOTP_GetTickMs();
    DBG_LOG("ISOTP", "TX FF len=%d, waiting FC", (int)length);
    return ISOTP_STATUS_OK;
}

ISOTP_Status_t ISOTP_Receive(uint8_t *buffer, uint16_t *length)
{
    if (!rxResult.complete) {
        return ISOTP_STATUS_NO_DATA;
    }

    memcpy(buffer, rxResult.buffer, rxResult.length);
    *length = rxResult.length;
    rxResult.complete = false;
    return ISOTP_STATUS_OK;
}

void ISOTP_Poll(void)
{
    uint32_t now = ISOTP_GetTickMs();

    if (txCtx.state == ISOTP_TX_STATE_WAIT_FC) {
        if ((now - txCtx.timerStart) >= ISOTP_TIMEOUT_N_BS_MS) {
            DBG_LOG("ISOTP", "TX timeout (N_Bs %dms)", (int)ISOTP_TIMEOUT_N_BS_MS);
            txCtx.state = ISOTP_TX_STATE_IDLE;
        }
    }

    if (txCtx.state == ISOTP_TX_STATE_SEND_CF) {
        if ((now - txCtx.cfTimerStart) >= txCtx.stMin) {
            if (txCtx.blockSize != 0u &&
                txCtx.blockCount >= txCtx.blockSize) {
                txCtx.state      = ISOTP_TX_STATE_WAIT_FC;
                txCtx.timerStart = now;
            } else {
                ISOTP_SendNextCF();
                txCtx.cfTimerStart = now;

                if (txCtx.offset >= txCtx.totalLen) {
                    DBG_LOG("ISOTP", "TX complete (%d bytes)", (int)txCtx.totalLen);
                    txCtx.state = ISOTP_TX_STATE_IDLE;
                }
            }
        }
    }

    if (rxCtx.state == ISOTP_RX_STATE_RECEIVING) {
        if ((now - rxCtx.timerStart) >= ISOTP_TIMEOUT_N_CR_MS) {
            DBG_LOG("ISOTP", "RX timeout (N_Cr %dms)", (int)ISOTP_TIMEOUT_N_CR_MS);
            rxCtx.state = ISOTP_RX_STATE_IDLE;
        }
    }
}

void ISOTP_OnCanFrameReceived(uint32_t canId, const uint8_t *data, uint8_t dlc)
{
    if (canId != ISOTP_RX_ID) {
        return;
    }
    if (dlc < 1u) {
        return;
    }

    uint8_t pciType = data[0] & 0xF0u;

    switch (pciType) {
        case PCI_SF:
            ISOTP_HandleSF(data, dlc);
            break;
        case PCI_FF:
            ISOTP_HandleFF(data, dlc);
            break;
        case PCI_CF:
            ISOTP_HandleCF(data, dlc);
            break;
        case PCI_FC:
            ISOTP_HandleFC(data, dlc);
            break;
        default:
            break;
    }
}

bool ISOTP_IsBusy(void)
{
    return (txCtx.state != ISOTP_TX_STATE_IDLE);
}
