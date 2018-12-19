source $board_path/config/ports.tcl

# Add PS and AXI Interconnect
set board_preset $board_path/config/board_preset.tcl
source $sdk_path/fpga/lib/starting_point.tcl

# Add ADCs and DACs
source $sdk_path/fpga/lib/redp_adc_dac.tcl
set adc_dac_name adc_dac
add_redp_adc_dac $adc_dac_name

# Rename clocks
set adc_clk $adc_dac_name/adc_clk

# Add processor system reset synchronous to adc clock
set rst_adc_clk_name proc_sys_reset_adc_clk
cell xilinx.com:ip:proc_sys_reset:5.0 $rst_adc_clk_name {} {
  ext_reset_in $ps_name/FCLK_RESET0_N
  slowest_sync_clk $adc_clk
}

# Add config and status registers
source $sdk_path/fpga/lib/ctl_sts.tcl
add_ctl_sts $adc_clk $rst_adc_clk_name/peripheral_aresetn

# Connect LEDs
connect_port_pin led_o [get_slice_pin [ctl_pin led] 7 0]

# Connect ADC to status register
for {set i 0} {$i < [get_parameter n_adc]} {incr i} {
  connect_pins [sts_pin adc$i] adc_dac/adc[expr $i + 1]
}

## Add DAC controller
#source $sdk_path/fpga/lib/bram.tcl
#set dac_bram_name [add_bram dac]

#connect_pins adc_dac/dac1 [get_slice_pin $dac_bram_name/doutb 13 0]
#connect_pins adc_dac/dac2 [get_slice_pin $dac_bram_name/doutb 29 16]

#connect_cell $dac_bram_name {
#  web  [get_constant_pin 0 4]
#  dinb [get_constant_pin 0 32]
#  clkb $adc_clk
 # rstb $rst_adc_clk_name/peripheral_reset
#}


# # Use AXI Stream clock converter (ADC clock -> FPGA clock)
# set intercon_idx 0
# set idx [add_master_interface $intercon_idx]
# cell xilinx.com:ip:axis_clock_converter:1.1 adc_clock_converter {
#   TDATA_NUM_BYTES 4
# } {
#   s_axis_aresetn $rst_adc_clk_name/peripheral_aresetn
#   m_axis_aresetn [set rst${intercon_idx}_name]/peripheral_aresetn
#   s_axis_aclk $adc_clk
#   m_axis_aclk [set ps_clk$intercon_idx]
# }

# # Add AXI stream FIFO to read pulse data from the PS
# cell xilinx.com:ip:axi_fifo_mm_s:4.1 adc_axis_fifo {
#   C_USE_TX_DATA 0
#   C_USE_TX_CTRL 0
#   C_USE_RX_CUT_THROUGH true
#   C_RX_FIFO_DEPTH 32768
#   C_RX_FIFO_PF_THRESHOLD 32760
# } {
#   s_axi_aclk [set ps_clk$intercon_idx]
#   s_axi_aresetn [set rst${intercon_idx}_name]/peripheral_aresetn
#   S_AXI [set interconnect_${intercon_idx}_name]/M${idx}_AXI
#   AXI_STR_RXD adc_clock_converter/M_AXIS
# }

# assign_bd_address [get_bd_addr_segs adc_axis_fifo/S_AXI/Mem0]
# set memory_segment  [get_bd_addr_segs /${::ps_name}/Data/SEG_adc_axis_fifo_Mem0]
# set_property offset [get_memory_offset adc_fifo] $memory_segment
# set_property range  [get_memory_range adc_fifo]  $memory_segment

################################### Make all the Blocks ################################################3
create_bd_cell -type ip -vlnv PSFC:user:trig_delay:1.0 trig_delay_0
create_bd_cell -type ip -vlnv PSFC:user:outputs:1.0 outputs_0
create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 Trigger_1
create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 Trigger_2
create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 Fast_trigger
create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 Master_trigger
##################################### Connected all the Blocks ######################################################


# Connect ADC pins to pressure gauge status registers
connect_bd_net [get_bd_pins adc_dac/adc1] [get_bd_pins sts/abs_gauge] -boundary_type upper
connect_bd_net [get_bd_pins adc_dac/adc2] [get_bd_pins sts/diff_gauge] -boundary_type upper


# Add pins from extension connectors
create_bd_port -dir I W7X_timings
create_bd_port -dir O -from 0 -to 0 slow_1_trigger
create_bd_port -dir O -from 0 -to 0 slow_2_trigger
create_bd_port -dir O -from 0 -to 0 slow_3_trigger
create_bd_port -dir O -from 0 -to 0 slow_4_trigger
create_bd_port -dir O -from 0 -to 0 fast_trigger


