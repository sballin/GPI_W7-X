-------------------------------------------------------------------------------
-- Test bench for output block
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity outputs_tb is

end entity outputs_tb;

architecture Behavior of outputs_tb is

    component outputs is

        port (
            adc_clk                 : in std_logic;
            GPI_safe_state_ctl      : in std_logic_vector(31 downto 0);
            slow_1_trigger_ctl      : in std_logic_vector(31 downto 0);
            slow_2_trigger_ctl      : in std_logic_vector(31 downto 0);
            slow_3_trigger_ctl      : in std_logic_vector(31 downto 0);
            slow_4_trigger_ctl      : in std_logic_vector(31 downto 0);
            W7X_permission_out_ctl  : in std_logic_vector(11 downto 0);
            fast_1_trigger_ctl      : in std_logic_vector(31 downto 0);
            fast_1_permission_1_ctl : in std_logic_vector(31 downto 0);
            fast_1_duration_1_ctl   : in std_logic_vector(31 downto 0);
            fast_1_permission_2_ctl : in std_logic_vector(31 downto 0);
            fast_1_duration_2_ctl   : in std_logic_vector(31 downto 0);
            fast_2_trigger_ctl      : in std_logic_vector(31 downto 0);
            fast_2_permission_1_ctl : in std_logic_vector(31 downto 0);
            fast_2_duration_1_ctl   : in std_logic_vector(31 downto 0);
            fast_2_permission_2_ctl : in std_logic_vector(31 downto 0);
            fast_2_duration_2_ctl   : in std_logic_vector(31 downto 0);


            GPI_safe_state_pin      : out std_logic;
            slow_1_trigger_pin      : out std_logic;
            slow_2_trigger_pin      : out std_logic;
            slow_3_trigger_pin      : out std_logic;
            slow_4_trigger_pin      : out std_logic;
            W7X_permission_out_pin  : out std_logic;
            fast_1_trigger_pin      : out std_logic;
            fast_1_permission_1_pin : out std_logic;
            fast_1_duration_1_pin   : out std_logic;
            fast_1_permission_2_pin : out std_logic;
            fast_1_duration_2_pin   : out std_logic;
            fast_2_trigger_pin      : out std_logic;
            fast_2_permission_1_pin : out std_logic;
            fast_2_duration_1_pin   : out std_logic;
            fast_2_permission_2_pin : out std_logic;
            fast_2_duration_2_pin   : out std_logic
        );

    end component outputs;

    signal adc_clk                 : std_logic                     := '0';
    signal GPI_safe_state_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal slow_1_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal slow_2_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal slow_3_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal slow_4_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal W7X_permission_out_ctl  : std_logic_vector(11 downto 0) := (others => '0');
    signal fast_1_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_1_permission_1_ctl : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_1_duration_1_ctl   : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_1_permission_2_ctl : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_1_duration_2_ctl   : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_2_trigger_ctl      : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_2_permission_1_ctl : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_2_duration_1_ctl   : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_2_permission_2_ctl : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_2_duration_2_ctl   : std_logic_vector(31 downto 0) := (others => '0');


    signal GPI_safe_state_pin      : std_logic :=  '0';
    signal slow_1_trigger_pin      : std_logic :=  '0';
    signal slow_2_trigger_pin      : std_logic :=  '0';
    signal slow_3_trigger_pin      : std_logic :=  '0';
    signal slow_4_trigger_pin      : std_logic :=  '0';
    signal W7X_permission_out_pin  : std_logic :=  '0';
    signal fast_1_trigger_pin      : std_logic :=  '0';
    signal fast_1_permission_1_pin : std_logic :=  '0';
    signal fast_1_duration_1_pin   : std_logic :=  '0';
    signal fast_1_permission_2_pin : std_logic :=  '0';
    signal fast_1_duration_2_pin   : std_logic :=  '0';
    signal fast_2_trigger_pin      : std_logic :=  '0';
    signal fast_2_permission_1_pin : std_logic :=  '0';
    signal fast_2_duration_1_pin   : std_logic :=  '0';
    signal fast_2_permission_2_pin : std_logic :=  '0';
    signal fast_2_duration_2_pin   : std_logic :=  '0';

    constant adc_clk_period : time := 8 ns;

