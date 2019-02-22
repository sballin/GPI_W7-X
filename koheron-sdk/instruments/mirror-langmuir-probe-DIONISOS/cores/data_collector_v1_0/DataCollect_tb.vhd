-------------------------------------------------------------------------------
-- Test bench for the SetVolts vhdl module
-------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

entity tb_DataCollect is

end entity tb_DataCollect;

architecture behaviour of tb_DataCollect is
  -- Instantiating the SetVolts module
  component DataCollect is
    port (
      adc_clk	 : in std_logic;	-- adc input clock
      volt_valid : in std_logic;
      Temp_valid : in std_logic;
      Temp	 : in std_logic_vector(15 downto 0);
      iSat	 : in std_logic_vector(15 downto 0);
      vFloat	 : in std_logic_vector(15 downto 0);
      v_in	 : in std_logic_vector(13 downto 0);
      v_out	 : in std_logic_vector(13 downto 0);
      clk_en	 : in std_logic;

      tvalid : out std_logic;
      tdata  : out std_logic_vector(31 downto 0);
      timestamp_out_afafafa : out std_logic_vector(4 downto 0)
      );
  end component DataCollect;

  -- input signals
  signal adc_clk    : std_logic			    := '0';
  signal volt_valid : std_logic			    := '0';
  signal Temp_valid : std_logic			    := '0';
  signal Temp	    : std_logic_vector(15 downto 0) := (others => '0');
  signal iSat	    : std_logic_vector(15 downto 0) := (others => '0');
  signal vFloat	    : std_logic_vector(15 downto 0) := (others => '0');
  signal v_in	    : std_logic_vector(13 downto 0) := (others => '0');
  signal v_out	    : std_logic_vector(13 downto 0) := (others => '0');
  signal clk_en	    : std_logic			    := '0';

  -- output signals
  signal tvalid : std_logic			:= '0';
  signal tdata	: std_logic_vector(31 downto 0) := (others => '0');
  signal timestamp_out_afafafa : std_logic_vector(4 downto 0) := (others => '0');
  -- Clock periods
  constant adc_clk_period : time := 8 ns;

begin  -- architecture behaviour
  -- Instantiating test unit
  uut : DataCollect
    port map (
      -- Inputs
      adc_clk	 => adc_clk,
      volt_valid => volt_valid,
      Temp_valid => Temp_valid,
      Temp	 => Temp,
      iSat	 => iSat,
      vFloat	 => vFloat,
      v_in	 => v_in,
      v_out	 => v_out,
      clk_en	 => clk_en,

      -- Outputs
      tvalid => tvalid,
      tdata  => tdata,
      timestamp_out_afafafa => timestamp_out_afafafa
      );

  -- Clock process definitions
  adc_clk_process : process
  begin
    adc_clk <= '0';
    wait for adc_clk_period/2;
    adc_clk <= '1';
    wait for adc_clk_period/2;
  end process;

  -- purpose: Process to produce data for the collector
  -- type   : combinational
  -- inputs : 
  -- outputs: v_in, v_out
  data_proc : process is
  begin	 -- process data_proc
    v_in  <= std_logic_vector(signed(v_in) + 1);
    v_out <= std_logic_vector(signed(v_out) - 1);
    wait for adc_clk_period;
  end process data_proc;

  -- purpose: process to set the volt store signal
  -- type   : combinational
  -- inputs : 
  -- outputs: volt_valid
  volt_proc: process is
  begin  -- process volt_proc
    wait for adc_clk_period*8;
    volt_valid <= '1';
    wait for adc_clk_period;
    volt_valid <= '0';
    wait for adc_clk_period*8;
    volt_valid <= '1';
    wait for adc_clk_period;
    volt_valid <= '0';
    wait for adc_clk_period*8;
    volt_valid <= '1';
    wait for adc_clk_period;
    volt_valid <= '0';
    wait for adc_clk_period*80;
  end process volt_proc;

  -- purpose: Proces to produce variable data for the collector
  -- type   : combinational
  -- inputs : 
  -- outputs: temp, iSat, vFloat
  var_proc : process is
  begin	 -- process var_proc
    wait for adc_clk_period;
    if Temp_valid = '1' then
      Temp   <= std_logic_vector(signed(Temp) + 1);
      iSat   <= std_logic_vector(signed(iSat) + 1);
      vFloat <= std_logic_vector(signed(vFloat) + 1);
    end if;
  end process var_proc;

  -- purpose: Process to set the data valid signal
  -- type   : combinational
  -- inputs : 
  -- outputs: Temp_valid
  valid_proc : process is
  begin	 -- process valid_proc
    wait for adc_clk_period*40;
    Temp_valid <= '1';
    wait for adc_clk_period*1;
    Temp_valid <= '0';
  end process valid_proc;

  -- purpose: Process to set the acquisition enable
  -- type   : combinational
  -- inputs : 
  -- outputs: clk_en
  enable_proc : process is
  begin	 -- process enable_proc
    wait for adc_clk_period*120;
    clk_en <= '1';
    wait for adc_clk_period*300;
    clk_en <= '0';
  end process enable_proc;

end architecture behaviour;
