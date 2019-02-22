-------------------------------------------------------------------------------
-- Intermediate block between RP control registers and output pins
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity outputs is

    port (
        adc_clk                 : in std_logic;
        W7X_ctl                 : in std_logic;
        trigger_1_delay         : in std_logic_vector(31 downto 0);
        trigger_2_delay         : in std_logic_vector(31 downto 0);
        trigger_1_duration      : in std_logic_vector(31 downto 0);
        trigger_2_duration      : in std_logic_vector(31 downto 0);



        trigger_1_out           : out std_logic;
        trigger_2_out           : out std_logic
    );

end entity outputs;

architecture Behavioral of outputs is

begin

    Pass_through_0 : process(adc_clk)
    variable delay_counter : unsigned(13 downto 0) := (others => '0');
    begin
        if (rising_edge(adc_clk)) then
            delay_counter := delay_counter + to_unsigned(1,delay_counter'length);

            if (delay_counter = unsigned(trigger_1_delay)) then
                trigger_1_out <= '1';
            elsif (delay_counter = unsigned(trigger_1_delay)+unsigned(trigger_1_duration)) then
                trigger_1_out <= '0';
            end if;

            --if (GPI_safe_state_ctl /= "00000000000000000000000000000000") then
            --    GPI_safe_state_pin <= std_logic_vector(to_signed(8000,GPI_safe_state_pin'length));
            --else
            --    GPI_safe_state_pin <= "00000000000000";
            --end if;
        end if;
    end process Pass_through_0;
    

end architecture Behavioral;