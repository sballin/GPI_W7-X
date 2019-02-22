-------------------------------------------------------------------------------
-- Module to calculate a moving average for the MLP input voltage 
-- April 19th by Charlie Vincent
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity MoveAve is
  port (
    adc_clk : in std_logic;		-- adc input clock
    volt_in : in std_logic_vector(13 downto 0);
    clk_rst : in std_logic;

    volt_out : out std_logic_vector(13 downto 0)
    );

end entity MoveAve;

architecture Behavioral of MoveAve is

  signal sum   : signed(22 downto 0)   := (others => '0');

  type sig_Memory is array (0 to 127) of signed(13 downto 0);
  signal sum_Store : sig_Memory := (others => (others => '0'));

begin  -- architecture Behavioral

  -- purpose: Process to sum and store values
  -- type   : sequential
  -- inputs : adc_clk, clk_rst, volt_in
  -- outputs: sum_Store
  store_proc : process (adc_clk) is
    variable count     : integer range 0 to 127 := 0;
    variable volt_mask : signed(13 downto 0)  := (others => '0');
  begin	 -- process sum_proc
    if rising_edge(adc_clk) then	-- rising clock edge
      volt_mask := signed(volt_in);
      if clk_rst = '1' then		-- synchronous reset (active high)
	     sum_Store <= (others => (others => '0'));
	     count	  := 0;
	     sum	  <= (others => '0');
      else
	     for index in 0 to 126 loop
	       sum_Store(index + 1) <= sum_Store(index);
	     end loop;  -- index
	     sum_Store(0) <= volt_mask;
	     if count /= 127 then
	       sum	<= sum + volt_mask;
	       count := count + 1;
	     else
	       sum <= sum - sum_Store(127) + volt_mask;
	     end if;
      end if;
    end if;
  end process store_proc;

  -- purpose: Process to sum the elements
  -- type   : sequential
  -- inputs : adc_clk, clk_rst
  -- outputs: volt_out
  sum_proc : process (adc_clk) is
  begin	 -- process sum_proc
    if rising_edge(adc_clk) then	-- rising clock edge
      if clk_rst = '1' then		-- synchronous reset (active high)
	volt_out <= (others => '0');
      else
	volt_out <= std_logic_vector(shift_right(sum, 7)(13 downto 0));
      end if;
    end if;
  end process sum_proc;

end architecture Behavioral;
