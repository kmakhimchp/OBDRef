# user.cmake — application-owned source files
# Added by the AI workflow for OBD-II diagnostic client modules.

target_sources(can_peripheral_trp_uart_default_default_XC32_compile PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/isotp_transport/isotp_transport.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/isotp_transport/isotp_frames.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/uds_client/uds_client.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/uds_client/uds_console.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/obd_pids/obd_pids.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/ble_diag_bridge/ble_diag_bridge.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/debug_log/debug_log.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/obdii/obdii.c"
)

target_include_directories(can_peripheral_trp_uart_default_default_XC32_compile PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/isotp_transport"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/uds_client"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/obd_pids"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/ble_diag_bridge"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/debug_log"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/obdii"
)
