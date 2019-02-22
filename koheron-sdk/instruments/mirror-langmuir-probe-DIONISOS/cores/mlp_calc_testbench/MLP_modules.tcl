
################################################################
# This is a generated script based on design: MLP_modules
#
# Though there are limitations about the generated script,
# the main purpose of this utility is to make learning
# IP Integrator Tcl commands easier.
################################################################

namespace eval _tcl {
proc get_script_folder {} {
   set script_path [file normalize [info script]]
   set script_folder [file dirname $script_path]
   return $script_folder
}
}
variable script_folder
set script_folder [_tcl::get_script_folder]

################################################################
# Check if script is running in correct Vivado version.
################################################################
set scripts_vivado_version 2017.4
set current_vivado_version [version -short]

if { [string first $scripts_vivado_version $current_vivado_version] == -1 } {
   puts ""
   catch {common::send_msg_id "BD_TCL-109" "ERROR" "This script was generated using Vivado <$scripts_vivado_version> and is being run in <$current_vivado_version> of Vivado. Please run the script in Vivado <$scripts_vivado_version> then open the design in Vivado <$current_vivado_version>. Upgrade the design by running \"Tools => Report => Report IP Status...\", then run write_bd_tcl to create an updated script."}

   return 1
}

################################################################
# START
################################################################

# To test this script, run the following commands from Vivado Tcl console:
# source MLP_modules_script.tcl


# The design that will be created by this Tcl script contains the following 
# module references:
# SetVolts, CurRes, TempCalc, iSatCalc, vFloatCalc

# Please add the sources of those modules before sourcing this Tcl script.

# If there is no project opened, this script will create a
# project, but make sure you do not have an existing project
# <./myproj/project_1.xpr> in the current working folder.

set list_projs [get_projects -quiet]
if { $list_projs eq "" } {
   create_project project_1 myproj -part xc7z010clg400-1
}


# CHANGE DESIGN NAME HERE
variable design_name
set design_name MLP_modules

# If you do not already have an existing IP Integrator design open,
# you can create a design using the following command:
#    create_bd_design $design_name

# Creating design if needed
set errMsg ""
set nRet 0

set cur_design [current_bd_design -quiet]
set list_cells [get_bd_cells -quiet]

if { ${design_name} eq "" } {
   # USE CASES:
   #    1) Design_name not set

   set errMsg "Please set the variable <design_name> to a non-empty value."
   set nRet 1

} elseif { ${cur_design} ne "" && ${list_cells} eq "" } {
   # USE CASES:
   #    2): Current design opened AND is empty AND names same.
   #    3): Current design opened AND is empty AND names diff; design_name NOT in project.
   #    4): Current design opened AND is empty AND names diff; design_name exists in project.

   if { $cur_design ne $design_name } {
      common::send_msg_id "BD_TCL-001" "INFO" "Changing value of <design_name> from <$design_name> to <$cur_design> since current design is empty."
      set design_name [get_property NAME $cur_design]
   }
   common::send_msg_id "BD_TCL-002" "INFO" "Constructing design in IPI design <$cur_design>..."

} elseif { ${cur_design} ne "" && $list_cells ne "" && $cur_design eq $design_name } {
   # USE CASES:
   #    5) Current design opened AND has components AND same names.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 1
} elseif { [get_files -quiet ${design_name}.bd] ne "" } {
   # USE CASES: 
   #    6) Current opened design, has components, but diff names, design_name exists in project.
   #    7) No opened design, design_name exists in project.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 2

} else {
   # USE CASES:
   #    8) No opened design, design_name not in project.
   #    9) Current opened design, has components, but diff names, design_name not in project.

   common::send_msg_id "BD_TCL-003" "INFO" "Currently there is no design <$design_name> in project, so creating one..."

   create_bd_design $design_name

   common::send_msg_id "BD_TCL-004" "INFO" "Making design <$design_name> as current_bd_design."
   current_bd_design $design_name

}

common::send_msg_id "BD_TCL-005" "INFO" "Currently the variable <design_name> is equal to \"$design_name\"."

