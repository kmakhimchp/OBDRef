/*******************************************************************************
* Copyright (C) 2020 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/

#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "definitions.h"
#include "app_modules/dos_console/dos_console.h"
#include "app_modules/cmd_parser/cmd_parser.h"
#include "app_modules/dos_commands/dos_commands.h"

static void printHelp(void)
{
    uint8_t i;
    uint8_t count = DosCommands_GetCount();

    DOS_Console_Print("Recognized DOS commands:\r\n");
    for (i = 0; i < count; i++)
    {
        DOS_Console_Print("  ");
        DOS_Console_Print(DosCommands_GetName(i));
        DOS_Console_Print("\r\n");
    }
}

static void onCommandReceived(const char* input)
{
    char command[CMD_PARSER_MAX_CMD_LENGTH];

    if (!CmdParser_ExtractCommand(input, command, CMD_PARSER_MAX_CMD_LENGTH))
    {
        return;
    }

    if (strcmp(command, "HELP") == 0)
    {
        printHelp();
    }
    else if (DosCommands_IsValid(command))
    {
        DOS_Console_Print("'");
        DOS_Console_Print(command);
        DOS_Console_Print("' is a valid DOS command\r\n");
    }
    else
    {
        DOS_Console_Print("'");
        DOS_Console_Print(command);
        DOS_Console_Print("' is not a valid DOS command\r\n");
    }
}

int main(void)
{
    SYS_Initialize(NULL);

    DOS_Console_RegisterCallback(onCommandReceived);
    DOS_Console_Initialize();

    while (1)
    {
        DOS_Console_Task();
    }

    return EXIT_FAILURE;
}
