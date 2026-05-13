#include "uds_client.h"
#include "../isotp_transport/isotp_transport.h"
#include "../debug_log/debug_log.h"
#include "FreeRTOS.h"
#include "task.h"
#include <string.h>

typedef struct {
    UDS_State_t  state;
    uint8_t      lastNrc;
    uint8_t      currentSession;
    uint8_t      pendingSid;
    bool         suppressResponse;
    uint32_t     timerStart;
    uint32_t     timeout;
    uint8_t      response[UDS_MAX_RESPONSE_LEN];
    uint16_t     responseLen;
    bool         responseReady;
    UDS_ResponseCallback_t callback;
} UDS_Context_t;

static UDS_Context_t ctx;

static uint32_t UDS_GetTickMs(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

static UDS_Status_t UDS_SendRequest(const uint8_t *data, uint16_t len,
                                    uint8_t sid, bool suppress)
{
    if (ctx.state != UDS_STATE_IDLE) {
        DBG_LOG("UDS", "Busy, rejecting SID=0x%02X", sid);
        return UDS_STATUS_BUSY;
    }
    if (ISOTP_IsBusy()) {
        DBG_LOG("UDS", "ISOTP busy, rejecting SID=0x%02X", sid);
        return UDS_STATUS_BUSY;
    }

    DBG_LOG("UDS", "Request SID=0x%02X len=%d", sid, (int)len);
    ISOTP_Status_t st = ISOTP_Send(data, len, false);
    if (st != ISOTP_STATUS_OK) {
        DBG_LOG("UDS", "ISOTP_Send failed, st=%d", (int)st);
        return UDS_STATUS_ERROR;
    }

    ctx.pendingSid = sid;
    ctx.suppressResponse = suppress;

    if (suppress) {
        ctx.state = UDS_STATE_IDLE;
        return UDS_STATUS_OK;
    }

    ctx.state = UDS_STATE_AWAITING_RESPONSE;
    ctx.timeout = UDS_P2_TIMEOUT_MS;
    ctx.timerStart = UDS_GetTickMs();
    ctx.responseReady = false;
    DBG_LOG("UDS", "State IDLE->AWAIT_RESP (P2=%dms)", (int)UDS_P2_TIMEOUT_MS);
    return UDS_STATUS_OK;
}

void UDS_Init(void)
{
    memset(&ctx, 0, sizeof(ctx));
    ctx.currentSession = UDS_SESSION_DEFAULT;
    DBG_LOG("UDS", "Init, session=default");
}

void UDS_Poll(void)
{
    if (ctx.state != UDS_STATE_AWAITING_RESPONSE) {
        return;
    }

    uint8_t rxBuf[UDS_MAX_RESPONSE_LEN];
    uint16_t rxLen = 0;

    if (ISOTP_Receive(rxBuf, &rxLen) == ISOTP_STATUS_OK && rxLen > 0) {
        if (rxBuf[0] == 0x7Fu && rxLen >= 3) {
            if (rxBuf[2] == UDS_NRC_RESPONSE_PENDING) {
                DBG_LOG("UDS", "Response pending (0x78), extending P2*");
                ctx.timeout = UDS_P2_STAR_TIMEOUT_MS;
                ctx.timerStart = UDS_GetTickMs();
                return;
            }
            DBG_LOG("UDS", "NRC 0x%02X for SID=0x%02X", rxBuf[2], ctx.pendingSid);
            ctx.lastNrc = rxBuf[2];
            ctx.state = UDS_STATE_IDLE;
            if (ctx.callback) {
                ctx.callback(UDS_STATUS_NEGATIVE, rxBuf, rxLen);
            }
            return;
        }

        uint8_t expectedPositive = ctx.pendingSid + 0x40u;
        if (rxBuf[0] == expectedPositive) {
            DBG_LOG("UDS", "Positive response SID=0x%02X len=%d", rxBuf[0], (int)rxLen);
            memcpy(ctx.response, rxBuf, rxLen);
            ctx.responseLen = rxLen;
            ctx.responseReady = true;
            ctx.state = UDS_STATE_IDLE;
            if (ctx.callback) {
                ctx.callback(UDS_STATUS_OK, rxBuf, rxLen);
            }
            return;
        }

        DBG_LOG("UDS", "Unexpected response byte=0x%02X (expected 0x%02X)", rxBuf[0], expectedPositive);
        ctx.state = UDS_STATE_ERROR;
        if (ctx.callback) {
            ctx.callback(UDS_STATUS_ERROR, rxBuf, rxLen);
        }
        return;
    }

    uint32_t elapsed = UDS_GetTickMs() - ctx.timerStart;
    if (elapsed >= ctx.timeout) {
        DBG_LOG("UDS", "Timeout after %dms (SID=0x%02X)", (int)elapsed, ctx.pendingSid);
        ctx.state = UDS_STATE_IDLE;
        if (ctx.callback) {
            ctx.callback(UDS_STATUS_TIMEOUT, NULL, 0);
        }
    }
}

UDS_Status_t UDS_DiagSessionControl(uint8_t sessionType)
{
    uint8_t req[2];
    req[0] = UDS_SID_DIAG_SESSION_CONTROL;
    req[1] = sessionType;

    UDS_Status_t st = UDS_SendRequest(req, 2, UDS_SID_DIAG_SESSION_CONTROL, false);
    if (st == UDS_STATUS_OK) {
        ctx.currentSession = sessionType;
    }
    return st;
}

UDS_Status_t UDS_TesterPresent(bool suppressResponse)
{
    uint8_t req[2];
    req[0] = UDS_SID_TESTER_PRESENT;
    req[1] = suppressResponse ? 0x80u : 0x00u;

    return UDS_SendRequest(req, 2, UDS_SID_TESTER_PRESENT, suppressResponse);
}

UDS_Status_t UDS_EcuReset(uint8_t resetType)
{
    uint8_t req[2];
    req[0] = UDS_SID_ECU_RESET;
    req[1] = resetType;

    return UDS_SendRequest(req, 2, UDS_SID_ECU_RESET, false);
}

UDS_Status_t UDS_ReadDataByIdentifier(const uint16_t *dids, uint8_t count)
{
    if (count == 0 || count > 15) {
        return UDS_STATUS_ERROR;
    }

    uint8_t req[UDS_MAX_REQUEST_LEN];
    uint16_t len = 1;
    req[0] = UDS_SID_READ_DATA_BY_ID;

    for (uint8_t i = 0; i < count; i++) {
        if (len + 2 > UDS_MAX_REQUEST_LEN) {
            return UDS_STATUS_ERROR;
        }
        req[len++] = (uint8_t)(dids[i] >> 8);
        req[len++] = (uint8_t)(dids[i] & 0xFFu);
    }

    return UDS_SendRequest(req, len, UDS_SID_READ_DATA_BY_ID, false);
}

UDS_Status_t UDS_GetResponse(uint8_t *buffer, uint16_t *length)
{
    if (!ctx.responseReady) {
        return UDS_STATUS_NO_RESPONSE;
    }
    memcpy(buffer, ctx.response, ctx.responseLen);
    *length = ctx.responseLen;
    ctx.responseReady = false;
    return UDS_STATUS_OK;
}

UDS_State_t UDS_GetState(void)
{
    return ctx.state;
}

uint8_t UDS_GetLastNrc(void)
{
    return ctx.lastNrc;
}

void UDS_SetResponseCallback(UDS_ResponseCallback_t cb)
{
    ctx.callback = cb;
}
