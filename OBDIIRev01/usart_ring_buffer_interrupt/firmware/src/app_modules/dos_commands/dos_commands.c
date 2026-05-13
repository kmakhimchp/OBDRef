#include "dos_commands.h"
#include <string.h>

static const char* const dosCommandTable[] = {
    "DIR",
    "CD",
    "CLS",
    "COPY",
    "DEL",
    "MKDIR",
    "RMDIR",
    "TYPE",
    "REN",
    "ECHO",
    "DATE",
    "TIME",
    "VER",
    "VOL",
    "PATH",
    "MOVE",
    "ATTRIB",
    "FIND",
    "MORE",
    "TREE"
};

#define DOS_COMMAND_COUNT (sizeof(dosCommandTable) / sizeof(dosCommandTable[0]))

bool DosCommands_IsValid(const char* command)
{
    uint8_t i;

    if (command == NULL || command[0] == '\0')
    {
        return false;
    }

    for (i = 0; i < DOS_COMMAND_COUNT; i++)
    {
        if (strcmp(command, dosCommandTable[i]) == 0)
        {
            return true;
        }
    }

    return false;
}

uint8_t DosCommands_GetCount(void)
{
    return (uint8_t)DOS_COMMAND_COUNT;
}

const char* DosCommands_GetName(uint8_t index)
{
    if (index < DOS_COMMAND_COUNT)
    {
        return dosCommandTable[index];
    }
    return NULL;
}
