#ifndef DEBUG_LOG_H
#define DEBUG_LOG_H

#include <stdint.h>

#define DBG_ENABLE  1

#if DBG_ENABLE
void DBG_Print(const char *tag, const char *fmt, ...);
#define DBG_LOG(tag, fmt, ...) DBG_Print(tag, fmt, ##__VA_ARGS__)
#else
#define DBG_LOG(tag, fmt, ...) ((void)0)
#endif

#endif /* DEBUG_LOG_H */
