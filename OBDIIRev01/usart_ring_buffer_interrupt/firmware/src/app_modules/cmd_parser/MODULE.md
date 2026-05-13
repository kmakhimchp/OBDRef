# Module: cmd_parser

## Responsibility
Parses raw command line input to extract the command name (first
whitespace-delimited token), converting it to uppercase for
case-insensitive matching.

## Files

| File | Purpose |
|------|---------|
| `cmd_parser.h` | Public interface — function prototypes and constants |
| `cmd_parser.c` | Implementation — whitespace skip, token extraction, toupper |

## Public Interface

| Function | Description |
|----------|-------------|
| `CmdParser_ExtractCommand(input, commandOut, maxLen)` | Extracts and uppercases the first token from input; returns false if input is empty/whitespace-only |

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `CMD_PARSER_MAX_CMD_LENGTH` | 20 | Maximum command name length (including null terminator) |

## Design Notes
- Skips leading whitespace (space and tab)
- Extracts until next whitespace or end of string
- Converts to uppercase during extraction (case-insensitive matching)
- Returns false for NULL input, empty string, or whitespace-only input
- Truncates command name at maxLen-1 characters (always null-terminates)
