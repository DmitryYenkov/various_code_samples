----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date: 05.03.2014 13:06:50
-- Design Name: 
-- Module Name: ADC_Frame_component - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 				Схема формирования кадров (отсчетов) данных с АЦП
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity ADC_Frame_component is
	port 
	(
		FCO_P 				: in  	STD_LOGIC 		-- кадровый сигнал (дифференциальный)
;		FCO_N 				: in  	STD_LOGIC
	
;		ADC_DCO_BUFIOOUT	: in STD_LOGIC
;		ADC_DCO_BUFROUT		: in STD_LOGIC
	
;		SYNC_VALID			: in  	STD_LOGIC		-- Флаг установления синхронизации (DCO с внутр. такт.)

--;		D1_BYTE				: in	STD_LOGIC_VECTOR (7 downto 0);
		 	
;		TEST_PROC			: out	STD_LOGIC
--;		ADC_WORD			: out	STD_LOGIC_VECTOR (15 downto 0)
	);
end entity ADC_Frame_component;

architecture Behavioral of ADC_Frame_component is

	signal sig_ADC_FCO				: STD_LOGIC;	-- Кадровый сигнал АЦП после входного дифф. буфера
	signal sig_ISERD_O				: STD_LOGIC;
	signal sig_FCO_DIV				: STD_LOGIC_VECTOR (3 downto 0)	:= (others => '0');

	-- сигналы в фазе и противофазе для тактирования двух ISERDES	
	signal sig_ISERDES_CLK_POS		: STD_LOGIC;
	signal sig_ISERDES_CLK_NEG		: STD_LOGIC;
	signal sig_ISERDES_CLKDIV_POS	: STD_LOGIC;
	signal sig_ISERDES_CLKDIV_NEG	: STD_LOGIC;
	
	signal sig_ISERDES_RST			: STD_LOGIC;
	
	-- сигналы выходов двух ISERDES	(зачем 2 - см. ниже)
	signal sig_ADC_FCO_Q_POS		: STD_LOGIC_VECTOR (3 downto 0) 	:= (others => '0');
	signal sig_ADC_FCO_Q_NEG		: STD_LOGIC_VECTOR (3 downto 0) 	:= (others => '0');
	signal sig_FCO_POS_DELAYED		: STD_LOGIC_VECTOR (3 downto 0)		:= (others => '0');

