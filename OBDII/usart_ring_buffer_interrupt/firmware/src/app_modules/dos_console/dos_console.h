#ifndef DOS_CONSOLE_H
#define DOS_CONSOLE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define DOS_CONSOLE_LINE_BUFFER_SIZE  80

typedef void (*DOS_Console_CommandCallback)(const char* command);

void DOS_Console_Initialize(void);
void DOS_Console_Task(void);
void DOS_Console_RegisterCallback(DOS_Console_CommandCallback callback);
void DOS_Console_Print(const char* str);

#endif /* DOS_CONSOLE_H */
