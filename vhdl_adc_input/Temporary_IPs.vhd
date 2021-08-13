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
		ADC_DATA_CLOCK 		: in STD_LOGIC	
;		ADC_FRAME_CLOCK 		: in STD_LOGIC
;		SYNC_VALID				: in STD_LOGIC
;        	EXT_ADC_ENBL	            : in STD_LOGIC
;       	ADC_WORD		                  : in	STD_LOGIC_VECTOR (15 downto 0)
        	
;	      DCO_TST					: out  	STD_LOGIC
;	      FCO_TST					: out  	STD_LOGIC
;	      SYNC_TST	      			: out  	STD_LOGIC
;	      DATA_TST1					: out  	STD_LOGIC
;	      DATA_TST2					: out  	STD_LOGIC
     	);
end entity Temporary_IPs;

architecture Structural of Temporary_IPs is

	-- IPCore Counter Binary
	component c_counter_binary_v11_0_0
	port
	(
		  clk : IN STD_LOGIC
	;        ce : IN STD_LOGIC
	;        thresh0 : OUT STD_LOGIC
	);
	end component c_counter_binary_v11_0_0;
    
	-- IPCore Counter Binary
	component c_counter_binary_v11_0_1
	port
	(
        clk : IN STD_LOGIC
;        ce : IN STD_LOGIC
;        thresh0 : OUT STD_LOGIC
	);
	end component c_counter_binary_v11_0_1;
        
	signal sig_DCO_DIV				: STD_LOGIC; -- Divided ADC Data Clock frequency (but with no 50% duty cycle)
	signal sig_LOOPBACK_C			: STD_LOGIC;
	signal sig_LOOPBACK_INV_C	: STD_LOGIC;
	signal sig_COUNT_OUT_C		: STD_LOGIC;
	
	signal sig_FCO_DIV				: STD_LOGIC; -- Divided ADC Frame Clock frequency (but with no 50% duty cycle)
	signal sig_LOOPBACK_F			: STD_LOGIC;
	signal sig_LOOPBACK_INV_F	: STD_LOGIC;
	signal sig_COUNT_OUT_F		: STD_LOGIC;
	
	signal sig_DATA_BIT1				: STD_LOGIC;
	signal sig_DATA_BIT2				: STD_LOGIC;
	
