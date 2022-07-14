source $board_path/config/ports.tcl

# Add PS and AXI Interconnect
set board_preset $board_path/config/board_preset.tcl
source $sdk_path/fpga/lib/starting_point.tcl

# Add ADCs and DACs
source $sdk_path/fpga/lib/redp_adc_dac.tcl
set adc_dac_name adc_dac
add_redp_adc_dac $adc_dac_name

# Add XADC wizard for analog inputs on E2
create_bd_cell -type ip -vlnv xilinx.com:ip:xadc_wiz:3.3 xadc_wiz_0
set_property -dict [list CONFIG.SINGLE_CHANNEL_SELECTION {VAUXP8_VAUXN8} CONFIG.ENABLE_AXI4STREAM {true} CONFIG.DCLK_FREQUENCY {125} CONFIG.ADC_CONVERSION_RATE {1000} CONFIG.XADC_STARUP_SELECTION {channel_sequencer} CONFIG.CHANNEL_ENABLE_VP_VN {false} CONFIG.CHANNEL_ENABLE_VAUXP0_VAUXN0 {true} CONFIG.CHANNEL_ENABLE_VAUXP8_VAUXN8 {true} CONFIG.SEQUENCER_MODE {Continuous} CONFIG.EXTERNAL_MUX_CHANNEL {VP_VN}] [get_bd_cells xadc_wiz_0]
# Add clock converter for XADC
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_clock_converter:2.1 axi_clock_converter_0

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

# Connect analog out with slice
connect_port_pin dac_pwm_o [get_slice_pin [ctl_pin analog_out] 3 0]

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
  C_RX_FIFO_PF_THRESHOLD 32763
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
create_bd_cell -type ip -vlnv PSFC:user:trig_delay:1.0 trig_delay_0
create_bd_cell -type ip -vlnv PSFC:user:outputs:1.0 outputs_0
create_bd_cell -type ip -vlnv PSFC:user:split:1.0 split_0
##################################### Connected all the Blocks ######################################################

# Connect ADC pins to pressure gauge status registers
connect_bd_net [get_bd_pins adc_dac/adc1] [get_bd_pins sts/abs_gauge] -boundary_type upper
connect_bd_net [get_bd_pins adc_dac/adc2] [get_bd_pins sts/diff_gauge] -boundary_type upper

# Add pins from extension connectors
create_bd_port -dir I W7X_T1
create_bd_port -dir I W7X_permission
create_bd_port -dir O -from 0 -to 0 slow_1_manual
create_bd_port -dir O -from 0 -to 0 slow_2_manual
create_bd_port -dir O -from 0 -to 0 slow_3_manual
create_bd_port -dir O -from 0 -to 0 slow_4_manual
create_bd_port -dir O -from 0 -to 0 fast_manual
create_bd_port -dir O -from 0 -to 0 fast_permission_1
create_bd_port -dir O -from 0 -to 0 fast_permission_2
create_bd_port -dir O -from 0 -to 0 fast_permission_3
create_bd_port -dir O -from 0 -to 0 fast_permission_4
create_bd_port -dir O -from 0 -to 0 fast_puff_1
create_bd_port -dir O -from 0 -to 0 fast_puff_2
create_bd_port -dir O -from 0 -to 0 fast_puff_3
create_bd_port -dir O -from 0 -to 0 fast_puff_4

# Connect to clock
connect_bd_net [get_bd_pins outputs_0/adc_clk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_pins trig_delay_0/adc_clk] [get_bd_pins adc_dac/adc_clk]

# Connect input ports
connect_bd_net [get_bd_ports W7X_permission] [get_bd_pins sts/W7X_permission]

