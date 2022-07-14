# Adding all of the necessary pins from the extension connectors
# Reference: https://raw.githubusercontent.com/RedPitaya/RedPitaya/14cca62dd58f29826ee89f4b28901602f5cdb1d8/doc/developerGuide/pinConfig.rst

set_property IOSTANDARD LVCMOS33 [get_ports W7X_permission]
set_property IOSTANDARD LVCMOS33 [get_ports W7X_T1]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_1_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_2_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_3_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {slow_4_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_manual[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_3[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_permission_4[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_1[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_2[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_3[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {fast_puff_4[0]}]

set_property PACKAGE_PIN G17 [get_ports W7X_permission] 
set_property PACKAGE_PIN H16 [get_ports W7X_T1]             

set_property PACKAGE_PIN J18 [get_ports {slow_1_manual[0]}]
set_property PACKAGE_PIN K17 [get_ports {slow_2_manual[0]}]
set_property PACKAGE_PIN L14 [get_ports {slow_3_manual[0]}]
set_property PACKAGE_PIN L16 [get_ports {slow_4_manual[0]}]

# Fast valve circuit card 1
set_property PACKAGE_PIN G18 [get_ports {fast_manual[0]}]       
set_property PACKAGE_PIN H17 [get_ports {fast_permission_1[0]}] 
set_property PACKAGE_PIN K18 [get_ports {fast_permission_2[0]}] 
set_property PACKAGE_PIN H18 [get_ports {fast_puff_1[0]}]       
set_property PACKAGE_PIN L15 [get_ports {fast_puff_2[0]}]   

# Fast valve circuit card 2
#set_property PACKAGE_PIN L17 [get_ports {fast_manual[0]}]
set_property PACKAGE_PIN J16 [get_ports {fast_permission_3[0]}]
set_property PACKAGE_PIN M15 [get_ports {fast_puff_3[0]}]
set_property PACKAGE_PIN K16 [get_ports {fast_permission_4[0]}]
set_property PACKAGE_PIN M14 [get_ports {fast_puff_4[0]}]    

# Analog out
set_property IOSTANDARD LVCMOS18 [get_ports {dac_pwm_o[*]}]
set_property SLEW FAST [get_ports {dac_pwm_o[*]}]
set_property DRIVE 12 [get_ports {dac_pwm_o[*]}]
set_property PACKAGE_PIN T10 [get_ports {dac_pwm_o[0]}]
set_property PACKAGE_PIN T11 [get_ports {dac_pwm_o[1]}]
set_property PACKAGE_PIN P15 [get_ports {dac_pwm_o[2]}]
set_property PACKAGE_PIN U13 [get_ports {dac_pwm_o[3]}]

# XADC
set_property IOSTANDARD LVCMOS33 [get_ports Vp_Vn_v_p]
set_property IOSTANDARD LVCMOS33 [get_ports Vp_Vn_v_n]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux0_v_p]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux0_v_n]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux1_v_p]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux1_v_n]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux8_v_p]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux8_v_n]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux9_v_p]
set_property IOSTANDARD LVCMOS33 [get_ports Vaux9_v_n]
set_property PACKAGE_PIN K9  [get_ports Vp_Vn_v_p]
set_property PACKAGE_PIN L10 [get_ports Vp_Vn_v_n]
set_property PACKAGE_PIN C20 [get_ports Vaux0_v_p]
set_property PACKAGE_PIN B20 [get_ports Vaux0_v_n]
set_property PACKAGE_PIN E17 [get_ports Vaux1_v_p]
set_property PACKAGE_PIN D18 [get_ports Vaux1_v_n]
set_property PACKAGE_PIN B19 [get_ports Vaux8_v_p]
set_property PACKAGE_PIN A20 [get_ports Vaux8_v_n]
set_property PACKAGE_PIN E18 [get_ports Vaux9_v_p]
set_property PACKAGE_PIN E19 [get_ports Vaux9_v_n]
