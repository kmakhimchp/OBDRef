#include "ble_diag_bridge.h"
#include "../uds_client/uds_client.h"
#include "../obd_pids/obd_pids.h"
#include "../debug_log/debug_log.h"
#include "ble_trsps/ble_trsps.h"
#include "peripheral/sercom/usart/plib_sercom0_usart.h"
#include <string.h>
#include <stdio.h>

static uint16_t bleConnHandle;
static bool     bleConnected;
static bool     transactionActive;
static uint8_t  pendingSid;

static void sendErrorResponse(uint8_t errorCode);
static void sendBleFrame(const uint8_t *payload, uint16_t len);
static void indicateActivity(const char *msg);

void BLE_DIAG_Init(void)
{
    bleConnHandle = 0;
    bleConnected = false;
    transactionActive = false;
    pendingSid = 0;
    DBG_LOG("BLE_DIAG", "Init");
}

void BLE_DIAG_OnConnected(uint16_t connHandle)
{
    bleConnHandle = connHandle;
    bleConnected = true;
    transactionActive = false;
    DBG_LOG("BLE_DIAG", "Connected hdl=%d", (int)connHandle);
    indicateActivity("BLE: Client connected\r\n");
}

void BLE_DIAG_OnDisconnected(void)
{
    bleConnected = false;
    transactionActive = false;
    pendingSid = 0;
    DBG_LOG("BLE_DIAG", "Disconnected");
    indicateActivity("BLE: Client disconnected\r\n");
}

bool BLE_DIAG_IsActive(void)
{
    return transactionActive;
}

void BLE_DIAG_OnDataReceived(const uint8_t *data, uint16_t length)
{
    if (length < BLE_DIAG_FRAME_MIN_LEN) {
        DBG_LOG("BLE_DIAG", "Malformed frame (len=%d < min)", (int)length);
        sendErrorResponse(BLE_DIAG_ERR_MALFORMED);
        return;
    }

    uint16_t frameLen = ((uint16_t)data[0] << 8) | (uint16_t)data[1];
    if (frameLen == 0 || frameLen > BLE_DIAG_MAX_PAYLOAD_LEN ||
        frameLen != (length - 2u)) {
        DBG_LOG("BLE_DIAG", "Malformed frame (frameLen=%d, actual=%d)", (int)frameLen, (int)(length - 2));
        sendErrorResponse(BLE_DIAG_ERR_MALFORMED);
        return;
    }

    if (UDS_GetState() != UDS_STATE_IDLE) {
        DBG_LOG("BLE_DIAG", "UDS busy, rejecting");
        sendErrorResponse(BLE_DIAG_ERR_BUSY);
        return;
    }

    uint8_t sid = data[2];
    DBG_LOG("BLE_DIAG", "Frame SID=0x%02X payload=%d", sid, (int)(frameLen - 1));
    const uint8_t *payload = &data[3];
    uint16_t payloadLen = frameLen - 1u;
    UDS_Status_t status;

    pendingSid = sid;

    switch (sid) {
        case UDS_SID_DIAG_SESSION_CONTROL:
            if (payloadLen < 1u) {
                sendErrorResponse(BLE_DIAG_ERR_MALFORMED);
                return;
            }
            status = UDS_DiagSessionControl(payload[0]);
            break;

        case UDS_SID_ECU_RESET:
            if (payloadLen < 1u) {
                sendErrorResponse(BLE_DIAG_ERR_MALFORMED);
                return;
            }
            status = UDS_EcuReset(payload[0]);
            break;

        case UDS_SID_READ_DATA_BY_ID: {
            if (payloadLen < 2u || (payloadLen % 2u) != 0) {
                sendErrorResponse(BLE_DIAG_ERR_MALFORMED);
                return;
            }
            uint8_t didCount = payloadLen / 2u;
            uint16_t dids[15];
            if (didCount > 15u) didCount = 15u;
            for (uint8_t i = 0; i < didCount; i++) {
                dids[i] = ((uint16_t)payload[i * 2u] << 8) |
                           (uint16_t)payload[i * 2u + 1u];
            }
            status = UDS_ReadDataByIdentifier(dids, didCount);
            break;
        }

        case UDS_SID_TESTER_PRESENT: {
            bool suppress = (payloadLen >= 1u && payload[0] == 0x80u);
            status = UDS_TesterPresent(suppress);
            break;
        }

        default:
            sendErrorResponse(BLE_DIAG_ERR_INVALID_SID);
            return;
    }

    if (status == UDS_STATUS_OK) {
        transactionActive = true;
        DBG_LOG("BLE_DIAG", "Request forwarded OK");
        indicateActivity("BLE: Diag request forwarded\r\n");
    } else {
        DBG_LOG("BLE_DIAG", "Request failed, status=%d", (int)status);
        sendErrorResponse(BLE_DIAG_ERR_BUSY);
    }
}

void BLE_DIAG_OnUdsResponse(uint8_t status, const uint8_t *data, uint16_t length)
{
    DBG_LOG("BLE_DIAG", "UDS response status=%d len=%d", (int)status, (int)length);

    if (!bleConnected || !transactionActive) {
        DBG_LOG("BLE_DIAG", "Dropping response (conn=%d active=%d)", bleConnected, transactionActive);
        transactionActive = false;
        return;
    }

    transactionActive = false;

    if (status == (uint8_t)UDS_STATUS_OK && data != NULL && length > 0) {
        DBG_LOG("BLE_DIAG", "Positive response, forwarding %d bytes", (int)length);
        sendBleFrame(data, length);
        indicateActivity("BLE: Response sent to client\r\n");
    } else if (status == (uint8_t)UDS_STATUS_NEGATIVE) {
        uint8_t nrcFrame[3];
        nrcFrame[0] = 0x7Fu;
        nrcFrame[1] = pendingSid;
        nrcFrame[2] = (data != NULL && length >= 3u) ? data[2] : 0x10u;
        DBG_LOG("BLE_DIAG", "NRC 0x%02X for SID=0x%02X", nrcFrame[2], pendingSid);
        sendBleFrame(nrcFrame, 3u);
        indicateActivity("BLE: NRC sent to client\r\n");
    } else {
        uint8_t errFrame[2];
        errFrame[0] = 0xFFu;
        errFrame[1] = (uint8_t)status;
        DBG_LOG("BLE_DIAG", "Error/timeout status=%d", (int)status);
        sendBleFrame(errFrame, 2u);
        indicateActivity("BLE: Timeout/error sent to client\r\n");
    }
}

static void sendBleFrame(const uint8_t *payload, uint16_t len)
{
    DBG_LOG("BLE_DIAG", "TX BLE frame %d bytes", (int)len);
    uint8_t frame[BLE_DIAG_MAX_PAYLOAD_LEN + 2u];
    frame[0] = (uint8_t)(len >> 8);
    frame[1] = (uint8_t)(len & 0xFFu);
    memcpy(&frame[2], payload, len);
    BLE_TRSPS_SendData(bleConnHandle, len + 2u, frame);
}

static void sendErrorResponse(uint8_t errorCode)
{
    DBG_LOG("BLE_DIAG", "Sending error 0x%02X", errorCode);
    uint8_t errPayload[2];
    errPayload[0] = 0xFEu;
    errPayload[1] = errorCode;
    sendBleFrame(errPayload, 2u);
}

static void indicateActivity(const char *msg)
{
    SERCOM0_USART_Write((uint8_t *)msg, strlen(msg));
}
