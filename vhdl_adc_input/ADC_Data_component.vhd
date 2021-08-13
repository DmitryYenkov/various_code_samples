----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date: 05.03.2014 13:06:50
-- Design Name: 
-- Module Name: ADC_Data_component - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 				Component for ADC data reception
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
--use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

entity ADC_Data_component is
	port 
	(
		ADC_DCO_SYNC_IN	: in 	STD_LOGIC	-- syncronized(with DCO)  internal clock for data reception
;		ADC_FCO_IN	: in 	STD_LOGIC -- Frame signal (same as divided DCO, but not phase aligned)
		
;		D1_P 				: in  	STD_LOGIC   	-- data signal (diff, 1-wire, DDR)
;		D1_N 				: in  	STD_LOGIC		-- (one of  8 channels in future)
;		SYNC_VALID			: in  	STD_LOGIC		-- Enable rada recording. 
                                                                                 -- Depends on DCo/FCO sync and manual enable
;		D1_WORD				: out	STD_LOGIC_VECTOR (15 downto 0)
--;		TEST_BIT			: out	STD_LOGIC
	);
end entity ADC_Data_component;

architecture Behavioral of ADC_Data_component is

	signal sig_ADC_DATA1_P			: STD_LOGIC;	-- ADC Channel No 1 data
	signal sig_ADC_DATA1_N			: STD_LOGIC;
	
	signal sig_SHIFTOUT1           : STD_LOGIC;
	signal sig_SHIFTOUT2           : STD_LOGIC;

	-- in-phase and inverted signals for ISERDES	clocking
	signal sig_ISERDES_CLK_POS		: STD_LOGIC;
	signal sig_ISERDES_CLK_NEG		: STD_LOGIC;
	signal sig_ISERDES_CLKDIV_POS	: STD_LOGIC;
	signal sig_ISERDES_CLKDIV_NEG	: STD_LOGIC;
	
	signal sig_ISERDES_RST			: STD_LOGIC;
	
begin

	D1_WORD(14) <= '0';
	D1_WORD(15) <= '0';
     
	sig_ISERDES_CLK_POS 			<= ADC_DCO_SYNC_IN;
	sig_ISERDES_CLK_NEG 		<= not ADC_DCO_SYNC_IN;
	sig_ISERDES_CLKDIV_POS 	<= ADC_FCO_IN;
	sig_ISERDES_CLKDIV_NEG 	<= not ADC_FCO_IN;
	sig_ISERDES_RST				<= not SYNC_VALID;
	
	DATA_IBUFDS_inst : IBUFDS
	-- ADC data input
	generic map
	(
		DIFF_TERM 		=> TRUE, -- Differential Termination 
		IBUF_LOW_PWR 	=> FALSE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
		IOSTANDARD 		=> "LVDS_25"
	) -- Specify the input I/O standard
	port map
	(
		O 	=> sig_ADC_DATA1_P,     -- Buffer diff_p output
		I 	=> D1_P,  -- Diff_p buffer input (connect directly to top-level port)
		IB 	=> D1_N -- Diff_n buffer input (connect directly to top-level port)
	);

