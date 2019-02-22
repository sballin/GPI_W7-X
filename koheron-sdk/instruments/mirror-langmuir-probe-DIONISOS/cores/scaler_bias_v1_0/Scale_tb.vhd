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
  -- Instantiating the Temp module
  component scale is
    port (    
    adc_clk        : in std_logic;      -- adc input clock
   
    signal_to_scale        : in std_logic_vector(13 downto 0);  -- Floating Voltage input
    
    BRAM_addr       : out std_logic_vector(12 downto 0)
    );

  end component scale;
  --------------------------------------------------------------------------------------------

  ------------------- Divider generator core
  
  -- Divider generator core ------------------
  
 
  ----------------------------------------------------------------------------------------------------
  -- Signals for scale module
 signal adc_clk       : std_logic                     := '0';

 signal signal_to_scale  : std_logic_vector(13 downto 0) := (others => '0');  
signal BRAM_addr  : std_logic_vector(12 downto 0) := (others => '0');  


  -- Signals for scale Module
  ---------------------------------------------------------------------------------------------------

  -- Signals for blk_mem_gen_0 ------------------------------------------------------------------
  -- input signals
 

  -- Clock periods
  constant adc_clk_period : time := 8 ns;

  -- Simulation signals


begin  -- architecture behaviour
  -- Instantiating test unit
  uut : scale
    port map (
      adc_clk       => adc_clk,
      BRAM_addr       => BRAM_addr,
      signal_to_scale => signal_to_scale
      );

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
    wait for adc_clk_period*5;
    signal_to_scale <= std_logic_vector(to_signed(7000,signal_to_scale'length));
wait for adc_clk_period*5;
    signal_to_scale <= std_logic_vector(to_signed(3000,signal_to_scale'length));
wait for adc_clk_period*5;
    signal_to_scale <= std_logic_vector(to_signed(1000,signal_to_scale'length));
wait for adc_clk_period*5;
    signal_to_scale <= std_logic_vector(to_signed(0,signal_to_scale'length));
wait for adc_clk_period*5;
    signal_to_scale <= std_logic_vector(to_signed(-3000,signal_to_scale'length));
  end process iSat_proc;

  

end architecture test_bench;