# Connect output pins
connect_bd_net [get_bd_pins outputs_0/adc_clk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_ports W7X_timings] [get_bd_pins sts/W7X_timings]
connect_bd_net [get_bd_pins ctl/slow_1_trigger] [get_bd_pins outputs_0/slow_1_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_2_trigger] [get_bd_pins outputs_0/slow_2_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_3_trigger] [get_bd_pins outputs_0/slow_3_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_4_trigger] [get_bd_pins outputs_0/slow_4_trigger_ctl]
connect_bd_net [get_bd_ports slow_1_trigger] [get_bd_pins outputs_0/slow_1_trigger_pin]
connect_bd_net [get_bd_ports slow_2_trigger] [get_bd_pins outputs_0/slow_2_trigger_pin]
connect_bd_net [get_bd_ports slow_3_trigger] [get_bd_pins outputs_0/slow_3_trigger_pin]
connect_bd_net [get_bd_ports slow_4_trigger] [get_bd_pins outputs_0/slow_4_trigger_pin]
connect_bd_net [get_bd_pins ctl/fast_1_permission] [get_bd_pins outputs_0/fast_1_permission_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_permission] [get_bd_pins outputs_0/fast_2_permission_ctl]
connect_bd_net [get_bd_pins ctl/GPI_safe_state] [get_bd_pins outputs_0/GPI_safe_state_ctl]

#Connect pins to the trig delay block
connect_bd_net [get_bd_ports W7X_timings] [get_bd_pins trig_delay_0/W7X_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_trigger] [get_bd_pins trig_delay_0/trigger_1_delay]
connect_bd_net [get_bd_pins ctl/fast_2_trigger] [get_bd_pins trig_delay_0/trigger_2_delay]
connect_bd_net [get_bd_pins ctl/fast_1_duration] [get_bd_pins trig_delay_0/trigger_1_duration]
connect_bd_net [get_bd_pins ctl/fast_2_duration] [get_bd_pins trig_delay_0/trigger_2_duration]
connect_bd_net [get_bd_pins ctl/reset_time] [get_bd_pins trig_delay_0/reset_trig_time]
connect_bd_net [get_bd_pins trig_delay_0/adc_clk] [get_bd_pins adc_dac/adc_clk]

#Configuring permission logics
set_property -dict [list CONFIG.C_SIZE {1}] [get_bd_cells Trigger_1]
set_property -dict [list CONFIG.C_SIZE {1}] [get_bd_cells Trigger_2]
connect_bd_net [get_bd_pins trig_delay_0/trigger_1_out] [get_bd_pins Trigger_1/Op1]
connect_bd_net [get_bd_pins trig_delay_0/trigger_2_out] [get_bd_pins Trigger_2/Op1]
set_property -dict [list CONFIG.C_OPERATION {or} CONFIG.LOGO_FILE {data/sym_orgate.png}] [get_bd_cells Fast_trigger]
set_property -dict [list CONFIG.C_SIZE {1}] [get_bd_cells Fast_trigger]
connect_bd_net [get_bd_pins Trigger_2/Res] [get_bd_pins Fast_trigger/Op1]
connect_bd_net [get_bd_pins Trigger_1/Res] [get_bd_pins Fast_trigger/Op2]
connect_bd_net [get_bd_pins outputs_0/fast_1_permission] [get_bd_pins Trigger_1/Op2]
connect_bd_net [get_bd_pins outputs_0/fast_2_permission] [get_bd_pins Trigger_2/Op2]
connect_bd_net [get_bd_pins outputs_0/GPI_safe_state_pin] [get_bd_pins Master_trigger/Op1]
connect_bd_net [get_bd_pins Fast_trigger/Res] [get_bd_pins Master_trigger/Op2]
connect_bd_net [get_bd_ports fast_trigger] [get_bd_pins Master_trigger/Res]
set_property -dict [list CONFIG.C_SIZE {1}] [get_bd_cells Master_trigger]

#Connect sts and ctr for the slow triggers
connect_bd_net [get_bd_pins ctl/slow_1_trigger] [get_bd_pins sts/slow_1_trigger_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_2_trigger] [get_bd_pins sts/slow_2_trigger_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_3_trigger] [get_bd_pins sts/slow_3_trigger_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_4_trigger] [get_bd_pins sts/slow_4_trigger_sts] -boundary_type upper
