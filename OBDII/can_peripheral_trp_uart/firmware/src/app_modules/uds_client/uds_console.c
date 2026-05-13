#include "uds_client.h"
#include "../obd_pids/obd_pids.h"
#include "../obdii/obdii.h"
#include "definitions.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define CONSOLE_TX_BUF_SIZE  256
#define CMD_BUF_SIZE         64

static char cmdBuf[CMD_BUF_SIZE];
static uint8_t cmdIdx = 0;
static char txBuf[CONSOLE_TX_BUF_SIZE];

static void console_print(const char *msg)
{
    SERCOM0_USART_Write((uint8_t *)msg, strlen(msg));
}

static void console_prompt(void)
{
    console_print("obd> ");
}

static void str_tolower(char *s)
{
    while (*s) {
        *s = (char)tolower((unsigned char)*s);
        s++;
    }
}

static void cmd_read(const char *arg)
{
    const OBD_PidEntry_t *pid = OBD_GetPidByName(arg);
    if (pid == NULL) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Unknown PID: %s\r\n", arg);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
        return;
    }

    uint16_t did = pid->did;
    UDS_Status_t st = UDS_ReadDataByIdentifier(&did, 1);
    if (st != UDS_STATUS_OK) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Request failed (status=%d)\r\n", (int)st);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
        return;
    }

    int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                     "Reading %s (DID 0x%04X)...\r\n", pid->name, pid->did);
    SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
}

static void cmd_session(const char *arg)
{
    uint8_t session;
    if (strcmp(arg, "default") == 0) {
        session = UDS_SESSION_DEFAULT;
    } else if (strcmp(arg, "extended") == 0) {
        session = UDS_SESSION_EXTENDED;
    } else if (strcmp(arg, "programming") == 0) {
        session = UDS_SESSION_PROGRAMMING;
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Unknown session: %s (use: default, extended, programming)\r\n", arg);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
        return;
    }

    UDS_Status_t st = UDS_DiagSessionControl(session);
    if (st == UDS_STATUS_OK) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Session request sent: %s\r\n", arg);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Session request failed (status=%d)\r\n", (int)st);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
}

static void cmd_reset(const char *arg)
{
    uint8_t resetType;
    if (strcmp(arg, "hard") == 0) {
        resetType = UDS_RESET_HARD;
    } else if (strcmp(arg, "keyoff") == 0) {
        resetType = UDS_RESET_KEY_OFF_ON;
    } else if (strcmp(arg, "soft") == 0) {
        resetType = UDS_RESET_SOFT;
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Unknown reset type: %s (use: hard, keyoff, soft)\r\n", arg);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
        return;
    }

    UDS_Status_t st = UDS_EcuReset(resetType);
    if (st == UDS_STATUS_OK) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "ECU reset request sent: %s\r\n", arg);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "ECU reset failed (status=%d)\r\n", (int)st);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
}

static void cmd_tester(const char *arg)
{
    bool suppress = (strcmp(arg, "suppress") == 0);
    UDS_Status_t st = UDS_TesterPresent(suppress);
    if (st == UDS_STATUS_OK) {
        console_print("TesterPresent sent\r\n");
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "TesterPresent failed (status=%d)\r\n", (int)st);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
}

static void obdii_result_callback(uint8_t pid, float value, bool success)
{
    if (success) {
        const char *name = "PID";
        const char *unit = "";
        switch (pid) {
            case OBDII_PID_ENGINE_RPM:     name = "RPM";     unit = "rpm"; break;
            case OBDII_PID_VEHICLE_SPEED:  name = "Speed";   unit = "km/h"; break;
            case OBDII_PID_COOLANT_TEMP:   name = "Coolant"; unit = "C"; break;
            default: break;
        }
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "%s: %.1f %s\r\n", name, (double)value, unit);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "OBD-II PID 0x%02X: no response\r\n", pid);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
    console_prompt();
}

static void cmd_obd(const char *arg)
{
    uint8_t pid;
    if (strcmp(arg, "rpm") == 0) {
        pid = OBDII_PID_ENGINE_RPM;
    } else if (strcmp(arg, "speed") == 0) {
        pid = OBDII_PID_VEHICLE_SPEED;
    } else if (strcmp(arg, "coolant") == 0) {
        pid = OBDII_PID_COOLANT_TEMP;
    } else {
        console_print("Usage: obd <rpm|speed|coolant>\r\n");
        return;
    }

    OBDII_SetCallback(obdii_result_callback);
    OBDII_Status_t st = OBDII_RequestPid(pid);
    if (st == OBDII_STATUS_OK) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "OBD-II request sent (Mode 01, PID 0x%02X)...\r\n", pid);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "OBD-II request failed (status=%d)\r\n", (int)st);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
}

