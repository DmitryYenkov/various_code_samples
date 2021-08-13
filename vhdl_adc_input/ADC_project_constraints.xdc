
####################################################################################
# System clock 200 MHz in KC705
create_clock -period 5.000 -name SYSCLK_IN -waveform {0.000 2.500} -add [get_ports {SYS_CLK_P SYS_CLK_N}]
set_input_jitter SYSCLK_IN 0.002
set_property PACKAGE_PIN AD12 [get_ports SYS_CLK_P]
set_property PACKAGE_PIN AD11 [get_ports SYS_CLK_N]
set_property IOSTANDARD LVDS [get_ports SYS_CLK_N]
set_property IOSTANDARD LVDS [get_ports SYS_CLK_P]
#create_generated_clock -name INNER_SYS_CLK -source [get_clocks SYSCLK_IN] -divide_by 1
# ADC Clock
#create_clock -period 2.198 -name ADC_DCO -waveform {0.000 1.099} -add [get_ports {DCO1_P DCO1_N}]
set_property PACKAGE_PIN C25 [get_ports DCO1_P]
set_property PACKAGE_PIN B25 [get_ports DCO1_N]
#set_property PACKAGE_PIN E28 [get_ports DCO1_P]
#set_property PACKAGE_PIN D28 [get_ports DCO1_N]
set_property IOSTANDARD LVDS_25 [get_ports DCO1_P]
set_property IOSTANDARD LVDS_25 [get_ports DCO1_N]
####################################################################################
# pin assignement
# I N P U T S
# ADC data
set_property PACKAGE_PIN B27 [get_ports D11_P]
set_property PACKAGE_PIN A27 [get_ports D11_N]
set_property IOSTANDARD LVDS_25 [get_ports D11_P]
set_property IOSTANDARD LVDS_25 [get_ports D11_N]
# ADC Frame
set_property PACKAGE_PIN D26 [get_ports FCO1_P]
set_property PACKAGE_PIN C26 [get_ports FCO1_N]
set_property IOSTANDARD LVDS_25 [get_ports FCO1_P]
set_property IOSTANDARD LVDS_25 [get_ports FCO1_N]
# Manual enable of ADC reception
set_property PACKAGE_PIN Y29 [get_ports EXT_ADC_ENBL]
set_property IOSTANDARD LVCMOS18 [get_ports EXT_ADC_ENBL]
# O U T P U T S
# ADC Data Clock Sync Event Flag
set_property PACKAGE_PIN AB8 [get_ports SYNC_VALID_OUT]
set_property IOSTANDARD LVCMOS18 [get_ports SYNC_VALID_OUT]
set_property DRIVE 12 [get_ports SYNC_VALID_OUT]
# ADC_DCO_Divided
set_property PACKAGE_PIN AA8 [get_ports TEST_BIT_C_OUT]
set_property IOSTANDARD LVCMOS18 [get_ports TEST_BIT_C_OUT]
set_property DRIVE 12 [get_ports TEST_BIT_C_OUT]
# ADC_FCO_Divided
set_property PACKAGE_PIN AC9 [get_ports TEST_BIT_F_OUT]
set_property IOSTANDARD LVCMOS18 [get_ports TEST_BIT_F_OUT]
set_property DRIVE 12 [get_ports TEST_BIT_F_OUT]
# ADC Word BIT out
set_property PACKAGE_PIN AB9 [get_ports TEST_BIT_D_OUT1]
set_property IOSTANDARD LVCMOS18 [get_ports TEST_BIT_D_OUT1]
set_property DRIVE 12 [get_ports TEST_BIT_D_OUT1]
set_property PACKAGE_PIN AE26 [get_ports TEST_BIT_D_OUT2]
set_property IOSTANDARD LVCMOS18 [get_ports TEST_BIT_D_OUT2]
set_property DRIVE 12 [get_ports TEST_BIT_D_OUT2]		
#




