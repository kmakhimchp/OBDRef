# The following variables contains the files used by the different stages of the build process.
set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assemble)
set_source_files_properties(${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assemble} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assemble})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assembleWithPreprocess)
set_source_files_properties(${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assembleWithPreprocess} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assembleWithPreprocess})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_ble/app_ble.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_ble/app_ble_handler.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_ble/app_ble_utility.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_ble/app_trsps_handler.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_idle_task.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/debug_log/debug_log.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_modules/obdii/obdii.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_user_edits.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_dm/ble_dm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_dm/ble_dm_conn.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_dm/ble_dm_dds.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_dm/ble_dm_info.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_dm/ble_dm_sm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_gcm/ble_dd.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble/ble_util/mw_aes.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/profile_ble/ble_trsps/ble_trsps.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/service_ble/ble_trs/ble_trs.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/exceptions.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/freertos_hooks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/initialization.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/interrupts.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/libc_syscalls.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/osal/osal_freertos.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/osal/osal_freertos_extend.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/can/plib_can1.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/clk/plib_clk.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/cmcc/plib_cmcc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/evsys/plib_evsys.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/gpio/plib_gpio.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/nvic/plib_nvic.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/nvm/plib_nvm.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/peripheral/sercom/usart/plib_sercom0_usart.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/startup_xc32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/stdio/xc32_monitor.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/system/cache/sys_cache.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/system/console/src/sys_console.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/system/console/src/sys_console_uart.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/system/int/src/sys_int.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/tasks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/main.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/FreeRTOS_tasks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/croutine.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/event_groups.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/list.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F/port.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/portable/MemMang/heap_4.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/queue.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/stream_buffer.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/timers.c")
set_source_files_properties(${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile} PROPERTIES LANGUAGE C)
set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile_cpp)
set_source_files_properties(${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile_cpp} PROPERTIES LANGUAGE CXX)
set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_link
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/lib/ble_stack_bz6_lib.a"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/driver/device_support/pic32cx_bz6_device_support.a"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/driver/pds/pds.a")
set(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_bin2hex)

# The linker script used for the build.
set(can_peripheral_trp_uart_default_LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/PIC32WM_BZ6204.ld")
set(can_peripheral_trp_uart_default_image_name "default.elf")
set(can_peripheral_trp_uart_default_image_base_name "default")

# The output directory of the final image.
set(can_peripheral_trp_uart_default_output_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../../out/can_peripheral_trp_uart")

# The full path to the final image.
set(can_peripheral_trp_uart_default_full_path_to_image ${can_peripheral_trp_uart_default_output_dir}/${can_peripheral_trp_uart_default_image_name})
