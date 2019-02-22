-------------------------------------------------------------------------------
-- Module to organise and store data for the MLP project
-- Started on March 26th by Charlie Vincent
--
-- Adjust variable is to lengthen period to a number that is indivisible by three
-- First two levels will be of length period, third level will be of length
-- period + adjust
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity DataCollect is
  port (
    adc_clk    : in std_logic;          -- adc input clock
    store_en : in std_logic;
    Temp_valid : in std_logic;
    Temp       : in std_logic_vector(19 downto 0);
    iSat       : in std_logic_vector(19 downto 0);
    vFloat     : in std_logic_vector(19 downto 0);
    v_in       : in std_logic_vector(13 downto 0);
    v_out      : in std_logic_vector(13 downto 0);
    clk_en     : in std_logic;

    tvalid : out std_logic;
    tdata  : out std_logic_vector(31 downto 0)
    );

end entity DataCollect;

architecture Behavioral of DataCollect is
  signal data_hold_v : std_logic_vector(31 downto 0) := (others => '0');
  signal data_hold_t : std_logic_vector(31 downto 0) := (others => '0');

  signal delivered_v : std_logic := '0';
  signal delivered_t : std_logic := '0';

  signal volt_stored : std_logic := '0';
  signal temp_stored : std_logic := '0';

  signal timestamp_a   : unsigned(4 downto 0) := (others => '0');

begin  -- architecture Behavioral

  -- purpose: Process to set the data timestamp_a per cycle
  -- type   : sequential
  -- inputs : adc_clk, clk_en, Temp_valid
  -- outputs: timestamp_a
  timestamp_a_proc : process (adc_clk) is
    variable counter : integer range 0 to 251 := 0;
  begin  -- process timestamp_a_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_en = '1' then              -- synchronous reset (active high)
        if counter = 12 then
          timestamp_a <= timestamp_a + 1;
         elsif (counter = 25) then
         counter := 0;
        end if;
        counter := counter + 1;
      elsif (to_integer(timestamp_a) > 12) then
          timestamp_a <= (others => '0');
      else
        timestamp_a <= (others => '0');
      end if;
    end if;
  end process timestamp_a_proc;


  -- purpose: Process to collect voltage values
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: data
  volt_collect : process (adc_clk) is
  begin  -- process data_collect
    if rising_edge(adc_clk) then
      if clk_en = '1' then
        if store_en = '1' then
          volt_stored <= '1';
          
          data_hold_v <= "0" &
                         std_logic_vector(timestamp_a) &
                         v_in(13 downto 1) &
                         v_out(13 downto 1);
        else
          if delivered_v = '1' then
            volt_stored <= '0';
          end if;
        end if;
      end if;
    end if;
  end process volt_collect;

  -- purpose: Process to collect voltage values
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: data
  temp_collect : process (adc_clk) is
  begin  -- process data_collect
    if rising_edge(adc_clk) then
      if clk_en = '1' then
        if Temp_valid = '1' then
          temp_stored <= '1';
          data_hold_t <= "1" &
                         std_logic_vector(timestamp_a) &
                         std_logic_vector(unsigned(Temp(11 downto 4))) &
                         std_logic_vector(signed(iSat(12 downto 4))) &
                         std_logic_vector(signed(vFloat(12 downto 4)));
        else
          if delivered_t = '1' then
            temp_stored <= '0';
          end if;
        end if;
      end if;
    end if;
  end process temp_collect;

  -- purpose: Process to set the data to ouput and the correct valid signal 
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: tdata, tvalid
  data_valid : process (adc_clk) is
    variable valid_switch : std_logic := '0';
  begin  -- process data_valid
    if rising_edge(adc_clk) then
      if clk_en = '1' then
        if temp_stored = '1' then
          if volt_stored = '1' then
            tdata       <= data_hold_v;
            delivered_v <= '1';
            if valid_switch = '0' then
              valid_switch := '1';
              tvalid       <= '1';
            else
              valid_switch := '0';
              tvalid       <= '0';
            end if;
          else
            tdata       <= data_hold_t;
            delivered_t <= '1';
            if valid_switch = '0' then
              valid_switch := '1';
              tvalid       <= '1';
            else
              valid_switch := '0';
              tvalid       <= '0';
            end if;
          end if;
        else
          if volt_stored = '1' then
            tdata       <= data_hold_v;
            delivered_v <= '1';
            if valid_switch = '0' then
              valid_switch := '1';
              tvalid       <= '1';
            else
              valid_switch := '0';
              tvalid       <= '0';
            end if;
          else
            delivered_v  <= '0';
            delivered_t  <= '0';
            valid_switch := '0';
            tvalid       <= '0';
          end if;
        end if;
      else
        tvalid       <= '0';
        valid_switch := '0';
      end if;
    end if;
  end process data_valid;


end architecture Behavioral;