begin

    uut : outputs
    port map (
        adc_clk                  => adc_clk,
        GPI_safe_state_ctl       => GPI_safe_state_ctl,
        slow_1_trigger_ctl       => slow_1_trigger_ctl,
        slow_2_trigger_ctl       => slow_2_trigger_ctl,
        slow_3_trigger_ctl       => slow_3_trigger_ctl,
        slow_4_trigger_ctl       => slow_4_trigger_ctl,
        W7X_permission_out_ctl   => W7X_permission_out_ctl,
        fast_1_trigger_ctl       => fast_1_trigger_ctl,
        fast_1_permission_1_ctl  => fast_1_permission_1_ctl,
        fast_1_duration_1_ctl    => fast_1_duration_1_ctl,
        fast_1_permission_2_ctl  => fast_1_permission_2_ctl,
        fast_1_duration_2_ctl    => fast_1_duration_2_ctl,
        fast_2_trigger_ctl       => fast_2_trigger_ctl,
        fast_2_permission_1_ctl  => fast_2_permission_1_ctl,
        fast_2_duration_1_ctl    => fast_2_duration_1_ctl,
        fast_2_permission_2_ctl  => fast_2_permission_2_ctl,
        fast_2_duration_2_ctl    => fast_2_duration_2_ctl,


        GPI_safe_state_pin       => GPI_safe_state_pin,
        slow_1_trigger_pin       => slow_1_trigger_pin,
        slow_2_trigger_pin       => slow_2_trigger_pin,
        slow_3_trigger_pin       => slow_3_trigger_pin,
        slow_4_trigger_pin       => slow_4_trigger_pin,
        W7X_permission_out_pin   => W7X_permission_out_pin,
        fast_1_trigger_pin       => fast_1_trigger_pin,
        fast_1_permission_1_pin  => fast_1_permission_1_pin,
        fast_1_duration_1_pin    => fast_1_duration_1_pin,
        fast_1_permission_2_pin  => fast_1_permission_2_pin,
        fast_1_duration_2_pin    => fast_1_duration_2_pin,
        fast_2_trigger_pin       => fast_2_trigger_pin,
        fast_2_permission_1_pin  => fast_2_permission_1_pin,
        fast_2_duration_1_pin    => fast_2_duration_1_pin,
        fast_2_permission_2_pin  => fast_2_permission_2_pin,
        fast_2_duration_2_pin    => fast_2_duration_2_pin
    );

    adc_clk_process : process
    begin
        adc_clk <= '0';
        wait for adc_clk_period / 2;
        adc_clk <= '1';
        wait for adc_clk_period / 2;
    end process;

    enable_proc_0 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 0;
        GPI_safe_state_ctl <= std_logic_vector(to_unsigned(1, GPI_safe_state_ctl'length));
        wait for adc_clk_period * 30;
        GPI_safe_state_ctl <= std_logic_vector(to_unsigned(0, GPI_safe_state_ctl'length));
    end process enable_proc_0;

    enable_proc_1 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 1;
        slow_1_trigger_ctl <= std_logic_vector(to_unsigned(1, slow_1_trigger_ctl'length));
        wait for adc_clk_period * 30;
        slow_1_trigger_ctl <= std_logic_vector(to_unsigned(0, slow_1_trigger_ctl'length));
    end process enable_proc_1;

    enable_proc_2 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 2;
        slow_2_trigger_ctl <= std_logic_vector(to_unsigned(1, slow_2_trigger_ctl'length));
        wait for adc_clk_period * 30;
        slow_2_trigger_ctl <= std_logic_vector(to_unsigned(0, slow_2_trigger_ctl'length));
    end process enable_proc_2;

    enable_proc_3 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 3;
        slow_3_trigger_ctl <= std_logic_vector(to_unsigned(1, slow_3_trigger_ctl'length));
        wait for adc_clk_period * 30;
        slow_3_trigger_ctl <= std_logic_vector(to_unsigned(0, slow_3_trigger_ctl'length));
    end process enable_proc_3;

    enable_proc_4 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 4;
        slow_4_trigger_ctl <= std_logic_vector(to_unsigned(1, slow_4_trigger_ctl'length));
        wait for adc_clk_period * 30;
        slow_4_trigger_ctl <= std_logic_vector(to_unsigned(0, slow_4_trigger_ctl'length));
    end process enable_proc_4;

    enable_proc_5 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 5;
        W7X_permission_out_ctl <= std_logic_vector(to_unsigned(1, W7X_permission_out_ctl'length));
        wait for adc_clk_period * 30;
        W7X_permission_out_ctl <= std_logic_vector(to_unsigned(0, W7X_permission_out_ctl'length));
    end process enable_proc_5;

    enable_proc_6 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 6;
        fast_1_trigger_ctl <= std_logic_vector(to_unsigned(1, fast_1_trigger_ctl'length));
        wait for adc_clk_period * 30;
        fast_1_trigger_ctl <= std_logic_vector(to_unsigned(0, fast_1_trigger_ctl'length));
    end process enable_proc_6;

    enable_proc_7 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 7;
        fast_1_permission_1_ctl <= std_logic_vector(to_unsigned(1, fast_1_permission_1_ctl'length));
        wait for adc_clk_period * 30;
        fast_1_permission_1_ctl <= std_logic_vector(to_unsigned(0, fast_1_permission_1_ctl'length));
    end process enable_proc_7;

    enable_proc_8 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 8;
        fast_1_duration_1_ctl <= std_logic_vector(to_unsigned(1, fast_1_duration_1_ctl'length));
        wait for adc_clk_period * 30;
        fast_1_duration_1_ctl <= std_logic_vector(to_unsigned(0, fast_1_duration_1_ctl'length));
    end process enable_proc_8;

    enable_proc_9 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 9;
        fast_1_permission_2_ctl <= std_logic_vector(to_unsigned(1, fast_1_permission_2_ctl'length));
        wait for adc_clk_period * 30;
        fast_1_permission_2_ctl <= std_logic_vector(to_unsigned(0, fast_1_permission_2_ctl'length));
    end process enable_proc_9;

    enable_proc_10 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 10;
        fast_1_duration_2_ctl <= std_logic_vector(to_unsigned(1, fast_1_duration_2_ctl'length));
        wait for adc_clk_period * 30;
        fast_1_duration_2_ctl <= std_logic_vector(to_unsigned(0, fast_1_duration_2_ctl'length));
    end process enable_proc_10;

    enable_proc_11 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 11;
        fast_2_trigger_ctl <= std_logic_vector(to_unsigned(1, fast_2_trigger_ctl'length));
        wait for adc_clk_period * 30;
        fast_2_trigger_ctl <= std_logic_vector(to_unsigned(0, fast_2_trigger_ctl'length));
    end process enable_proc_11;

    enable_proc_12 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 12;
        fast_2_permission_1_ctl <= std_logic_vector(to_unsigned(1, fast_2_permission_1_ctl'length));
        wait for adc_clk_period * 30;
        fast_2_permission_1_ctl <= std_logic_vector(to_unsigned(0, fast_2_permission_1_ctl'length));
    end process enable_proc_12;

    enable_proc_13 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 13;
        fast_2_duration_1_ctl <= std_logic_vector(to_unsigned(1, fast_2_duration_1_ctl'length));
        wait for adc_clk_period * 30;
        fast_2_duration_1_ctl <= std_logic_vector(to_unsigned(0, fast_2_duration_1_ctl'length));
    end process enable_proc_13;

    enable_proc_14 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 14;
        fast_2_permission_2_ctl <= std_logic_vector(to_unsigned(1, fast_2_permission_2_ctl'length));
        wait for adc_clk_period * 30;
        fast_2_permission_2_ctl <= std_logic_vector(to_unsigned(0, fast_2_permission_2_ctl'length));
    end process enable_proc_14;

    enable_proc_15 : process is
    begin  -- process enable_proc
        wait for adc_clk_period * 15;
        fast_2_duration_2_ctl <= std_logic_vector(to_unsigned(1, fast_2_duration_2_ctl'length));
        wait for adc_clk_period * 30;
        fast_2_duration_2_ctl <= std_logic_vector(to_unsigned(0, fast_2_duration_2_ctl'length));
    end process enable_proc_15;

end architecture Behavior;