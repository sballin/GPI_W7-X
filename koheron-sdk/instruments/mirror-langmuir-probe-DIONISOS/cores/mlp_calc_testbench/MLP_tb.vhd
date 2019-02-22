-------------------------------------------------------------------------------
-- Test bench for the SetVolts vhdl module
-------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

library UNISIM;
use UNISIM.vcomponents.all;

entity tb_MLP is
end entity tb_MLP;

architecture test_bench of tb_MLP is

  component MLP_modules is
    port (
      clk_100MHz    : in std_logic;
      Temp_In       : in std_logic_vector(15 downto 0);
      iSat_In       : in std_logic_vector(15 downto 0);
      vFloat_in     : in std_logic_vector(15 downto 0);
      input_voltage : in std_logic_vector(13 downto 0);
      period        : in std_logic_vector(31 downto 0);
      Reset_In      : in std_logic;

      LP_voltage     : out std_logic_vector(13 downto 0);
      output_voltage : out std_logic_vector(13 downto 0));

  end component MLP_modules;

  signal adc_clk   : std_logic                     := '0';
  signal volt_in   : std_logic_vector(13 downto 0) := (others => '0');
  signal period    : std_logic_vector(31 downto 0) := (others => '0');
  signal Temp_In   : std_logic_vector(15 downto 0) := std_logic_vector(to_signed(100, 16));
  signal iSat_In   : std_logic_vector(15 downto 0) := std_logic_vector(to_signed(-100, 16));
  signal vFloat_In : std_logic_vector(15 downto 0) := std_logic_vector(to_signed(0, 16));
  signal Reset_in  : std_logic := '0';

  signal LP_voltage : std_logic_vector(13 downto 0) := (others => '0');
  signal volt_out   : std_logic_vector(13 downto 0) := (others => '0');

  -- Clock periods
  constant adc_clk_period : time := 10 ns;

  -- Simulation signals


begin  -- architecture behaviour

  dut : MLP_modules
    port map (
      Temp_In       => Temp_in,
      iSat_In       => iSat_in,
      vFloat_In     => vFloat_in,
      clk_100MHz    => adc_clk,
      input_voltage => volt_in,
      period        => period,
      Reset_In      => Reset_In,

      LP_voltage     => LP_voltage,
      output_voltage => volt_out
      );

  -- purpose: Process for sim clock
  -- type   : combinational
  -- inputs : 
  -- outputs: adc_clk
  clk_proc : process is
  begin  -- process clk_proc
    wait for adc_clk_period/2;
    adc_clk <= '1';
    wait for adc_clk_period/2;
    adc_clk <= '0';
  end process clk_proc;

  -- purpose: Process to set the voltage input
  -- type   : combinational
  -- inputs : 
  -- outputs: volt_in
  volt_proc : process is
  begin  -- process volt_proc
    volt_in <= std_logic_vector(to_signed(-50, volt_in'length));
    wait for adc_clk_period*125;
    volt_in <= std_logic_vector(to_signed(86, volt_in'length));
    wait for adc_clk_period*125;
    volt_in <= std_logic_vector(to_signed(0, volt_in'length));
    wait for adc_clk_period*125;
  end process volt_proc;

  -- purpose: Process to shift the temperature periodically
  -- type   : combinational
  -- inputs : 
  -- outputs: Temp_In
  temp_proc: process is
  begin  -- process temp_proc
    wait for adc_clk_period*10000;
    Temp_In <= std_logic_vector(to_signed(40, 16));
    wait for adc_clk_period*10000;
    Temp_In <= std_logic_vector(to_signed(80, 16));
    wait for adc_clk_period*10000;
    Temp_In <= std_logic_vector(to_signed(60, 16));
    wait for adc_clk_period*10000;
    Temp_In <= std_logic_vector(to_signed(20, 16));
    wait for adc_clk_period*10000;
    Temp_In <= std_logic_vector(to_signed(100, 16));
  end process temp_proc;

  float_proc: process is
  begin  -- process temp_proc
    wait for adc_clk_period*5000;
    vFloat_In <= std_logic_vector(to_signed(-12, 16));
    wait for adc_clk_period*10000;
    vFloat_In <= std_logic_vector(to_signed(-33, 16));
    wait for adc_clk_period*10000;
    vFloat_In <= std_logic_vector(to_signed(-20, 16));
    wait for adc_clk_period*10000;
    vFloat_In <= std_logic_vector(to_signed(-10, 16));
    wait for adc_clk_period*10000;
    vFloat_In <= std_logic_vector(to_signed(-60, 16));
  end process float_proc;
  
  isat_proc: process is
    begin  -- process temp_proc
      wait for adc_clk_period*6000;
      iSat_In <= std_logic_vector(to_signed(-100, 16));
      wait for adc_clk_period*10000;
      iSat_In <= std_logic_vector(to_signed(-66, 16));
      wait for adc_clk_period*10000;
      iSat_In <= std_logic_vector(to_signed(-150, 16));
      wait for adc_clk_period*10000;
      iSat_In <= std_logic_vector(to_signed(-20, 16));
      wait for adc_clk_period*10000;
      iSat_In <= std_logic_vector(to_signed(100, 16));
    end process isat_proc;

end architecture test_bench;
