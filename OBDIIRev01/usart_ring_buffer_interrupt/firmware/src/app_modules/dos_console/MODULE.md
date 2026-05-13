# Module: dos_console

## Responsibility
Provides USART-based interactive console I/O for the DOS command simulator.
Handles character echo, backspace processing, line buffering, prompt display,
and dispatching complete command lines to the command processor.

## Files

| File | Purpose |
|------|---------|
| `dos_console.h` | Public interface — types, constants, function prototypes |
| `dos_console.c` | Implementation — USART I/O, buffer management, character handling |

## Public Interface

| Function | Description |
|----------|-------------|
| `DOS_Console_Initialize(void)` | Print welcome banner and first prompt |
| `DOS_Console_Task(void)` | Polled task — reads USART, handles echo/backspace, dispatches on Enter |
| `DOS_Console_RegisterCallback(callback)` | Register the command processing callback |
| `DOS_Console_Print(const char* str)` | Print a null-terminated string to the console |

## Types

| Type | Description |
|------|-------------|
| `DOS_Console_CommandCallback` | Function pointer: `void (*)(const char* command)` |

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DOS_CONSOLE_LINE_BUFFER_SIZE` | 80 | Maximum characters in the command line buffer |

## Design Notes
- Uses SERCOM1 USART ring buffer API for non-blocking read/write
- Polling model: `DOS_Console_Task()` called in the main loop
- Supports printable ASCII (0x20–0x7E), backspace (0x08/0x7F), and Enter (0x0D)
- Backspace visual feedback: sends `\b \b` (back, space, back) to terminal
- Prompt format: `C:\>`
- Welcome banner identifies application name and version
