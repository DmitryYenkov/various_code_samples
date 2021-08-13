----------------------------------------------------------------------------------
-- Company: 		AEROMASH
-- Engineer: 		Dmitry Yenkov
-- 
-- Create Date:    05-03-2014 
-- Design Name: 
-- Module Name:    Frame Clock - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--                   The module for ADC Input Frame Clock Syncronization
--                    Based on Global clock network deskew using 2 BUFGs
--                    schematic in 7series Clocking resources datasheet (ug472)
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

entity FCO_PLL_component is
    port 
	(
		-- frame clock input
		FCO_P 		: in STD_LOGIC 	
;		FCO_N 		: in STD_LOGIC
		
;		EXT_ADC_ENBL	: in  	STD_LOGIC		-- enables data recording from ADC

;		SYNC_VALID		: out STD_LOGIC	-- PLL Lock flag
;		FRAME_CLK	: out  	STD_LOGIC	
	);
end entity FCO_PLL_component;

architecture Behavioral of FCO_PLL_component is

	signal FCO_IN 			                 : STD_LOGIC; 	-- clock to MMCM
	signal MMCM_FB_OUT		     : STD_LOGIC; 	-- internal feedback input of MMCM
	signal MMCM_FB_BUFG		     : STD_LOGIC; 	-- internal feedback input of MMCM
	signal MMCM_CLKOUT0			     : STD_LOGIC; 	-- output to BUFG

begin

-- ===========================================================================================================

   IBUFGDS_inst_FCO : IBUFGDS
   -- input diff. buffer of ADC Frame clock
   generic map
    (
       DIFF_TERM => TRUE,              
      IBUF_LOW_PWR 	=> FALSE, -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
      IOSTANDARD 	=> "LVDS_25"   
   ) 
   port map
   (
      O 	=>FCO_IN,  	-- Clock buffer output
      I 	=> FCO_P,  	-- Diff_p clock buffer input
      IB 	=> FCO_N 	-- Diff_n clock buffer input
   );

   MMCME2_BASE_FCO_inst : MMCME2_BASE      -- Main system clock generator
   generic map
   (
      BANDWIDTH => "LOW",  -- Jitter programming (OPTIMIZED, HIGH, LOW) 
      -- Low - for better jitter cleaning (according to datasheet)
      CLKFBOUT_MULT_F => 16.0,    -- Multiply value for all CLKOUT (2.000-64.000).  
      -- The less - the better   But F_VCO should be between 600 and 1440 MHz for -2 speed grade
      -- So 65 MHz input * 16 = 1040 MHz
      CLKFBOUT_PHASE => 0.0,     -- Phase offset in degrees of CLKFB (-360.000-360.000).   -- Dont care (yet)
      CLKIN1_PERIOD => 15.385,      -- Input clock period in ns to ps resolution (i.e. 33.333 is 30 MHz).    (15.385 ns - for 65 MHz)
      -- CLKOUT0_DIVIDE - CLKOUT6_DIVIDE: Divide amount for each CLKOUT (1-128)
      CLKOUT1_DIVIDE => 1,
      CLKOUT2_DIVIDE => 1,
      CLKOUT3_DIVIDE => 1,
      CLKOUT4_DIVIDE => 1,
      CLKOUT5_DIVIDE => 1,
      CLKOUT6_DIVIDE => 1,
      CLKOUT0_DIVIDE_F => 16.0,   -- Divide amount for CLKOUT0 (1.000-128.000).   -- VCO divider for output
      -- CLKOUT0_DUTY_CYCLE - CLKOUT6_DUTY_CYCLE: Duty cycle for each CLKOUT (0.01-0.99).
      CLKOUT0_DUTY_CYCLE => 0.5,
      CLKOUT1_DUTY_CYCLE => 0.5,
      CLKOUT2_DUTY_CYCLE => 0.5,
      CLKOUT3_DUTY_CYCLE => 0.5,
      CLKOUT4_DUTY_CYCLE => 0.5,
      CLKOUT5_DUTY_CYCLE => 0.5,
      CLKOUT6_DUTY_CYCLE => 0.5,
      -- CLKOUT0_PHASE - CLKOUT6_PHASE: Phase offset for each CLKOUT (-360.000-360.000).
      CLKOUT0_PHASE => 0.0,
      CLKOUT1_PHASE => 0.0,
      CLKOUT2_PHASE => 0.0,
      CLKOUT3_PHASE => 0.0,
      CLKOUT4_PHASE => 0.0,
      CLKOUT5_PHASE => 0.0,
      CLKOUT6_PHASE => 0.0,
      CLKOUT4_CASCADE => FALSE,  -- Cascade CLKOUT4 counter with CLKOUT6 (FALSE, TRUE)
      DIVCLK_DIVIDE => 1,        -- Master division value (1-106)
      REF_JITTER1 => 0.010,        -- Reference input jitter in UI (0.000-0.999).
      STARTUP_WAIT => TRUE      -- Delays DONE until MMCM is locked (FALSE, TRUE)
   )
   port map (
      -- Clock Outputs: 1-bit (each) output: User configurable clock outputs
      CLKOUT0 => MMCM_CLKOUT0,     -- 1-bit output: CLKOUT0
      CLKOUT0B => open,   -- 1-bit output: Inverted CLKOUT0
      CLKOUT1 => open,     -- 1-bit output: CLKOUT1
      CLKOUT1B => open,   -- 1-bit output: Inverted CLKOUT1
      CLKOUT2 => open,     -- 1-bit output: CLKOUT2
      CLKOUT2B => open,   -- 1-bit output: Inverted CLKOUT2
      CLKOUT3 => open,     -- 1-bit output: CLKOUT3
      CLKOUT3B => open,   -- 1-bit output: Inverted CLKOUT3
      CLKOUT4 => open,     -- 1-bit output: CLKOUT4
      CLKOUT5 => open,     -- 1-bit output: CLKOUT5
      CLKOUT6 => open,     -- 1-bit output: CLKOUT6
      -- Feedback Clocks: 1-bit (each) output: Clock feedback ports
      CLKFBOUT => MMCM_FB_OUT,   -- 1-bit output: Feedback clock
      CLKFBOUTB => open, -- 1-bit output: Inverted CLKFBOUT
      -- Status Ports: 1-bit (each) output: MMCM status ports
      LOCKED => SYNC_VALID,       -- 1-bit output: LOCK
      -- Clock Inputs: 1-bit (each) input: Clock input
      CLKIN1 => FCO_IN,       -- 1-bit input: Clock
      -- Control Ports: 1-bit (each) input: MMCM control ports
      PWRDWN => '0',       -- 1-bit input: Power-down
      RST => '0',             -- 1-bit input: Reset
      -- Power down and Reset should be system global signals. Not used now.
      -- Feedback Clocks: 1-bit (each) input: Clock feedback ports
      CLKFBIN =>  MMCM_FB_BUFG      -- 1-bit input: Feedback clock
   );

   FCO_OUT_BUFG_inst : BUFGCE
   port map (
      O           => FRAME_CLK,   -- 1-bit output: Clock output
      CE        => EXT_ADC_ENBL, -- 1-bit input: Clock enable input for I0
      I             => MMCM_CLKOUT0    -- 1-bit input: Primary clock
   );   
   
   FCO_FB_BUFG_inst : BUFGCE
   port map (
      O           => MMCM_FB_BUFG,   -- 1-bit output: Clock output
      CE        => '1', -- 1-bit input: Clock enable input for I0
      I             => MMCM_FB_OUT    -- 1-bit input: Primary clock
   );      

end architecture Behavioral;
