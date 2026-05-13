# Module: dos_commands

## Responsibility
Maintains the lookup table of recognized DOS commands and provides
the validation function that determines if a command is valid or invalid.

## Files

| File | Purpose |
|------|---------|
| `dos_commands.h` | Public interface — validation and query functions |
| `dos_commands.c` | Implementation — command table and string matching |

## Public Interface

| Function | Description |
|----------|-------------|
| `DosCommands_IsValid(const char* command)` | Returns true if command matches a known DOS command (exact match, expects uppercase input) |
| `DosCommands_GetCount(void)` | Returns the number of commands in the lookup table |
| `DosCommands_GetName(uint8_t index)` | Returns the command name at the given index, or NULL if out of bounds |

## Design Notes
- Lookup table stored as const array of 20 string pointers
- Comparison uses strcmp (expects pre-uppercased input from cmd_parser)
- Commands: DIR, CD, CLS, COPY, DEL, MKDIR, RMDIR, TYPE, REN, ECHO, DATE, TIME, VER, VOL, PATH, MOVE, ATTRIB, FIND, MORE, TREE
