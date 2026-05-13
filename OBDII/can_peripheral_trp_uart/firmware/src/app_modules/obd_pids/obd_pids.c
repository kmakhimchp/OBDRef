#include "obd_pids.h"
#include <string.h>
#include <stddef.h>

static float scale_engine_load(const uint8_t *data)
{
    return (float)data[0] * 100.0f / 255.0f;
}

static float scale_coolant_temp(const uint8_t *data)
{
    return (float)data[0] - 40.0f;
}

static float scale_engine_rpm(const uint8_t *data)
{
    return ((float)data[0] * 256.0f + (float)data[1]) / 4.0f;
}

static float scale_vehicle_speed(const uint8_t *data)
{
    return (float)data[0];
}

static float scale_throttle_position(const uint8_t *data)
{
    return (float)data[0] * 100.0f / 255.0f;
}

static const OBD_PidEntry_t pidTable[] = {
    { 0x04, 0xF404, "load",     "%",    1, scale_engine_load },
    { 0x05, 0xF405, "coolant",  "C",    1, scale_coolant_temp },
    { 0x0C, 0xF40C, "rpm",      "rpm",  2, scale_engine_rpm },
    { 0x0D, 0xF40D, "speed",    "km/h", 1, scale_vehicle_speed },
    { 0x11, 0xF411, "throttle", "%",    1, scale_throttle_position },
};

#define PID_TABLE_SIZE (sizeof(pidTable) / sizeof(pidTable[0]))

const OBD_PidEntry_t *OBD_GetPidByNumber(uint8_t pid)
{
    for (uint8_t i = 0; i < PID_TABLE_SIZE; i++) {
        if (pidTable[i].pid == pid) {
            return &pidTable[i];
        }
    }
    return NULL;
}

const OBD_PidEntry_t *OBD_GetPidByName(const char *name)
{
    for (uint8_t i = 0; i < PID_TABLE_SIZE; i++) {
        if (strcmp(pidTable[i].name, name) == 0) {
            return &pidTable[i];
        }
    }
    return NULL;
}

uint16_t OBD_PidToDid(uint8_t pid)
{
    const OBD_PidEntry_t *entry = OBD_GetPidByNumber(pid);
    if (entry != NULL) {
        return entry->did;
    }
    return 0;
}

float OBD_ScaleResponse(uint8_t pid, const uint8_t *data)
{
    const OBD_PidEntry_t *entry = OBD_GetPidByNumber(pid);
    if (entry != NULL && entry->scale != NULL) {
        return entry->scale(data);
    }
    return 0.0f;
}

const char *OBD_GetPidName(uint8_t pid)
{
    const OBD_PidEntry_t *entry = OBD_GetPidByNumber(pid);
    if (entry != NULL) {
        return entry->name;
    }
    return "unknown";
}

const char *OBD_GetPidUnit(uint8_t pid)
{
    const OBD_PidEntry_t *entry = OBD_GetPidByNumber(pid);
    if (entry != NULL) {
        return entry->unit;
    }
    return "";
}

uint8_t OBD_GetPidCount(void)
{
    return (uint8_t)PID_TABLE_SIZE;
}
