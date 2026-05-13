#ifndef CMD_PARSER_H
#define CMD_PARSER_H

#include <stdint.h>
#include <stdbool.h>

#define CMD_PARSER_MAX_CMD_LENGTH 20

bool CmdParser_ExtractCommand(const char* input, char* commandOut, uint8_t maxLen);

#endif /* CMD_PARSER_H */
