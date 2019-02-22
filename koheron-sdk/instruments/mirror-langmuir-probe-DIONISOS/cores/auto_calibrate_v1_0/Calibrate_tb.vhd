-------------------------------------------------------------------------------
-- Title      : Testbench for design "Calibrate"
-- Project    : 
-------------------------------------------------------------------------------
-- File       : Calibrate_tb.vhd
-- Author     : Vincent  <charlesv@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-01
-- Last update: 2018-05-02
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author  Description
-- 2018-05-01  1.0      charlesv        Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------------------------------------

entity Calibrate_tb is

end entity Calibrate_tb;

-------------------------------------------------------------------------------

architecture behaviour of Calibrate_tb is

  -- component ports
  signal adc_clk  : std_logic                     := '0';
  signal clk_rst  : std_logic                     := '0';
  signal volt_in  : std_logic_vector(13 downto 0) := (others => '0');
  signal volt_out : std_logic_vector(13 downto 0);
  signal complete : std_logic;

  -- clock
  constant Clk_period : time      := 10 ns;
  signal Clk          : std_logic := '1';

begin  -- architecture behaviour

  -- component instantiation
  DUT : entity work.Calibrate
    port map (
      adc_clk  => Clk,
      clk_rst  => clk_rst,
      volt_in  => volt_in,
      volt_out => volt_out,
      complete => complete);

  -- clock generation
  Clk <= not Clk after Clk_period/2;

  -- waveform generation
  WaveGen_Proc : process
  begin
    -- insert signal assignments here

    wait until Clk = '1';
  end process WaveGen_Proc;

  -- purpose: Process to set the testing voltage
  -- type   : combinational
  -- inputs : 
  -- outputs: volt_in
  volt_in_proc : process is
    variable volt_in_mask : std_logic_vector(27 downto 0) := (others => '0');
  begin  -- process volt_in_proc
    if volt_out = std_logic_vector(to_signed(0, 14)) or volt_out = std_logic_vector(to_signed(4096, 14)) then
      volt_in_mask := std_logic_vector(shift_right(signed(volt_out)*29, 5) + to_signed(-2, 14));
      volt_in <= volt_in_mask(13 downto 0);
    else
      volt_in <= std_logic_vector(to_signed(0, 14));
    end if;
    wait until Clk = '1';
  end process volt_in_proc;

  -- purpose: Process to set test the reset behaviour
  -- type   : combinational
  -- inputs : 
  -- outputs: clk_rst
  reset_proc: process is
  begin  -- process reset_proc
    wait for Clk_period*800;
    clk_rst <= '1';
    --wait for Clk_period*;
    --clk_rst <= '0';
  end process reset_proc;

end architecture behaviour;

-------------------------------------------------------------------------------

configuration Calibrate_tb_behaviour_cfg of Calibrate_tb is
  for behaviour
  end for;
end Calibrate_tb_behaviour_cfg;

-------------------------------------------------------------------------------
