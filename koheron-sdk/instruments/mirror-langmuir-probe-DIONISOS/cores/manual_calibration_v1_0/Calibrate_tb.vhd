-------------------------------------------------------------------------------
-- Title      : Testbench for design "Calibrate"
-- Project    : 
-------------------------------------------------------------------------------
-- File       : Calibrate_tb.vhd
-- Author     : root  <root@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-04
-- Last update: 2018-05-09
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author          Description
-- 2018-05-04  1.0      CharlieV  Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------------------------------------

entity Calibrate_tb is

end entity Calibrate_tb;

-------------------------------------------------------------------------------

architecture behaviour of Calibrate_tb is

component Calibrate is
  port (
  signal adc_clk  : std_logic                     := '0';
  signal clk_rst  : std_logic                     := '0';
  signal scale    : std_logic_vector(15 downto 0) := (others => '0');
  signal offset   : std_logic_vector(31 downto 0) := (others => '0');
  signal volt_in  : std_logic_vector(13 downto 0) := (others => '0');
  signal volt_out : std_logic_vector(13 downto 0)
  );
end component Calibrate;




  -- component ports
  signal adc_clk  : std_logic                     := '0';
  signal clk_rst  : std_logic                     := '0';
  signal scale    : std_logic_vector(15 downto 0) := (others => '0');
  signal offset   : std_logic_vector(31 downto 0) := (others => '0');
  signal volt_in  : std_logic_vector(13 downto 0) := (others => '0');
  signal volt_out : std_logic_vector(13 downto 0);
  
  signal increment : integer := 0;

  -- clock
  constant Clk_period : time := 10 ns;
  signal Clk : std_logic := '1';

begin  -- architecture behaviour

  -- component instantiation
  DUT: entity work.Calibrate
    port map (
      adc_clk  => Clk,
      clk_rst  => clk_rst,
      scale    => scale,
      offset   => offset,
      volt_in  => volt_in,
      volt_out => volt_out);

  -- clock generation
  Clk <= not Clk after Clk_period/2;

  -- waveform generation
  WaveGen_Proc: process
  begin
    -- insert signal assignments here
    volt_in <= std_logic_vector(to_signed(300 + 2*increment, 14));
    --volt_in <= std_logic_vector(to_signed(50, 14));
    wait until Clk = '1';
  end process WaveGen_Proc;

  -- purpose: Process to vary the scale and offset
  -- type   : combinational
  -- inputs : 
  -- outputs: scale, offset
  scale_offset_proc: process is
  begin  -- process scale_offset_proc
    wait for Clk_period*100;
    scale <= std_logic_vector(to_signed(2*1024, 16));
    wait for Clk_period*100;
    offset <= std_logic_vector(to_signed(-25, 32));
  end process scale_offset_proc;
  
  increment_proc: process is
  begin
    wait for Clk_period;
    increment <= increment + 1;
  end process increment_proc;

end architecture behaviour;

-------------------------------------------------------------------------------

configuration Calibrate_tb_behaviour_cfg of Calibrate_tb is
  for behaviour
  end for;
end Calibrate_tb_behaviour_cfg;

-------------------------------------------------------------------------------
