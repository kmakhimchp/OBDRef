#include "obdii.h"
#include "../isotp_transport/isotp_transport.h"
#include "../debug_log/debug_log.h"
#include "FreeRTOS.h"
#include "task.h"
#include <string.h>

typedef enum {
    OBDII_STATE_IDLE = 0,
    OBDII_STATE_AWAITING_RESPONSE
} OBDII_State_t;

typedef struct {
    OBDII_State_t           state;
    uint8_t                 pendingPid;
    uint32_t                timerStart;
    OBDII_Result_t          lastResult;
    OBDII_ResultCallback_t  callback;
} OBDII_Context_t;

static OBDII_Context_t ctx;

static uint32_t OBDII_GetTickMs(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

static const char *OBDII_PidName(uint8_t pid)
{
    switch (pid) {
        case OBDII_PID_COOLANT_TEMP:   return "Coolant";
        case OBDII_PID_ENGINE_RPM:     return "RPM";
        case OBDII_PID_VEHICLE_SPEED:  return "Speed";
        default:                       return "Unknown";
    }
}

static float OBDII_ScalePid(uint8_t pid, const uint8_t *data, uint8_t dataLen)
{
    switch (pid) {
        case OBDII_PID_ENGINE_RPM:
            if (dataLen >= 2u) {
                return (float)((uint16_t)data[0] * 256u + data[1]) / 4.0f;
            }
            break;
        case OBDII_PID_VEHICLE_SPEED:
            if (dataLen >= 1u) {
                return (float)data[0];
            }
            break;
        case OBDII_PID_COOLANT_TEMP:
            if (dataLen >= 1u) {
                return (float)data[0] - 40.0f;
            }
            break;
        default:
            break;
    }
    return 0.0f;
}

static uint8_t OBDII_PidDataBytes(uint8_t pid)
{
    switch (pid) {
        case OBDII_PID_ENGINE_RPM:     return 2u;
        case OBDII_PID_VEHICLE_SPEED:  return 1u;
        case OBDII_PID_COOLANT_TEMP:   return 1u;
        default:                       return 1u;
    }
}

void OBDII_Init(void)
{
    memset(&ctx, 0, sizeof(ctx));
    ctx.state = OBDII_STATE_IDLE;
    DBG_LOG("OBDII", "Init");
}

void OBDII_Poll(void)
{
    if (ctx.state != OBDII_STATE_AWAITING_RESPONSE) {
        return;
    }

    uint8_t rxBuf[16];
    uint16_t rxLen = 0;

    if (ISOTP_Receive(rxBuf, &rxLen) == ISOTP_STATUS_OK && rxLen > 0) {
        uint8_t expectedMode = OBDII_MODE_CURRENT_DATA + OBDII_RESPONSE_OFFSET;

        if (rxLen >= 2u && rxBuf[0] == expectedMode && rxBuf[1] == ctx.pendingPid) {
            uint8_t dataBytes = OBDII_PidDataBytes(ctx.pendingPid);
            uint8_t availData = (uint8_t)(rxLen - 2u);

            if (availData >= dataBytes) {
                float value = OBDII_ScalePid(ctx.pendingPid, &rxBuf[2], availData);
                DBG_LOG("OBDII", "Response PID=0x%02X (%s) value=%.1f",
                        ctx.pendingPid, OBDII_PidName(ctx.pendingPid), (double)value);

                ctx.lastResult.pid   = ctx.pendingPid;
                ctx.lastResult.value = value;
                ctx.lastResult.valid = true;
                ctx.state = OBDII_STATE_IDLE;

                if (ctx.callback) {
                    ctx.callback(ctx.pendingPid, value, true);
                }
                return;
            }
        }

        if (rxBuf[0] == 0x7Fu && rxLen >= 3u) {
            DBG_LOG("OBDII", "Negative response NRC=0x%02X for PID=0x%02X",
                    rxBuf[2], ctx.pendingPid);
        } else {
            DBG_LOG("OBDII", "Unexpected response [%02X %02X ...] for PID=0x%02X",
                    rxBuf[0], rxLen > 1 ? rxBuf[1] : 0, ctx.pendingPid);
        }

        ctx.lastResult.pid   = ctx.pendingPid;
        ctx.lastResult.value = 0.0f;
        ctx.lastResult.valid = false;
        ctx.state = OBDII_STATE_IDLE;

        if (ctx.callback) {
            ctx.callback(ctx.pendingPid, 0.0f, false);
        }
        return;
    }

    uint32_t elapsed = OBDII_GetTickMs() - ctx.timerStart;
    if (elapsed >= OBDII_TIMEOUT_MS) {
        DBG_LOG("OBDII", "Timeout PID=0x%02X (%s) after %dms",
                ctx.pendingPid, OBDII_PidName(ctx.pendingPid), (int)elapsed);

        ctx.lastResult.pid   = ctx.pendingPid;
        ctx.lastResult.value = 0.0f;
        ctx.lastResult.valid = false;
        ctx.state = OBDII_STATE_IDLE;

        if (ctx.callback) {
            ctx.callback(ctx.pendingPid, 0.0f, false);
        }
    }
}

OBDII_Status_t OBDII_RequestPid(uint8_t pid)
{
    if (ctx.state != OBDII_STATE_IDLE) {
        DBG_LOG("OBDII", "Busy, rejecting PID=0x%02X", pid);
        return OBDII_STATUS_BUSY;
    }

    if (ISOTP_IsBusy()) {
        DBG_LOG("OBDII", "ISOTP busy, rejecting PID=0x%02X", pid);
        return OBDII_STATUS_BUSY;
    }

    uint8_t req[2];
    req[0] = OBDII_MODE_CURRENT_DATA;
    req[1] = pid;

    DBG_LOG("OBDII", "Request PID=0x%02X (%s)", pid, OBDII_PidName(pid));

    ISOTP_Status_t st = ISOTP_Send(req, 2u, false);
    if (st != ISOTP_STATUS_OK) {
        DBG_LOG("OBDII", "ISOTP_Send failed, st=%d", (int)st);
        return OBDII_STATUS_ERROR;
    }

    ctx.pendingPid = pid;
    ctx.state = OBDII_STATE_AWAITING_RESPONSE;
    ctx.timerStart = OBDII_GetTickMs();
    ctx.lastResult.valid = false;

    return OBDII_STATUS_OK;
}

OBDII_Status_t OBDII_GetResult(OBDII_Result_t *result)
{
    if (!ctx.lastResult.valid) {
        return OBDII_STATUS_NO_RESPONSE;
    }
    *result = ctx.lastResult;
    return OBDII_STATUS_OK;
}

void OBDII_SetCallback(OBDII_ResultCallback_t cb)
{
    ctx.callback = cb;
}

bool OBDII_IsBusy(void)
{
    return (ctx.state != OBDII_STATE_IDLE);
}
