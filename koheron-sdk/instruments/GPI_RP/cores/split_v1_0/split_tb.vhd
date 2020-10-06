-------------------------------------------------------------------------------
-- Test bench for split block
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity split_tb is

end entity split_tb;

architecture Behavior of split_tb is

    component split is

    port (
        clk               : in  std_logic                    ;
        xadc_data             : in  std_logic_vector(15 downto 0);
        xadc_channel          : in  std_logic_vector(4 downto 0); 
        
        analog_input_0                   : out std_logic_vector(15 downto 0);
        analog_input_1                   : out std_logic_vector(15 downto 0)                     
    );

    end component split;

    signal clk                 : std_logic                     := '0';
    signal xadc_data               : std_logic_vector(15 downto 0) := (others => '0');
    signal xadc_channel            : std_logic_vector(4 downto 0)  := (others => '0');

    signal analog_input_0      : std_logic_vector(15 downto 0) := (others => '0');
    signal analog_input_1      : std_logic_vector(15 downto 0) := (others => '0');

    constant adc_clk_period : time := 8 ns;

begin

    uut : split
    port map (
        clk       => clk,
        xadc_data     => xadc_data,
        xadc_channel  => xadc_channel,
        analog_input_0           => analog_input_0,
        analog_input_0           => analog_input_1
    );

    clk_process : process
    begin
        clk <= '0';
        wait for adc_clk_period / 2;
        clk <= '1';
        wait for adc_clk_period / 2;
    end process;

end architecture Behavior;