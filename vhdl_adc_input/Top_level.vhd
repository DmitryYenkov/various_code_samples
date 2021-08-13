----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date:    13:31:10 12/23/2013 
-- Design Name: 
-- Module Name:    Top_level - Structural 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--                    Signal reception from ADC AD9257
--                    Clock frequency (ext. from ADC) = 448 MHz
--                    14 databits. 1 channel (8 channels later, then 3 ADCs)
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity Top_level is
port 
(
		-- system clock (200 MHz on KC705)
		SYS_CLK_P 		: in STD_LOGIC 	
;		SYS_CLK_N 		: in STD_LOGIC
		-- this sysclk is required for  IDELAYCTRL module
		-- For delay line that adjusts input signal (it is independent of input frequency)

		-- Digit 1 - ADC number (will be 1,2,3)
		-- 11 - number of ADC input channel (will be 11 ... 18 - 1st  ADC, inputs 1...8)	
;		DCO1_P 			: in  	STD_LOGIC 		-- data clock signal (differential)
;		DCO1_N 			: in  	STD_LOGIC
;		FCO1_P 			: in  	STD_LOGIC 		-- data frame signal (differential)
;		FCO1_N 			: in  	STD_LOGIC
;		D11_P 			: in  	STD_LOGIC   	-- data signal (differential) 1-wire
;		D11_N 			: in  	STD_LOGIC

;		EXT_ADC_ENBL	: in  	STD_LOGIC		-- Enable ADC recording (external)

;		SYNC_VALID_OUT		: out  	STD_LOGIC
;		TEST_BIT_C_OUT		: out  	STD_LOGIC
;		TEST_BIT_F_OUT		: out  	STD_LOGIC
;		TEST_BIT_D_OUT1	: out 	STD_LOGIC
;		TEST_BIT_D_OUT2	: out 	STD_LOGIC
);
end entity Top_level;

architecture Structural of Top_level is 

	component Sysclk_component
	port
	(
		SYS_CLK_P 		: in 	STD_LOGIC 	
;		SYS_CLK_N 		: in 	STD_LOGIC
;		MMCM_LOCKED		: out 	STD_LOGIC	-- PLL Lock flag
;		INNER_SYS_CLK	: out  	STD_LOGIC	-- Sysclk output after 
	);	
	end component Sysclk_component;

	component Temporary_IPs
	port 
	(
		ADC_DATA_CLOCK 		: in STD_LOGIC 	
;		ADC_FRAME_CLOCK 		: in STD_LOGIC
;		SYNC_VALID     				: in STD_LOGIC
;	      EXT_ADC_ENBL	            : in STD_LOGIC	
;	      ADC_WORD		                  : in	STD_LOGIC_VECTOR (15 downto 0)
	      
;	      DCO_TST					: out  	STD_LOGIC
;	      FCO_TST					: out  	STD_LOGIC
;	      SYNC_TST	      			: out  	STD_LOGIC
;	      DATA_TST1					: out  	STD_LOGIC
;	      DATA_TST2					: out  	STD_LOGIC
	);
	end component Temporary_IPs;
	
	signal sig_MMCM_LOCKED		: STD_LOGIC;	-- for providing the outputs of Sysclk_component
	signal sig_INNER_SYS_CLK		: STD_LOGIC;	-- to the inputs of ADC_component
	signal sig_TEST_BIT_C                : STD_LOGIC;
	signal sig_TEST_BIT_F                 : STD_LOGIC;
	signal sig_TEST_BIT_D                : STD_LOGIC;
	signal sig_SYNC_VALID			: STD_LOGIC;
	signal sig_ADC_WORD			: STD_LOGIC_VECTOR (15 downto 0);	
		
	component ADC_component
	port 
	(
		DCO_P 			: in  	STD_LOGIC
;		DCO_N 			: in  	STD_LOGIC
;		FCO_P 			: in  	STD_LOGIC
;		FCO_N 			: in  	STD_LOGIC
;		D1_P 				: in  	STD_LOGIC
;		D1_N 				: in  	STD_LOGIC
;		MMCM_LOCKED	: in 	STD_LOGIC		-- PLL Lock flag
;		INNER_SYS_CLK	: in  	STD_LOGIC		-- 200 MHz input for IDELAYCTRL
;		EXT_ADC_ENBL	: in  	STD_LOGIC		-- Enable data reception from ADC

;		SYNC_VALID	: out  	STD_LOGIC		-- Sync flag DCO-inner clock
;		ADC_WORD		: out	STD_LOGIC_VECTOR (15 downto 0)
;		TEST_BIT_C		: out	STD_LOGIC
;		TEST_BIT_F		: out	STD_LOGIC
	);										   
	end component ADC_component;
	
begin

	System_Clock : Sysclk_component
	port map
	(
		SYS_CLK_P 		=> SYS_CLK_P
,		SYS_CLK_N 		=> SYS_CLK_N
,		MMCM_LOCKED 	=> sig_MMCM_LOCKED
,		INNER_SYS_CLK	=> sig_INNER_SYS_CLK
	);

	ADC_1_Workflow : ADC_component
	port map
	(
		DCO_P 				=> DCO1_P
,		DCO_N 				=> DCO1_N
,		FCO_P 				=> FCO1_P
,		FCO_N 				=> FCO1_N
,		D1_P 					=> D11_P
,		D1_N 					=> D11_N
,		MMCM_LOCKED	=> sig_MMCM_LOCKED
,		INNER_SYS_CLK	=> sig_INNER_SYS_CLK
,		EXT_ADC_ENBL	=> EXT_ADC_ENBL

,		SYNC_VALID	=> sig_SYNC_VALID
,		ADC_WORD		=> sig_ADC_WORD
,		TEST_BIT_C		=> sig_TEST_BIT_C
,		TEST_BIT_F		=> sig_TEST_BIT_F
	);
	
	Tst_Output_Component : Temporary_IPs
	port map
	(
		ADC_DATA_CLOCK 		=> sig_TEST_BIT_C
,		ADC_FRAME_CLOCK 		=> sig_TEST_BIT_F
,		SYNC_VALID     				=> sig_SYNC_VALID
,	      EXT_ADC_ENBL	            => EXT_ADC_ENBL
,	      ADC_WORD		                  => sig_ADC_WORD
	      
,	      DCO_TST					=> TEST_BIT_C_OUT
,	      FCO_TST					=> TEST_BIT_F_OUT
,	      DATA_TST1	      			=> TEST_BIT_D_OUT1
,	      DATA_TST2	      			=> TEST_BIT_D_OUT2
,	      SYNC_TST					=> SYNC_VALID_OUT
	);
	
end architecture Structural;

