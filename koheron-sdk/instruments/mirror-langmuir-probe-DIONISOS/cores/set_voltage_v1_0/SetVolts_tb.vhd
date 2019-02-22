-------------------------------------------------------------------------------
-- Title      : Testbench for design "SetVolts"
-- Project    : 
-------------------------------------------------------------------------------
-- File       : SetVolts_tb.vhd
-- Author     : Vincent  <charlesv@cmodws123>
-- Company    : 
-- Created    : 2018-04-20
-- Last update: 2018-05-14
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author  Description
-- 2018-04-20  1.0      charlesv        Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------------------------------------

entity SetVolts_tb is

end entity SetVolts_tb;

-------------------------------------------------------------------------------

architecture behaviour of SetVolts_tb is

  -- component generics
  constant period     : integer := 40;
  constant Temp_guess : integer := 200;
  constant negBias    : integer := -246;
  constant posBias    : integer := 82;

  -- component ports
  signal adc_clk    : std_logic                     := '0';
  signal clk_rst    : std_logic                     := '0';
  signal period_in  : std_logic_vector(31 downto 0) := (others => '0');
  signal Temp       : std_logic_vector(15 downto 0) := std_logic_vector(to_signed(200, 16));
  signal Temp_valid : std_logic                     := '0';
  signal volt_out   : std_logic_vector(13 downto 0) := (others => '0');
  signal iSat_en    : std_logic                     := '0';
  signal vFloat_en  : std_logic                     := '0';
  signal Temp_en    : std_logic                     := '0';
  signal volt1      : std_logic_vector(13 downto 0) := (others => '0');
  signal volt2      : std_logic_vector(13 downto 0) := (others => '0');
  signal store_en   : std_logic                     := '0';
  -- clock
  signal Clk              : std_logic := '1';
  constant adc_clk_period : time      := 8 ns;

begin  -- architecture behaviour

  -- component instantiation
  DUT : entity work.SetVolts
    generic map (
      period     => period,
      Temp_guess => Temp_guess,
      negBias    => negBias,
      posBias    => posBias)
    port map (
      adc_clk    => adc_clk,
      clk_rst    => clk_rst,
      period_in  => period_in,
      Temp       => Temp,
      Temp_valid => Temp_valid,
      volt_out   => volt_out,
      iSat_en    => iSat_en,
      vFloat_en  => vFloat_en,
      Temp_en    => Temp_en,
      store_en   => store_en,
      volt1      => volt1,
      volt2      => volt2);

  -- clock generation
  adc_clk <= not adc_clk after adc_clk_period/2;

  -- waveform generation
  WaveGen_Proc : process
  begin
    -- insert signal assignments here    
    wait until Clk = '1';
  end process WaveGen_Proc;

  -- purpose: Process to set temp valid signal
  -- type   : combinational
  -- inputs : 
  -- outputs: temp_valid
  temp_valid_proc : process is
  begin  -- process temp_valid_proc
    wait for adc_clk_period*300;
    Temp_valid <= '1';
    wait for adc_clk_period;
    Temp_valid <= '0';
    wait for adc_clk_period*5;
    Temp <= std_logic_vector(to_signed(50,Temp'length));
    wait for adc_clk_period*300;
    temp_valid <= '1';
    wait for adc_clk_period;
    Temp_valid <= '0';
    wait for adc_clk_period*5;
    Temp <= std_logic_vector(to_signed(200,Temp'length));
  end process temp_valid_proc;

end architecture behaviour;

-------------------------------------------------------------------------------

configuration SetVolts_tb_behaviour_cfg of SetVolts_tb is
  for behaviour
  end for;
end SetVolts_tb_behaviour_cfg;

-------------------------------------------------------------------------------
