-------------------------------------------------------------------------------
-- Module to set 3 different voltages levels for inital MLP demonstration
-- Started on March 26th by Charlie Vincent
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity CurrentResponse is
    -- adjustment for non-divisible periods

  port (
    adc_clk : in std_logic;             -- adc input clock
    T_electron_in : in std_logic_vector(13 downto 0); 
    Bias_voltage : in std_logic_vector(13 downto 0);


    T_electron_out : out std_logic_vector(13 downto 0);
    V_LP : out std_logic_vector(13 downto 0);
    V_LP_tvalid : out std_logic

    );

end entity CurrentResponse;

architecture Behavioral of CurrentResponse is
 
begin  -- architecture Behavioral



	Pass_through : process(adc_clk)
	variable clock_timer : integer := 0; 
    variable V_LP_mask : std_logic_vector(13 downto 0) := (others => '0');
	begin
		if (rising_edge(adc_clk)) then
			-- Passing electron temerature through to the Div block 
			T_electron_out <= T_electron_in;

			-- Calculate the diffrence in voltages


            V_LP <= std_logic_vector(shift_right(signed(Bias_voltage), 1) - signed(V_floating));
			--V_LP_mask := std_logic_vector(signed(Bias_voltage) - signed(V_floating));
           -- V_LP <= V_LP_mask(13 downto 13) & "00" & V_LP_mask(12 downto 0);
		end if;
	end process;





end architecture Behavioral;