if { $nRet != 0 } {
   catch {common::send_msg_id "BD_TCL-114" "ERROR" $errMsg}
   return $nRet
}

set bCheckIPsPassed 1
##################################################################
# CHECK IPs
##################################################################
set bCheckIPs 1
if { $bCheckIPs == 1 } {
   set list_check_ips "\ 
xilinx.com:ip:blk_mem_gen:8.4\
xilinx.com:ip:div_gen:5.1\
xilinx.com:ip:xlconstant:1.1\
"

   set list_ips_missing ""
   common::send_msg_id "BD_TCL-006" "INFO" "Checking if the following IPs exist in the project's IP catalog: $list_check_ips ."

   foreach ip_vlnv $list_check_ips {
      set ip_obj [get_ipdefs -all $ip_vlnv]
      if { $ip_obj eq "" } {
         lappend list_ips_missing $ip_vlnv
      }
   }

   if { $list_ips_missing ne "" } {
      catch {common::send_msg_id "BD_TCL-115" "ERROR" "The following IPs are not found in the IP Catalog:\n  $list_ips_missing\n\nResolution: Please add the repository containing the IP(s) to the project." }
      set bCheckIPsPassed 0
   }

}

##################################################################
# CHECK Modules
##################################################################
set bCheckModules 1
if { $bCheckModules == 1 } {
   set list_check_mods "\ 
SetVolts\
CurRes\
TempCalc\
iSatCalc\
vFloatCalc\
"

   set list_mods_missing ""
   common::send_msg_id "BD_TCL-006" "INFO" "Checking if the following modules exist in the project's sources: $list_check_mods ."

   foreach mod_vlnv $list_check_mods {
      if { [can_resolve_reference $mod_vlnv] == 0 } {
         lappend list_mods_missing $mod_vlnv
      }
   }

   if { $list_mods_missing ne "" } {
      catch {common::send_msg_id "BD_TCL-115" "ERROR" "The following module(s) are not found in the project: $list_mods_missing" }
      common::send_msg_id "BD_TCL-008" "INFO" "Please add source files for the missing module(s) above."
      set bCheckIPsPassed 0
   }
}

if { $bCheckIPsPassed != 1 } {
  common::send_msg_id "BD_TCL-1003" "WARNING" "Will not continue with creation of design due to the error(s) above."
  return 3
}

##################################################################
# DESIGN PROCs
##################################################################


