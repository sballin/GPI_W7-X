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

entity Scale_bias is
    port (
    adc_clk        : in std_logic;      -- adc input clock
   
    signal_to_scale        : in std_logic_vector(13 downto 0);  -- Floating Voltage input
    
    BRAM_addr       : out std_logic_vector(9 downto 0)
    );  -- BRAM address out


end entity Scale_bias;

architecture Behavioral of Scale_bias is
begin  -- architecture Behavioral
  -- purpose: process to set the BRAM address for data data retrieval.
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: BRAM_addr, waitBRAM
  BRAM_proc : process (adc_clk) is
    variable sig_mask : integer range -600 to 199 := 0;
    variable addr_mask : unsigned(9 downto 0) := (others => '0') ;
  begin  -- process BRAM_proc
    if rising_edge(adc_clk) then
        sig_mask := to_integer(signed(signal_to_scale));
        addr_mask := to_unsigned(600 + sig_mask,addr_mask'length);
        BRAM_addr <= std_logic_vector(addr_mask);
    end if;
  end process BRAM_proc;

end architecture Behavioral;
