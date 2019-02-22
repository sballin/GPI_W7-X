-------------------------------------------------------------------------------
-- Title      : Testbench for design "LineSmooth"
-- Project    : 
-------------------------------------------------------------------------------
-- File       : LineSmooth_tb.vhd
-- Author     : Vincent  <charlesv@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-10
-- Last update: 2018-05-10
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author  Description
-- 2018-05-10  1.0      charlesv	Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------------------------------------

entity LineSmooth_tb is

end entity LineSmooth_tb;

-------------------------------------------------------------------------------

architecture behavioural of LineSmooth_tb is

  -- component ports
  signal adc_clk : std_logic := '0';
  signal clk_rst : std_logic := '0';
  signal v_in    : std_logic_vector(13 downto 0) := std_logic_vector(to_signed(240, 14));
  signal v_out   : std_logic_vector(13 downto 0) := (others => '0');

  -- clock
  constant Clk_period : time := 10 ns;
  signal Clk : std_logic := '1';

begin  -- architecture behavioural

  -- component instantiation
  DUT: entity work.LineSmooth
    port map (
      adc_clk => adc_clk,
      clk_rst => clk_rst,
      v_in    => v_in,
      v_out   => v_out);

  -- clock generation
  Clk <= not Clk after Clk_period/2;
  adc_clk <= Clk;
  -- waveform generation
  WaveGen_Proc: process
  begin
    -- insert signal assignments here
    -- v_in <= std_logic_vector(signed(v_in) + 1);
    wait until Clk = '1';
  end process WaveGen_Proc;

  -- purpose: To prodice an input for the testbench
  -- type   : combinational
  -- inputs : 
  -- outputs: v_in
  input_proc: process is
  begin  -- process input_proc
    wait for Clk_period*1000;
    v_in <= std_logic_vector(to_signed(340, 14));
    wait for Clk_period*1000;
    v_in <= std_logic_vector(to_signed(140, 14));
  end process input_proc;
  

end architecture behavioural;

-------------------------------------------------------------------------------

configuration LineSmooth_tb_behavioural_cfg of LineSmooth_tb is
  for behavioural
  end for;
end LineSmooth_tb_behavioural_cfg;

-------------------------------------------------------------------------------
