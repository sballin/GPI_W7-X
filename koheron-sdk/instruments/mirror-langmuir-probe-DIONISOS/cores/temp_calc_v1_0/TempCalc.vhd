-------------------------------------------------------------------------------
-- Module to calculate the Temp constant for MLP bias setting
-- This module must be used in conjuction with a divider core and a bram
-- generator core. The latency from clock_enable to data valid is currently 36
-- clock cycles
-- Started on March 2nd by Charlie Vincent
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity TempCalc is
  generic (
    iSat_guess   : integer := -3200;
    vFloat_guess : integer := 0);
  port (
    adc_clk        : in std_logic;      -- adc input clock
    clk_rst        : in std_logic;      -- clk reset
    vFloat         : in std_logic_vector(19 downto 0);  -- Floating Voltage input
    iSat           : in std_logic_vector(19 downto 0);  -- Temperature input
    BRAMret        : in std_logic_vector(19 downto 0);  -- data returned by BRAM
    LP_current        : in std_logic_vector(13 downto 0);  -- Current Value from LP
    LB_Voltage          : in std_logic_vector(13 downto 0);  -- Loopback Voltage Value
    clk_en         : in std_logic;      -- Clock Enable to set period start
    divider_tdata  : in std_logic_vector(31 downto 0);
    divider_tvalid : in std_logic;
    Temp_lower_lim : in std_logic_vector(31 downto 0);
	  Temp_upper_lim : in std_logic_vector(31 downto 0);

    divisor_tdata   : out std_logic_vector(15 downto 0);
    divisor_tvalid  : out std_logic;
    dividend_tdata  : out std_logic_vector(15 downto 0);
    dividend_tvalid : out std_logic;
    BRAM_addr       : out std_logic_vector(13 downto 0);  -- BRAM address out
    Temp            : out std_logic_vector(19 downto 0);  -- Saturation current
    data_valid      : out std_logic);  -- valid to propagate to float and temp block

end entity TempCalc;

architecture Behavioral of TempCalc is

  signal exp_count       : integer range 0 to 31 := 0;
  signal exp_en          : std_logic             := '0';
  signal exp_ret         : signed(13 downto 0)   := (others => '0');
  signal index           : std_logic             := '0';
  signal waitBRAM        : std_logic             := '0';  -- Signal to indicate when
                                        -- to wait for the bram return
  signal storeSig        : signed(13 downto 0)   := (others => '0');
  signal storeSig2       : signed(19 downto 0)   := (others => '0');
  signal Temp_mask       : signed(39 downto 0)   := (others => '0');
  signal Temp_proxy      : signed(19 downto 0)   := signed(Temp_upper_lim(19 downto 0));
  signal difference_hold : signed(19 downto 0)   := (others => '0');

  signal addr_mask_store : integer := 0;
  signal int_store       : integer := 0;
  signal rem_store       : integer := 0;
  signal Temp_guess      : integer := 0;
  signal Temp_High       : integer := 0;
  signal Temp_Low        : integer := 0;


  signal calc_switch : std_logic_vector(1 downto 0) := "00";

  signal output_trigger : std_logic := '0';

  constant Temp_max : signed(13 downto 0) := (13 => '0', others => '1');

