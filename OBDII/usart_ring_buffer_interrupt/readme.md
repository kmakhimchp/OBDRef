[![MCHP](https://raw.githubusercontent.com/wiki/Microchip-MPLAB-Harmony/Microchip-MPLAB-Harmony.github.io/images/microchip_logo.png)](https://www.microchip.com)

# DOSConsole_WBZ451

DOS command console simulator running on the WBZ451 Curiosity board.
Recognizes common DOS commands and prints whether the input is a valid
or invalid DOS command.

## Module Map

```
firmware/src/
├── main.c                          Application entry point
├── config/                         [MCC-generated — do not modify]
├── packs/                          [MCC-generated — do not modify]
└── app_modules/
    ├── dos_console/                Console I/O (echo, buffer, prompt)
    ├── cmd_parser/                 Command line parsing and tokenization
    └── dos_commands/               DOS command lookup table and validation
```

## Data Flow

```
UART RX ──► dos_console (echo + buffer) ──► cmd_parser (extract command)
                                                    │
                                                    ▼
UART TX ◄── dos_console (print result) ◄── dos_commands (validate)
```

## Use Cases

1. **Valid command:** User types `DIR` + Enter → Console prints `'DIR' is a valid DOS command`
2. **Invalid command:** User types `FOOBAR` + Enter → Console prints `'FOOBAR' is not a valid DOS command`
3. **Help:** User types `HELP` + Enter → Console lists all recognized DOS commands
4. **Empty input:** User presses Enter → Console redisplays prompt

## Target Hardware

- **Board:** WBZ451 Curiosity Board
- **MCU:** PIC32CX-BZ2 (WBZ451)
- **UART:** SERCOM1 (ring buffer interrupt mode, pre-configured via MCC)
- **Terminal settings:** 115200 baud, 8N1

## Build

Build via VS Code CMake Tools using the preset
`usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_conf`.
Output: `out/usart_ring_buffer_interrupt_wbz451_curiosity/wbz451_curiosity.elf`

## Original Harmony Demo

[Click here](https://onlinedocs.microchip.com/v2/keyword-lookup?keyword=CSP_APPS_PIC32CXBZ2_WBZ45_SERCOM_USART_RING_BUFFER&redirect=true) to view the original USART ring buffer interrupt documentation.
