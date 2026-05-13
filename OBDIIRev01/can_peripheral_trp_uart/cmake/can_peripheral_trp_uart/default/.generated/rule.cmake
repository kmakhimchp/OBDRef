# The following functions contains all the flags passed to the different build stages.

set(PACK_REPO_PATH "C:/Users/i66779/.mchp_packs" CACHE PATH "Path to the root of a pack repository.")

function(can_peripheral_trp_uart_default_default_XC32_assemble_rule target)
    set(options
        "-g"
        "${ASSEMBLER_PRE}"
        "-mprocessor=32CX2051BZ62132"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,--gdwarf-2,-I${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target} PRIVATE "__DEBUG=1")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X")
endfunction()
function(can_peripheral_trp_uart_default_default_XC32_assembleWithPreprocess_rule target)
    set(options
        "-x"
        "assembler-with-cpp"
        "-g"
        "${MP_EXTRA_AS_PRE}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132"
        "-mprocessor=32CX2051BZ62132"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--gdwarf-2,--defsym=__DEBUG=1,-I${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG=1"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X")
endfunction()
function(can_peripheral_trp_uart_default_default_XC32_compile_rule target)
    set(options
        "-g"
        "${CC_PRE}"
        "-x"
        "c"
        "-c"
        "-mprocessor=32CX2051BZ62132"
        "-ffunction-sections"
        "-fdata-sections"
        "-O1"
        "-fcommon"
        "-Wall"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/app_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/lib/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/middleware_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/profile_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/ble/service_ble"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default/driver/pds/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/PIC32WM_BZ6204_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X"
        PRIVATE "${PACK_REPO_PATH}/ARM/CMSIS/6.2.0/CMSIS/Core/Include")
endfunction()
function(can_peripheral_trp_uart_default_default_XC32_compile_cpp_rule target)
    set(options
        "-g"
        "${CC_PRE}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mprocessor=32CX2051BZ62132"
        "-frtti"
        "-fexceptions"
        "-fno-check-new"
        "-fenforce-eh-specs"
        "-ffunction-sections"
        "-O1"
        "-fno-common"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_default=default")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/default"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/PIC32WM_BZ6204_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/third_party/rtos/FreeRTOS/Source/portable/GCC/SAM/ARM_CM4F"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X"
        PRIVATE "${PACK_REPO_PATH}/ARM/CMSIS/6.2.0/CMSIS/Core/Include")
endfunction()
function(can_peripheral_trp_uart_default_dependentObject_rule target)
    set(options
        "-mprocessor=32CX2051BZ62132"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
endfunction()
function(can_peripheral_trp_uart_default_link_rule target)
    set(options
        "-g"
        "${MP_EXTRA_LD_PRE}"
        "${DEBUGGER_OPTION_TO_LINKER}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mprocessor=32CX2051BZ62132"
        "-mno-device-startup-code"
        "-Wl,--defsym=__MPLAB_BUILD=1${MP_EXTRA_LD_POST},--script=${can_peripheral_trp_uart_default_LINKER_SCRIPT},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,--defsym=_min_heap_size=512,--gc-sections,-L${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/can_peripheral_trp_uart.X,-Map=mem.map,--memorysummary,memoryfile.xml"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ6_DFP/1.3.38/PIC32CX2051BZ62132")
    list(REMOVE_ITEM options "")
    target_link_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target} PRIVATE "XPRJ_default=default")
endfunction()
function(can_peripheral_trp_uart_default_bin2hex_rule target)
    add_custom_target(
        can_peripheral_trp_uart_default_Bin2Hex ALL
        COMMAND ${MP_BIN2HEX} ${can_peripheral_trp_uart_default_image_name}
        WORKING_DIRECTORY ${can_peripheral_trp_uart_default_output_dir}
        BYPRODUCTS "${can_peripheral_trp_uart_default_output_dir}/${can_peripheral_trp_uart_default_image_base_name}.hex"
        COMMENT "Convert build file to .hex")
    add_dependencies(can_peripheral_trp_uart_default_Bin2Hex ${target})
endfunction()
