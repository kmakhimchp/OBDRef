# The following functions contains all the flags passed to the different build stages.

set(PACK_REPO_PATH "C:/Users/I41802/.mchp_packs" CACHE PATH "Path to the root of a pack repository.")

function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_assemble_rule target)
    set(options
        "-g"
        "${ASSEMBLER_PRE}"
        "-mprocessor=WBZ451"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1"
        "-g,-I${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target} PRIVATE "__DEBUG=1")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X")
endfunction()
function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_assembleWithPreprocess_rule target)
    set(options
        "-x"
        "assembler-with-cpp"
        "-g"
        "${MP_EXTRA_AS_PRE}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451"
        "-mprocessor=WBZ451"
        "-Wa,--defsym=__MPLAB_BUILD=1${MP_EXTRA_AS_POST},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,-I${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_wbz451_curiosity=wbz451_curiosity")
    target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X")
endfunction()
function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_compile_rule target)
    set(options
        "-g"
        "${CC_PRE}"
        "-x"
        "c"
        "-c"
        "-mprocessor=WBZ451"
        "-ffunction-sections"
        "-O1"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_wbz451_curiosity=wbz451_curiosity")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/WBZ451_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X"
        PRIVATE "${PACK_REPO_PATH}/ARM/CMSIS/5.9.0/CMSIS/Core/Include")
endfunction()
function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_compile_cpp_rule target)
    set(options
        "-g"
        "${CC_PRE}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mprocessor=WBZ451"
        "-frtti"
        "-fexceptions"
        "-fno-check-new"
        "-fenforce-eh-specs"
        "-ffunction-sections"
        "-O1"
        "-fno-common"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target}
        PRIVATE "__DEBUG"
        PRIVATE "XPRJ_wbz451_curiosity=wbz451_curiosity")
    target_include_directories(${target}
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/CMSIS/CMSIS/Core/Include"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/packs/WBZ451_DFP"
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X"
        PRIVATE "${PACK_REPO_PATH}/ARM/CMSIS/5.9.0/CMSIS/Core/Include")
endfunction()
function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_dependentObject_rule target)
    set(options
        "-mprocessor=WBZ451"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451")
    list(REMOVE_ITEM options "")
    target_compile_options(${target} PRIVATE "${options}")
endfunction()
function(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_link_rule target)
    set(options
        "-g"
        "${MP_EXTRA_LD_PRE}"
        "${DEBUGGER_OPTION_TO_LINKER}"
        "${DEBUGGER_NAME_AS_MACRO}"
        "-mprocessor=WBZ451"
        "-mno-device-startup-code"
        "-Wl,--defsym=__MPLAB_BUILD=1${MP_EXTRA_LD_POST},--script=${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_LINKER_SCRIPT},--defsym=__MPLAB_DEBUG=1,--defsym=__DEBUG=1,--defsym=_min_heap_size=512,--gc-sections,-L${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/wbz451_curiosity.X,-Map=mem.map,-DVECTOR_REGION=boot_rom,--memorysummary,memoryfile.xml"
        "-mdfp=${PACK_REPO_PATH}/Microchip/PIC32CX-BZ_DFP/1.4.243/WBZ451")
    list(REMOVE_ITEM options "")
    target_link_options(${target} PRIVATE "${options}")
    target_compile_definitions(${target} PRIVATE "XPRJ_wbz451_curiosity=wbz451_curiosity")
endfunction()