# XADC and clock converter connections (AI0,1,2,3=Vaux8,0,1,9)
connect_bd_intf_net [get_bd_intf_ports Vaux8] [get_bd_intf_pins xadc_wiz_0/Vaux8]
connect_bd_intf_net [get_bd_intf_ports Vaux0] [get_bd_intf_pins xadc_wiz_0/Vaux0]
connect_bd_intf_net [get_bd_intf_ports Vp_Vn] [get_bd_intf_pins xadc_wiz_0/Vp_Vn]
set_property -dict [list CONFIG.NUM_MI {4}] [get_bd_cells axi_mem_intercon_0]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_mem_intercon_0/M03_AXI] [get_bd_intf_pins axi_clock_converter_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_clock_converter_0/M_AXI] [get_bd_intf_pins xadc_wiz_0/s_axi_lite]
connect_bd_net [get_bd_pins axi_clock_converter_0/s_axi_aclk] [get_bd_pins ps_0/FCLK_CLK0]
connect_bd_net [get_bd_pins axi_clock_converter_0/s_axi_aresetn] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
connect_bd_net [get_bd_pins axi_clock_converter_0/m_axi_aclk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_pins axi_clock_converter_0/m_axi_aresetn] [get_bd_pins proc_sys_reset_adc_clk/peripheral_aresetn]
connect_bd_net [get_bd_pins xadc_wiz_0/s_axis_aclk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_pins xadc_wiz_0/s_axi_aclk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_pins xadc_wiz_0/s_axi_aresetn] [get_bd_pins proc_sys_reset_adc_clk/peripheral_aresetn]
connect_bd_net [get_bd_pins axi_mem_intercon_0/M03_ACLK] [get_bd_pins ps_0/FCLK_CLK0]
connect_bd_net [get_bd_pins axi_mem_intercon_0/M03_ARESETN] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
connect_bd_net [get_bd_pins xadc_wiz_0/m_axis_tdata] [get_bd_pins split_0/xadc_data]
connect_bd_net [get_bd_pins xadc_wiz_0/m_axis_tid] [get_bd_pins split_0/xadc_channel]
connect_bd_net [get_bd_pins adc_dac/adc_clk] [get_bd_pins split_0/clk]
connect_bd_net [get_bd_pins split_0/analog_input_0] [get_bd_pins sts/analog_input_0]
connect_bd_net [get_bd_pins split_0/analog_input_1] [get_bd_pins sts/analog_input_1]

# Connect to status block
connect_bd_net [get_bd_pins ctl/slow_1_manual] [get_bd_pins sts/slow_1_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_2_manual] [get_bd_pins sts/slow_2_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_3_manual] [get_bd_pins sts/slow_3_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/slow_4_manual] [get_bd_pins sts/slow_4_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/fast_manual] [get_bd_pins sts/fast_sts] -boundary_type upper
connect_bd_net [get_bd_pins ctl/analog_out] [get_bd_pins sts/analog_out_sts] -boundary_type upper
connect_bd_net [get_bd_pins trig_delay_0/w7x_t1_out] [get_bd_pins sts/W7X_T1]

# Connect to outputs block
connect_bd_net [get_bd_pins ctl/slow_1_manual] [get_bd_pins outputs_0/slow_1_manual_ctl]
connect_bd_net [get_bd_pins ctl/slow_2_manual] [get_bd_pins outputs_0/slow_2_manual_ctl]
connect_bd_net [get_bd_pins ctl/slow_3_manual] [get_bd_pins outputs_0/slow_3_manual_ctl]
connect_bd_net [get_bd_pins ctl/slow_4_manual] [get_bd_pins outputs_0/slow_4_manual_ctl]
connect_bd_net [get_bd_pins ctl/GPI_safe_state] [get_bd_pins outputs_0/GPI_safe_state_ctl]
connect_bd_net [get_bd_pins ctl/fast_permission_1] [get_bd_pins outputs_0/fast_permission_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_permission_2] [get_bd_pins outputs_0/fast_permission_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_permission_3] [get_bd_pins outputs_0/fast_permission_3_ctl]
connect_bd_net [get_bd_pins ctl/fast_permission_4] [get_bd_pins outputs_0/fast_permission_4_ctl]
connect_bd_net [get_bd_pins ctl/fast_manual] [get_bd_pins outputs_0/fast_manual_ctl]

