#include "cmd_parser.h"
#include <string.h>
#include <ctype.h>

bool CmdParser_ExtractCommand(const char* input, char* commandOut, uint8_t maxLen)
{
    uint8_t i = 0;
    uint8_t cmdIdx = 0;

    if (input == NULL || commandOut == NULL || maxLen == 0)
    {
        return false;
    }

    while (input[i] == ' ' || input[i] == '\t')
    {
        i++;
    }

    if (input[i] == '\0')
    {
        commandOut[0] = '\0';
        return false;
    }

    while (input[i] != '\0' && input[i] != ' ' && input[i] != '\t')
    {
        if (cmdIdx < (maxLen - 1))
        {
            commandOut[cmdIdx] = (char)toupper((unsigned char)input[i]);
            cmdIdx++;
        }
        i++;
    }

    commandOut[cmdIdx] = '\0';
    return (cmdIdx > 0);
}
