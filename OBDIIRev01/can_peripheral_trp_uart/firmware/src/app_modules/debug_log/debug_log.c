#include "debug_log.h"
#include "peripheral/sercom/usart/plib_sercom0_usart.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#if DBG_ENABLE

#define DBG_BUF_SIZE 200

static char dbgBuf[DBG_BUF_SIZE];

void DBG_Print(const char *tag, const char *fmt, ...)
{
    uint32_t tick = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);

    int offset = snprintf(dbgBuf, DBG_BUF_SIZE, "[%lu] %s: ", (unsigned long)tick, tag);
    if (offset < 0 || offset >= DBG_BUF_SIZE) {
        return;
    }

    va_list args;
    va_start(args, fmt);
    int msgLen = vsnprintf(&dbgBuf[offset], DBG_BUF_SIZE - offset, fmt, args);
    va_end(args);

    if (msgLen < 0) {
        return;
    }
    offset += msgLen;
    if (offset > DBG_BUF_SIZE - 3) {
        offset = DBG_BUF_SIZE - 3;
    }

    dbgBuf[offset++] = '\r';
    dbgBuf[offset++] = '\n';

    SERCOM0_USART_Write((uint8_t *)dbgBuf, (size_t)offset);
}

#endif /* DBG_ENABLE */