-- ==========================================================

   ADC_DATA1_ISERDESE2_inst1 : ISERDESE2
   generic map
   (
      DATA_RATE => "DDR",           -- DDR, SDR
      DATA_WIDTH => 14,              -- Parallel data width (2-8,10,14)
      DYN_CLKDIV_INV_EN => "FALSE", -- Enable DYNCLKDIVINVSEL inversion (FALSE, TRUE)
      DYN_CLK_INV_EN => "FALSE",    -- Enable DYNCLKINVSEL inversion (FALSE, TRUE)
      -- INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
      INIT_Q1 => '0',
      INIT_Q2 => '0',
      INIT_Q3 => '0',
      INIT_Q4 => '0',
      INTERFACE_TYPE => "NETWORKING",   -- MEMORY, MEMORY_DDR3, MEMORY_QDR, NETWORKING, OVERSAMPLE
      IOBDELAY => "NONE",           -- NONE, BOTH, IBUF, IFD
      NUM_CE => 2,                  -- Number of clock enables (1,2)
      OFB_USED => "FALSE",          -- Select OFB path (FALSE, TRUE)
      SERDES_MODE => "MASTER",      -- MASTER, SLAVE
      -- SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
      SRVAL_Q1 => '0',
      SRVAL_Q2 => '0',
      SRVAL_Q3 => '0',
      SRVAL_Q4 => '0' 
   )
   port map
   (
      O => open,                       -- 1-bit output: Combinatorial output
      -- Q1 - Q8: 1-bit (each) output: Registered data outputs
      Q1 => D1_WORD(0),
      Q2 => D1_WORD(1),
      Q3 => D1_WORD(2),
      Q4 => D1_WORD(3),
      Q5 => D1_WORD(4),
      Q6 => D1_WORD(5),
      Q7 => D1_WORD(6),
      Q8 => D1_WORD(7),
      -- SHIFTOUT1-SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
      SHIFTOUT1 => sig_SHIFTOUT1,
      SHIFTOUT2 => sig_SHIFTOUT2,
      BITSLIP => '0',           -- 1-bit input: The BITSLIP pin performs a Bitslip operation synchronous to
                                    -- CLKDIV when asserted (active High). Subsequently, the data seen on the
                                    -- Q1 to Q8 output ports will shift, as in a barrel-shifter operation, one
                                    -- position every time Bitslip is invoked (DDR operation is different from
                                    -- SDR).

      -- CE1, CE2: 1-bit (each) input: Data register clock enable inputs
      CE1 => '1',
      CE2 => '1',
      CLKDIVP => '0',           -- 1-bit input: TBD
      -- Clocks: 1-bit (each) input: ISERDESE2 clock input ports
      CLK => sig_ISERDES_CLK_POS,                   -- 1-bit input: High-speed clock
      CLKB => sig_ISERDES_CLK_NEG,                 -- 1-bit input: High-speed secondary clock
      CLKDIV => sig_ISERDES_CLKDIV_POS,             -- 1-bit input: Divided clock
      OCLK => '0',                 -- 1-bit input: High speed output clock used when INTERFACE_TYPE="MEMORY" 
      -- Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
      DYNCLKDIVSEL => '0', -- 1-bit input: Dynamic CLKDIV inversion
      DYNCLKSEL => '0',       -- 1-bit input: Dynamic CLK/CLKB inversion
      -- Input Data: 1-bit (each) input: ISERDESE2 data input ports
      D => sig_ADC_DATA1_P,                       -- 1-bit input: Data input
      DDLY => '0',                 -- 1-bit input: Serial data from IDELAYE2
      OFB => '0',                   -- 1-bit input: Data feedback from OSERDESE2
      OCLKB => '0',               -- 1-bit input: High speed negative edge output clock
      RST => sig_ISERDES_RST,                   -- 1-bit input: Active high asynchronous reset
      -- SHIFTIN1-SHIFTIN2: 1-bit (each) input: Data width expansion input ports
      SHIFTIN1 => '0',
      SHIFTIN2 => '0' 
   );

   ADC_DATA1_ISERDESE2_inst2 : ISERDESE2
   generic map
   (
      DATA_RATE => "DDR",           -- DDR, SDR
      DATA_WIDTH => 14,              -- Parallel data width (2-8,10,14)
      DYN_CLKDIV_INV_EN => "FALSE", -- Enable DYNCLKDIVINVSEL inversion (FALSE, TRUE)
      DYN_CLK_INV_EN => "FALSE",    -- Enable DYNCLKINVSEL inversion (FALSE, TRUE)
      -- INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
      INIT_Q1 => '0',
      INIT_Q2 => '0',
      INIT_Q3 => '0',
      INIT_Q4 => '0',
      INTERFACE_TYPE => "NETWORKING",   -- MEMORY, MEMORY_DDR3, MEMORY_QDR, NETWORKING, OVERSAMPLE
      IOBDELAY => "NONE",           -- NONE, BOTH, IBUF, IFD
      NUM_CE => 2,                  -- Number of clock enables (1,2)
      OFB_USED => "FALSE",          -- Select OFB path (FALSE, TRUE)
      SERDES_MODE => "SLAVE",      -- MASTER, SLAVE
      -- SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
      SRVAL_Q1 => '0',
      SRVAL_Q2 => '0',
      SRVAL_Q3 => '0',
      SRVAL_Q4 => '0' 
   )
   port map
   (
      O => open,                       -- 1-bit output: Combinatorial output
      -- Q1 - Q8: 1-bit (each) output: Registered data outputs
      Q1 => open,
      Q2 => open,
      Q3 => D1_WORD(8),
      Q4 => D1_WORD(9),
      Q5 => D1_WORD(10),
      Q6 => D1_WORD(11),
      Q7 => D1_WORD(12),
      Q8 => D1_WORD(13),
      -- SHIFTOUT1-SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
      SHIFTOUT1 => open,
      SHIFTOUT2 => open,
      BITSLIP => '0',           -- 1-bit input: The BITSLIP pin performs a Bitslip operation synchronous to
                                    -- CLKDIV when asserted (active High). Subsequently, the data seen on the
                                    -- Q1 to Q8 output ports will shift, as in a barrel-shifter operation, one
                                    -- position every time Bitslip is invoked (DDR operation is different from
                                    -- SDR).

      -- CE1, CE2: 1-bit (each) input: Data register clock enable inputs
      CE1 => '1',
      CE2 => '1',
      CLKDIVP => '0',           -- 1-bit input: TBD
      -- Clocks: 1-bit (each) input: ISERDESE2 clock input ports
      CLK => sig_ISERDES_CLK_POS,                   -- 1-bit input: High-speed clock
      CLKB => sig_ISERDES_CLK_NEG,                 -- 1-bit input: High-speed secondary clock
      CLKDIV =>  sig_ISERDES_CLKDIV_POS,             -- 1-bit input: Divided clock
      OCLK => '0',                 -- 1-bit input: High speed output clock used when INTERFACE_TYPE="MEMORY" 
      -- Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
      DYNCLKDIVSEL => '0', -- 1-bit input: Dynamic CLKDIV inversion
      DYNCLKSEL => '0',       -- 1-bit input: Dynamic CLK/CLKB inversion
      -- Input Data: 1-bit (each) input: ISERDESE2 data input ports
      D => '0',--sig_ADC_DATA1_P,                       -- 1-bit input: Data input
      DDLY => '0',                 -- 1-bit input: Serial data from IDELAYE2
      OFB => '0',                   -- 1-bit input: Data feedback from OSERDESE2
      OCLKB => '0',               -- 1-bit input: High speed negative edge output clock
      RST => sig_ISERDES_RST,                   -- 1-bit input: Active high asynchronous reset
      -- SHIFTIN1-SHIFTIN2: 1-bit (each) input: Data width expansion input ports
      SHIFTIN1 => sig_SHIFTOUT1,
      SHIFTIN2 => sig_SHIFTOUT2 
   );