static void cmd_help(void)
{
    console_print(
        "Commands:\r\n"
        "  obd <pid>        - Standard OBD-II Mode 01 (rpm, speed, coolant)\r\n"
        "  read <pid>       - UDS ReadDataByID (rpm, speed, coolant, throttle, load)\r\n"
        "  session <type>   - DiagSessionControl (default, extended, programming)\r\n"
        "  reset <type>     - ECU Reset (hard, keyoff, soft)\r\n"
        "  tester [suppress]- TesterPresent keepalive\r\n"
        "  help             - Show this help\r\n"
    );
}

static void process_command(const char *line)
{
    char cmd[CMD_BUF_SIZE];
    strncpy(cmd, line, CMD_BUF_SIZE - 1);
    cmd[CMD_BUF_SIZE - 1] = '\0';
    str_tolower(cmd);

    char *verb = strtok(cmd, " ");
    if (verb == NULL) {
        return;
    }

    char *arg = strtok(NULL, " ");
    if (arg == NULL) {
        arg = "";
    }

    if (strcmp(verb, "obd") == 0) {
        cmd_obd(arg);
    } else if (strcmp(verb, "read") == 0) {
        cmd_read(arg);
    } else if (strcmp(verb, "session") == 0) {
        cmd_session(arg);
    } else if (strcmp(verb, "reset") == 0) {
        cmd_reset(arg);
    } else if (strcmp(verb, "tester") == 0) {
        cmd_tester(arg);
    } else if (strcmp(verb, "help") == 0 || strcmp(verb, "?") == 0) {
        cmd_help();
    } else {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Unknown command: %s (type 'help')\r\n", verb);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    }
}

void UDS_ConsoleInit(void)
{
    cmdIdx = 0;
    memset(cmdBuf, 0, CMD_BUF_SIZE);
    console_print("\r\n--- OBD-II Diagnostic Console ---\r\n");
    cmd_help();
    console_prompt();
}

void UDS_ConsoleProcessChar(char c)
{
    if (c == '\r' || c == '\n') {
        console_print("\r\n");
        if (cmdIdx > 0) {
            cmdBuf[cmdIdx] = '\0';
            process_command(cmdBuf);
            cmdIdx = 0;
        }
        console_prompt();
        return;
    }

    if (c == '\b' || c == 0x7F) {
        if (cmdIdx > 0) {
            cmdIdx--;
            console_print("\b \b");
        }
        return;
    }

    if (cmdIdx < CMD_BUF_SIZE - 1) {
        cmdBuf[cmdIdx++] = c;
        char echo[2] = { c, '\0' };
        console_print(echo);
    }
}

void UDS_ConsoleOnResponse(UDS_Status_t status, const uint8_t *data, uint16_t length)
{
    if (status == UDS_STATUS_OK && length > 0) {
        uint8_t sid = data[0] - 0x40u;
        if (sid == UDS_SID_READ_DATA_BY_ID && length >= 4) {
            uint16_t did = ((uint16_t)data[1] << 8) | data[2];
            uint8_t pidNum = (uint8_t)(did & 0xFFu);
            const OBD_PidEntry_t *pid = OBD_GetPidByNumber(pidNum);
            if (pid != NULL) {
                float val = pid->scale(&data[3]);
                int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                                 "%s: %.1f %s\r\n", pid->name, (double)val, pid->unit);
                SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
            } else {
                int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                                 "Response DID 0x%04X: %d bytes\r\n", did, length - 3);
                SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
            }
        } else if (sid == UDS_SID_DIAG_SESSION_CONTROL) {
            console_print("Session changed OK\r\n");
        } else if (sid == UDS_SID_ECU_RESET) {
            console_print("ECU reset OK\r\n");
        } else if (sid == UDS_SID_TESTER_PRESENT) {
            console_print("TesterPresent OK\r\n");
        } else {
            int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                             "Positive response SID 0x%02X (%d bytes)\r\n",
                             data[0], length);
            SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
        }
    } else if (status == UDS_STATUS_NEGATIVE && length >= 3) {
        int n = snprintf(txBuf, CONSOLE_TX_BUF_SIZE,
                         "Negative response: NRC 0x%02X\r\n", data[2]);
        SERCOM0_USART_Write((uint8_t *)txBuf, (size_t)n);
    } else if (status == UDS_STATUS_TIMEOUT) {
        console_print("Response timeout\r\n");
    } else {
        console_print("Error\r\n");
    }
    console_prompt();
}
