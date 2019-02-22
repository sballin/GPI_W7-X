-------------------------------------------------------------------------------
-- Title      : Line smoothng
-- Project    : 
-------------------------------------------------------------------------------
-- File       : LineSmoothing.vhd
-- Author     : Vincent  <charlesv@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-10
-- Last update: 2018-05-10
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: Module to operate on an input to do a lin smoothing algorithm
-- similiar to a moving average
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author          Description
-- 2018-05-10  1.0      charlesv        Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity LineSmooth is

  port (
    adc_clk : in  std_logic;            -- input clk
    clk_rst : in  std_logic;            -- output clk
    v_in    : in std_logic_vector(13 downto 0);

    v_out : out std_logic_vector(13 downto 0));

end entity LineSmooth;

architecture behavioural of LineSmooth is

  signal v_out_buff : signed(13 downto 0) := (others => '0');

begin  -- architecture behavioural

  -- purpose: Process to apply the smoothing
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, v_in
  -- outputs: v_out
  smooth_proc : process (adc_clk) is
    variable v_out_prev : signed(13 downto 0) := (others => '0');
  begin  -- process smooth_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        v_out_buff <= (others => '0');
      else
        v_out_buff <= shift_right(shift_left(v_out_prev, 2) - v_out_prev + signed(v_in), 2);
        v_out_prev := v_out_buff;
      end if;
    end if;
  end process smooth_proc;

  v_out <= std_logic_vector(v_out_buff(13 downto 4)) & "0000";

end architecture behavioural;
