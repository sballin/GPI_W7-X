-------------------------------------------------------------------------------
-- Title      : Output Multiplexer for MLP instrument
-- Project    : 
-------------------------------------------------------------------------------
-- File       : OutMux.vhd
-- Author     : root  <root@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-02
-- Last update: 2018-05-02
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: Module to multiplex the ouput of the MLP instrument in
-- conjunction with the auto calibration module
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author          Description
-- 2018-05-02  1.0      CharlieV	Created
-------------------------------------------------------------------------------

library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity OutMux is
  
  port (
    signal_1 : in std_logic_vector(13 downto 0);
    signal_2 : in std_logic_vector(13 downto 0);
    adc_clk  : in std_logic;
    switch   : in std_logic;

    signal_out : out std_logic_vector(13 downto 0)
    );

end entity OutMux;

architecture behaviour of OutMux is

begin  -- architecture behaviour

  -- purpose: Process to impelement the multiplexer
  -- type   : sequential
  -- inputs : adc_clk, switch, signal_1, signal_2
  -- outputs: switch
  mux_proc: process (adc_clk) is
  begin  -- process mux_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if switch = '1' then              -- synchronous reset (active high)
        signal_out <= signal_2;
      else
        signal_out <= signal_1;
      end if;
    end if;
  end process mux_proc;

end architecture behaviour;
