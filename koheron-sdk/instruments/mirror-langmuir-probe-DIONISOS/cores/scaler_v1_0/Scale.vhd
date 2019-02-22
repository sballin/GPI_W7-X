-------------------------------------------------------------------------------
-- Module to calculate the Temp constant for MLP bias setting
-- This module must be used in conjuction with a divider core and a bram
-- generator core. The latency from clock_enable to data valid is currently 36
-- clock cycles
-- Started on March 2nd by Charlie Vincent
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity Scale is
    port (
    adc_clk        : in std_logic;      -- adc input clock
    clk_rst        : in std_logic; 
    signal_to_scale        : in std_logic_vector(13 downto 0);  -- Floating Voltage input
    
    Scaled_signal       : out std_logic_vector(13 downto 0)
    );  -- BRAM address out


end entity Scale;

architecture Behavioral of Scale is
begin  -- architecture Behavioral
  -- purpose: This core applys a division by 1.28 which will translate into a 1V on probe being represented by 128 in the bit logic or 1 Amp as 6400 in the new bit logic
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: Scaled_signal, waitBRAM
  BRAM_proc : process (adc_clk) is
    variable Curr_mask : integer range -8191 to 8191 := 0;
    variable signal_mask : signed(18 downto 0) := (others => '0') ;
  begin  -- process BRAM_proc
    if rising_edge(adc_clk) then
    if clk_rst = '1' then
    Scaled_signal <= (others => '0');
    signal_mask := to_signed(0,signal_mask'length);
    Scaled_signal <= std_logic_vector(signal_mask(18 downto 5));    
    else
    Curr_mask := to_integer(signed(signal_to_scale));
    signal_mask := to_signed(Curr_mask*25,signal_mask'length);
    Scaled_signal <= std_logic_vector(signal_mask(18 downto 5));
    end if ;
    end if;
  end process BRAM_proc;

end architecture Behavioral;
