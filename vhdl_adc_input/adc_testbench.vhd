--------------------------------------------------------------------------------
-- Company: 
-- Engineer:
--
-- Create Date:   15:14:42 01/30/2014
-- Design Name:   
-- Module Name:   D:/Projects/FPGA/Iserdes/dco_testbench2.vhd
-- Project Name:  Iserdes
-- Target Device:  
-- Tool versions:  
-- Description:   
-- 
-- VHDL Test Bench Created by ISE for module: Top_level
-- 
-- Dependencies:
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
-- Notes: 
-- This testbench has been automatically generated using types std_logic and
-- std_logic_vector for the ports of the unit under test.  Xilinx recommends
-- that these types always be used for the top-level I/O of a design in order
-- to guarantee that the testbench will bind correctly to the post-implementation 
-- simulation model.
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
 
-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--USE ieee.numeric_std.ALL;
 
ENTITY adc_testbench IS
END adc_testbench;
 
ARCHITECTURE behavior OF adc_testbench IS 
 
    -- Component Declaration for the Unit Under Test (UUT)
 
    COMPONENT Top_level
    PORT
    (
		SYS_CLK_P 		: in  	STD_LOGIC
;		SYS_CLK_N 		: in  	STD_LOGIC
;		DCO1_P 				: in  	STD_LOGIC
;		DCO1_N 				: in  	STD_LOGIC
;		FCO1_P 				: in  	STD_LOGIC
;		FCO1_N 				: in  	STD_LOGIC
;		D11_P 				: in  	STD_LOGIC  
;		D11_N 				: in  	STD_LOGIC         
;		EXT_ADC_ENBL 	: in  	STD_LOGIC

--;   		ADC_WORD_OUT		: out	STD_LOGIC_VECTOR (15 downto 0)
;		TEST_BIT_C_OUT		: out  	STD_LOGIC
;		TEST_BIT_F_OUT		: out  	STD_LOGIC
;		TEST_BIT_D_OUT1		: out  	STD_LOGIC
;		TEST_BIT_D_OUT2		: out  	STD_LOGIC
;		SYNC_VALID_OUT		: out  	STD_LOGIC
    );
    END COMPONENT;
    

	--Inputs
	signal SYS_CLK_P 		: STD_LOGIC := '0';
	signal SYS_CLK_N 		: STD_LOGIC := '0';
	signal DCO1_P 				: STD_LOGIC := '0';
	signal DCO1_N 			: STD_LOGIC := '0';
	signal FCO1_P 				: STD_LOGIC := '0';
	signal FCO1_N 				: STD_LOGIC := '0';   
	signal D11_P 				: STD_LOGIC := '0';
	signal D11_N 				: STD_LOGIC := '0';   	
	signal EXT_ADC_ENBL 	: STD_LOGIC := '0';
	
	--Outputs
--	signal ADC_WORD_OUT		: STD_LOGIC_VECTOR (15 downto 0);	
	signal TEST_BIT_C_OUT		: STD_LOGIC;
	signal TEST_BIT_F_OUT		: STD_LOGIC;
	signal TEST_BIT_D_OUT1		: STD_LOGIC;
	signal TEST_BIT_D_OUT2		: STD_LOGIC;		
	signal SYNC_VALID_OUT		: STD_LOGIC;
	
	constant SYS_CLK_period 	: time := 5.000 ns;
	constant DCO_period 			: time := 2.198 ns;
	constant FCO_period 			: time := DCO_period*7;
	
	constant PN_SEQUENCE 	: STD_LOGIC_VECTOR(0 to 61)
	:= "00001001011001111100011011101010000100101100111110001101110101";
	--constant PN_SEQUENCE : std_logic_vector(0 to 5) := "110010";

BEGIN

	-- Instantiate the Unit Under Test (UUT)
	uut: Top_level
	PORT MAP
	(
		SYS_CLK_P 		=> SYS_CLK_P
,		SYS_CLK_N 		=> SYS_CLK_N
,		DCO1_P 			=> DCO1_P
,		DCO1_N 			=> DCO1_N
,		FCO1_P 			=> FCO1_P
,		FCO1_N 			=> FCO1_N
,		D11_P 			=> D11_P
,		D11_N 			=> D11_N                     
,		EXT_ADC_ENBL 	=> EXT_ADC_ENBL
--,		SYNC_VALID 		=> SYNC_VALID
--,		TEMP_SAMPLE		=> TEMP_SAMPLE
--,		TEST_PROC		=> TEST_PROC
--,		ADC_WORD_OUT		=> ADC_WORD_OUT
,		TEST_BIT_C_OUT		=> TEST_BIT_C_OUT
,		TEST_BIT_F_OUT		=> TEST_BIT_F_OUT
,		TEST_BIT_D_OUT1		=> TEST_BIT_D_OUT1
,		TEST_BIT_D_OUT2		=> TEST_BIT_D_OUT2
,		SYNC_VALID_OUT		=> SYNC_VALID_OUT
	);

	SYS_CLK_P <= not SYS_CLK_P after SYS_CLK_period/2;
	SYS_CLK_N <= not SYS_CLK_P;

	DCO1_P <= not DCO1_P after DCO_period/2;
	DCO1_N <= not DCO1_P;
	
	FCO1_process: process
	begin
		wait for (FCO_period/28);
		FCO1_P <= '1';
		wait for (FCO_period/2);
		FCO1_P <= '0';
		wait for (13*FCO_period/28);		
	end process FCO1_process;
	FCO1_N <= not FCO1_P;

	Data_process: process
	begin
		wait until FCO1_P = '1';
		loop	
			for j in 0 to 30 loop
				D11_P <= PN_SEQUENCE(2*j);
				wait until DCO1_P = '1';
				wait for (FCO_period/28);
				D11_P <= PN_SEQUENCE(2*j+1);
				wait until DCO1_P = '0';
				wait for (FCO_period/28);
			end loop;
		end loop;
	end process Data_process;
	D11_N <= not D11_P;

	Stimulus_process: process
	begin
	
		wait for 9 us; -- until MMCM LOCKED
	
	  	-- insert stimulus here 
		EXT_ADC_ENBL <= '1';


		
    	wait;
	end process Stimulus_process;

END;
