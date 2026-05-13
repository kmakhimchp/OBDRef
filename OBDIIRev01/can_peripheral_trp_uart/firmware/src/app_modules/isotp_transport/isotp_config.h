#ifndef ISOTP_CONFIG_H
#define ISOTP_CONFIG_H

#define ISOTP_TX_ID_PHYSICAL    0x7E0u
#define ISOTP_TX_ID_FUNCTIONAL  0x7DFu
#define ISOTP_RX_ID             0x7E8u

#define ISOTP_MAX_PAYLOAD       4095u
#define ISOTP_RX_BUFFER_SIZE    256u
#define ISOTP_TX_BUFFER_SIZE    256u

#define ISOTP_TIMEOUT_N_BS_MS   1000u
#define ISOTP_TIMEOUT_N_CR_MS   1000u

#define ISOTP_DEFAULT_BS        0u
#define ISOTP_DEFAULT_STMIN     10u

#define ISOTP_CAN_DL            8u

#endif /* ISOTP_CONFIG_H */
