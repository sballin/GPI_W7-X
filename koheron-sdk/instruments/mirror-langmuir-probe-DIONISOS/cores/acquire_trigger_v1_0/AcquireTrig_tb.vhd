-------------------------------------------------------------------------------
-- Title      : Testbench for design "AcquireTrig"
-- Project    : 
-------------------------------------------------------------------------------
-- File       : AcquireTrig_tb.vhd
-- Author     : Charles Vincent  <charliev@cmodws122>
-- Company    : 
-- Created    : 2018-04-16
-- Last update: 2018-04-27
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author  Description
-- 2018-04-16  1.0      charliev        Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------------------------------------

entity AcquireTrig_tb is

end entity AcquireTrig_tb;

-------------------------------------------------------------------------------

architecture testbench of AcquireTrig_tb is

  -- component generics
  constant adc_clk_period : integer := 125;

  -- component ports
  signal adc_clk : std_logic := '0';

  signal AcqTime       : std_logic_vector(29 downto 0) := std_logic_vector(to_unsigned(100, 30));
  signal trigger       : std_logic                     := '0';
  signal timestamp     : std_logic_vector(24 downto 0) := (others => '0');
  signal acquire_valid : std_logic                     := '0';
  signal clear_pulse   : std_logic                     := '0';

  signal Temp_valid : std_logic                     := '0';
  signal Temp       : std_logic_vector(15 downto 0) := (others => '0');
  signal iSat       : std_logic_vector(15 downto 0) := (others => '0');
  signal vFloat     : std_logic_vector(15 downto 0) := (others => '0');
  signal v_in       : std_logic_vector(13 downto 0) := (others => '0');
  signal v_out      : std_logic_vector(13 downto 0) := (others => '0');
  signal clk_en     : std_logic                     := '0';

  signal tvalid : std_logic                     := '0';
  signal tdata  : std_logic_vector(31 downto 0) := (others => '0');

  constant adc_clk_time : time := 8 ns;

begin  -- architecture testbench

  -- component instantiation
  DUT : entity work.AcquireTrig
    generic map (
      adc_clk_period => adc_clk_period)
    port map (
      adc_clk       => adc_clk,
      AcqTime       => AcqTime,
      trigger       => trigger,
      timestamp     => timestamp,
      acquire_valid => acquire_valid,
      clear_pulse   => clear_pulse);

  BUT : entity work.DataCollect
    port map(
      adc_clk    => adc_clk,
      Temp_valid => Temp_valid,
      Temp       => Temp,
      iSat       => iSat,
      vFloat     => vFloat,
      v_in       => v_in,
      v_out      => v_out,
      clk_en     => clk_en,
      tvalid     => tvalid,
      tdata      => tdata
      );

  -- clock generation
  adc_clk <= not adc_clk after adc_clk_time/2;

  clk_en <= acquire_valid;

  -- waveform generation
  Trigger_Proc : process
  begin
    wait for adc_clk_time*10;
    trigger <= '1';
    wait for adc_clk_time*2;
    trigger <= '0';
    wait for 120 us;
  end process Trigger_Proc;



end architecture testbench;

-------------------------------------------------------------------------------

configuration AcquireTrig_tb_testbench_cfg of AcquireTrig_tb is
  for testbench
  end for;
end AcquireTrig_tb_testbench_cfg;

-------------------------------------------------------------------------------
