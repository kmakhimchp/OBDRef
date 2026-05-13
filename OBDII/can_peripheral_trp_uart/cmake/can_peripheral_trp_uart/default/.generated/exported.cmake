set(DEPENDENT_MP_BIN2HEXcan_peripheral_trp_uart_default_wokfOG92 "c:/Program Files/Microchip/xc32/v5.10/bin/xc32-bin2hex.exe")
set(DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default_wokfOG92 "${CMAKE_CURRENT_LIST_DIR}/../../../../out/can_peripheral_trp_uart/default.elf")
set(DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default_wokfOG92 "${CMAKE_CURRENT_LIST_DIR}/../../../../out/can_peripheral_trp_uart")
set(DEPENDENT_BYPRODUCTScan_peripheral_trp_uart_default_wokfOG92 ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default_wokfOG92}/${sourceFileNamecan_peripheral_trp_uart_default_wokfOG92}.c)
add_custom_command(
    OUTPUT ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default_wokfOG92}/${sourceFileNamecan_peripheral_trp_uart_default_wokfOG92}.c
    COMMAND ${DEPENDENT_MP_BIN2HEXcan_peripheral_trp_uart_default_wokfOG92} --image ${DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default_wokfOG92} --image-generated-c ${sourceFileNamecan_peripheral_trp_uart_default_wokfOG92}.c --image-generated-h ${sourceFileNamecan_peripheral_trp_uart_default_wokfOG92}.h --image-copy-mode ${modecan_peripheral_trp_uart_default_wokfOG92} --image-offset ${addresscan_peripheral_trp_uart_default_wokfOG92} 
    WORKING_DIRECTORY ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default_wokfOG92}
    DEPENDS ${DEPENDENT_DEPENDENT_TARGET_ELFcan_peripheral_trp_uart_default_wokfOG92})
add_custom_target(
    dependent_produced_source_artifactcan_peripheral_trp_uart_default_wokfOG92 
    DEPENDS ${DEPENDENT_TARGET_DIRcan_peripheral_trp_uart_default_wokfOG92}/${sourceFileNamecan_peripheral_trp_uart_default_wokfOG92}.c
    )
