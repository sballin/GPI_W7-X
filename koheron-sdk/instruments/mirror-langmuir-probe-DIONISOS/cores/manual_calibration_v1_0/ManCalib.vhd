-------------------------------------------------------------------------------
-- Title      : Manual Calibration module for MLP instrument
-- Project    : 
-------------------------------------------------------------------------------
-- File       : ManCalib.vhd
-- Author     : root  <root@cmodws122.psfc.mit.edu>
-- Company    : 
-- Created    : 2018-05-03
-- Last update: 2018-05-21
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: Module to adjust the voltage inputs such that they match the
-- output of the paired instrument
-------------------------------------------------------------------------------
-- Copyright (c) 2018 
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author          Description
-- 2018-05-03  1.0      CharlieV        Created
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity Calibrate is

  port (
    adc_clk  : in  std_logic;
    clk_rst  : in  std_logic;
    scale    : in  std_logic_vector(15 downto 0);
    offset   : in  std_logic_vector(31 downto 0);
    volt_in  : in  std_logic_vector(13 downto 0);
    volt_out : out std_logic_vector(13 downto 0)
    );

end entity Calibrate;

architecture behaviour of Calibrate is

  signal scale_proxy  : signed(15 downto 0) := to_signed(1024, 16);
  signal offset_proxy : signed(15 downto 0) := to_signed(0, 16);

  signal volt_proxy : signed(15 downto 0) := to_signed(0, 16);
  signal volt_proxy_2 : signed(13 downto 0) := to_signed(0, 14);  
begin  -- architecture behaviour

  -- purpose: Process to apply the offset to the scaled input voltage
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in, scale, offset
  -- outputs: volt_out
  scale_proc : process (adc_clk) is
  begin  -- process apply_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        volt_proxy <= (others => '0');
      else
        volt_proxy <= shift_right(scale_proxy * to_signed(to_integer(signed(volt_in)),16), 10)(15 downto 0);
      end if;
    end if;
  end process scale_proc;

  offset_proc : process (adc_clk) is
    variable volt_proxy_var : signed(15 downto 0) := (others => '0');
  begin  -- process apply_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        volt_proxy_2 <= (others => '0');
      else
      volt_proxy_var := volt_proxy + offset_proxy;
        if (volt_proxy_var < to_signed(-8191,volt_proxy'length)) then
          volt_proxy_2 <= to_signed(-8191,volt_proxy_2'length);
        elsif (volt_proxy_var > to_signed(8191,volt_proxy'length)) then
          volt_proxy_2 <= to_signed(8191,volt_proxy_2'length);
        else   
          volt_proxy_2 <= volt_proxy_var(13 downto 0);           
        end if;
      end if;
    end if;
  end process offset_proc;

  -- purpose: Process to apply the scaling to the input voltage
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in, scale, offset
  -- outputs: volt_out
  output_proc : process (adc_clk) is
  --variable volt_proxy : signed(27 downto 0) := (others => '0');
  begin  -- process apply_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        volt_out <= (others => '0');
      else
        volt_out <= std_logic_vector(volt_proxy_2);        
      end if;
    end if;
  end process output_proc;

  -- purpose: Process to set the scale and offset values and reset them to defaults
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, scale
  -- outputs: scale_proxy, offset_proxy
  proxy_proc : process (adc_clk) is
    variable offset_var : signed(15 downto 0) := (others => '0');
  begin  -- process proxy_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        scale_proxy  <= to_signed(1024, 16);
        offset_proxy <= to_signed(0, 16);
      else
        if scale = std_logic_vector(to_signed(0, 16)) then
          scale_proxy <= to_signed(1024, 16);
        else
          scale_proxy <= signed(scale);
        end if;
        if offset = std_logic_vector(to_signed(0, 16)) then
          offset_proxy <= to_signed(0, 16);
        else
          offset_var := signed(offset(15 downto 0));
          offset_proxy <= offset_var(15 downto 0);
        end if;
      end if;
    end if;
  end process proxy_proc;
end architecture behaviour;
