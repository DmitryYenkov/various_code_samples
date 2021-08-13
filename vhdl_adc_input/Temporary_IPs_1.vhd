----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date:    05-03-2014 
-- Design Name: 
-- Module Name:    Temporary IP Cores  - Structural 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--                  This module is for usage with KC705 EVALB - for outputs
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--					Moved down from Top_level
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity Temporary_IPs is
    port 
	(
		ADC_DATA_CLOCK 		     : in STD_LOGIC; 	
		ADC_FRAME_CLOCK 		: in STD_LOGIC;
        	EXT_ADC_ENBL	               : in  	STD_LOGIC;	
        	ADC_WORD		                  : in	STD_LOGIC_VECTOR (15 downto 0);
        	DCO_DIV						: out  	STD_LOGIC;
        	FCO_DIV						: out  	STD_LOGIC
	);
end entity Temporary_IPs;

architecture Structural of Temporary_IPs is

constant CountWidth : integer := 5;

    component c_counter_binary_v11_0_0
    port
    (
        clk : IN STD_LOGIC;
        ce : IN STD_LOGIC;
        q : OUT STD_LOGIC_VECTOR(CountWidth-1 DOWNTO 0)
    );
    end component c_counter_binary_v11_0_0;
    
	signal sig_DCO_DIV	: STD_LOGIC; -- Divided ADC Clock frequency (but with no 50% duty cycle)
	signal sig_LOOPBACK	: STD_LOGIC;
	signal sig_LOOPBACK_INV	: STD_LOGIC;
	signal sig_Q_OUTS			: STD_LOGIC_VECTOR(CountWidth-1 DOWNTO 0);
	
begin
	
	sig_LOOPBACK_INV <= not sig_LOOPBACK;

	DCO_counter: c_counter_binary_v11_0_0
	port map
	(
   		clk     => ADC_DATA_CLOCK,
       	q        => sig_Q_OUTS,
       	ce      => EXT_ADC_ENBL
	);
	
--	FDCE_Out_inst : FDCE
--	generic map
--	(
--		INIT => '0'		-- Initial value of register ('0' or '1')  
--	) 
--	port map
--	(
--		Q 		=> sig_DCO_DIV,      -- Data output
--		C 		=> sig_COUNT_OUT,      -- Clock input
--		CE 	=> '1',    -- Clock enable input
--		CLR 	=> '0',  -- Asynchronous clear input
--		D 		=> sig_LOOPBACK_INV       -- Data input
--	);							

--	FDCE_LoopBack_inst : FDCE
--	generic map
--	(
--		INIT => '0'		-- Initial value of register ('0' or '1')  
--	) 
--	port map
--	(
--		Q 		=> sig_LOOPBACK,      -- Data output
--		C 		=> sig_COUNT_OUT,      -- Clock input
--		CE 	=> '1',    -- Clock enable input
--		CLR 	=> '0',  -- Asynchronous clear input
--		D 		=> sig_DCO_DIV       -- Data input
--	);						

	OBUF_inst : OBUF
	generic map
	(
		DRIVE => 12,
		IOSTANDARD => "LVCMOS12",
		SLEW => "FAST"
	)
	port map 
	(
		O => DCO_DIV,     -- Buffer output (connect directly to top-level port)
		I => sig_Q_OUTS(CountWidth-1)      -- Buffer input 
	);

end architecture Structural;