begin  -- architecture Behavioral


  Temp_guess <= to_integer(signed(Temp_upper_lim)); 
  index <= divider_tvalid;

  Temp_High <= to_integer(signed(Temp_upper_lim)); 
  Temp_Low <= to_integer(signed(Temp_lower_lim));

  -- purpose: Process to do core reset and assign calculation results
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, iSat_guess
  -- outputs: Temp
  reset_proc : process (adc_clk) is
  begin  -- process reset_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        Temp <= std_logic_vector(to_signed(Temp_guess, 20));
      else
        if output_trigger = '1' then
          if Temp_mask > to_signed(Temp_High, Temp_mask'length) then
            Temp <= std_logic_vector(to_signed(Temp_High, 20));
          elsif Temp_mask < to_signed(Temp_Low, Temp_mask'length) then
            if Temp_mask < to_signed(0, Temp_mask'length) then
              Temp <= std_logic_vector(to_signed(Temp_guess, 20));
            else
              Temp <= std_logic_vector(to_signed(Temp_Low, 20));
            end if;
          else
            Temp <= std_logic_vector(Temp_mask(19 downto 0));
          end if;
          data_valid <= '1';
        else
          data_valid <= '0';
        end if;
      end if;
    end if;
  end process reset_proc;

-- purpose: process to set the divisor and dividend for the divider
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: divisor, dividend, tUser
  div_proc : process (adc_clk) is
    variable divisor_mask : signed(13 downto 0) := (others => '0');
  begin  -- process diff_proc
    if rising_edge(adc_clk) then
      if clk_en = '1' then
        -- Setting the variables to go into the division
        divisor_mask := signed(iSat(13 downto 0));
        if divisor_mask /= to_signed(0, 14) then
          divisor_tdata <= "00" & std_logic_vector(divisor_mask);
        else
          divisor_tdata <= "00" & std_logic_vector(to_signed(iSat_guess, 14));
        end if;
        dividend_tdata  <= "00" & std_logic_vector(shift_right(signed(LP_current), 0));
        --dividend_tdata  <= "00" & std_logic_vector(signed(LP_current));
        dividend_tvalid <= '1';
        divisor_tvalid  <= '1';
        storeSig        <= signed(LB_Voltage);
        --storeSig        <= signed(LB_Voltage);
        storeSig2       <= signed(vFloat);
      else
        dividend_tvalid <= '0';
        divisor_tvalid  <= '0';
      end if;
    end if;
  end process div_proc;


  -- purpose: process to set the BRAM address for data data retrieval.
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: BRAM_addr, waitBRAM
  BRAM_proc : process (adc_clk) is
    variable divider_int : integer range -8191 to 8191 := 0;
    variable divider_rem : integer range -4095 to 4095 := 0;
    variable addr_mask   : integer range 0 to 16383    := 0;
  begin  -- process BRAM_proc
    if rising_edge(adc_clk) then
      if index = '1' then
        -- Extracting the integer part and the fractional part returned by the
        -- divider core to use in the bram address mapping
        divider_rem := to_integer(signed(divider_tdata(11 downto 0)));
        divider_int := to_integer(signed(divider_tdata(25 downto 12)));
        int_store   <= divider_int;
        rem_store   <= divider_rem;
        case divider_int is
          when -1 =>
            addr_mask   := 0;
            calc_switch <= "01";
          when 0 =>
            addr_mask := 4095 + divider_rem;
            if addr_mask < 4095 then
              calc_switch <= "01";
            else
              calc_switch <= "00";
            end if;
          when 1 =>
            addr_mask   := 8191 + divider_rem;
            calc_switch <= "10";
          when 2 =>
            addr_mask   := 12288 + divider_rem;
            calc_switch <= "10";
          when others =>
            if divider_int < to_signed(-1, 14) then
              addr_mask   := 0;
              calc_switch <= "01";
            elsif divider_int >= to_signed(3, 14) then
              addr_mask   := 16383;
              calc_switch <= "10";
            end if;
        end case;
        addr_mask_store <= addr_mask;
        BRAM_addr       <= std_logic_vector(to_unsigned(addr_mask, 14));
        waitBRAM        <= '1';
      else
        waitBRAM <= '0';
      end if;
    end if;
  end process BRAM_proc;

  -- purpose: process to collect bram data after address is set by division module
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: exp_ret, exp_en
  collect_proc : process (adc_clk) is
  begin  -- process collect_proc
    -- Setting a collection tick to get the right block ram memory back once
    -- the address has been assigned.
    if rising_edge(adc_clk) then
      if waitBRAM = '1' then
        exp_count <= exp_count + 1;
      end if;
      if exp_count = 1 then
        exp_count <= exp_count + 1;
      elsif exp_count = 2 then
        exp_en <= '1';
      end if;
      if exp_en = '1' then
        exp_count <= 0;
        exp_en    <= '0';
      end if;
    end if;
  end process collect_proc;


-- purpose: Process to calculate the difference between bias and floating voltage
-- type   : sequential
-- inputs : adc_clk, waitBRAM, storeSig, storeSig2
-- outputs: difference_hold
  difference_proc : process (adc_clk                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ) is
  begin  -- process difference_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if waitBRAM = '1' then            -- synchronous reset (active high)
        difference_hold <= storeSig - storeSig2;
      end if;
    end if;
  end process difference_proc;


 -- purpose: Process to calculate Temperature value
  -- type   : combinational
  -- inputs : adc_clk
  -- outputs: saturation current
  Temp_proc : process (adc_clk) is
  begin
    if rising_edge(adc_clk) then
      if exp_en = '1' then
        if calc_switch = "01" then
          Temp_mask <= shift_right(difference_hold * signed(BRAMret), 9);
        elsif calc_switch = "10" then
          Temp_mask <= shift_right(to_signed(to_integer(difference_hold) * to_integer(unsigned(BRAMret)), 32), 13);
        elsif calc_switch = "00" then
          Temp_mask <= shift_right(difference_hold * signed(BRAMret), 9);
          --Temp_mask <= difference_hold * signed(BRAMret);
        end if;
        output_trigger <= '1';
      else
        output_trigger <= '0';
      end if;
    end if;
  end process Temp_proc;





end architecture Behavioral;
