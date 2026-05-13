#ifndef DOS_COMMANDS_H
#define DOS_COMMANDS_H

#include <stdbool.h>
#include <stdint.h>

bool DosCommands_IsValid(const char* command);
uint8_t DosCommands_GetCount(void);
const char* DosCommands_GetName(uint8_t index);

#endif /* DOS_COMMANDS_H */
