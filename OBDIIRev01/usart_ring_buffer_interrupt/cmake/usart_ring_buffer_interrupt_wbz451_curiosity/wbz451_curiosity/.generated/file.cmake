# The following variables contains the files used by the different stages of the build process.
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assemble)
set_source_files_properties(${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assemble} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assemble})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assembleWithPreprocess)
set_source_files_properties(${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assembleWithPreprocess} PROPERTIES LANGUAGE ASM)

# For assembly files, add "." to the include path for each file so that .include with a relative path works
foreach(source_file ${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_assembleWithPreprocess})
        set_source_files_properties(${source_file} PROPERTIES INCLUDE_DIRECTORIES "$<PATH:NORMAL_PATH,$<PATH:REMOVE_FILENAME,${source_file}>>")
endforeach()

set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_compile
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/exceptions.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/initialization.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/interrupts.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/libc_syscalls.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/clk/plib_clk.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/cmcc/plib_cmcc.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/evsys/plib_evsys.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/gpio/plib_gpio.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/nvic/plib_nvic.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/peripheral/sercom/usart/plib_sercom1_usart.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/startup_xc32.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/stdio/xc32_monitor.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/main.c")
set_source_files_properties(${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_compile} PROPERTIES LANGUAGE C)
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_compile_cpp)
set_source_files_properties(${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_compile_cpp} PROPERTIES LANGUAGE CXX)
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_wbz451_curiosity_XC32_FILE_TYPE_link)

# The linker script used for the build.
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/../../../firmware/src/config/wbz451_curiosity/WBZ451.ld")
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_image_name "wbz451_curiosity.elf")
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_image_base_name "wbz451_curiosity")

# The output directory of the final image.
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_output_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../../out/usart_ring_buffer_interrupt_wbz451_curiosity")

# The full path to the final image.
set(usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_full_path_to_image ${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_output_dir}/${usart_ring_buffer_interrupt_wbz451_curiosity_wbz451_curiosity_image_name})
