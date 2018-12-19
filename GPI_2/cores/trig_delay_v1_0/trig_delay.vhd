-------------------------------------------------------------------------------
-- Intermediate block between RP control registers and output pins
-------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity delay_trig is

    port (
        adc_clk                 : in std_logic;
        w7x_ctl                 : in std_logic;
        trigger_1_delay         : in std_logic_vector(31 downto 0);
        trigger_2_delay         : in std_logic_vector(31 downto 0);
        trigger_1_duration      : in std_logic_vector(31 downto 0);
        trigger_2_duration      : in std_logic_vector(31 downto 0);
        reset_trig_time 		: in std_logic_vector(31 downto 0);


        trigger_1_out           : out std_logic;
        trigger_2_out           : out std_logic
    );

end entity delay_trig;

architecture Behavioral of delay_trig is
signal w7x_ctl_go : std_logic := '0';
begin

    Pass_through_0 : process(adc_clk)
    variable delay_counter : integer range 0 to 125000 := 0 ;
    variable mili_delay_timer :integer range 0 to 100000 := 0;
    begin
        if (rising_edge(adc_clk)) then
        	if (w7x_ctl = '1') then
        		if (w7x_ctl_go = '0') then
        			delay_counter := 0;
        			mili_delay_timer := 0;
        			w7x_ctl_go <= '1';
        			trigger_1_out <= '0';
        			trigger_2_out <= '0';
        		end if;
        	end if;

        	if (w7x_ctl_go = '1') then
            	delay_counter := delay_counter + 1;
            	if (delay_counter = 125000) then
            		delay_counter := 0;
            		mili_delay_timer := mili_delay_timer + 1;
            	end if;
        
        		--Control valve 1
        		if (mili_delay_timer = to_integer(unsigned(trigger_1_delay))) then
                	trigger_1_out <= '1';
        		elsif (mili_delay_timer = to_integer(unsigned(trigger_1_delay)+unsigned(trigger_1_duration))) then
                	trigger_1_out <= '0';
        		end if;

        		--Control valve 2
				if (mili_delay_timer = to_integer(unsigned(trigger_2_delay))) then
                	trigger_2_out <= '1';
        		elsif (mili_delay_timer = to_integer(unsigned(trigger_2_delay)+unsigned(trigger_2_duration))) then
                	trigger_2_out <= '0';
                	w7x_ctl_go <= '0';
        		end if;

        		--Trigger Reset
        		if (mili_delay_timer = to_integer(unsigned(reset_trig_time))) then
        			w7x_ctl_go <= '0';
        			delay_counter := 0;
        			mili_delay_timer := 0;
        		end if;
			end if;
		end if;


    end process Pass_through_0;
    

end architecture Behavioral;