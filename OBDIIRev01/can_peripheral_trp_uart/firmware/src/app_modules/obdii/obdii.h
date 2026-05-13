#ifndef OBDII_H
#define OBDII_H

#include <stdint.h>
#include <stdbool.h>

#define OBDII_PID_COOLANT_TEMP    0x05u
#define OBDII_PID_ENGINE_RPM      0x0Cu
#define OBDII_PID_VEHICLE_SPEED   0x0Du

#define OBDII_MODE_CURRENT_DATA   0x01u
#define OBDII_RESPONSE_OFFSET     0x40u

#define OBDII_TIMEOUT_MS          2000u

typedef enum {
    OBDII_STATUS_OK = 0,
    OBDII_STATUS_BUSY,
    OBDII_STATUS_TIMEOUT,
    OBDII_STATUS_ERROR,
    OBDII_STATUS_NO_RESPONSE
} OBDII_Status_t;

typedef struct {
    uint8_t  pid;
    float    value;
    bool     valid;
} OBDII_Result_t;

typedef void (*OBDII_ResultCallback_t)(uint8_t pid, float value, bool success);

void           OBDII_Init(void);
void           OBDII_Poll(void);
OBDII_Status_t OBDII_RequestPid(uint8_t pid);
OBDII_Status_t OBDII_GetResult(OBDII_Result_t *result);
void           OBDII_SetCallback(OBDII_ResultCallback_t cb);
bool           OBDII_IsBusy(void);

#endif
