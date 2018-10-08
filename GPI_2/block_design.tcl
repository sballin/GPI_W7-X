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


# Use AXI Stream clock converter (ADC clock -> FPGA clock)
set intercon_idx 0
set idx [add_master_interface $intercon_idx]
cell xilinx.com:ip:axis_clock_converter:1.1 adc_clock_converter {
  TDATA_NUM_BYTES 4
} {
  s_axis_aresetn $rst_adc_clk_name/peripheral_aresetn
  m_axis_aresetn [set rst${intercon_idx}_name]/peripheral_aresetn
  s_axis_aclk $adc_clk
  m_axis_aclk [set ps_clk$intercon_idx]
}

# Add AXI stream FIFO to read pulse data from the PS
cell xilinx.com:ip:axi_fifo_mm_s:4.1 adc_axis_fifo {
  C_USE_TX_DATA 0
  C_USE_TX_CTRL 0
  C_USE_RX_CUT_THROUGH true
  C_RX_FIFO_DEPTH 32768
  C_RX_FIFO_PF_THRESHOLD 32760
} {
  s_axi_aclk [set ps_clk$intercon_idx]
  s_axi_aresetn [set rst${intercon_idx}_name]/peripheral_aresetn
  S_AXI [set interconnect_${intercon_idx}_name]/M${idx}_AXI
  AXI_STR_RXD adc_clock_converter/M_AXIS
}

assign_bd_address [get_bd_addr_segs adc_axis_fifo/S_AXI/Mem0]
set memory_segment  [get_bd_addr_segs /${::ps_name}/Data/SEG_adc_axis_fifo_Mem0]
set_property offset [get_memory_offset adc_fifo] $memory_segment
set_property range  [get_memory_range adc_fifo]  $memory_segment

################################### Make all the Blocks ################################################3
create_bd_cell -type ip -vlnv PSFC:user:data_collector:1.0 data_collector_0


##################################### Connected all the Blocks ######################################################

connect_bd_net [get_bd_pins data_collector_0/tdata] [get_bd_pins adc_clock_converter/s_axis_tdata]
connect_bd_net [get_bd_pins data_collector_0/tvalid] [get_bd_pins adc_clock_converter/s_axis_tvalid]
connect_bd_net [get_bd_pins data_collector_0/adc_clk] [get_bd_pins adc_dac/adc_clk]



# Connect ADC pins to pressure gauge status registers
connect_bd_net [get_bd_pins adc_dac/adc1] [get_bd_pins sts/abs_gauge] -boundary_type upper
connect_bd_net [get_bd_pins adc_dac/adc2] [get_bd_pins sts/diff_gauge] -boundary_type upper

# Add pins from extension connectors
create_bd_port -dir I W7X_permission_in
create_bd_port -dir I W7X_timings
create_bd_port -dir O -from 0 -to 0 slow_1_trigger
create_bd_port -dir O -from 0 -to 0 slow_2_trigger
create_bd_port -dir O -from 0 -to 0 slow_3_trigger
create_bd_port -dir O -from 0 -to 0 slow_4_trigger
create_bd_port -dir O -from 0 -to 0 fast_1_trigger
create_bd_port -dir O -from 0 -to 0 fast_1_permission_1
create_bd_port -dir O -from 0 -to 0 fast_1_duration_1
create_bd_port -dir O -from 0 -to 0 fast_1_permission_2
create_bd_port -dir O -from 0 -to 0 fast_1_duration_2
create_bd_port -dir O -from 0 -to 0 fast_2_trigger
create_bd_port -dir O -from 0 -to 0 fast_2_permission_1
create_bd_port -dir O -from 0 -to 0 fast_2_duration_1
create_bd_port -dir O -from 0 -to 0 fast_2_permission_2
create_bd_port -dir O -from 0 -to 0 fast_2_duration_2

# Add block which processes the outputs
create_bd_cell -type ip -vlnv PSFC:user:outputs:1.0 outputs_0

