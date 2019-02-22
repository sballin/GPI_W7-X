### Adding all of the necessary pins from the extension connectors


set_property IOSTANDARD LVCMOS33 [get_ports W7X_permission_in]
set_property IOSTANDARD LVCMOS33 [get_ports W7X_timings]

set_property PACKAGE_PIN G17 [get_ports W7X_permission_in]
set_property PACKAGE_PIN H16 [get_ports W7X_timings]


set_property IOSTANDARD LVCMOS33 [get_ports {slow_1_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_2_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_3_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_4_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_1_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_1_permission_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_1_duration_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_1_permission_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_1_duration_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_2_trigger[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_2_permission_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_2_duration_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_2_permission_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_2_duration_2[0]}]

set_property PACKAGE_PIN J18 [get_ports {slow_1_trigger[0]}]
set_property PACKAGE_PIN K17 [get_ports {slow_2_trigger[0]}]
set_property PACKAGE_PIN L14 [get_ports {slow_3_trigger[0]}]
set_property PACKAGE_PIN L16 [get_ports {slow_4_trigger[0]}]
set_property PACKAGE_PIN G18 [get_ports {fast_1_trigger[0]}]
set_property PACKAGE_PIN H17 [get_ports {fast_1_permission_1[0]}]
set_property PACKAGE_PIN H18 [get_ports {fast_1_duration_1[0]}]
set_property PACKAGE_PIN K18 [get_ports {fast_1_permission_2[0]}]
set_property PACKAGE_PIN L15 [get_ports {fast_1_duration_2[0]}]
set_property PACKAGE_PIN L17 [get_ports {fast_2_trigger[0]}]
set_property PACKAGE_PIN J16 [get_ports {fast_2_permission_1[0]}]
set_property PACKAGE_PIN M15 [get_ports {fast_2_duration_1[0]}]
set_property PACKAGE_PIN K16 [get_ports {fast_2_permission_2[0]}]
set_property PACKAGE_PIN M14 [get_ports {fast_2_duration_2[0]}]
