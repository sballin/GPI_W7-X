-------------------------------------------------------------------------------
-- Intermediate block between RP control registers and output pins
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity outputs is
    port (
        adc_clk               : in  std_logic                    ;
        GPI_safe_state_ctl    : in  std_logic_vector(31 downto 0);
        slow_1_manual_ctl     : in  std_logic_vector(31 downto 0);
        slow_2_manual_ctl     : in  std_logic_vector(31 downto 0);
        slow_3_manual_ctl     : in  std_logic_vector(31 downto 0);
        slow_4_manual_ctl     : in  std_logic_vector(31 downto 0);
        fast_manual_ctl       : in  std_logic_vector(31 downto 0);
        fast_permission_1_ctl : in  std_logic_vector(31 downto 0);
        fast_permission_2_ctl : in  std_logic_vector(31 downto 0);
        fast_permission_3_ctl : in  std_logic_vector(31 downto 0);
        fast_permission_4_ctl : in  std_logic_vector(31 downto 0);
        
        slow_1_manual_pin     : out std_logic                    ;
        slow_2_manual_pin     : out std_logic                    ;
        slow_3_manual_pin     : out std_logic                    ;
        slow_4_manual_pin     : out std_logic                    ;
        fast_manual_pin       : out std_logic                    ;
        fast_permission_1_pin : out std_logic                    ;
        fast_permission_2_pin : out std_logic                    ;
        fast_permission_3_pin : out std_logic                    ;
        fast_permission_4_pin : out std_logic                     
    );
end entity outputs;

architecture Behavioral of outputs is

begin

    Pass_through_1 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_1_manual_ctl /= "00000000000000000000000000000000") then
                slow_1_manual_pin <= '1';
            else
                slow_1_manual_pin <= '0';
            end if;
        end if;
    end process Pass_through_1;

    Pass_through_2 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_2_manual_ctl /= "00000000000000000000000000000000") then
                slow_2_manual_pin <= '1';
            else
                slow_2_manual_pin <= '0';
            end if;
        end if;
    end process Pass_through_2;

    Pass_through_3 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_3_manual_ctl /= "00000000000000000000000000000000") then
                slow_3_manual_pin <= '1';
            else
                slow_3_manual_pin <= '0';
            end if;
        end if;
    end process Pass_through_3;

    Pass_through_4 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (slow_4_manual_ctl /= "00000000000000000000000000000000") then
                slow_4_manual_pin <= '1';
            else
                slow_4_manual_pin <= '0';
            end if;
        end if;
    end process Pass_through_4;

    Pass_through_5 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_permission_1_ctl /= "00000000000000000000000000000000") then
                fast_permission_1_pin <= '1';
            else
                fast_permission_1_pin <= '0';
            end if;
        end if;
    end process Pass_through_5;
    
    Pass_through_6 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_permission_2_ctl /= "00000000000000000000000000000000") then
                fast_permission_2_pin <= '1';
            else
                fast_permission_2_pin <= '0';
            end if;
        end if;
    end process Pass_through_6;

    Pass_through_7 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_permission_3_ctl /= "00000000000000000000000000000000") then
                fast_permission_3_pin <= '1';
            else
                fast_permission_3_pin <= '0';
            end if;
        end if;
    end process Pass_through_7;
     
    Pass_through_8 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_permission_4_ctl /= "00000000000000000000000000000000") then
                fast_permission_4_pin <= '1';
            else
                fast_permission_4_pin <= '0';
            end if;
        end if;
    end process Pass_through_8;
    
    Pass_through_9 : process(adc_clk)
    begin
        if (rising_edge(adc_clk)) then
            if (fast_manual_ctl /= "00000000000000000000000000000000") then
                fast_manual_pin <= '1';
            else
                fast_manual_pin <= '0';
            end if;
        end if;
    end process Pass_through_9;
end architecture Behavioral;