begin
	
	sig_LOOPBACK_INV_C 	<= not sig_LOOPBACK_C;
	sig_LOOPBACK_INV_F 	<= not sig_LOOPBACK_F;
	sig_DATA_BIT1				<= ADC_WORD(8);
	sig_DATA_BIT2				<= ADC_WORD(0);

	-- Instantiation of Counter Binary IPCore for ADC Data Clock Division
	DCO_counter: c_counter_binary_v11_0_0
	port map
	(
   		clk     		=> ADC_DATA_CLOCK
,       	thresh0 	=> sig_COUNT_OUT_C
,       	ce      		=> EXT_ADC_ENBL
	);
	
	-- Instantiation of Counter Binary IPCore for ADC Frame Clock Division
	FCO_counter: c_counter_binary_v11_0_1
	port map
	(
   		clk     		=> ADC_FRAME_CLOCK
,        	thresh0 	=> sig_COUNT_OUT_F
,       	ce      		=> EXT_ADC_ENBL
	);	
	
	-- Instantiation of D-Flip-Flop for ADC Data Clock
	-- conversion to meander (50% duty cycle)
	-- Feed forward signal
	FDCE_Out_C_inst : FDCE
	generic map
	(
		INIT => '0'		-- Initial value of register ('0' or '1')  
	) 
	port map
	(
		Q 		=> sig_DCO_DIV,      -- Data output
		C 		=> sig_COUNT_OUT_C,      -- Clock input
		CE 	=> '1',    -- Clock enable input
		CLR 	=> '0',  -- Asynchronous clear input
		D 		=> sig_LOOPBACK_INV_C       -- Data input
	);							

	-- Instantiation of D-Flip-Flop for ADC Data Clock
	-- conversion to meander (50% duty cycle)
	-- Feed back signal
	FDCE_LoopBack_C_inst : FDCE
	generic map
	(
		INIT => '0'		-- Initial value of register ('0' or '1')  
	) 
	port map
	(
		Q 		=> sig_LOOPBACK_C,      -- Data output
		C 		=> sig_COUNT_OUT_C,      -- Clock input
		CE 	=> '1',    -- Clock enable input
		CLR 	=> '0',  -- Asynchronous clear input
		D 		=> sig_DCO_DIV       -- Data input
	);						

	-- Output Buffer Instantiation  for ADC Data Clock
	OBUF_C_inst : OBUF
	generic map
	(
		DRIVE 			=> 12,
		IOSTANDARD 	=> "LVCMOS18",
		SLEW 			=> "FAST"
	)
	port map 
	(
		O 	=> DCO_TST,     -- Buffer output (connect directly to top-level port)
		I 	=> ADC_DATA_CLOCK--sig_DCO_DIV--sig_Q_OUTS(CountWidth-1)      -- Buffer input 
	);

	-- Instantiation of D-Flip-Flop for ADC Frame Clock
	-- conversion to meander (50% duty cycle)
	-- Feed forward signal	
	FDCE_Out_F_inst : FDCE
	generic map
	(
		INIT => '0'		-- Initial value of register ('0' or '1')  
	) 
	port map
	(
		Q 		=> sig_FCO_DIV,      -- Data output
		C 		=> sig_COUNT_OUT_F,      -- Clock input
		CE 	=> '1',    -- Clock enable input
		CLR 	=> '0',  -- Asynchronous clear input
		D 		=> sig_LOOPBACK_INV_F       -- Data input
	);							

	-- Instantiation of D-Flip-Flop for ADC Frame Clock
	-- conversion to meander (50% duty cycle)
	-- Feed back signal
	FDCE_LoopBack_F_inst : FDCE
	generic map
	(
		INIT => '0'		-- Initial value of register ('0' or '1')  
	) 
	port map
	(
		Q 		=> sig_LOOPBACK_F,      -- Data output
		C 		=> sig_COUNT_OUT_F,      -- Clock input
		CE 	=> '1',    -- Clock enable input
		CLR 	=> '0',  -- Asynchronous clear input
		D 		=> sig_FCO_DIV       -- Data input
	);						

	-- Output Buffer Instantiation  for ADC Frame Clock
	OBUF_F_inst : OBUF
	generic map
	(
		DRIVE 			=> 12,
		IOSTANDARD	=> "LVCMOS18",
		SLEW 			=> "FAST"
	)
	port map 
	(
		O 	=> FCO_TST,     -- Buffer output (connect directly to top-level port)
		I 	=> ADC_FRAME_CLOCK--sig_FCO_DIV--sig_Q_OUTS(CountWidth-1)      -- Buffer input 
	);

	-- Output Buffer Instantiation  for ADC Clock Sync Valid Signal	
	OBUF_S_inst : OBUF
	generic map
	(
		DRIVE 			=> 12,
		IOSTANDARD 	=> "LVCMOS18",
		SLEW 			=> "FAST"
	)
	port map 
	(
		O 	=> SYNC_TST,     -- Buffer output (connect directly to top-level port)
		I 	=> SYNC_VALID  -- Buffer input 
	);			

	-- Output Buffer Instantiation  for ADC Data Reception Module Test Bit Output
	OBUF_D1_inst : OBUF
	generic map
	(
		DRIVE 			=> 12,
		IOSTANDARD 	=> "LVCMOS18",
		SLEW 			=> "FAST"
	)
	port map 
	(
		O 	=> DATA_TST1,     -- Buffer output (connect directly to top-level port)
		I 	=> sig_DATA_BIT1--      -- Buffer input 
	);			
	
	OBUF_D2_inst : OBUF
	generic map
	(
		DRIVE 			=> 12,
		IOSTANDARD 	=> "LVCMOS18",
		SLEW 			=> "FAST"
	)
	port map 
	(
		O 	=> DATA_TST2,     -- Buffer output (connect directly to top-level port)
		I 	=> sig_DATA_BIT2--      -- Buffer input 
	);				

end architecture Structural;
