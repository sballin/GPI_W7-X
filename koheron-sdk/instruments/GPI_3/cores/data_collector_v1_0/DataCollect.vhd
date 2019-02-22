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
    adc_clk    : in  std_logic                    ; -- adc input clock
    abs_gauge  : in  std_logic_vector(13 downto 0);
    diff_gauge : in  std_logic_vector(13 downto 0);

    tvalid     : out std_logic                    ;
    tdata      : out std_logic_vector(31 downto 0) 
  );
end entity DataCollect;

architecture Behavioral of DataCollect is
begin  -- architecture Behavioral
  
    Pass_through_1 : process(adc_clk)
    variable clock_counter_local : integer range 0 to 125000 := 0 ;
    begin
        if rising_edge(adc_clk) then
            --clock_counter_out <= std_logic_vector(to_unsigned(clock_counter_local, clock_counter_out'length));
            clock_counter_local := clock_counter_local + 1;
            -- When clock timer reaches 125 MHz/10000 meas/s
            if clock_counter_local = 12500 then
                clock_counter_local := 0;
                --clock_counter_out <= std_logic_vector(to_unsigned(clock_counter_local, clock_counter_out'length));
                tdata <= "0000" & abs_gauge & diff_gauge;
                tvalid <= '1';
            else
                tvalid <= '0';
                tdata <= (others => '0');
            end if;
        end if;
    end process Pass_through_1;

end architecture Behavioral;
