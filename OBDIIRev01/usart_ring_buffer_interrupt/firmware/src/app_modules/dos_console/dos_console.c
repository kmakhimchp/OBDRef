#include "dos_console.h"
#include "definitions.h"
#include <string.h>

#define CHAR_BACKSPACE_1  0x08
#define CHAR_BACKSPACE_2  0x7F
#define CHAR_ENTER        0x0D
#define CHAR_NEWLINE      0x0A
#define CHAR_PRINTABLE_MIN 0x20
#define CHAR_PRINTABLE_MAX 0x7E

static char lineBuffer[DOS_CONSOLE_LINE_BUFFER_SIZE + 1];
static uint8_t bufferIndex;
static DOS_Console_CommandCallback commandCallback;

static const char welcomeBanner[] =
    "\r\n"
    "========================================\r\n"
    "  DOS Console Simulator v1.0\r\n"
    "  WBZ451 Curiosity Board\r\n"
    "========================================\r\n"
    "\r\n";

static const char prompt[] = "C:\\>";

static void printPrompt(void)
{
    SERCOM1_USART_Write((uint8_t*)prompt, sizeof(prompt) - 1);
}

void DOS_Console_Initialize(void)
{
    bufferIndex = 0;
    commandCallback = NULL;
    memset(lineBuffer, 0, sizeof(lineBuffer));

    SERCOM1_USART_Write((uint8_t*)welcomeBanner, sizeof(welcomeBanner) - 1);
    printPrompt();
}

void DOS_Console_Task(void)
{
    uint8_t rxByte;

    if (SERCOM1_USART_ReadCountGet() == 0)
    {
        return;
    }

    SERCOM1_USART_Read(&rxByte, 1);

    if (rxByte == CHAR_ENTER)
    {
        SERCOM1_USART_Write((uint8_t*)"\r\n", 2);
        lineBuffer[bufferIndex] = '\0';

        if (commandCallback != NULL)
        {
            commandCallback(lineBuffer);
        }

        bufferIndex = 0;
        memset(lineBuffer, 0, sizeof(lineBuffer));
        printPrompt();
    }
    else if (rxByte == CHAR_BACKSPACE_1 || rxByte == CHAR_BACKSPACE_2)
    {
        if (bufferIndex > 0)
        {
            bufferIndex--;
            lineBuffer[bufferIndex] = '\0';
            SERCOM1_USART_Write((uint8_t*)"\b \b", 3);
        }
    }
    else if (rxByte >= CHAR_PRINTABLE_MIN && rxByte <= CHAR_PRINTABLE_MAX)
    {
        if (bufferIndex < DOS_CONSOLE_LINE_BUFFER_SIZE)
        {
            lineBuffer[bufferIndex] = (char)rxByte;
            bufferIndex++;
            SERCOM1_USART_Write(&rxByte, 1);
        }
    }
}

void DOS_Console_RegisterCallback(DOS_Console_CommandCallback callback)
{
    commandCallback = callback;
}

void DOS_Console_Print(const char* str)
{
    if (str != NULL)
    {
        SERCOM1_USART_Write((uint8_t*)str, strlen(str));
    }
}
