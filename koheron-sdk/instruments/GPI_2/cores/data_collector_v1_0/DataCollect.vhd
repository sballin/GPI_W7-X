-------------------------------------------------------------------------------
-- Module to organise and store data for the MLP project
-- Started on March 26th by Charlie Vincent
--
-- Adjust variable is to lengthen period to a number that is indivisible by three
-- First two levels will be of length period, third level will be of length
-- period + adjust
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity DataCollect is
  port (
    adc_clk    : in std_logic;          -- adc input clock
    data_1_valid : in std_logic;
    data_2_valid : in std_logic;
    data_1       : in std_logic_vector(15 downto 0);
    data_2       : in std_logic_vector(15 downto 0);
    clk_en     : in std_logic;

    tvalid : out std_logic;
    tdata  : out std_logic_vector(31 downto 0)
    );

end entity DataCollect;

architecture Behavioral of DataCollect is

  
begin  -- architecture Behavioral

  -- purpose: Process to collect voltage values
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: data
  temp_collect : process (adc_clk) is
  begin  -- process data_collect
    if rising_edge(adc_clk) then
      if clk_en = '1' then
        if data_1_valid = '1' then
         
          --tdata <= data_1 & data_2;
          tdata <= "00000000000000000000000000000000";

          tvalid <= '1';
        end if;
      else
      tvalid <= '0';   
      end if;
    end if;
  end process temp_collect;

end architecture Behavioral;