# Connect output pins
connect_bd_net [get_bd_pins adc_dac/adc_clk] [get_bd_pins outputs_0/adc_clk]
connect_bd_net [get_bd_pins ctl/GPI_safe_state] [get_bd_pins outputs_0/GPI_safe_state_ctl]
connect_bd_net [get_bd_pins ctl/slow_1_trigger] [get_bd_pins outputs_0/slow_1_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_2_trigger] [get_bd_pins outputs_0/slow_2_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_3_trigger] [get_bd_pins outputs_0/slow_3_trigger_ctl]
connect_bd_net [get_bd_pins ctl/slow_4_trigger] [get_bd_pins outputs_0/slow_4_trigger_ctl]
connect_bd_net [get_bd_ports W7X_permission_in] [get_bd_pins outputs_0/W7X_permission_out_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_trigger] [get_bd_pins outputs_0/fast_1_trigger_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_permission_1] [get_bd_pins outputs_0/fast_1_permission_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_duration_1] [get_bd_pins outputs_0/fast_1_duration_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_permission_2] [get_bd_pins outputs_0/fast_1_permission_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_1_duration_2] [get_bd_pins outputs_0/fast_1_duration_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_trigger] [get_bd_pins outputs_0/fast_2_trigger_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_permission_1] [get_bd_pins outputs_0/fast_2_permission_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_duration_1] [get_bd_pins outputs_0/fast_2_duration_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_permission_2] [get_bd_pins outputs_0/fast_2_permission_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_2_duration_2] [get_bd_pins outputs_0/fast_2_duration_2_ctl]

connect_bd_net [get_bd_ports slow_1_trigger] [get_bd_pins outputs_0/slow_1_trigger_pin]
connect_bd_net [get_bd_ports slow_2_trigger] [get_bd_pins outputs_0/slow_2_trigger_pin]
connect_bd_net [get_bd_ports slow_3_trigger] [get_bd_pins outputs_0/slow_3_trigger_pin]
connect_bd_net [get_bd_ports slow_4_trigger] [get_bd_pins outputs_0/slow_4_trigger_pin]
connect_bd_net [get_bd_ports fast_1_trigger] [get_bd_pins outputs_0/fast_1_trigger_pin]
connect_bd_net [get_bd_ports fast_1_permission_1] [get_bd_pins outputs_0/fast_1_permission_1_pin]
connect_bd_net [get_bd_ports fast_1_duration_1] [get_bd_pins outputs_0/fast_1_duration_1_pin]
connect_bd_net [get_bd_ports fast_1_permission_2] [get_bd_pins outputs_0/fast_1_permission_2_pin]
connect_bd_net [get_bd_ports fast_1_duration_2] [get_bd_pins outputs_0/fast_1_duration_2_pin]
connect_bd_net [get_bd_ports fast_2_trigger] [get_bd_pins outputs_0/fast_2_trigger_pin]
connect_bd_net [get_bd_ports fast_2_permission_1] [get_bd_pins outputs_0/fast_2_permission_1_pin]
connect_bd_net [get_bd_ports fast_2_duration_1] [get_bd_pins outputs_0/fast_2_duration_1_pin]
connect_bd_net [get_bd_ports fast_2_permission_2] [get_bd_pins outputs_0/fast_2_permission_2_pin]
connect_bd_net [get_bd_ports fast_2_duration_2] [get_bd_pins outputs_0/fast_2_duration_2_pin]

connect_bd_net [get_bd_pins outputs_0/GPI_safe_state_pin] [get_bd_pins adc_dac/dac1]
connect_bd_net [get_bd_pins outputs_0/W7X_permission_out_pin] [get_bd_pins adc_dac/dac2]

connect_bd_net [get_bd_ports W7X_timings] [get_bd_pins sts/W7X_timings]
connect_bd_net [get_bd_ports W7X_permission_in] [get_bd_pins sts/W7X_permission_in]

