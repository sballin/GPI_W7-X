-------------------------------------------------------------------------------
-- Test bench for the SetVolts vhdl module
-------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

library UNISIM;
use UNISIM.vcomponents.all;

entity tb_Temp is
end entity tb_Temp;

architecture test_bench of tb_Temp is

  ----------------------------------------------------------------------------------------------
  -- Instantiating the Temp module
  component design_1_wrapper is
    port (
      adc_clk       : in std_logic;
      LB_Voltage    : in std_logic_vector(13 downto 0);
      LP_current : in std_logic_vector(13 downto 0);
      Temp_lower_lim : in std_logic_vector(31 downto 0);
      Temp_upper_lim : in std_logic_vector(31 downto 0);
      Period_in : in std_logic_vector(31 downto 0);
      clk_rst  : in std_logic;

	  Isat_out : out std_logic_vector(19 downto 0);
	  Temp_out : out std_logic_vector(19 downto 0);
	  VFloat_out : out std_logic_vector(19 downto 0);
	  Volt_out_2 : out std_logic_vector(13 downto 0)
	        );
  end component design_1_wrapper;
  --------------------------------------------------------------------------------------------

  -- COMP_TAG_END ------ End COMPONENT Declaration ------------
  
  ----------------------------------------------------------------------------------------------------
  -- Signals for design_1_wrapper module

  -- input signals
  signal adc_clk       : std_logic                     := '0';
  signal clk_rst       : std_logic                     := '0';
  signal LB_Voltage : std_logic_vector(13 downto 0) := (others => '0');
signal LP_current : std_logic_vector(13 downto 0) := (others => '0');
signal Temp_lower_lim : std_logic_vector(31 downto 0) := (others => '0');
signal Temp_upper_lim : std_logic_vector(31 downto 0) := (others => '0');
signal Period_in : std_logic_vector(31 downto 0) := (others => '0');
-- output signals
signal Isat : std_logic_vector(19 downto 0) := (others => '0');
signal Temp : std_logic_vector(19 downto 0) := (others => '0');
signal VFloat : std_logic_vector(19 downto 0) := (others => '0');
signal Volt_out : std_logic_vector(13 downto 0) := (others => '0');


  -- Clock periods
  constant adc_clk_period : time := 8 ns;

  -- Simulation signals


begin  -- architecture behaviour
  -- Instantiating test unit
  uut : design_1_wrapper
    port map (
      	adc_clk       => adc_clk,
      	clk_rst       => clk_rst,
		LB_Voltage  => LB_Voltage,
		LP_current  => LP_current,
		Temp_lower_lim  => Temp_lower_lim,
		Temp_upper_lim  => Temp_upper_lim,
		Period_in  => Period_in,

		Isat_out  => Isat,
		Temp_out    =>  Temp,
		VFloat_out  => VFloat,
		Volt_out_2  => Volt_out
			);

  
  -- Clock process definitions
  adc_clk_process : process
  begin
    adc_clk <= '0';
    wait for adc_clk_period/2;
    adc_clk <= '1';
    wait for adc_clk_period/2;
  end process;

 
  -- Stimulus process
  stim_proc : process
  begin
    wait for adc_clk_period;
  end process;

end architecture test_bench;
