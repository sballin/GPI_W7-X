-------------------------------------------------------------------------------
-- VHDL module for automatic calibration of the MLP system.
-- Input will be an uncalibrated voltage source and output will be a callibrated
-- voltage
-- Charlie Vincent 2018
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity Calibrate is

  port (
    adc_clk   : in std_logic;
    clk_rst   : in std_logic;
    volt_in   : in std_logic_vector(13 downto 0);

    volt_out   : out std_logic_vector(13 downto 0);
    scale_out  : out std_logic_vector(13 downto 0);
    offset_out : out std_logic_vector(13 downto 0);
    complete   : out std_logic
    );

end entity Calibrate;

architecture behavioural of Calibrate is

  signal volt_in_mask  : signed(13 downto 0) := (others => '0');
  signal volt_out_mask : signed(13 downto 0) := (others => '0');
  signal volt_out_reg  : signed(27 downto 0) := (others => '0');

  signal offset       : signed(13 downto 0) := (others => '0');
  signal offset_found : std_logic           := '0';

  signal scale       : signed(13 downto 0) := (others => '0');
  signal scale_found : std_logic           := '0';

  signal stage         : integer range 0 to 2 := 0;  -- defines which point in the
                                                     -- calibration we're at.
  constant scale_const : integer              := 4096;

  signal counter_out     : integer range 127 downto 0 := 0;
  signal accumulator_out : signed(19 downto 0)        := (others => '0');

  signal reset_mask : std_logic := '0';

begin  -- architecture behavioural

  volt_in_mask <= signed(volt_in);
  volt_out     <= std_logic_vector(volt_out_mask);
  scale_out    <= std_logic_vector(scale);
  offset_out   <= std_logic_vector(offset);

  -- purpose: Process to make the reset a one clock reset
  -- type   : sequential
  -- inputs : adc_clk, clk_rst
  -- outputs: reset_mask
  one_clock_reset : process (adc_clk) is
    variable prev_reset : std_logic := '0';
  begin  -- process one_clock_reset
    if rising_edge(adc_clk) then        -- rising clock edge
      reset_mask <= clk_rst and (not prev_reset);
      prev_reset := clk_rst;
    end if;
  end process one_clock_reset;

  -- purpose: Process to find the zero offset for the voltage calibration
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in_mask
  -- outputs: offset
  offset_proc : process (adc_clk) is
    variable counter     : integer range 127 downto 0 := 0;
    variable accumulator : signed(19 downto 0)        := (others => '0');
  begin  -- process offset_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if reset_mask = '1' then          -- synchronous reset (active high)
        offset       <= (others => '0');
        offset_found <= '0';
        counter      := 0;
        accumulator  := (others => '0');
      else
        if stage = 0 then
          if counter = 127 then
            offset       <= shift_right(accumulator, 7)(13 downto 0);
            offset_found <= '1';
          else
            accumulator     := accumulator + volt_in_mask;
            counter         := counter + 1;
            counter_out     <= counter;
            accumulator_out <= accumulator;
          end if;
        end if;
      end if;
    end if;
  end process offset_proc;

  -- purpose: Process to find the calibration coefficient
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in_mask
  -- outputs: scale
  scale_proc : process (adc_clk) is
    variable counter     : integer range 127 downto 0 := 0;
    variable accumulator : signed(19 downto 0)        := (others => '0');
  begin  -- process scale_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if reset_mask = '1' then          -- synchronous reset (active high)
        scale       <= (others => '0');
        scale_found <= '0';
        counter     := 0;
        accumulator := (others => '0');
      else
        if stage = 1 then
          if counter = 127 then
            scale       <= shift_right(accumulator, 7)(13 downto 0) - offset;
            scale_found <= '1';
          else
            accumulator := accumulator + volt_in_mask;
            counter     := counter + 1;
          end if;
        end if;
      end if;
    end if;
  end process scale_proc;

  -- purpose: Process to set whish stage in the calibration we're at
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, varous offset switches
  -- outputs: stage
  stage_proc : process (adc_clk) is
  begin  -- process stage_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if reset_mask = '1' then          -- synchronous reset (active high)
        stage    <= 0;
        complete <= '0';
      elsif offset_found = '1' and scale_found = '0' then
        stage <= 1;
      elsif offset_found = '1' and scale_found = '1' then
        stage    <= 2;
        complete <= '1';
      else
        stage    <= 0;
        complete <= '0';
      end if;
    end if;
  end process stage_proc;

  -- purpose: Process to register the voltage output calculation
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in_mask
  -- outputs: volt_out_mask
  calc_proc : process (adc_clk) is
  begin  -- process calc_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      if clk_rst = '1' then             -- synchronous reset (active high)
        volt_out_reg <= shift_right((scale * volt_in_mask), 12);
      else

      end if;
    end if;
  end process calc_proc;

  -- purpose: Process to set the output voltage
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in_mask
  -- outputs: volt_out_mask
  volt_out_proc : process (adc_clk) is
  begin  -- process volt_out_proc
    if rising_edge(adc_clk) then        -- rising clock edge
      case stage is
        when 0      => volt_out_mask <= (others => '0');
        when 1      => volt_out_mask <= to_signed(scale_const, 14);
        when 2      => volt_out_mask <= volt_out_reg(13 downto 0) - offset;
        when others => null;
      end case;
    end if;
  end process volt_out_proc;

end architecture behavioural;
