-------------------------------------------------------------------------------
-- Test bench for output block
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity trig_delay_tb is

end entity trig_delay_tb;

architecture Behavior of trig_delay_tb is

    component delay_trig is
        port (
            adc_clk             : in  std_logic                    ;
            w7x_t1_ctl          : in  std_logic_vector(31 downto 0);
            fast_delay_1_ctl    : in  std_logic_vector(31 downto 0);
            fast_delay_2_ctl    : in  std_logic_vector(31 downto 0);
            fast_duration_1_ctl : in  std_logic_vector(31 downto 0);
            fast_duration_2_ctl : in  std_logic_vector(31 downto 0);
            reset_time_ctl      : in  std_logic_vector(31 downto 0);

            w7x_t1_out          : out std_logic                    ;
            fast_puff_1_pin     : out std_logic                    ;
            fast_puff_2_pin     : out std_logic                    ;
            mili_counter_out    : out std_logic_vector(31 downto 0);
            clock_counter_out   : out std_logic_vector(31 downto 0);
            timer_started_out   : out std_logic
        );
    end component delay_trig;

    signal adc_clk                 : std_logic                     := '0';
    signal w7x_t1_ctl              : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_delay_1_ctl        : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_delay_2_ctl        : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_duration_1_ctl     : std_logic_vector(31 downto 0) := (others => '0');
    signal fast_duration_2_ctl     : std_logic_vector(31 downto 0) := (others => '0');
    signal reset_time_ctl          : std_logic_vector(31 downto 0) := (others => '0');
    signal w7x_t1_out              : std_logic                     := '0';
    signal fast_puff_1_pin         : std_logic                     := '0';
    signal fast_puff_2_pin         : std_logic                     := '0';
    signal mili_counter_out        : std_logic_vector(31 downto 0) := (others => '0');
    signal clock_counter_out       : std_logic_vector(31 downto 0) := (others => '0');
    signal timer_started_out       : std_logic := '0';

    constant adc_clk_period : time := 8 ns;

begin

    uut : delay_trig
        port map (
            adc_clk             => adc_clk            ,
            w7x_t1_ctl          => w7x_t1_ctl         ,
            fast_delay_1_ctl    => fast_delay_1_ctl   ,
            fast_delay_2_ctl    => fast_delay_2_ctl   ,
            fast_duration_1_ctl => fast_duration_1_ctl,
            fast_duration_2_ctl => fast_duration_2_ctl,
            reset_time_ctl      => reset_time_ctl     ,
            w7x_t1_out          => w7x_t1_out         ,
            fast_puff_1_pin     => fast_puff_1_pin    ,
            fast_puff_2_pin     => fast_puff_2_pin    ,
            mili_counter_out    => mili_counter_out   ,
            clock_counter_out   => clock_counter_out  ,
            timer_started_out   => timer_started_out   
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
        
        w7x_t1_ctl <= "00000000000000000000000000000000";
        fast_delay_1_ctl <= "00000000000000000000000000000000";
        fast_delay_2_ctl <= "00000000000000000000000000000000";
        fast_duration_1_ctl <= "00000000000000000000000000000000";
        fast_duration_2_ctl <= "00000000000000000000000000000000";
        reset_time_ctl <= "00000000000000000000000000000000";
        
        wait for adc_clk_period * 10;
        
        w7x_t1_ctl <= std_logic_vector(to_unsigned(1, w7x_t1_ctl'length));
        fast_delay_1_ctl <= std_logic_vector(to_unsigned(1, w7x_t1_ctl'length));
        fast_delay_2_ctl <= std_logic_vector(to_unsigned(3, w7x_t1_ctl'length));
        fast_duration_1_ctl <= std_logic_vector(to_unsigned(1, w7x_t1_ctl'length));
        fast_duration_2_ctl <= std_logic_vector(to_unsigned(1, w7x_t1_ctl'length));
        reset_time_ctl <= std_logic_vector(to_unsigned(5, w7x_t1_ctl'length));
        
        wait for adc_clk_period * 1;
        -- Finish T1 pulse by setting back to 0
        w7x_t1_ctl <= std_logic_vector(to_unsigned(0, w7x_t1_ctl'length));
        
        wait for adc_clk_period * 125000*6; -- all of above will repeat after 6 ms
        
    end process enable_proc_0;

end architecture Behavior;