# Connect to trig delay block
connect_bd_net [get_bd_pins ctl/fast_delay_1] [get_bd_pins trig_delay_0/fast_delay_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_delay_2] [get_bd_pins trig_delay_0/fast_delay_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_delay_3] [get_bd_pins trig_delay_0/fast_delay_3_ctl]
connect_bd_net [get_bd_pins ctl/fast_delay_4] [get_bd_pins trig_delay_0/fast_delay_4_ctl]
connect_bd_net [get_bd_pins ctl/fast_duration_1] [get_bd_pins trig_delay_0/fast_duration_1_ctl]
connect_bd_net [get_bd_pins ctl/fast_duration_2] [get_bd_pins trig_delay_0/fast_duration_2_ctl]
connect_bd_net [get_bd_pins ctl/fast_duration_3] [get_bd_pins trig_delay_0/fast_duration_3_ctl]
connect_bd_net [get_bd_pins ctl/fast_duration_4] [get_bd_pins trig_delay_0/fast_duration_4_ctl]
connect_bd_net [get_bd_pins ctl/reset_time] [get_bd_pins trig_delay_0/reset_time_ctl]
connect_bd_net [get_bd_ports W7X_T1] [get_bd_pins trig_delay_0/w7x_t1_hw]
connect_bd_net [get_bd_pins ctl/send_T1] [get_bd_pins trig_delay_0/w7x_t1_ctl]

# FIFO-required connections
connect_bd_net [get_bd_pins data_collector_0/adc_clk] [get_bd_pins adc_dac/adc_clk]
connect_bd_net [get_bd_pins adc_clock_converter/s_axis_tvalid] [get_bd_pins data_collector_0/tvalid]
connect_bd_net [get_bd_pins adc_clock_converter/s_axis_tdata] [get_bd_pins data_collector_0/tdata]
connect_bd_net [get_bd_pins data_collector_0/abs_gauge] [get_bd_pins adc_dac/adc1]
connect_bd_net [get_bd_pins data_collector_0/diff_gauge] [get_bd_pins adc_dac/adc2]

# Connect output ports
connect_bd_net [get_bd_ports slow_1_manual] [get_bd_pins outputs_0/slow_1_manual_pin]
connect_bd_net [get_bd_ports slow_2_manual] [get_bd_pins outputs_0/slow_2_manual_pin]
connect_bd_net [get_bd_ports slow_3_manual] [get_bd_pins outputs_0/slow_3_manual_pin]
connect_bd_net [get_bd_ports slow_4_manual] [get_bd_pins outputs_0/slow_4_manual_pin]
connect_bd_net [get_bd_ports fast_puff_1] [get_bd_pins trig_delay_0/fast_puff_1_pin]
connect_bd_net [get_bd_ports fast_puff_2] [get_bd_pins trig_delay_0/fast_puff_2_pin]
connect_bd_net [get_bd_ports fast_puff_3] [get_bd_pins trig_delay_0/fast_puff_3_pin]
connect_bd_net [get_bd_ports fast_puff_4] [get_bd_pins trig_delay_0/fast_puff_4_pin]
connect_bd_net [get_bd_ports fast_manual] [get_bd_pins outputs_0/fast_manual_pin]

connect_bd_net [get_bd_ports fast_permission_1] [get_bd_pins outputs_0/fast_permission_1_pin]
connect_bd_net [get_bd_ports fast_permission_2] [get_bd_pins outputs_0/fast_permission_2_pin]
connect_bd_net [get_bd_ports fast_permission_3] [get_bd_pins outputs_0/fast_permission_3_pin]
connect_bd_net [get_bd_ports fast_permission_4] [get_bd_pins outputs_0/fast_permission_4_pin]
