#ifndef UDS_CONSOLE_H
#define UDS_CONSOLE_H

#include "uds_client.h"

void UDS_ConsoleInit(void);
void UDS_ConsoleProcessChar(char c);
void UDS_ConsoleOnResponse(UDS_Status_t status, const uint8_t *data, uint16_t length);

#endif /* UDS_CONSOLE_H */
