#ifndef BLE_DIAG_BRIDGE_H
#define BLE_DIAG_BRIDGE_H

#include <stdint.h>
#include <stdbool.h>

#define BLE_DIAG_FRAME_MIN_LEN      3u
#define BLE_DIAG_MAX_PAYLOAD_LEN    64u

#define BLE_DIAG_ERR_MALFORMED      0x01u
#define BLE_DIAG_ERR_BUSY           0x02u
#define BLE_DIAG_ERR_INVALID_SID    0x03u

void BLE_DIAG_Init(void);
void BLE_DIAG_OnDataReceived(const uint8_t *data, uint16_t length);
void BLE_DIAG_OnConnected(uint16_t connHandle);
void BLE_DIAG_OnDisconnected(void);
void BLE_DIAG_OnUdsResponse(uint8_t status, const uint8_t *data, uint16_t length);
bool BLE_DIAG_IsActive(void);

#endif /* BLE_DIAG_BRIDGE_H */
