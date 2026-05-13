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


# Main target for this project
add_executable(can_peripheral_trp_uart_default_image_wokfOG92 ${can_peripheral_trp_uart_default_library_list})

set_target_properties(can_peripheral_trp_uart_default_image_wokfOG92 PROPERTIES
    OUTPUT_NAME "default"
    SUFFIX ".elf"
    RUNTIME_OUTPUT_DIRECTORY "${can_peripheral_trp_uart_default_output_dir}")
target_link_libraries(can_peripheral_trp_uart_default_image_wokfOG92 PRIVATE ${can_peripheral_trp_uart_default_default_XC32_FILE_TYPE_link})

# Add the link options from the rule file.
can_peripheral_trp_uart_default_link_rule( can_peripheral_trp_uart_default_image_wokfOG92)

# Add bin2hex target for converting built file to a .hex file.
string(REGEX REPLACE [.]elf$ .hex can_peripheral_trp_uart_default_image_name_hex ${can_peripheral_trp_uart_default_image_name})
add_custom_target(can_peripheral_trp_uart_default_Bin2Hex ALL
    COMMAND ${MP_BIN2HEX} \"${can_peripheral_trp_uart_default_output_dir}/${can_peripheral_trp_uart_default_image_name}\"
    BYPRODUCTS ${can_peripheral_trp_uart_default_output_dir}/${can_peripheral_trp_uart_default_image_name_hex}
    COMMENT "Convert built file to .hex")
add_dependencies(can_peripheral_trp_uart_default_Bin2Hex can_peripheral_trp_uart_default_image_wokfOG92)



# The following step will be performed after each build if final image is rebuilt
add_custom_command(TARGET can_peripheral_trp_uart_default_Bin2Hex POST_BUILD
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\\scripts\\mplab-secureboot-sign.ps1 \"C:\\Users\\I41802\\.mchp_packs\\Microchip\\PIC32CX-BZ6_DFP\\1.3.38\" \"PIC32WM_BZ6204\" \"d:\\CAN BLE\\OBDII\\can_peripheral_trp_uart\\out\\can_peripheral_trp_uart\\default.elf\" \"d:\\CAN BLE\\OBDII\\can_peripheral_trp_uart\" \"default\"
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../../../..)
