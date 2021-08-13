----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date:    05-03-2014 
-- Design Name: 
-- Module Name:    ADC - Structural 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--                 ADC Module
-- Dependencies: 
--					DCO_PLL_component - Behavioral, ADC_Data_component - Behavioral
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--					Will be included tp Top Level as a component. It is a structural description.
-- 					Consists of DCO sync module - for sync DCO input and 
--					internal DCO after input buffer and routing to ISERDES
--					and of Data reception module (will be 8 - all channels)
--					Behavioral models - in dedicated files.
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity ADC_component is
	port 
	(
		-- 1 - ADC data input channel number (will be 1...8)
		DCO_P 			: in  	STD_LOGIC 		-- clock signal (diff)
;		DCO_N 			: in  	STD_LOGIC
;		FCO_P 			: in  	STD_LOGIC 		-- frame signal (diff)
;		FCO_N 			: in  	STD_LOGIC
;		D1_P 				: in  	STD_LOGIC   	-- data signal (diff, 1-wire, DDR)
;		D1_N 				: in  	STD_LOGIC

		-- From SYSTEM Clock
;		MMCM_LOCKED	: in 	STD_LOGIC		-- 
;		INNER_SYS_CLK	: in  	STD_LOGIC		-- SYS CLK 200 MHz for IDELAYCTRL
		
;		EXT_ADC_ENBL	: in  	STD_LOGIC		-- Enable ADC data reception

;		SYNC_VALID	: out  	STD_LOGIC		-- Sync flag DCO-inner clock
;		ADC_WORD		: out	STD_LOGIC_VECTOR (15 downto 0)
;		TEST_BIT_C		: out	STD_LOGIC
;		TEST_BIT_F		: out	STD_LOGIC
	);										   
end entity ADC_component;

architecture Structural of ADC_component is

	component DCO_PLL_component
	port 
	(
		-- these outputs are for use of ISERDES in data reception
		ADC_DCO_SYNC_OUT	: out 	STD_LOGIC		-- Delay Line output after BUFIO
;		ADC_DCO_BUFR7_OUT	: out 	STD_LOGIC		-- Delay Line output after BUFR (divided freq.)
;		SYNC_VALID				: out	STD_LOGIC		-- Sync event flag - DCO after IBUFDS is in sync 
                                                                                			-- with DCO after delay line and BUFIO
;		DCO_P 					: in  	STD_LOGIC 		-- input clock signal (differential)
;		DCO_N 					: in  	STD_LOGIC
;		MMCM_LOCKED		: in 	STD_LOGIC		-- Internal clock lock (in MMCM) flag
;		INNER_SYS_CLK		: in  	STD_LOGIC		-- 200 MHz input for  IDELAYCTRL
;		EXT_ADC_ENBL		: in  	STD_LOGIC		-- ADC enable signal 
	);						 
	end component DCO_PLL_component;

	component FCO_PLL_component is
	port 
	(
		FCO_P 				: in STD_LOGIC 	-- frame clock input
;		FCO_N 				: in STD_LOGIC
;		EXT_ADC_ENBL	: in STD_LOGIC		-- enables data recording from ADC
;		SYNC_VALID		: out STD_LOGIC	-- PLL Lock flag
;		FRAME_CLK			: out STD_LOGIC	
 	);
    end component FCO_PLL_component;

	component ADC_Data_component
	port 
	(
		-- these intputs are for use of ISERDES in data reception
		ADC_DCO_SYNC_IN	: in 	STD_LOGIC	-- Delay Line output after BUFIO
;        	ADC_FCO_IN			: in 	STD_LOGIC	-- Delay Line output after BUFIO
;		D1_P 						: in  	STD_LOGIC   	-- data channel (differential, 1-wire)
;		D1_N 						: in  	STD_LOGIC		-- (supposed to be 8 of them in future)
;		SYNC_VALID			: in  	STD_LOGIC		-- Sync event flag (see above)

;		D1_WORD				: out	STD_LOGIC_VECTOR (15 downto 0)
	);
	end component ADC_Data_component;

	signal sig_SYNC_VALID					: STD_LOGIC;
	signal sig_DCO_SYNC_FLAG			: STD_LOGIC;
	signal sig_FCO_SYNC_FLAG			: STD_LOGIC;
	signal sig_ADC_DCO_SYNC_OUT		: STD_LOGIC;
	signal sig_ADC_DCO_BUFR7_OUT	: STD_LOGIC;
	
begin

	sig_SYNC_VALID 		<= sig_DCO_SYNC_FLAG and sig_FCO_SYNC_FLAG;
	SYNC_VALID 			<= sig_SYNC_VALID;
	TEST_BIT_C				<= sig_ADC_DCO_BUFR7_OUT;

	DCO_Syncronization : DCO_PLL_component
	port map
	(
		ADC_DCO_SYNC_OUT	=> sig_ADC_DCO_SYNC_OUT	
,		ADC_DCO_BUFR7_OUT 	=> sig_ADC_DCO_BUFR7_OUT
			
,		DCO_P 				=> DCO_P
,		DCO_N 				=> DCO_N
		
,		MMCM_LOCKED 		=> MMCM_LOCKED
,		INNER_SYS_CLK		=> INNER_SYS_CLK
		
,		EXT_ADC_ENBL		=> EXT_ADC_ENBL
		
,		SYNC_VALID			=> sig_DCO_SYNC_FLAG
	);	
	
	FCO_Syncronization : FCO_PLL_component
	port map
	(
		FCO_P 				=> FCO_P
,		FCO_N 				=> FCO_N
,		EXT_ADC_ENBL	=> EXT_ADC_ENBL
,		SYNC_VALID		=> sig_FCO_SYNC_FLAG
,      	FRAME_CLK             => TEST_BIT_F
	);
	
	Data_Reception : ADC_Data_component
	port map 
	(
		ADC_DCO_SYNC_IN	=> sig_ADC_DCO_SYNC_OUT	
,       	ADC_FCO_IN			=> sig_ADC_DCO_BUFR7_OUT
,		D1_P 						=> D1_P
,		D1_N 						=> D1_N
,		SYNC_VALID			=> sig_SYNC_VALID
,		D1_WORD				=> ADC_WORD
	);

end architecture Structural;
