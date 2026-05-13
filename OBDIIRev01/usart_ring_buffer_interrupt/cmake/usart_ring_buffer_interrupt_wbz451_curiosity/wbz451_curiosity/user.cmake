# user.cmake — Application source files for DOSConsole_WBZ451
# This file is included by CMakeLists.txt AFTER main.cmake.
# Use target_sources to add files to the existing compile OBJECT library.

# Add application module source files to the C compile target
target_sources(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_compile PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/dos_console/dos_console.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/cmd_parser/cmd_parser.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/dos_commands/dos_commands.c"
)

# Add application include path so app_modules/ headers are found
target_include_directories(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_compile PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
)
