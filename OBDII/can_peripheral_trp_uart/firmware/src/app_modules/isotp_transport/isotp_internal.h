#ifndef ISOTP_INTERNAL_H
#define ISOTP_INTERNAL_H

#include <stdint.h>
#include <stdbool.h>
#include "isotp_transport.h"
#include "isotp_config.h"

#define PCI_SF  0x00u
#define PCI_FF  0x10u
#define PCI_CF  0x20u
#define PCI_FC  0x30u

#define FC_FLOW_STATUS_CTS   0x00u
#define FC_FLOW_STATUS_WAIT  0x01u
#define FC_FLOW_STATUS_OVFL  0x02u

typedef struct {
    ISOTP_TxState_t state;
    uint8_t         buffer[ISOTP_TX_BUFFER_SIZE];
    uint16_t        totalLen;
    uint16_t        offset;
    uint8_t         seqNum;
    uint8_t         blockSize;
    uint8_t         blockCount;
    uint8_t         stMin;
    uint32_t        timerStart;
    uint32_t        cfTimerStart;
    bool            functional;
} ISOTP_TxContext_t;

typedef struct {
    ISOTP_RxState_t state;
    uint8_t         buffer[ISOTP_RX_BUFFER_SIZE];
    uint16_t        totalLen;
    uint16_t        offset;
    uint8_t         expectedSeq;
    uint32_t        timerStart;
} ISOTP_RxContext_t;

typedef struct {
    bool     complete;
    uint8_t  buffer[ISOTP_RX_BUFFER_SIZE];
    uint16_t length;
} ISOTP_RxResult_t;

extern ISOTP_TxContext_t txCtx;
extern ISOTP_RxContext_t rxCtx;
extern ISOTP_RxResult_t  rxResult;

uint32_t ISOTP_GetTickMs(void);
bool ISOTP_TransmitFrame(uint32_t canId, const uint8_t *data, uint8_t len);
void ISOTP_SendFlowControl(void);
void ISOTP_SendNextCF(void);

void ISOTP_HandleSF(const uint8_t *data, uint8_t dlc);
void ISOTP_HandleFF(const uint8_t *data, uint8_t dlc);
void ISOTP_HandleCF(const uint8_t *data, uint8_t dlc);
void ISOTP_HandleFC(const uint8_t *data, uint8_t dlc);

#endif /* ISOTP_INTERNAL_H */
