-------------------------------------------------------------------------------
-- Intermediate block between RP control registers and output pins
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity delay_trig is
    port (
        adc_clk             : in  std_logic                    ;
        w7x_t1_ctl          : in  std_logic_vector(31 downto 0);
        fast_delay_1_ctl    : in  std_logic_vector(31 downto 0);
        fast_delay_2_ctl    : in  std_logic_vector(31 downto 0);
        fast_duration_1_ctl : in  std_logic_vector(31 downto 0);
        fast_duration_2_ctl : in  std_logic_vector(31 downto 0);
        reset_time_ctl      : in  std_logic_vector(31 downto 0);

        fast_puff_1_pin     : out std_logic                    ;
        fast_puff_2_pin     : out std_logic                    ;
        mili_counter_out    : out std_logic_vector(31 downto 0);
        clock_counter_out   : out std_logic_vector(31 downto 0);
        w7x_t1_out          : out std_logic                    ;
        timer_started_out   : out std_logic                     
    );
end entity delay_trig;

architecture Behavioral of delay_trig is
signal timer_started : std_logic := '0';
signal mili_counter  : unsigned(31 downto 0); -- counts millis elapsed
begin
    
-- Note: each signal can only be set by one process! Disobeying this lead to unassigned signal problems.

    -- INITALIZE AND RESET TIMERS
    Pass_through_0 : process(adc_clk)
    begin
        if rising_edge(adc_clk) then
            -- When T1 is received, start timers
            if timer_started = '0' and w7x_t1_ctl /= "00000000000000000000000000000000" then
    			timer_started <= '1';
                
            -- Reset timers when the time comes
            -- reset_time_ctl should be assigned a value greater than both puffs' duration
            elsif mili_counter = unsigned(reset_time_ctl) then
                timer_started <= '0';
            end if;
        end if;
    end process Pass_through_0;

    -- INCREMENT TIMERS
    Pass_through_1 : process(adc_clk)
    variable clock_counter_local : integer range 0 to 125000 := 0 ;
    variable mili_counter_local : unsigned(31 downto 0);
    begin
        if rising_edge(adc_clk) then
        	if timer_started = '1' then
            	clock_counter_local := clock_counter_local + 1;
                clock_counter_out <= std_logic_vector(to_unsigned(clock_counter_local, clock_counter_out'length));
                -- Increment mili counter when clock timer reaches 125 MHz/1000 ms/s and reset clock timer
            	if clock_counter_local = 125000 then
            		mili_counter <= mili_counter + to_unsigned(1, mili_counter'length);
                    mili_counter_out <= std_logic_vector(mili_counter);
                    clock_counter_local := 0;
                    clock_counter_out <= std_logic_vector(to_unsigned(clock_counter_local, clock_counter_out'length));
            	end if;
            else
                mili_counter_local := to_unsigned(0, mili_counter_local'length);
                mili_counter_out <= std_logic_vector(mili_counter_local);
                mili_counter <= mili_counter_local;
                clock_counter_local := 0;
                clock_counter_out <= std_logic_vector(to_unsigned(clock_counter_local, clock_counter_out'length));
            end if;
        end if;
    end process Pass_through_1;
        
    -- PUFF 1
    Pass_through_2 : process(adc_clk)
    begin
        if rising_edge(adc_clk) then
            if mili_counter = unsigned(fast_delay_1_ctl) and timer_started = '1' then
                fast_puff_1_pin <= '1';
            elsif mili_counter = unsigned(fast_delay_1_ctl)+unsigned(fast_duration_1_ctl) or timer_started = '0' then
                fast_puff_1_pin <= '0';
            end if;
        end if;
    end process Pass_through_2;

    -- PUFF 2
    Pass_through_3 : process(adc_clk)
    begin
        if rising_edge(adc_clk) then
			if mili_counter = unsigned(fast_delay_2_ctl) and timer_started = '1' then
                fast_puff_2_pin <= '1';
            elsif mili_counter = unsigned(fast_delay_2_ctl)+unsigned(fast_duration_2_ctl) or timer_started = '0' then
                fast_puff_2_pin <= '0';
    		end if;
        end if;
    end process Pass_through_3;

    -- TRACK W7X_T1_CTL VALUE FOR SIMULATION
    Pass_through_5 : process(adc_clk)
    begin
        if rising_edge(adc_clk) then
            if w7x_t1_ctl /= "00000000000000000000000000000000" then
                w7x_t1_out <= '1';
            else
                w7x_t1_out <= '0';
            end if;
        end if;
    end process Pass_through_5;
    
    -- TRACK TIMER_STARTED VALUE FOR SIMULATION
    Pass_through_6 : process(adc_clk)
    begin
        if rising_edge(adc_clk) then
            timer_started_out <= timer_started;
        end if;
    end process Pass_through_6;

end architecture Behavioral;
