#ifndef UDS_CLIENT_H
#define UDS_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

#define UDS_SID_DIAG_SESSION_CONTROL  0x10u
#define UDS_SID_ECU_RESET             0x11u
#define UDS_SID_READ_DATA_BY_ID       0x22u
#define UDS_SID_TESTER_PRESENT        0x3Eu

#define UDS_NRC_GENERAL_REJECT              0x10u
#define UDS_NRC_SERVICE_NOT_SUPPORTED       0x11u
#define UDS_NRC_SUBFUNCTION_NOT_SUPPORTED   0x12u
#define UDS_NRC_BUSY_REPEAT_REQUEST         0x21u
#define UDS_NRC_CONDITIONS_NOT_CORRECT      0x22u
#define UDS_NRC_REQUEST_OUT_OF_RANGE        0x31u
#define UDS_NRC_SECURITY_ACCESS_DENIED      0x33u
#define UDS_NRC_RESPONSE_PENDING            0x78u

#define UDS_SESSION_DEFAULT     0x01u
#define UDS_SESSION_EXTENDED    0x03u
#define UDS_SESSION_PROGRAMMING 0x02u

#define UDS_RESET_HARD          0x01u
#define UDS_RESET_KEY_OFF_ON    0x02u
#define UDS_RESET_SOFT          0x03u

#define UDS_P2_TIMEOUT_MS       150u
#define UDS_P2_STAR_TIMEOUT_MS  5000u

#define UDS_MAX_RESPONSE_LEN    128u
#define UDS_MAX_REQUEST_LEN     32u

typedef enum {
    UDS_STATUS_OK = 0,
    UDS_STATUS_BUSY,
    UDS_STATUS_NO_RESPONSE,
    UDS_STATUS_NEGATIVE,
    UDS_STATUS_TIMEOUT,
    UDS_STATUS_ERROR
} UDS_Status_t;

typedef enum {
    UDS_STATE_IDLE = 0,
    UDS_STATE_SENDING,
    UDS_STATE_AWAITING_RESPONSE,
    UDS_STATE_ERROR
} UDS_State_t;

typedef void (*UDS_ResponseCallback_t)(UDS_Status_t status,
                                       const uint8_t *data, uint16_t length);

void UDS_Init(void);
void UDS_Poll(void);

UDS_Status_t UDS_DiagSessionControl(uint8_t sessionType);
UDS_Status_t UDS_TesterPresent(bool suppressResponse);
UDS_Status_t UDS_EcuReset(uint8_t resetType);
UDS_Status_t UDS_ReadDataByIdentifier(const uint16_t *dids, uint8_t count);

UDS_Status_t UDS_GetResponse(uint8_t *buffer, uint16_t *length);
UDS_State_t  UDS_GetState(void);
uint8_t      UDS_GetLastNrc(void);
void UDS_SetResponseCallback(UDS_ResponseCallback_t cb);

#endif /* UDS_CLIENT_H */
