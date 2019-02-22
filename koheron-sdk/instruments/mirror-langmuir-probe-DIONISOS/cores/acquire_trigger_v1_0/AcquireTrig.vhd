-------------------------------------------------------------------------------
-- Module to trigger data acquisition for the digital mirror langmuir probe
-- Started on March 26th by Charlie Vincent
--
-- Adjust variable is to lengthen period to a number that is indivisible by three
-- First two levels will be of length period, third level will be of length
-- period + adjust
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity AcquireTrig is
  generic (
    adc_clk_period : integer := 125
    );
  port (
    adc_clk : in std_logic;             -- adc input clock
    AcqTime : in std_logic_vector(29 downto 0);
    trigger : in std_logic;

    timestamp     : out std_logic_vector(24 downto 0);
    acquire_valid : out std_logic;
    clear_pulse   : out std_logic
    );

end entity AcquireTrig;

architecture Behavioral of AcquireTrig is
  signal trig_reset      : std_logic              := '0';
  signal acquire         : std_logic              := '0';
  signal acquire_counter : integer range 0 to 250 := 0;
  signal acquire_time    : integer                := 0;
begin  -- architecture Behavioral

  acquire_valid <= acquire;
  timestamp     <= std_logic_vector(to_unsigned(acquire_time, timestamp'length));

  -- purpose: Process to send the reset clk to the other modules
  -- type   : sequential
  -- inputs : adc_clk, acquire
  -- outputs: clear_pulse
  clear_proc: process (adc_clk) is
  begin  -- process clear_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      clear_pulse <= trigger and (not trig_reset);
    end if;
  end process clear_proc;

  -- purpose: process to start acquisition and triggering
  -- type   : sequential
  -- inputs : adc_clk, trigger
  -- outputs: trig_reset
  trig_reset_proc : process (adc_clk) is
  begin  -- process timestamp_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if trigger = '1' then             -- synchronous reset (active high)
        trig_reset <= '1';
      elsif trigger = '0' then
        trig_reset <= '0';
      end if;
    end if;
  end process trig_reset_proc;

  -- purpose: Process to start the acquistion period
  -- type   : sequential
  -- inputs : adc_clk, acquire
  -- outputs: acquire
  start_proc : process (adc_clk) is
  begin  -- process start_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if acquire = '0' then             -- synchronous reset (active high)
        if trigger = '1' and trig_reset = '0' then
          acquire <= '1';
        end if;
      else
        if acquire_time = to_integer(unsigned(AcqTime)) then
          acquire <= '0';
        end if;
      end if;
    end if;
  end process start_proc;

  -- purpose: Process to count clock cycles
  -- type   : sequential
  -- inputs : adc_clk, acquire
  -- outputs: timestamp
  counter_proc : process (adc_clk) is
  begin  -- process timestamp_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if acquire = '1' then             -- synchronous reset (active high)
        if acquire_counter = (adc_clk_period -1) then
          acquire_counter <= 0;
        else
          acquire_counter <= acquire_counter + 1;
        end if;
      else
        acquire_counter <= 0;
      end if;
    end if;
  end process counter_proc;

  -- purpose: process to set the timestamp
  -- type   : sequential
  -- inputs : adc_clk, acquire_counter
  -- outputs: timestamp
  timestamp_proc : process (adc_clk) is
  begin  -- process counter_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if acquire_counter = (adc_clk_period - 1) then  -- synchronous reset (active high)
        acquire_time <= acquire_time + 1;
      end if;
      if acquire_time = to_integer(unsigned(AcqTime)) then
        acquire_time <= 0;
      end if;
    end if;
  end process timestamp_proc;

end architecture Behavioral;
