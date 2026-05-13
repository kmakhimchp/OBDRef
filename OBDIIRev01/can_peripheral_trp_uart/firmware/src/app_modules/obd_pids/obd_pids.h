#ifndef OBD_PIDS_H
#define OBD_PIDS_H

#include <stdint.h>

typedef float (*OBD_ScaleFn_t)(const uint8_t *data);

typedef struct {
    uint8_t         pid;
    uint16_t        did;
    const char     *name;
    const char     *unit;
    uint8_t         dataBytes;
    OBD_ScaleFn_t   scale;
} OBD_PidEntry_t;

const OBD_PidEntry_t *OBD_GetPidByNumber(uint8_t pid);
const OBD_PidEntry_t *OBD_GetPidByName(const char *name);
uint16_t OBD_PidToDid(uint8_t pid);
float OBD_ScaleResponse(uint8_t pid, const uint8_t *data);
const char *OBD_GetPidName(uint8_t pid);
const char *OBD_GetPidUnit(uint8_t pid);
uint8_t OBD_GetPidCount(void);

#endif /* OBD_PIDS_H */
