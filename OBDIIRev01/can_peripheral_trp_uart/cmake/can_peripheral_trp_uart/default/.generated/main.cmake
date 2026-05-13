include("${CMAKE_CURRENT_LIST_DIR}/rule.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/file.cmake")

set(can_peripheral_trp_uart_default_library_list )

# Handle files with suffix s, for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assemble)
add_library(can_peripheral_trp_uart_default_default_XC32_assemble OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assemble})
    can_peripheral_trp_uart_default_default_XC32_assemble_rule(can_peripheral_trp_uart_default_default_XC32_assemble)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_assemble>")

endif()

# Handle files with suffix S, for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assembleWithPreprocess)
add_library(can_peripheral_trp_uart_default_default_XC32_assembleWithPreprocess OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_assembleWithPreprocess})
    can_peripheral_trp_uart_default_default_XC32_assembleWithPreprocess_rule(can_peripheral_trp_uart_default_default_XC32_assembleWithPreprocess)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_assembleWithPreprocess>")

endif()

# Handle files with suffix [cC], for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile)
add_library(can_peripheral_trp_uart_default_default_XC32_compile OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile})
    can_peripheral_trp_uart_default_default_XC32_compile_rule(can_peripheral_trp_uart_default_default_XC32_compile)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_compile>")

endif()

# Handle files with suffix cpp, for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile_cpp)
add_library(can_peripheral_trp_uart_default_default_XC32_compile_cpp OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_compile_cpp})
    can_peripheral_trp_uart_default_default_XC32_compile_cpp_rule(can_peripheral_trp_uart_default_default_XC32_compile_cpp)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_compile_cpp>")

endif()

# Handle files with suffix [cC], for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_dependentObject)
add_library(can_peripheral_trp_uart_default_default_XC32_dependentObject OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_dependentObject})
    can_peripheral_trp_uart_default_default_XC32_dependentObject_rule(can_peripheral_trp_uart_default_default_XC32_dependentObject)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_dependentObject>")

endif()

# Handle files with suffix elf, for group default-XC32
if(can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_bin2hex)
add_library(can_peripheral_trp_uart_default_default_XC32_bin2hex OBJECT ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_bin2hex})
    can_peripheral_trp_uart_default_default_XC32_bin2hex_rule(can_peripheral_trp_uart_default_default_XC32_bin2hex)
    list(APPEND can_peripheral_trp_uart_default_library_list "$<TARGET_OBJECTS:can_peripheral_trp_uart_default_default_XC32_bin2hex>")

endif()


# Main target for this project
add_executable(can_peripheral_trp_uart_default_image__yHo8Ncw ${can_peripheral_trp_uart_default_library_list})

set_target_properties(can_peripheral_trp_uart_default_image__yHo8Ncw PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf"
    RUNTIME_OUTPUT_DIRECTORY "${can_peripheral_trp_uart_default_output_dir}")
target_link_libraries(can_peripheral_trp_uart_default_image__yHo8Ncw PRIVATE ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_link})

# Add the link options from the rule file.
can_peripheral_trp_uart_default_link_rule( can_peripheral_trp_uart_default_image__yHo8Ncw)

# Call bin2hex function from the rule file
can_peripheral_trp_uart_default_bin2hex_rule(can_peripheral_trp_uart_default_image__yHo8Ncw)

# The following step will be performed after each build if final image is rebuilt
add_custom_command(TARGET can_peripheral_trp_uart_default_Bin2Hex POST_BUILD
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\\scripts\\mplab-secureboot-sign.ps1 \"C:\\Users\\i66779\\.mchp_packs\\Microchip\\PIC32CX-BZ6_DFP\\1.3.38\" \"PIC32CX2051BZ62132\" d:\\CANOBD\\OBDII\\can_peripheral_trp_uart\\out\\can_peripheral_trp_uart\\default.elf d:\\CANOBD\\OBDII\\can_peripheral_trp_uart \"default\"
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../../../..)