--	Parallel_8bit_trig_process : process (	SYNC_VALID, 
--											sig_ISERDES_CLKDIV_POS )
--	begin
--		if ( SYNC_VALID = '1' )
--		then
--			if ( falling_edge(sig_ISERDES_CLKDIV_POS) )
--			then
--				Cur_state <= Next_state;
--			end if;
--		elsif
--			Cur_state <= Idle;
--		end if;
--	end process Parallel_8bit_trig_process;  
--
--	Parallel_8bit_logic_process : process (	Cur_state )
--	begin
--		case Cur_state is
--		when Idle 	=>
--			
--		when Ready 	=>
--		when Do		=>
--		end case;
--	end process Parallel_8bit_logic_process;  


	-- Процесс записи 8 параллельных битов с выходов двух ISERDES
	-- Фактически это просто элемент задержки выходов Q1...Q4 ISERDES #1
	-- на полпериода CLKDIV	
--	Parallel_8bit_process : process (	SYNC_VALID, 
--										sig_ISERDES_CLKDIV_POS,
----										sig_ISERDES_CLKDIV_NEG, 
--										sig_ADC_OUT_Q_POS, 
--										sig_ADC_OUT_Q_NEG, 
--										sig_POS_DELAYED )
--		variable HALF_WORD	: STD_LOGIC := '0';
--	begin
--		if ( SYNC_VALID = '1' )
--		then
--			--if ( falling_edge(sig_ISERDES_CLKDIV_NEG) )
--			if ( rising_edge(sig_ISERDES_CLKDIV_POS) )
--			then
--				sig_POS_DELAYED <= sig_ADC_OUT_Q_POS;
--			end if;
--			if ( falling_edge(sig_ISERDES_CLKDIV_POS) )
--			then
--				if ( HALF_WORD = '0' )
--				then
--					sig_BUF_BYTE(7) 		<= sig_POS_DELAYED(3);
--					sig_BUF_BYTE(6) 		<= sig_POS_DELAYED(2);
--					sig_BUF_BYTE(5) 		<= sig_POS_DELAYED(1);
--					sig_BUF_BYTE(4) 		<= sig_POS_DELAYED(0);
--					sig_BUF_BYTE(3) 		<= sig_ADC_OUT_Q_NEG(3);
--					sig_BUF_BYTE(2) 		<= sig_ADC_OUT_Q_NEG(2);
--					sig_BUF_BYTE(1) 		<= sig_ADC_OUT_Q_NEG(1);
--					sig_BUF_BYTE(0) 		<= sig_ADC_OUT_Q_NEG(0);
--					HALF_WORD	:= '1';
--				else
--					D1_WORD(15 downto 8) 	<= sig_BUF_BYTE;
--					D1_WORD(7) 				<= sig_POS_DELAYED(3);
--					D1_WORD(6) 				<= sig_POS_DELAYED(2);
--					D1_WORD(5) 				<= sig_POS_DELAYED(1);
--					D1_WORD(4) 				<= sig_POS_DELAYED(0);
--					D1_WORD(3) 				<= sig_ADC_OUT_Q_NEG(3);
--					D1_WORD(2) 				<= sig_ADC_OUT_Q_NEG(2);
--					D1_WORD(1) 				<= sig_ADC_OUT_Q_NEG(1);
--					D1_WORD(0) 				<= sig_ADC_OUT_Q_NEG(0);					
--					HALF_WORD	:= '0';
--				end if;
--			end if;
--		else
--			HALF_WORD	:= '0';
--			D1_WORD		<= (others => '0');
--		end if;
--	end process Parallel_8bit_process;

end architecture Behavioral;