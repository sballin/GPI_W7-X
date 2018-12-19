-------------------------------------------------------------------------------
-- Intermediate block between RP control registers and output pins
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity outputs is

    port (
        adc_clk                 : in std_logic;
        GPI_safe_state_ctl      : in std_logic_vector(31 downto 0);
        slow_1_trigger_ctl      : in std_logic_vector(31 downto 0);
        slow_2_trigger_ctl      : in std_logic_vector(31 downto 0);
        slow_3_trigger_ctl      : in std_logic_vector(31 downto 0);
        slow_4_trigger_ctl      : in std_logic_vector(31 downto 0);
        fast_1_permission_ctl : in std_logic_vector(31 downto 0);
        fast_2_permission_ctl : in std_logic_vector(31 downto 0);
        
        GPI_safe_state_pin      : out std_logic;
        slow_1_trigger_pin      : out std_logic;
        slow_2_trigger_pin      : out std_logic;
        slow_3_trigger_pin      : out std_logic;
        slow_4_trigger_pin      : out std_logic;
        fast_1_permission : out std_logic;
        fast_2_permission : out std_logic

    );

end entity outputs;

architecture Behavioral of outputs is

begin

    Pass_through_0 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (GPI_safe_state_ctl /= "00000000000000000000000000000000") then
                GPI_safe_state_pin <= '1';
            else
                GPI_safe_state_pin <= '0';
            end if;
        end if;
    end process Pass_through_0;

    Pass_through_1 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_1_trigger_ctl /= "00000000000000000000000000000000") then
                slow_1_trigger_pin <= '1';
            else
                slow_1_trigger_pin <= '0';
            end if;
        end if;
    end process Pass_through_1;

    Pass_through_2 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_2_trigger_ctl /= "00000000000000000000000000000000") then
                slow_2_trigger_pin <= '1';
            else
                slow_2_trigger_pin <= '0';
            end if;
        end if;
    end process Pass_through_2;

    Pass_through_3 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_3_trigger_ctl /= "00000000000000000000000000000000") then
                slow_3_trigger_pin <= '1';
            else
                slow_3_trigger_pin <= '0';
            end if;
        end if;
    end process Pass_through_3;

    Pass_through_4 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_4_trigger_ctl /= "00000000000000000000000000000000") then
                slow_4_trigger_pin <= '1';
            else
                slow_4_trigger_pin <= '0';
            end if;
        end if;
    end process Pass_through_4;

   Pass_through_5 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_1_permission_ctl /= "00000000000000000000000000000000") then
                fast_1_permission <= '1';
            else
                fast_1_permission <= '0';
            end if;
        end if;
    end process Pass_through_5;
    
   Pass_through_6 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_2_permission_ctl /= "00000000000000000000000000000000") then
                fast_2_permission <= '1';
            else
                fast_2_permission <= '0';
            end if;
        end if;
    end process Pass_through_6;
end architecture Behavioral;