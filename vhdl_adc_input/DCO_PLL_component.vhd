----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date: 05.03.2014 13:06:50
-- Design Name: 
-- Module Name: DCO_PLL_component - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 				Clock syncronization module. For edge alignement
--              of input CLK signal after IBUFDS and the same one being 
--				introduced into a region clock circuits after BUFIO
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity DCO_PLL_component is
port 
	(
		-- Delay Line IDELAY outputs
		ADC_DCO_SYNC_OUT	: out STD_LOGIC      -- for clocking data 
;		ADC_DCO_BUFR7_OUT		: out STD_LOGIC	-- divided by 4 for syncronization
	
;		DCO_P 			: in  	STD_LOGIC 		-- input clock differential
;		DCO_N 			: in  	STD_LOGIC

		-- signals from System Clk MMCM
;		MMCM_LOCKED		: in 	STD_LOGIC		-- 
;		INNER_SYS_CLK	: in  	STD_LOGIC		-- 200 MHz for IDELAYCTRL
		-- external manual enable
;		EXT_ADC_ENBL	: in  	STD_LOGIC		-- enables dadta recording from ADC
		
		-- output
;		SYNC_VALID		: out  	STD_LOGIC		-- Sync event flag
	);					
end entity DCO_PLL_component;

architecture Behavioral of DCO_PLL_component is

	-- Signals for IDELAYCTRL primitive
	signal IDELCTRL_RDY			: STD_LOGIC; 	-- output of IDELAYCTRL
	signal IDELCTRL_RST			: STD_LOGIC; 	-- reset (input) of IDELAYCTRL
	signal DCO_SYNC_RST			: STD_LOGIC;	-- combined signal - internal ready and external enable
	
	attribute IODELAY_GROUP 	: string;
	-- Assignement of DCO delay line to IDELAYCTRL in the same IOBank
	attribute IODELAY_GROUP of ADC_IDELCTRL_inst	: label is "ACD_IDELGRP";	
	attribute IODELAY_GROUP of ADC_DCO_IDEL_inst	: label is "ACD_IDELGRP";
		
	-- Signals for  DCO delay tuning logic
	signal ADC_DCO				: STD_LOGIC;	-- acoording to xapp1071 - from IBUFDS to IDELAYE2
	signal ADC_DCO_IDELOUT		: STD_LOGIC;	-- Delay line output (input to clock buffers
	signal ADC_DCO_DIV7		: STD_LOGIC;
	signal ADC_DCO_ISRDS_OOUT	: STD_LOGIC;
	signal sig_BUFR_OUT			: STD_LOGIC;	-- BUFR output (divided)
	signal sig_BUFIO_OUT		: STD_LOGIC;
	-- The following signal are for control logic
	signal ADC_OUT_Q1			: STD_LOGIC;	--  ISERDES outputs
	signal ADC_OUT_Q2			: STD_LOGIC;
	signal ADC_OUT_Q3			: STD_LOGIC;
	signal ADC_OUT_Q4			: STD_LOGIC;
	signal ADC_OUT_Q5			: STD_LOGIC;
	signal ADC_OUT_Q6			: STD_LOGIC;
	signal ADC_OUT_Q7			: STD_LOGIC;
	signal ADC_OUT_Q8			: STD_LOGIC;

	signal ADC_IODEL_INC		: STD_LOGIC := '0';
	signal ADC_IODEL_CE			: STD_LOGIC := '1';
	signal ADC_Q_AND			: STD_LOGIC;	-- Signals, composed from Q-outputs of ISERDES
	signal ADC_Q_OR				: STD_LOGIC;
	
	signal NEG_MMCM_LOCKED		: STD_LOGIC;
	
begin

	NEG_MMCM_LOCKED 	<= not MMCM_LOCKED;
	ADC_DCO_SYNC_OUT	<= sig_BUFIO_OUT;

	IDELCTRL_RST_DELAY_inst : SRLC32E
	--  IDELAYCTRL reset delay (32 clock pulses) in case of MMCM lock fail
	generic map
	(
		INIT 	=> X"00000000"
	)
	port map
	(
		Q 		=> open,        			-- SRL data output
		Q31 	=> IDELCTRL_RST,    		-- SRL cascade output pin
		A 		=> "00000",        			-- 5-bit shift depth select input
		CE 		=> '1',      				-- Clock enable input
		CLK 	=> INNER_SYS_CLK,    		-- Clock input
		D 		=> NEG_MMCM_LOCKED         	-- SRL data input
	);

	ADC_IDELCTRL_inst : IDELAYCTRL
	-- IODELAY Control Unit for definite IOBlock (ADC) - one of 3 total in future
	port map
	(
		RDY 	=> IDELCTRL_RDY,       		-- 1-bit output indicates validity of the REFCLK
		-- this signal itself is not used directly
		REFCLK 	=> INNER_SYS_CLK, 	-- 1-bit reference clock input
		RST 	=> IDELCTRL_RST     -- 1-bit reset input
	);

	ADC_DCO_IBUFDS_inst : IBUFDS
	-- ADC Data Clock input
	generic map
	(
		DIFF_TERM 		=> TRUE, 	-- Differential Termination
		-- terminal resistor is enabled because of LVDS interface
		IBUF_LOW_PWR 	=> FALSE, 	-- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
		-- fist of all - perfomance. Power saving - will see later.
		IOSTANDARD 		=> "LVDS_25"
	)
	port map
	(
		O 	=> ADC_DCO,  	-- Buffer output
		I 	=> DCO_P,  		-- Diff_p buffer input (connect directly to top-level port)
		IB 	=> DCO_N 		-- Diff_n buffer input (connect directly to top-level port)
	);

	ADC_DCO_IDEL_inst : IDELAYE2
	-- Delay line aacording to xapp524 (fig.6)
	generic map
	(
		CINVCTRL_SEL 				=>"FALSE",       -- Enable dynamic clock inversion ("TRUE"/"FALSE")
		DELAY_SRC 					=> "IDATAIN",         -- Delay input 
		HIGH_PERFORMANCE_MODE 		=> "TRUE", 		-- Reduced jitter ("TRUE"), Reduced power ("FALSE")
		IDELAY_TYPE 				=> "VARIABLE", 
		-- VARIABLE - because we will tune the leday by means of control logic -  finite state machine
		IDELAY_VALUE 				=> 0,           -- Input delay tap setting (0-32)
		REFCLK_FREQUENCY 			=> 200.0,       -- IDELAYCTRL clock input frequency in MHz
		-- the frequency from MMCM
		SIGNAL_PATTERN 				=> "CLOCK",        -- "DATA" or "CLOCK" input signal
		PIPE_SEL                          => "FALSE"
	)
	port map
	(
		CNTVALUEOUT 	=> open, 				-- 5-bit output - Counter value for monitoring purpose
		DATAOUT 		=> ADC_DCO_IDELOUT,		-- 1-bit output - Delayed data output
		C 				=> sig_BUFR_OUT,		-- 1-bit input - Clock input
		-- There is a feedback from BUFR. Clock signal for self-tuning (automatic lock)
		CE 				=> ADC_IODEL_CE,      	-- 1-bit input - Active high enable increment/decrement function
		-- from FSM logic
		CINVCTRL 		=> '0',       			-- 1-bit input - Dynamically inverts the Clock (C) polarity
		CNTVALUEIN 		=> "00000",   			-- 5-bit input - Counter value for loadable counter application
		DATAIN 			=> '0',           		-- 1-bit input - Internal delay data
		IDATAIN 		=> ADC_DCO,         	-- 1-bit input - Delay data input
		INC 			=> ADC_IODEL_INC,  		-- 1-bit input - Increment / Decrement tap delay
		-- from FSM logic
		REGRST 			=> '0',   		-- Reset for PIPELINE - used only in VAR_LOAD_PIPE mode
		-- it is very strange cause in xapp 524 there is an RST signal, but actually we may be not needed it. We'll see
		LD                       => '0',
		LDPIPEEN        => '0'
	);
	
	ADC_DCO_BUFIO_inst : BUFIO
	--Output of this primitive is the output clock for ADC data
	port map
	(
		O 	=> sig_BUFIO_OUT, 		-- 1-bit output: Clock output port (connect to I/O clock loads)
		I 	=> ADC_DCO_IDELOUT--ADC_DCO_ISRDS_OOUT  	-- 1-bit input
	);
	
	ADC_DCO_BUFR_DIV4_inst : BUFR
	-- Feedback signal for IDELAYE2 and ISERDESE2. Clocking for delay self-tuning logic.
	generic map
	(
		BUFR_DIVIDE 	=> "4",		-- "BYPASS", "1", "2", "3", "4", "5", "6", "7", "8"
		-- it should correspond  ISERDES DATA_WIDTH
		SIM_DEVICE 	=> "7SERIES"
	)   
	port map
	(
		O 		=> sig_BUFR_OUT,   	-- 1-bit output: Clock output port
		CE 		=> '1',   				-- 1-bit input: Active high, clock enable (Divided modes only)
		CLR 	=> '0', 				-- 1-bit input: Active high, asynchronous clear (Divided mode only)
		I 		=> ADC_DCO_IDELOUT--ADC_DCO_ISRDS_OOUT   	-- 1-bit input: Clock buffer input driven by an IBUFG, MMCM or local interconnect
	);
	
	ADC_DCO_BUFR_DIV7_inst : BUFR
	-- Feedback signal for IDELAYE2 and ISERDESE2. Clocking for delay self-tuning logic.
	generic map
	(
		BUFR_DIVIDE 	=> "7",		-- "BYPASS", "1", "2", "3", "4", "5", "6", "7", "8"
		-- it should correspond  ISERDES DATA_WIDTH
		SIM_DEVICE 	=> "7SERIES"
	)   
	port map
	(
		O 		=> ADC_DCO_DIV7,   	-- 1-bit output: Clock output port
		CE 		=> '1',   				-- 1-bit input: Active high, clock enable (Divided modes only)
		CLR 	=> '0', 				-- 1-bit input: Active high, asynchronous clear (Divided mode only)
		I 		=> ADC_DCO_IDELOUT--ADC_DCO_ISRDS_OOUT   	-- 1-bit input: Clock buffer input driven by an IBUFG, MMCM or local interconnect
	);	
	
	DCO_OUT_DIV7_BUFG_inst : BUFGCE
	port map
	(
	   O           => ADC_DCO_BUFR7_OUT,   -- 1-bit output: Clock output
	   CE        => EXT_ADC_ENBL, -- 1-bit input: Clock enable input for I0
	   I             => ADC_DCO_DIV7    -- 1-bit input: Primary clock
	);   	
	
	ADC_DCO_ISERDES_inst : ISERDESE2
	generic map  -- all generics coeerspond to that of ISERDESE1 of 6 series
	(
		DATA_RATE 			=> "SDR", 	-- "SDR" or "DDR" 
		DATA_WIDTH 			=> 4,      	-- Parallel data width (2-8, 10)
		DYN_CLKDIV_INV_EN	=> "FALSE", 	-- Enable DYNCLKDIVINVSEL inversion (TRUE/FALSE)
		DYN_CLK_INV_EN 		=> "FALSE",  	-- Enable DYNCLKINVSEL inversion (TRUE/FALSE)
		-- INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
		INIT_Q1 			=> '0',
		INIT_Q2 			=> '0',
		INIT_Q3 			=> '0',
		INIT_Q4 			=> '0',
		INTERFACE_TYPE 	=> "NETWORKING", 	-- "MEMORY", "MEMORY_DDR3", "MEMORY_QDR", "NETWORKING", or "OVERSAMPLE"
		IOBDELAY 			=> "NONE",	-- "NONE", "IBUF", "IFD", "BOTH"
		-- I'm not sure
		NUM_CE 				=> 1,		-- Number of clock enables (1 or 2)
		-- We have 1 clock enable input
		OFB_USED 			=> "FALSE", 	-- Select OFB path (TRUE/FALSE)
		SERDES_MODE 		=> "MASTER",-- "MASTER" or "SLAVE" 
		-- SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
		SRVAL_Q1 			=> '0',
		SRVAL_Q2 			=> '0',
		SRVAL_Q3 			=> '0',
		SRVAL_Q4 			=> '0' 
	)
	port map
	(
		O 				=> ADC_DCO_ISRDS_OOUT,			-- 1-bit output: Combinatorial output
		-- Q1 - Q6: 1-bit (each) output: Registered data outputs
		Q1 				=> ADC_OUT_Q1,
		Q2 				=> ADC_OUT_Q2,
		Q3 				=> ADC_OUT_Q3,
		Q4 				=> ADC_OUT_Q4,
		Q5 				=> ADC_OUT_Q5,
		Q6 				=> ADC_OUT_Q6,
		Q7 				=> ADC_OUT_Q7,
		Q8 				=> ADC_OUT_Q8,--open,
		-- SHIFTOUT1-SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
		SHIFTOUT1		=> open,
		SHIFTOUT2 		=> open,
		BITSLIP 		=> '0', 			-- 1-bit input: Bitslip enable input
		-- we dont care about word alignement cause this is just a clock sync - meander
		-- CE1, CE2: 1-bit (each) input: Data register clock enable inputs
		CE1 			=> '1',
		CE2 			=> '0',
		-- Clocks: 1-bit (each) input: ISERDESE1 clock input ports
		CLK 			=> sig_BUFIO_OUT,	-- 1-bit input: High-speed clock input
		-- acoording to xapp524
		CLKB 			=> '0',				-- 1-bit input: High-speed secondary clock input
		CLKDIV 			=> sig_BUFR_OUT,	-- 1-bit input: Divided clock input
		-- acoording to xapp524
		CLKDIVP 			=> '0',
		OCLK 			=> '0',				-- 1-bit input: High speed output clock input used when
		OCLKB 			=> '0',									-- INTERFACE_TYPE="MEMORY" 
		-- Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
		DYNCLKDIVSEL 	=> '0', 			-- 1-bit input: Dynamic CLKDIV inversion input
		DYNCLKSEL 		=> '0',       		-- 1-bit input: Dynamic CLK/CLKB inversion input
		-- Input Data: 1-bit (each) input: ISERDESE1 data input ports
		D 				=> ADC_DCO,    		-- 1-bit input: Data input
		-- acoording to xapp524
		DDLY 			=> ADC_DCO_IDELOUT,           	-- 1-bit input: Serial input data from IODELAYE1
		OFB 			=> '0',          	-- 1-bit input: Data feedback input from OSERDESE1
		RST 			=> DCO_SYNC_RST,	-- 1-bit input: Active high asynchronous reset input
		-- SHIFTIN1-SHIFTIN2: 1-bit (each) input: Data width expansion input ports
		SHIFTIN1 		=> '0',
		SHIFTIN2 		=> '0' 
	);

	DCO_SYNC_RST <= not (IDELCTRL_RDY and EXT_ADC_ENBL);

	ADC_Q_AND 	<= ADC_OUT_Q1 and ADC_OUT_Q2 and ADC_OUT_Q3 and ADC_OUT_Q4;-- and ADC_OUT_Q5 and ADC_OUT_Q6 and ADC_OUT_Q7 and ADC_OUT_Q8;	
	ADC_Q_OR 	<= ADC_OUT_Q1 or ADC_OUT_Q2 or ADC_OUT_Q3 or ADC_OUT_Q4;-- or ADC_OUT_Q5 or ADC_OUT_Q6 or ADC_OUT_Q7 or ADC_OUT_Q8;
	-- Sync process will start only after IDELCTRL is ready and external enable signal is present (positive)

	-- Finite-state machipe operation:
	DCO_SYNC_process : process(DCO_SYNC_RST, sig_BUFR_OUT)
		variable var_AND_BIT			: STD_LOGIC := '0';
		-- it is required as sync process starts with  Q_AND=1.
		variable var_SYNC_BIT			: STD_LOGIC := '0';	-- sync event flag
		-- it is required cause at the moment it appears the delay goes further 1 clock chip
		-- so it will help to roll this 1 chip back.
	begin
		if (DCO_SYNC_RST = '0')				-- process is active only when Reset signal is disabled
		then
			if (rising_edge(sig_BUFR_OUT)) 	-- pulse front is a triggering event for logic
			then
				if ( var_SYNC_BIT = '0' )			-- while sync event flag is not set
				then							-- incremet/decrement process is on the go
					ADC_IODEL_CE <= '1';		-- that means clock enable signal is ON
					if ( ADC_Q_AND = '1' )		-- when all Qs' are 1, the delay should be decremented
					then						-- Upon this time Q_OR is also = 1
						var_AND_BIT		:= '1'; 
					else
						if ( var_AND_BIT	= '1' )
						then
							if ( ADC_Q_OR = '0' )	-- But when all Qs' are 0
							then					
								ADC_IODEL_INC 	<= '1';	--  the delay should be incremented
							else						-- If Q_AND not equal to 1, and Q_OR is equal to 1	
								SYNC_VALID 		<= '1';		-- this means a transition - the bouncing
								ADC_IODEL_INC 	<= '1';	-- that assumes the best syncronization
								var_SYNC_BIT 	:= '1';		-- So it is time to set a sync flag
							end if;	
						end if;
					end if;							-- and whet var_SYNC_BIT enable
				else								-- we set off increment enable signal CE
					ADC_IODEL_CE 	<= '0';			-- on the next step (cause on current step 
					ADC_IODEL_INC 	<= '0';     -- it is already shifted 1 chip further
				end if;						                       --  (relative to sync event moment)
			end if;	
		else					--set initial state by Reset signal
			SYNC_VALID 		<= '0';
			var_SYNC_BIT 	:= '0';
			var_AND_BIT		:= '0';
		end if;
	end process DCO_SYNC_process;

end architecture Behavioral;
