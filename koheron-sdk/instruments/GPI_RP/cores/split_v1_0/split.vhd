-------------------------------------------------------------------------------
-- Split interleaved signal from XADC to separate signals
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity split is
    port (
        clk               : in  std_logic                    ;
        xadc_data             : in  std_logic_vector(15 downto 0);
        xadc_channel          : in  std_logic_vector(4 downto 0); 
        
        analog_input_0                   : out std_logic_vector(15 downto 0);
        analog_input_1                   : out std_logic_vector(15 downto 0)                     
    );
end entity split;

architecture Behavioral of split is

begin

    Pass_through_1 : process(clk)
    begin
        if (rising_edge(clk)) then
            if (xadc_channel = "11000") then
                analog_input_0 <= xadc_data;
            elsif (xadc_channel = "10000") then
                analog_input_1 <= xadc_data;
            end if;
        end if;
    end process Pass_through_1;

end architecture Behavioral;