# Hierarchical cell: vFloat_hier
proc create_hier_cell_vFloat_hier { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_vFloat_hier() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -from 13 -to 0 LP_voltage
  create_bd_pin -dir I -type rst Reset_In
  create_bd_pin -dir I -from 15 -to 0 Temp
  create_bd_pin -dir I -type clk clk_100MHz
  create_bd_pin -dir I clk_en
  create_bd_pin -dir I -from 15 -to 0 iSat
  create_bd_pin -dir I -from 13 -to 0 output_voltage
  create_bd_pin -dir O -from 15 -to 0 vFloat

  # Create instance: blk_mem_gen_2, and set properties
  set blk_mem_gen_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 blk_mem_gen_2 ]
  set_property -dict [ list \
   CONFIG.Byte_Size {9} \
   CONFIG.Coe_File {../../../../../../../../../../../../../../../instruments/mirror-langmuir-probe/cores/vfloat_calc_v1_0/vFloat_lut.coe} \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_32bit_Address {false} \
   CONFIG.Enable_A {Always_Enabled} \
   CONFIG.Load_Init_File {true} \
   CONFIG.Operating_Mode_A {READ_FIRST} \
   CONFIG.Read_Width_A {16} \
   CONFIG.Read_Width_B {16} \
   CONFIG.Register_PortA_Output_of_Memory_Primitives {true} \
   CONFIG.Use_Byte_Write_Enable {false} \
   CONFIG.Use_RSTA_Pin {false} \
   CONFIG.Write_Depth_A {16384} \
   CONFIG.Write_Width_A {16} \
   CONFIG.Write_Width_B {16} \
   CONFIG.use_bram_block {Stand_Alone} \
 ] $blk_mem_gen_2

  # Create instance: div_gen_1, and set properties
  set div_gen_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:div_gen:5.1 div_gen_1 ]
  set_property -dict [ list \
   CONFIG.dividend_and_quotient_width {14} \
   CONFIG.dividend_has_tuser {false} \
   CONFIG.dividend_tuser_width {1} \
   CONFIG.divisor_has_tuser {false} \
   CONFIG.divisor_width {14} \
   CONFIG.fractional_width {10} \
   CONFIG.latency {28} \
   CONFIG.remainder_type {Fractional} \
 ] $div_gen_1

  # Create instance: vFloatCalc_0, and set properties
  set block_name vFloatCalc
  set block_cell_name vFloatCalc_0
  if { [catch {set vFloatCalc_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_msg_id "BD_TCL-105" "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $vFloatCalc_0 eq "" } {
     catch {common::send_msg_id "BD_TCL-106" "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  # Create interface connections
  connect_bd_intf_net -intf_net div_gen_1_M_AXIS_DOUT [get_bd_intf_pins div_gen_1/M_AXIS_DOUT] [get_bd_intf_pins vFloatCalc_0/divider]
  connect_bd_intf_net -intf_net vFloatCalc_0_dividend [get_bd_intf_pins div_gen_1/S_AXIS_DIVIDEND] [get_bd_intf_pins vFloatCalc_0/dividend]
  connect_bd_intf_net -intf_net vFloatCalc_0_divisor [get_bd_intf_pins div_gen_1/S_AXIS_DIVISOR] [get_bd_intf_pins vFloatCalc_0/divisor]

  # Create port connections
  connect_bd_net -net Net [get_bd_pins clk_100MHz] [get_bd_pins blk_mem_gen_2/clka] [get_bd_pins div_gen_1/aclk] [get_bd_pins vFloatCalc_0/adc_clk]
  connect_bd_net -net Reset_In_1 [get_bd_pins Reset_In] [get_bd_pins vFloatCalc_0/clk_rst]
  connect_bd_net -net SetVolts_0_vFloat_en [get_bd_pins clk_en] [get_bd_pins vFloatCalc_0/clk_en]
  connect_bd_net -net SetVolts_0_volt_out [get_bd_pins output_voltage] [get_bd_pins vFloatCalc_0/volt3]
  connect_bd_net -net TempCalc_0_Temp [get_bd_pins Temp] [get_bd_pins vFloatCalc_0/Temp]
  connect_bd_net -net blk_mem_gen_2_douta [get_bd_pins blk_mem_gen_2/douta] [get_bd_pins vFloatCalc_0/BRAMret]
  connect_bd_net -net iSatCalc_0_iSat [get_bd_pins iSat] [get_bd_pins vFloatCalc_0/iSat]
  connect_bd_net -net input_voltage_1 [get_bd_pins LP_voltage] [get_bd_pins vFloatCalc_0/volt_in]
  connect_bd_net -net vFloatCalc_0_BRAM_addr [get_bd_pins blk_mem_gen_2/addra] [get_bd_pins vFloatCalc_0/BRAM_addr]
  connect_bd_net -net vFloatCalc_0_vFloat [get_bd_pins vFloat] [get_bd_pins vFloatCalc_0/vFloat]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: iSat_hier
proc create_hier_cell_iSat_hier { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_iSat_hier() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -from 13 -to 0 LP_voltage
  create_bd_pin -dir I -type rst Reset_In
  create_bd_pin -dir I -from 15 -to 0 Temp
  create_bd_pin -dir I -type clk clk_100MHz
  create_bd_pin -dir I clk_en
  create_bd_pin -dir O -from 15 -to 0 iSat
  create_bd_pin -dir I -from 13 -to 0 output_voltage
  create_bd_pin -dir I -from 15 -to 0 vFloat

  # Create instance: blk_mem_gen_1, and set properties
  set blk_mem_gen_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 blk_mem_gen_1 ]
  set_property -dict [ list \
   CONFIG.Byte_Size {9} \
   CONFIG.Coe_File {../../../../../../../../../../../../../../../instruments/mirror-langmuir-probe/cores/isat_calc_v1_0/iSat_lut.coe} \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_32bit_Address {false} \
   CONFIG.Enable_A {Always_Enabled} \
   CONFIG.Load_Init_File {true} \
   CONFIG.Operating_Mode_A {READ_FIRST} \
   CONFIG.Read_Width_A {16} \
   CONFIG.Read_Width_B {16} \
   CONFIG.Register_PortA_Output_of_Memory_Primitives {true} \
   CONFIG.Use_Byte_Write_Enable {false} \
   CONFIG.Use_RSTA_Pin {false} \
   CONFIG.Write_Depth_A {16384} \
   CONFIG.Write_Width_A {16} \
   CONFIG.Write_Width_B {16} \
   CONFIG.use_bram_block {Stand_Alone} \
 ] $blk_mem_gen_1

  # Create instance: div_gen_2, and set properties
  set div_gen_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:div_gen:5.1 div_gen_2 ]
  set_property -dict [ list \
   CONFIG.dividend_and_quotient_width {14} \
   CONFIG.dividend_has_tuser {false} \
   CONFIG.dividend_tuser_width {1} \
   CONFIG.divisor_has_tuser {false} \
   CONFIG.divisor_width {14} \
   CONFIG.fractional_width {10} \
   CONFIG.latency {28} \
   CONFIG.latency_configuration {Automatic} \
   CONFIG.remainder_type {Fractional} \
 ] $div_gen_2

  # Create instance: iSatCalc_0, and set properties
  set block_name iSatCalc
  set block_cell_name iSatCalc_0
  if { [catch {set iSatCalc_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_msg_id "BD_TCL-105" "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $iSatCalc_0 eq "" } {
     catch {common::send_msg_id "BD_TCL-106" "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /iSat_hier/iSatCalc_0/dividend]

  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /iSat_hier/iSatCalc_0/divider]

  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /iSat_hier/iSatCalc_0/divisor]

  # Create interface connections
  connect_bd_intf_net -intf_net div_gen_2_M_AXIS_DOUT [get_bd_intf_pins div_gen_2/M_AXIS_DOUT] [get_bd_intf_pins iSatCalc_0/divider]
  connect_bd_intf_net -intf_net iSatCalc_0_dividend [get_bd_intf_pins div_gen_2/S_AXIS_DIVIDEND] [get_bd_intf_pins iSatCalc_0/dividend]
  connect_bd_intf_net -intf_net iSatCalc_0_divisor [get_bd_intf_pins div_gen_2/S_AXIS_DIVISOR] [get_bd_intf_pins iSatCalc_0/divisor]

  # Create port connections
  connect_bd_net -net Net [get_bd_pins clk_100MHz] [get_bd_pins blk_mem_gen_1/clka] [get_bd_pins div_gen_2/aclk] [get_bd_pins iSatCalc_0/adc_clk]
  connect_bd_net -net Reset_In_1 [get_bd_pins Reset_In] [get_bd_pins iSatCalc_0/clk_rst]
  connect_bd_net -net SetVolts_0_iSat_en [get_bd_pins clk_en] [get_bd_pins iSatCalc_0/clk_en]
  connect_bd_net -net SetVolts_0_volt_out [get_bd_pins output_voltage] [get_bd_pins iSatCalc_0/volt1]
  connect_bd_net -net TempCalc_0_Temp [get_bd_pins Temp] [get_bd_pins iSatCalc_0/Temp]
  connect_bd_net -net blk_mem_gen_1_douta [get_bd_pins blk_mem_gen_1/douta] [get_bd_pins iSatCalc_0/BRAMret]
  connect_bd_net -net iSatCalc_0_BRAM_addr [get_bd_pins blk_mem_gen_1/addra] [get_bd_pins iSatCalc_0/BRAM_addr]
  connect_bd_net -net iSatCalc_0_iSat [get_bd_pins iSat] [get_bd_pins iSatCalc_0/iSat]
  connect_bd_net -net input_voltage_1 [get_bd_pins LP_voltage] [get_bd_pins iSatCalc_0/volt_in]
  connect_bd_net -net vFloatCalc_0_vFloat [get_bd_pins vFloat] [get_bd_pins iSatCalc_0/vFloat]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: Temp_hier
proc create_hier_cell_Temp_hier { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_Temp_hier() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -from 13 -to 0 LP_voltage
  create_bd_pin -dir I -type rst Reset_In
  create_bd_pin -dir O -from 15 -to 0 Temp
  create_bd_pin -dir I -type clk clk_100MHz
  create_bd_pin -dir I clk_en
  create_bd_pin -dir O data_valid
  create_bd_pin -dir I -from 15 -to 0 iSat
  create_bd_pin -dir I -from 13 -to 0 output_voltage
  create_bd_pin -dir I -from 15 -to 0 vFloat

  # Create instance: TempCalc_0, and set properties
  set block_name TempCalc
  set block_cell_name TempCalc_0
  if { [catch {set TempCalc_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_msg_id "BD_TCL-105" "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $TempCalc_0 eq "" } {
     catch {common::send_msg_id "BD_TCL-106" "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  # Create instance: blk_mem_gen_0, and set properties
  set blk_mem_gen_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 blk_mem_gen_0 ]
  set_property -dict [ list \
   CONFIG.Byte_Size {9} \
   CONFIG.Coe_File {../../../../../../../../../../../../../../../instruments/mirror-langmuir-probe/cores/temp_calc_v1_0/Temp_lut.coe} \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_32bit_Address {false} \
   CONFIG.Enable_A {Always_Enabled} \
   CONFIG.Load_Init_File {true} \
   CONFIG.Operating_Mode_A {READ_FIRST} \
   CONFIG.Read_Width_A {16} \
   CONFIG.Read_Width_B {16} \
   CONFIG.Register_PortA_Output_of_Memory_Primitives {true} \
   CONFIG.Use_Byte_Write_Enable {false} \
   CONFIG.Use_RSTA_Pin {false} \
   CONFIG.Write_Depth_A {16384} \
   CONFIG.Write_Width_A {16} \
   CONFIG.Write_Width_B {16} \
   CONFIG.use_bram_block {Stand_Alone} \
 ] $blk_mem_gen_0

  # Create instance: div_gen_0, and set properties
  set div_gen_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:div_gen:5.1 div_gen_0 ]
  set_property -dict [ list \
   CONFIG.dividend_and_quotient_width {14} \
   CONFIG.dividend_has_tuser {false} \
   CONFIG.dividend_tuser_width {1} \
   CONFIG.divisor_has_tuser {false} \
   CONFIG.divisor_width {14} \
   CONFIG.fractional_width {12} \
   CONFIG.latency {30} \
   CONFIG.operand_sign {Signed} \
   CONFIG.remainder_type {Fractional} \
 ] $div_gen_0

  # Create interface connections
  connect_bd_intf_net -intf_net TempCalc_0_dividend [get_bd_intf_pins TempCalc_0/dividend] [get_bd_intf_pins div_gen_0/S_AXIS_DIVIDEND]
  connect_bd_intf_net -intf_net TempCalc_0_divisor [get_bd_intf_pins TempCalc_0/divisor] [get_bd_intf_pins div_gen_0/S_AXIS_DIVISOR]
  connect_bd_intf_net -intf_net div_gen_0_M_AXIS_DOUT [get_bd_intf_pins TempCalc_0/divider] [get_bd_intf_pins div_gen_0/M_AXIS_DOUT]

  # Create port connections
  connect_bd_net -net Net [get_bd_pins clk_100MHz] [get_bd_pins TempCalc_0/adc_clk] [get_bd_pins blk_mem_gen_0/clka] [get_bd_pins div_gen_0/aclk]
  connect_bd_net -net Reset_In_1 [get_bd_pins Reset_In] [get_bd_pins TempCalc_0/clk_rst]
  connect_bd_net -net SetVolts_0_Temp_en [get_bd_pins clk_en] [get_bd_pins TempCalc_0/clk_en]
  connect_bd_net -net SetVolts_0_volt_out [get_bd_pins output_voltage] [get_bd_pins TempCalc_0/volt2]
  connect_bd_net -net TempCalc_0_BRAM_addr [get_bd_pins TempCalc_0/BRAM_addr] [get_bd_pins blk_mem_gen_0/addra]
  connect_bd_net -net TempCalc_0_Temp [get_bd_pins Temp] [get_bd_pins TempCalc_0/Temp]
  connect_bd_net -net TempCalc_0_data_valid [get_bd_pins data_valid] [get_bd_pins TempCalc_0/data_valid]
  connect_bd_net -net blk_mem_gen_0_douta [get_bd_pins TempCalc_0/BRAMret] [get_bd_pins blk_mem_gen_0/douta]
  connect_bd_net -net iSatCalc_0_iSat [get_bd_pins iSat] [get_bd_pins TempCalc_0/iSat]
  connect_bd_net -net input_voltage_1 [get_bd_pins LP_voltage] [get_bd_pins TempCalc_0/volt_in]
  connect_bd_net -net vFloatCalc_0_vFloat [get_bd_pins vFloat] [get_bd_pins TempCalc_0/vFloat]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: Current_hier
proc create_hier_cell_Current_hier { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_Current_hier() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir O -from 13 -to 0 LP_voltage
  create_bd_pin -dir I -from 15 -to 0 Temp_In
  create_bd_pin -dir I -type clk clk_100MHz
  create_bd_pin -dir I -from 15 -to 0 iSat_in
  create_bd_pin -dir I -from 13 -to 0 output_voltage
  create_bd_pin -dir I -from 15 -to 0 vFloat_In

  # Create instance: CurRes_0, and set properties
  set block_name CurRes
  set block_cell_name CurRes_0
  if { [catch {set CurRes_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_msg_id "BD_TCL-105" "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $CurRes_0 eq "" } {
     catch {common::send_msg_id "BD_TCL-106" "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
  
  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /Current_hier/CurRes_0/dividend]

  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /Current_hier/CurRes_0/divider]

  set_property -dict [ list \
   CONFIG.CLK_DOMAIN {MLP_modules_clk_100MHz} \
 ] [get_bd_intf_pins /Current_hier/CurRes_0/divisor]

  # Create instance: blk_mem_gen_3, and set properties
  set blk_mem_gen_3 [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 blk_mem_gen_3 ]
  set_property -dict [ list \
   CONFIG.Byte_Size {9} \
   CONFIG.Coe_File {../../../../../../../../../../../../../../../instruments/mirror-langmuir-probe/cores/mlp_calc_testbench/current_lut.coe} \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_32bit_Address {false} \
   CONFIG.Enable_A {Always_Enabled} \
   CONFIG.Load_Init_File {true} \
   CONFIG.Operating_Mode_A {READ_FIRST} \
   CONFIG.Read_Width_A {16} \
   CONFIG.Read_Width_B {16} \
   CONFIG.Register_PortA_Output_of_Memory_Primitives {true} \
   CONFIG.Use_Byte_Write_Enable {false} \
   CONFIG.Use_RSTA_Pin {false} \
   CONFIG.Write_Depth_A {16384} \
   CONFIG.Write_Width_A {16} \
   CONFIG.Write_Width_B {16} \
   CONFIG.use_bram_block {Stand_Alone} \
 ] $blk_mem_gen_3

  # Create instance: div_gen_3, and set properties
  set div_gen_3 [ create_bd_cell -type ip -vlnv xilinx.com:ip:div_gen:5.1 div_gen_3 ]
  set_property -dict [ list \
   CONFIG.dividend_and_quotient_width {14} \
   CONFIG.divisor_width {14} \
   CONFIG.fractional_width {10} \
   CONFIG.latency {28} \
   CONFIG.remainder_type {Fractional} \
 ] $div_gen_3

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]

  # Create interface connections
  connect_bd_intf_net -intf_net CurRes_0_dividend [get_bd_intf_pins CurRes_0/dividend] [get_bd_intf_pins div_gen_3/S_AXIS_DIVIDEND]
  connect_bd_intf_net -intf_net CurRes_0_divisor [get_bd_intf_pins CurRes_0/divisor] [get_bd_intf_pins div_gen_3/S_AXIS_DIVISOR]
  connect_bd_intf_net -intf_net div_gen_3_M_AXIS_DOUT [get_bd_intf_pins CurRes_0/divider] [get_bd_intf_pins div_gen_3/M_AXIS_DOUT]

  # Create port connections
  connect_bd_net -net CurRes_0_BRAM_addr [get_bd_pins CurRes_0/BRAM_addr] [get_bd_pins blk_mem_gen_3/addra]
  connect_bd_net -net Net [get_bd_pins clk_100MHz] [get_bd_pins CurRes_0/adc_clk] [get_bd_pins blk_mem_gen_3/clka] [get_bd_pins div_gen_3/aclk]
  connect_bd_net -net SetVolts_0_volt_out [get_bd_pins output_voltage] [get_bd_pins CurRes_0/volt_in]
  connect_bd_net -net Temp_In_1 [get_bd_pins Temp_In] [get_bd_pins CurRes_0/Temp]
  connect_bd_net -net blk_mem_gen_3_douta [get_bd_pins CurRes_0/BRAMret] [get_bd_pins blk_mem_gen_3/douta]
  connect_bd_net -net iSat_in_1 [get_bd_pins iSat_in] [get_bd_pins CurRes_0/iSat]
  connect_bd_net -net input_voltage_1 [get_bd_pins LP_voltage] [get_bd_pins CurRes_0/ResLP]
  connect_bd_net -net vFloat_In_1 [get_bd_pins vFloat_In] [get_bd_pins CurRes_0/vFloat]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins CurRes_0/clk_en] [get_bd_pins xlconstant_0/dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}


# Procedure to create entire design; Provide argument to make
# procedure reusable. If parentCell is "", will use root.
proc create_root_design { parentCell } {

  variable script_folder
  variable design_name

  if { $parentCell eq "" } {
     set parentCell [get_bd_cells /]
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj


  # Create interface ports

  # Create ports
  set LP_voltage [ create_bd_port -dir O -from 13 -to 0 LP_voltage ]
  set Reset_In [ create_bd_port -dir I -type rst Reset_In ]
  set_property -dict [ list \
   CONFIG.POLARITY {ACTIVE_HIGH} \
 ] $Reset_In
  set Temp_In [ create_bd_port -dir I -from 15 -to 0 -type data Temp_In ]
  set clk_100MHz [ create_bd_port -dir I -type clk clk_100MHz ]
  set_property -dict [ list \
   CONFIG.FREQ_HZ {100000000} \
 ] $clk_100MHz
  set iSat_in [ create_bd_port -dir I -from 15 -to 0 -type data iSat_in ]
  set input_voltage [ create_bd_port -dir I -from 13 -to 0 input_voltage ]
  set output_voltage [ create_bd_port -dir O -from 13 -to 0 output_voltage ]
  set period [ create_bd_port -dir I -from 31 -to 0 period ]
  set vFloat_In [ create_bd_port -dir I -from 15 -to 0 -type data vFloat_In ]

  # Create instance: Current_hier
  create_hier_cell_Current_hier [current_bd_instance .] Current_hier

  # Create instance: SetVolts_0, and set properties
  set block_name SetVolts
  set block_cell_name SetVolts_0
  if { [catch {set SetVolts_0 [create_bd_cell -type module -reference $block_name $block_cell_name] } errmsg] } {
     catch {common::send_msg_id "BD_TCL-105" "ERROR" "Unable to add referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   } elseif { $SetVolts_0 eq "" } {
     catch {common::send_msg_id "BD_TCL-106" "ERROR" "Unable to referenced block <$block_name>. Please add the files for ${block_name}'s definition into the project."}
     return 1
   }
    set_property -dict [ list \
   CONFIG.period {125} \
 ] $SetVolts_0

  # Create instance: Temp_hier
  create_hier_cell_Temp_hier [current_bd_instance .] Temp_hier

  # Create instance: iSat_hier
  create_hier_cell_iSat_hier [current_bd_instance .] iSat_hier

  # Create instance: vFloat_hier
  create_hier_cell_vFloat_hier [current_bd_instance .] vFloat_hier

  # Create port connections
  connect_bd_net -net Net [get_bd_ports clk_100MHz] [get_bd_pins Current_hier/clk_100MHz] [get_bd_pins SetVolts_0/adc_clk] [get_bd_pins Temp_hier/clk_100MHz] [get_bd_pins iSat_hier/clk_100MHz] [get_bd_pins vFloat_hier/clk_100MHz]
  connect_bd_net -net Reset_In_1 [get_bd_ports Reset_In] [get_bd_pins SetVolts_0/clk_rst] [get_bd_pins Temp_hier/Reset_In] [get_bd_pins iSat_hier/Reset_In] [get_bd_pins vFloat_hier/Reset_In]
  connect_bd_net -net SetVolts_0_Temp_en [get_bd_pins SetVolts_0/Temp_en] [get_bd_pins Temp_hier/clk_en]
  connect_bd_net -net SetVolts_0_iSat_en [get_bd_pins SetVolts_0/iSat_en] [get_bd_pins iSat_hier/clk_en]
  connect_bd_net -net SetVolts_0_vFloat_en [get_bd_pins SetVolts_0/vFloat_en] [get_bd_pins vFloat_hier/clk_en]
  connect_bd_net -net SetVolts_0_volt_out [get_bd_ports output_voltage] [get_bd_pins Current_hier/output_voltage] [get_bd_pins SetVolts_0/volt_out] [get_bd_pins Temp_hier/output_voltage] [get_bd_pins iSat_hier/output_voltage] [get_bd_pins vFloat_hier/output_voltage]
  connect_bd_net -net TempCalc_0_Temp [get_bd_pins SetVolts_0/Temp] [get_bd_pins Temp_hier/Temp] [get_bd_pins iSat_hier/Temp] [get_bd_pins vFloat_hier/Temp]
  connect_bd_net -net TempCalc_0_data_valid [get_bd_pins SetVolts_0/Temp_valid] [get_bd_pins Temp_hier/data_valid]
  connect_bd_net -net Temp_In_1 [get_bd_ports Temp_In] [get_bd_pins Current_hier/Temp_In]
  connect_bd_net -net iSatCalc_0_iSat [get_bd_pins Temp_hier/iSat] [get_bd_pins iSat_hier/iSat] [get_bd_pins vFloat_hier/iSat]
  connect_bd_net -net iSat_in_1 [get_bd_ports iSat_in] [get_bd_pins Current_hier/iSat_in]
  connect_bd_net -net input_voltage_1 [get_bd_ports LP_voltage] [get_bd_pins Current_hier/LP_voltage] [get_bd_pins Temp_hier/LP_voltage] [get_bd_pins iSat_hier/LP_voltage] [get_bd_pins vFloat_hier/LP_voltage]
  connect_bd_net -net period_1 [get_bd_ports period] [get_bd_pins SetVolts_0/period_in]
  connect_bd_net -net vFloatCalc_0_vFloat [get_bd_pins Temp_hier/vFloat] [get_bd_pins iSat_hier/vFloat] [get_bd_pins vFloat_hier/vFloat]
  connect_bd_net -net vFloat_In_1 [get_bd_ports vFloat_In] [get_bd_pins Current_hier/vFloat_In]

  # Create address segments


  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


common::send_msg_id "BD_TCL-1000" "WARNING" "This Tcl script was generated from a block design that has not been validated. It is possible that design <$design_name> may result in errors during validation."

