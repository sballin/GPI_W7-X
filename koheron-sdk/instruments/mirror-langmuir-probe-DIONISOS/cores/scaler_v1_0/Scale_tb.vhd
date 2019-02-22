-------------------------------------------------------------------------------
-- Test bench for the SetVolts vhdl module
-------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

library UNISIM;
use UNISIM.vcomponents.all;

entity tb_scale is
end entity tb_scale;

architecture test_bench of tb_scale is

  ----------------------------------------------------------------------------------------------
  -- Instantiating the scale module
  component design_1_wrapper is
    port (    
    adc_clk        : in std_logic;      -- adc input clock
    clk_rst         : in std_logic;
    in_offset        : in std_logic_vector(31 downto 0);  -- Floating Voltage input
    in_scale        : in std_logic_vector(15 downto 0);
    in_signal        : in std_logic_vector(13 downto 0);

    Ave_out       : out std_logic_vector(13 downto 0);
    Scaled_signal       : out std_logic_vector(13 downto 0);
    volt_out       : out std_logic_vector(13 downto 0)
    );
  end component design_1_wrapper;





   ----------------------------------------------------------------------------------------------------
  -- Signals for common signals
 signal adc_clk       : std_logic                     := '0';
 signal clk_rst       : std_logic                     := '0';
-- Signals for Scale
signal Scaled_signal  : std_logic_vector(13 downto 0) := (others => '0');  
-- Signals for Calibrate
 signal   in_scale    : std_logic_vector(15 downto 0) := (others => '0');
 signal   in_offset   : std_logic_vector(31 downto 0) := (others => '0');
 signal   in_signal  : std_logic_vector(13 downto 0) := (others => '0');
 signal   volt_out : std_logic_vector(13 downto 0) := (others => '0');
-- Signals for Moving Average
signal    Ave_out : std_logic_vector(13 downto 0);
-- Clock periods
constant adc_clk_period : time := 8 ns;

-- Simulation signals


begin  -- architecture behaviour
  -- Instantiating test unit
  uut1 : design_1_wrapper
    port map (
      adc_clk       => adc_clk,
      clk_rst => clk_rst,
      in_scale => in_scale,
      in_offset => in_offset,
      in_signal => in_signal,
      volt_out => volt_out,
      Ave_out => Ave_out,
      Scaled_signal => Scaled_signal

      );

--Connecting everything up

--signal_to_scale <= volt_out;
--volt_in_3 <= Scaled_signal;

  ------------- Begin Cut here for INSTANTIATION Template ----- INST_TAG
   -- INST_TAG_END ------ End INSTANTIATION Template --------- 
  
  ------------- Begin Cut here for INSTANTIATION Template ----- INST_TAG
 
  -- Clock process definitions
  adc_clk_process : process
  begin
    adc_clk <= '0';
    wait for adc_clk_period/2;
    adc_clk <= '1';
    wait for adc_clk_period/2;
  end process;

  -- purpose: Process to fluctuate temperature
  -- type   : combinational
  -- inputs : 
  -- outputs: Temp
  iSat_proc: process is
  begin  -- process temp_proc
    in_signal <= std_logic_vector(to_signed(7000,in_signal'length));
    in_offset <= std_logic_vector(to_signed(30,in_offset'length));
    in_scale <= std_logic_vector(to_signed(1126,in_scale'length));
    clk_rst <= '1';
wait for adc_clk_period*1;
clk_rst <= '0';
wait for adc_clk_period*15;
    in_signal <= std_logic_vector(to_signed(3000,in_signal'length));
wait for adc_clk_period*15;
    in_signal <= std_logic_vector(to_signed(1000,in_signal'length));
wait for adc_clk_period*15;
    in_signal <= std_logic_vector(to_signed(0,in_signal'length));
wait for adc_clk_period*15;
    in_signal <= std_logic_vector(to_signed(-3000,in_signal'length));
wait for adc_clk_period*15;    
  end process iSat_proc;

  

end architecture test_bench;