begin

	sig_ISERDES_CLK_POS 	<= ADC_DCO_BUFIOOUT;
	sig_ISERDES_CLK_NEG 	<= not ADC_DCO_BUFIOOUT;
	sig_ISERDES_CLKDIV_POS 	<= ADC_DCO_BUFROUT;
	sig_ISERDES_CLKDIV_NEG 	<= not ADC_DCO_BUFROUT;
	sig_ISERDES_RST			<= not SYNC_VALID;
	sig_ADC_FCO_NN			<= not sig_ADC_FCO_N;
	
	IBUFDS_FCO_DIFF_inst : IBUFDS_DIFF_OUT
	-- Вход данных АЦП
	generic map
	(
		DIFF_TERM 		=> FALSE, -- Differential Termination 
		IBUF_LOW_PWR 	=> TRUE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
		IOSTANDARD 		=> "DEFAULT"
	) -- Specify the input I/O standard
	port map
	(
		O 	=> sig_ADC_FCO_P,     -- Buffer diff_p output
		OB	=> sig_ADC_FCO_N,   -- Buffer diff_n output
		I 	=> FCO_P,  -- Diff_p buffer input (connect directly to top-level port)
		IB 	=> D1FCO_N -- Diff_n buffer input (connect directly to top-level port)
	);

	ADC_FCO_ISERDESE1_inst1 : ISERDESE1
	generic map
	(
		DATA_RATE 			=> "DDR", 	-- "SDR" or "DDR" 
		DATA_WIDTH 			=> 4,      	-- Parallel data width (2-8, 10)
		-- пока 4 для экспериментов
		DYN_CLKDIV_INV_EN	=> FALSE, 	-- Enable DYNCLKDIVINVSEL inversion (TRUE/FALSE)
		DYN_CLK_INV_EN 		=> FALSE,  	-- Enable DYNCLKINVSEL inversion (TRUE/FALSE)
		-- INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
		INIT_Q1 			=> '0',
		INIT_Q2 			=> '0',
		INIT_Q3 			=> '0',
		INIT_Q4 			=> '0',
		INTERFACE_TYPE 	=> "NETWORKING", 	-- "MEMORY", "MEMORY_DDR3", "MEMORY_QDR", "NETWORKING", or "OVERSAMPLE"
		-- этот тип соответствует рис.6 в харр1071
		IOBDELAY 			=> "IBUF",	-- "NONE", "IBUF", "IFD", "BOTH"
		-- Непонятный параметр, нигде не удалось найти. 
		-- Судя по табл. 3-4 в UG361 SelectIO, подходят варианты "NONE", "IBUF"
		NUM_CE 				=> 2,		-- Number of clock enables (1 or 2)
		-- у нас один тактовый
		OFB_USED 			=> FALSE, 	-- Select OFB path (TRUE/FALSE)
		SERDES_MODE 		=> "MASTER",-- "MASTER" or "SLAVE" 
		-- SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
		SRVAL_Q1 			=> '0',
		SRVAL_Q2 			=> '0',
		SRVAL_Q3 			=> '0',
		SRVAL_Q4 			=> '0' 
	)
	port map
	(
		O 				=> open,			-- 1-bit output: Combinatorial output
		-- Q1 - Q6: 1-bit (each) output: Registered data outputs
		Q1 				=> sig_ADC_FCO_Q_POS(0),
		Q2 				=> sig_ADC_FCO_Q_POS(1),
		Q3 				=> sig_ADC_FCO_Q_POS(2),
		Q4 				=> sig_ADC_FCO_Q_POS(3),
		Q5 				=> open,
		Q6 				=> open,
		-- SHIFTOUT1-SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
		SHIFTOUT1		=> open,
		SHIFTOUT2 		=> open,
		BITSLIP 		=> '0', 			-- 1-bit input: Bitslip enable input
		-- очевидно, не нужен, т.к. незачем сдвигать туда-сюда меандр
		-- CE1, CE2: 1-bit (each) input: Data register clock enable inputs
		CE1 			=> '1',
		CE2 			=> '1',
		-- Clocks: 1-bit (each) input: ISERDESE1 clock input ports
		CLK 			=> sig_ISERDES_CLK_POS,	-- 1-bit input: High-speed clock input
		-- в соотв. со схемой
		CLKB 			=> sig_ISERDES_CLK_NEG,		-- 1-bit input: High-speed secondary clock input
		CLKDIV 			=> sig_ISERDES_CLKDIV_POS,	-- 1-bit input: Divided clock input
		-- в соотв. со схемой
		OCLK 			=> '0',				-- 1-bit input: High speed output clock input used when
											-- INTERFACE_TYPE="MEMORY" 
		-- Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
		DYNCLKDIVSEL 	=> '0', 			-- 1-bit input: Dynamic CLKDIV inversion input
		DYNCLKSEL 		=> '0',       		-- 1-bit input: Dynamic CLK/CLKB inversion input
		-- Input Data: 1-bit (each) input: ISERDESE1 data input ports
		D 				=> sig_ADC_FCO_P,    		-- 1-bit input: Data input
		-- в соотв. со схемой
		DDLY 			=> '0',           	-- 1-bit input: Serial input data from IODELAYE1
		OFB 			=> '0',          	-- 1-bit input: Data feedback input from OSERDESE1
		RST 			=> sig_ISERDES_RST,	-- 1-bit input: Active high asynchronous reset input
		-- SHIFTIN1-SHIFTIN2: 1-bit (each) input: Data width expansion input ports
		SHIFTIN1 		=> '0',
		SHIFTIN2 		=> '0' 
	);

	ADC_FCO_ISERDESE1_inst2 : ISERDESE1
	generic map
	(
		DATA_RATE 			=> "DDR", 	-- "SDR" or "DDR" 
		DATA_WIDTH 			=> 4,      	-- Parallel data width (2-8, 10)
		-- пока 4 для экспериментов
		DYN_CLKDIV_INV_EN	=> FALSE, 	-- Enable DYNCLKDIVINVSEL inversion (TRUE/FALSE)
		DYN_CLK_INV_EN 		=> FALSE,  	-- Enable DYNCLKINVSEL inversion (TRUE/FALSE)
		-- INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
		INIT_Q1 			=> '0',
		INIT_Q2 			=> '0',
		INIT_Q3 			=> '0',
		INIT_Q4 			=> '0',
		INTERFACE_TYPE 	=> "NETWORKING", 	-- "MEMORY", "MEMORY_DDR3", "MEMORY_QDR", "NETWORKING", or "OVERSAMPLE"
		-- этот тип соответствует рис.6 в харр1071
		IOBDELAY 			=> "IBUF",	-- "NONE", "IBUF", "IFD", "BOTH"
		-- Непонятный параметр, нигде не удалось найти. 
		-- Судя по табл. 3-4 в UG361 SelectIO, подходят варианты "NONE", "IBUF"
		NUM_CE 				=> 2,		-- Number of clock enables (1 or 2)
		-- у нас один тактовый
		OFB_USED 			=> FALSE, 	-- Select OFB path (TRUE/FALSE)
		SERDES_MODE 		=> "MASTER",-- "MASTER" or "SLAVE" 
		-- SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
		SRVAL_Q1 			=> '0',
		SRVAL_Q2 			=> '0',
		SRVAL_Q3 			=> '0',
		SRVAL_Q4 			=> '0' 
	)
	port map
	(
		O 				=> open,			-- 1-bit output: Combinatorial output
		-- Q1 - Q6: 1-bit (each) output: Registered data outputs
		Q1 				=> sig_ADC_FCO_Q_NEG(0),
		Q2 				=> sig_ADC_FCO_Q_NEG(1),
		Q3 				=> sig_ADC_FCO_Q_NEG(2),
		Q4 				=> sig_ADC_FCO_Q_NEG(3),
		Q5 				=> open,
		Q6 				=> open,
		-- SHIFTOUT1-SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
		SHIFTOUT1		=> open,
		SHIFTOUT2 		=> open,
		BITSLIP 		=> '0', 			-- 1-bit input: Bitslip enable input
		-- очевидно, не нужен, т.к. незачем сдвигать туда-сюда меандр
		-- CE1, CE2: 1-bit (each) input: Data register clock enable inputs
		CE1 			=> '1',
		CE2 			=> '1',
		-- Clocks: 1-bit (each) input: ISERDESE1 clock input ports
		CLK 			=> sig_ISERDES_CLK_POS,	-- 1-bit input: High-speed clock input
		-- в соотв. со схемой
		CLKB 			=> sig_ISERDES_CLK_NEG,		-- 1-bit input: High-speed secondary clock input
		CLKDIV 			=> sig_ISERDES_CLKDIV_NEG,	-- 1-bit input: Divided clock input
		-- в соотв. со схемой
		OCLK 			=> '0',				-- 1-bit input: High speed output clock input used when
											-- INTERFACE_TYPE="MEMORY" 
		-- Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
		DYNCLKDIVSEL 	=> '0', 			-- 1-bit input: Dynamic CLKDIV inversion input
		DYNCLKSEL 		=> '0',       		-- 1-bit input: Dynamic CLK/CLKB inversion input
		-- Input Data: 1-bit (each) input: ISERDESE1 data input ports
		D 				=> sig_ADC_FCO_NN,    		-- 1-bit input: Data input
		-- в соотв. со схемой
		DDLY 			=> '0',           	-- 1-bit input: Serial input data from IODELAYE1
		OFB 			=> '0',          	-- 1-bit input: Data feedback input from OSERDESE1
		RST 			=> sig_ISERDES_RST,	-- 1-bit input: Active high asynchronous reset input
		-- SHIFTIN1-SHIFTIN2: 1-bit (each) input: Data width expansion input ports
		SHIFTIN1 		=> '0',
		SHIFTIN2 		=> '0' 
	);

end architecture Behavioral;