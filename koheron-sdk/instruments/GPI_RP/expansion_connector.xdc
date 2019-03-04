### Adding all of the necessary pins from the extension connectors

set_property IOSTANDARD LVCMOS33 [get_ports W7X_permission]
set_property IOSTANDARD LVCMOS33 [get_ports W7X_T1]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_1_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_2_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_3_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_4_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_2[0]}]


set_property PACKAGE_PIN G17 [get_ports W7X_permission] 
set_property PACKAGE_PIN H16 [get_ports W7X_T1]             

set_property PACKAGE_PIN J18 [get_ports {slow_1_manual[0]}]
set_property PACKAGE_PIN K17 [get_ports {slow_2_manual[0]}]
set_property PACKAGE_PIN L14 [get_ports {slow_3_manual[0]}]
set_property PACKAGE_PIN L16 [get_ports {slow_4_manual[0]}]

set_property PACKAGE_PIN G18 [get_ports {fast_manual[0]}]       
set_property PACKAGE_PIN H17 [get_ports {fast_permission_1[0]}] 
set_property PACKAGE_PIN H18 [get_ports {fast_puff_1[0]}]       
set_property PACKAGE_PIN K18 [get_ports {fast_permission_2[0]}] 
set_property PACKAGE_PIN L15 [get_ports {fast_puff_2[0]}]       

# Fast valve circuit card 2
#set_property PACKAGE_PIN L17 [get_ports {fast_manual[0]}]
#set_property PACKAGE_PIN J16 [get_ports {fast_permission_1[0]}]
#set_property PACKAGE_PIN M15 [get_ports {fast_puff_1[0]}]
#set_property PACKAGE_PIN K16 [get_ports {fast_permission_2[0]}]
#set_property PACKAGE_PIN M14 [get_ports {fast_puff_2[0]}]
