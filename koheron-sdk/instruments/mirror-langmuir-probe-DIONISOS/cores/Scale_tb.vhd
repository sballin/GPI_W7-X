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
  component Scale is
    port (    
    adc_clk        : in std_logic;      -- adc input clock
    clk_rst         : in std_logic;
    signal_to_scale        : in std_logic_vector(13 downto 0);  -- Floating Voltage input
    
    Scaled_signal       : out std_logic_vector(13 downto 0)
    );
  end component Scale;
  --------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
  -- Instantiating the Calibration module
  component Calibrate is
    port (    
    adc_clk  : in  std_logic;
    clk_rst  : in  std_logic;
    scale    : in  std_logic_vector(15 downto 0);
    offset   : in  std_logic_vector(31 downto 0);
    volt_in  : in  std_logic_vector(13 downto 0);
    volt_out : out std_logic_vector(13 downto 0)
    );
  end component Calibrate;
  --------------------------------------------------------------------------------------------
  ----------------------------------------------------------------------------------------------
  -- Instantiating the Moving Average module
  --------------------------------------------------------------------------------------------
  component MoveAve is
    port (    
    adc_clk : in std_logic;   -- adc input clock
    volt_in : in std_logic_vector(13 downto 0);
    clk_rst : in std_logic;

    volt_out : out std_logic_vector(13 downto 0)
    );
  end component MoveAve;





   ----------------------------------------------------------------------------------------------------
  -- Signals for common signals
 signal adc_clk       : std_logic                     := '0';
 signal clk_rst       : std_logic                     := '0';
-- Signals for Scale
signal signal_to_scale  : std_logic_vector(13 downto 0) := (others => '0');  
signal Scaled_signal  : std_logic_vector(13 downto 0) := (others => '0');  
-- Signals for Calibrate
 signal   Cal_scale    : std_logic_vector(15 downto 0) := (others => '0');
 signal   Cal_offset   : std_logic_vector(31 downto 0) := (others => '0');
 signal   volt_in  : std_logic_vector(13 downto 0) := (others => '0');
 signal   volt_out : std_logic_vector(13 downto 0) := (others => '0');
-- Signals for Moving Average

signal    volt_in_3 : std_logic_vector(13 downto 0);
signal    volt_out_3 : std_logic_vector(13 downto 0);

-- Clock periods
constant adc_clk_period : time := 8 ns;

-- Simulation signals


begin  -- architecture behaviour
  -- Instantiating test unit
  uut1 : Calibrate
    port map (
      adc_clk       => adc_clk,
      clk_rst => clk_rst,
      scale => Cal_scale,
      offset => Cal_offset,
      volt_in => volt_in,
      volt_out => volt_out
      );

  uut : Scale
    port map (
      adc_clk       => adc_clk,
      clk_rst => clk_rst,
      Scaled_signal       => Scaled_signal,
      signal_to_scale => signal_to_scale
      );

uut2 : MoveAve
    port map (
      adc_clk       => adc_clk,
      clk_rst => clk_rst,
      volt_in => volt_in_3,
      volt_out => volt_out_3
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
    volt_in <= std_logic_vector(to_signed(7000,volt_in'length));
    Cal_offset <= std_logic_vector(to_signed(30,Cal_offset'length));
    Cal_scale <= std_logic_vector(to_signed(1126,Cal_scale'length));
    clk_rst <= '1';
wait for adc_clk_period*1;
clk_rst <= '0';
wait for adc_clk_period*15;
    volt_in <= std_logic_vector(to_signed(3000,volt_in'length));
wait for adc_clk_period*15;
    volt_in <= std_logic_vector(to_signed(1000,volt_in'length));
wait for adc_clk_period*15;
    volt_in <= std_logic_vector(to_signed(0,volt_in'length));
wait for adc_clk_period*15;
    volt_in <= std_logic_vector(to_signed(-3000,volt_in'length));
wait for adc_clk_period*15;    
  end process iSat_proc;

  

end architecture test_bench;
