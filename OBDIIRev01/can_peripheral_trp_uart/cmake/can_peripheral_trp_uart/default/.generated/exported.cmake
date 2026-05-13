set(DEPENDENT_MP_BIN2HEXcan_peripheral_trp_uart_default__yHo8Ncw "c:/Program Files/Microchip/xc32/v5.00/bin/xc32-bin2hex.exe")
set(DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default__yHo8Ncw ${CMAKE_CURRENT_LIST_DIR}/../../../../out/can_peripheral_trp_uart/default.elf)
set(DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default__yHo8Ncw ${CMAKE_CURRENT_LIST_DIR}/../../../../out/can_peripheral_trp_uart)
set(DEPENDENT_BYPRODUCTScan_peripheral_trp_uart_default__yHo8Ncw ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default__yHo8Ncw}/${sourceFileNamecan_peripheral_trp_uart_default__yHo8Ncw}.c)
add_custom_command(
    OUTPUT ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default__yHo8Ncw}/${sourceFileNamecan_peripheral_trp_uart_default__yHo8Ncw}.c
    COMMAND ${DEPENDENT_MP_BIN2HEXcan_peripheral_trp_uart_default__yHo8Ncw} --image ${DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default__yHo8Ncw} --image-generated-c ${sourceFileNamecan_peripheral_trp_uart_default__yHo8Ncw}.c --image-generated-h ${sourceFileNamecan_peripheral_trp_uart_default__yHo8Ncw}.h --image-copy-mode ${modecan_peripheral_trp_uart_default__yHo8Ncw} --image-offset ${addresscan_peripheral_trp_uart_default__yHo8Ncw} 
    WORKING_DIRECTORY ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default__yHo8Ncw}
    DEPENDS ${DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default__yHo8Ncw})
add_custom_target(
    dependent_produced_source_artifactcan_peripheral_trp_uart_default__yHo8Ncw 
    DEPENDS ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default__yHo8Ncw}/${sourceFileNamecan_peripheral_trp_uart_default__yHo8Ncw}.c
    )
