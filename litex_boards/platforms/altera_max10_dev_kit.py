#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2019 Hans Baier <hansfbaier@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("rst_n", 0, Pins("D9"), IOStandard("3.3-V LVCMOS")),
    ("clk50", 0, Pins("M9"), IOStandard("2.5 V")),
    ("clk25", 0, Pins("M8"), IOStandard("2.5 V")),
    ("clk100_ddr3_n", 0, Pins("N15")),
    ("clk100_ddr3_p", 0, Pins("N14"), IOStandard("DIFFERENTIAL 1.5-V SSTL")),
    ("clk10_adc", 0, Pins("N5"), IOStandard("2.5 V")),
    ("clk125_lvds_n", 0, Pins("R11")),
    ("clk125_lvds_p", 0, Pins("P11"), IOStandard("LVDS")),

    # LEDs
    ("user_led", 0, Pins("T20"), IOStandard("1.5 V")),
    ("user_led", 1, Pins("U22"), IOStandard("1.5 V")),
    ("user_led", 2, Pins("U21"), IOStandard("1.5 V")),
    ("user_led", 3, Pins("AA21"), IOStandard("1.5 V")),
    ("user_led", 4, Pins("AA22"), IOStandard("1.5 V")),

    # Switches
    ("user_sw", 0, Pins("H21"), IOStandard("1.5 V")),
    ("user_sw", 1, Pins("H22"), IOStandard("1.5 V")),
    ("user_sw", 2, Pins("J21"), IOStandard("1.5 V")),
    ("user_sw", 3, Pins("J22"), IOStandard("1.5 V")),
    ("user_sw", 4, Pins("G19"), IOStandard("1.5 V")),

    # Buttons
    ("user_btn", 0, Pins("L22"), IOStandard("1.5 V")),
    ("user_btn", 1, Pins("M21"), IOStandard("1.5 V")),
    ("user_btn", 2, Pins("M22"), IOStandard("1.5 V")),
    ("user_btn", 3, Pins("N21"), IOStandard("1.5 V")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("W18")),
        Subsignal("rx", Pins("Y19")),
        IOStandard("2.5 V")
     ),

    # RGMII Ethernet running at 100 mbit
    # Port 0 / A (bottom jack)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("E10"), IOStandard("3.3-V LVCMOS")),
        Subsignal("rx", Pins("P3")),
        IOStandard("2.5 V")
     ),
    ("eth", 0,
         Subsignal("rst_n", Pins("V8")),
         Subsignal("mdio", Pins("Y5")),
         Subsignal("mdc", Pins("Y6")),
         Subsignal("rx_dv", Pins("T2")),
         Subsignal("rx_er", Pins("U2")),
         Subsignal("rx_data", Pins("N9 T1 N1 T3")),
         Subsignal("tx_en", Pins("R4")),
         Subsignal("tx_er", Pins("P4")),
         Subsignal("tx_data", Pins("R5 P5 W1 W2")),
         Subsignal("col", Pins("P1")),
         Subsignal("crs", Pins("N8")),
         IOStandard("2.5 V")
    ),

    # Port 1 / B (top jack)
    ("eth_clocks", 1,
        Subsignal("tx", Pins("E11"), IOStandard("3.3-V LVCMOS")),
        Subsignal("rx", Pins("R3")),
        IOStandard("2.5 V")
     ),
    ("eth", 1,
        Subsignal("rst_n", Pins("AB4")),
        Subsignal("rx_dv", Pins("R1")),
        Subsignal("rx_er", Pins("R2")),
        Subsignal("rx_data", Pins("P8 M1 M2 R7")),
        Subsignal("tx_en", Pins("V3")),
        Subsignal("tx_er", Pins("U5")),
        Subsignal("tx_data", Pins("U1 V1 U3 U4")),
        Subsignal("col", Pins("N2")),
        Subsignal("crs", Pins("N3")),
        IOStandard("2.5 V")
    ),


    # Port 0 (top/bottom?)
    ("eneta_gtx_clk", 0, Pins("T5"), IOStandard("2.5 V")),
    ("eneta_intn", 0, Pins("V7"), IOStandard("2.5 V")),
    ("eneta_led_link100", 0, Pins("R9"), IOStandard("2.5 V")),

    # Port 1 (top/bottom?)
    ("enetb_gtx_clk", 0, Pins("T6"), IOStandard("2.5 V")),
    ("enetb_intn", 0, Pins("AA3"), IOStandard("2.5 V")),
    ("enetb_led_link100", 0, Pins("P9"), IOStandard("2.5 V")),

    ("usb_clk", 0, Pins("H11"), IOStandard("3.3-V LVCMOS")),
    ("usb_wrn", 0, Pins("D14"), IOStandard("3.3-V LVCMOS")),
    ("usb_sda", 0, Pins("E12"), IOStandard("3.3-V LVCMOS")),
    ("usb_scl", 0, Pins("J11"), IOStandard("3.3-V LVCMOS")),
    ("usb_rdn", 0, Pins("D13"), IOStandard("3.3-V LVCMOS")),
    ("usb_full", 0, Pins("H12"), IOStandard("3.3-V LVCMOS")),
    ("usb_resetn", 0, Pins("B8"), IOStandard("3.3-V LVCMOS")),
    ("usb_oen", 0, Pins("A9"), IOStandard("3.3-V LVCMOS")),
    ("usb_empty", 0, Pins("C17"), IOStandard("3.3-V LVCMOS")),

    ("ddr3_odt", 0, Pins("W19"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_rasn", 0, Pins("V18"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_resetn", 0, Pins("B22"), IOStandard("1.5V"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_wen", 0, Pins("Y21"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_casn", 0, Pins("U19"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_cke", 0, Pins("W20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_clk_n", 0, Pins("E18"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_clk_p", 0, Pins("D18"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_csn", 0, Pins("Y22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),



    ("hsmc_clk_in0", 0, Pins("N4"), IOStandard("2.5 V")),
    ("hsmc_scl", 0, Pins("Y18"), IOStandard("2.5 V")),
    ("hsmc_sda", 0, Pins("AA19"), IOStandard("2.5 V")),
    ("hsmc_clk_out0", 0, Pins("AA13"), IOStandard("2.5 V")),
    ("hsmc_prsntn", 0, Pins("AB14"), IOStandard("2.5 V")),

    ("hdmi_scl", 0, Pins("A10"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_sda", 0, Pins("B15"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_clk", 0, Pins("D6"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_de", 0, Pins("C10"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_hs", 0, Pins("A19"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_int", 0, Pins("D15"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_vs", 0, Pins("J12"), IOStandard("3.3-V LVCMOS")),

    ("qspi_clk", 0, Pins("B2"), IOStandard("3.3-V LVCMOS")),
    ("qspi_csn", 0, Pins("C2"), IOStandard("3.3-V LVCMOS")),
    ("qspi_io", 0, Pins("C6"), IOStandard("3.3-V LVCMOS")),
    ("qspi_io", 1, Pins("C3"), IOStandard("3.3-V LVCMOS")),
    ("qspi_io", 2, Pins("C5"), IOStandard("3.3-V LVCMOS")),
    ("qspi_io", 3, Pins("B1"), IOStandard("3.3-V LVCMOS")),

    ("dac_sync", 0, Pins("B10"), IOStandard("3.3-V LVCMOS")),
    ("dac_sclk", 0, Pins("A7"), IOStandard("3.3-V LVCMOS")),
    ("dac_din", 0, Pins("A8"), IOStandard("3.3-V LVCMOS")),

    ("ip_sequrity", 0, Pins("E6"), IOStandard("3.3-V LVCMOS")),
    ("jtag_safe", 0, Pins("D7"), IOStandard("3.3-V LVCMOS")),

    ("usb_data", 0, Pins("B14"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 1, Pins("E15"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 2, Pins("E16"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 3, Pins("H14"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 4, Pins("J13"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 5, Pins("C13"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 6, Pins("C14"), IOStandard("3.3-V LVCMOS")),
    ("usb_data", 7, Pins("A14"), IOStandard("3.3-V LVCMOS")),
    ("usb_addr", 0, Pins("D17"), IOStandard("3.3-V LVCMOS")),
    ("usb_addr", 1, Pins("E13"), IOStandard("3.3-V LVCMOS")),

    ("ddr3_a", 0, Pins("V20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 1, Pins("D19"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 2, Pins("A21"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 3, Pins("U20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 4, Pins("C20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 5, Pins("F19"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 6, Pins("E21"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 7, Pins("B20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 8, Pins("D22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 9, Pins("E22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 10, Pins("Y20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 11, Pins("E20"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 12, Pins("J14"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_a", 13, Pins("C22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_ba", 0, Pins("V22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_ba", 1, Pins("N18"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_ba", 2, Pins("W22"), IOStandard("SSTL-15"), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dm",  0, Pins("J15"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["DM_PIN", "ON"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dm",  1, Pins("N19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["DM_PIN", "ON"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dm",  2, Pins("T18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["DM_PIN", "ON"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  0, Pins("J18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  1, Pins("K20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  2, Pins("H18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  3, Pins("K18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  4, Pins("H19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  5, Pins("J20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  6, Pins("H20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  7, Pins("K19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  8, Pins("L20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq",  9, Pins("M18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 10, Pins("M20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 11, Pins("M14"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 12, Pins("L18"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 13, Pins("M15"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 14, Pins("L19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 15, Pins("N20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 16, Pins("R14"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 17, Pins("P19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 18, Pins("P14"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 19, Pins("R20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 20, Pins("R15"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 21, Pins("T19"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 22, Pins("P15"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dq", 23, Pins("P20"), IOStandard("SSTL-15"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_n", 0, Pins("K15"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_n", 1, Pins("L15"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_n", 2, Pins("P18"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_p", 0, Pins("K14"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_p", 1, Pins("L14"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),
    ("ddr3_dqs_p", 2, Pins("R18"), IOStandard("DIFFERENTIAL 1.5-V SSTL"), Misc(["OUTPUT_TERMINATION", "SERIES 40 OHM WITHOUT CALIBRATION"]), Misc(["PACKAGE_SKEW_COMPENSATION", "OFF"])),

    ("hsmc_clk_in_n", 0, Pins("AB21")),
    ("hsmc_clk_in_n", 1, Pins("V9")),
    ("hsmc_clk_in_p", 0, Pins("AA20"), IOStandard("LVDS")),
    ("hsmc_clk_in_p", 1, Pins("V10"), IOStandard("LVDS")),
    ("hsmc_clk_out_n", 0, Pins("R13")),
    ("hsmc_clk_out_n", 1, Pins("V14")),
    ("hsmc_clk_out_p", 0, Pins("P13"), IOStandard("LVDS")),
    ("hsmc_clk_out_p", 1, Pins("W15"), IOStandard("LVDS")),
    ("hsmc_d", 0, Pins("Y7"), IOStandard("2.5 V")),
    ("hsmc_d", 1, Pins("Y8"), IOStandard("2.5 V")),
    ("hsmc_d", 2, Pins("AB2"), IOStandard("2.5 V")),
    ("hsmc_d", 3, Pins("AB3"), IOStandard("2.5 V")),
    ("hsmc_rx_d_n", 0, Pins("V4")),
    ("hsmc_rx_d_n", 1, Pins("Y1")),
    ("hsmc_rx_d_n", 2, Pins("AA1")),
    ("hsmc_rx_d_n", 3, Pins("AA8")),
    ("hsmc_rx_d_n", 4, Pins("AA9")),
    ("hsmc_rx_d_n", 5, Pins("AB6")),
    ("hsmc_rx_d_n", 6, Pins("Y3")),
    ("hsmc_rx_d_n", 7, Pins("AA5")),
    ("hsmc_rx_d_n", 8, Pins("W12")),
    ("hsmc_rx_d_n", 9, Pins("AA14")),
    ("hsmc_rx_d_n", 10, Pins("AA15")),
    ("hsmc_rx_d_n", 11, Pins("AB16")),
    ("hsmc_rx_d_n", 12, Pins("AB17")),
    ("hsmc_rx_d_n", 13, Pins("W11")),
    ("hsmc_rx_d_n", 14, Pins("AB10")),
    ("hsmc_rx_d_n", 15, Pins("AB12")),
    ("hsmc_rx_d_n", 16, Pins("AB19")),
    ("hsmc_rx_d_p", 0, Pins("V5"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 1, Pins("Y2"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 2, Pins("AA2"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 3, Pins("AB8"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 4, Pins("AB9"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 5, Pins("AB7"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 6, Pins("Y4"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 7, Pins("AB5"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 8, Pins("W13"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 9, Pins("AB15"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 10, Pins("Y16"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 11, Pins("AA16"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 12, Pins("AB18"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 13, Pins("Y11"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 14, Pins("AB11"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 15, Pins("AB13"), IOStandard("LVDS")),
    ("hsmc_rx_d_p", 16, Pins("AB20"), IOStandard("LVDS")),
    ("hsmc_tx_d_n", 0, Pins("W4")),
    ("hsmc_tx_d_n", 1, Pins("U6")),
    ("hsmc_tx_d_n", 2, Pins("W5")),
    ("hsmc_tx_d_n", 3, Pins("W7")),
    ("hsmc_tx_d_n", 4, Pins("Y10")),
    ("hsmc_tx_d_n", 5, Pins("AA6")),
    ("hsmc_tx_d_n", 6, Pins("R10")),
    ("hsmc_tx_d_n", 7, Pins("W9")),
    ("hsmc_tx_d_n", 8, Pins("V13")),
    ("hsmc_tx_d_n", 9, Pins("Y13")),
    ("hsmc_tx_d_n", 10, Pins("U15")),
    ("hsmc_tx_d_n", 11, Pins("V15")),
    ("hsmc_tx_d_n", 12, Pins("W17")),
    ("hsmc_tx_d_n", 13, Pins("V11")),
    ("hsmc_tx_d_n", 14, Pins("R12")),
    ("hsmc_tx_d_n", 15, Pins("AA11")),
    ("hsmc_tx_d_n", 16, Pins("AA17")),
    ("hsmc_tx_d_p", 0, Pins("W3"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 1, Pins("U7"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 2, Pins("W6"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 3, Pins("W8"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 4, Pins("AA10"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 5, Pins("AA7"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 6, Pins("P10"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 7, Pins("W10"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 8, Pins("W14"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 9, Pins("Y14"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 10, Pins("V16"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 11, Pins("W16"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 12, Pins("V17"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 13, Pins("V12"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 14, Pins("P12"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 15, Pins("AA12"), IOStandard("LVDS")),
    ("hsmc_tx_d_p", 16, Pins("Y17"), IOStandard("LVDS")),

    ("hdmi_tx_d", 0, Pins("A17"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 1, Pins("A18"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 2, Pins("A12"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 3, Pins("F16"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 4, Pins("A16"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 5, Pins("B12"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 6, Pins("F15"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 7, Pins("B11"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 8, Pins("A13"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 9, Pins("C15"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 10, Pins("C11"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 11, Pins("A11"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 12, Pins("A20"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 13, Pins("H13"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 14, Pins("E14"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 15, Pins("D12"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 16, Pins("C12"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 17, Pins("C19"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 18, Pins("C18"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 19, Pins("B19"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 20, Pins("B17"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 21, Pins("B16"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 22, Pins("C16"), IOStandard("3.3-V LVCMOS")),
    ("hdmi_tx_d", 23, Pins("A15"), IOStandard("3.3-V LVCMOS")),

    ("pmoda_io", 0, Pins("C7"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 1, Pins("C8"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 2, Pins("A6"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 3, Pins("B7"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 4, Pins("D8"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 5, Pins("A4"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 6, Pins("A5"), IOStandard("3.3-V LVCMOS")),
    ("pmoda_io", 7, Pins("E9"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 0, Pins("E8"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 1, Pins("D5"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 2, Pins("B5"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 3, Pins("C4"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 4, Pins("A2"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 5, Pins("A3"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 6, Pins("B4"), IOStandard("3.3-V LVCMOS")),
    ("pmodb_io", 7, Pins("B3"), IOStandard("3.3-V LVCMOS")),



    ("adc1in", 0, Pins("F5"), IOStandard("2.5 V")),
    ("adc1in", 1, Pins("F4"), IOStandard("2.5 V")),
    ("adc1in", 2, Pins("J8"), IOStandard("2.5 V")),
    ("adc1in", 3, Pins("J9"), IOStandard("2.5 V")),
    ("adc1in", 4, Pins("J4"), IOStandard("2.5 V")),
    ("adc1in", 5, Pins("H3"), IOStandard("2.5 V")),
    ("adc1in", 6, Pins("K5"), IOStandard("2.5 V")),
    ("adc1in", 7, Pins("K6"), IOStandard("2.5 V")),
    ("adc2in", 0, Pins("E4"), IOStandard("2.5 V")),
    ("adc2in", 1, Pins("J3"), IOStandard("2.5 V")),
    ("adc2in", 2, Pins("G4"), IOStandard("2.5 V")),
    ("adc2in", 3, Pins("F3"), IOStandard("2.5 V")),
    ("adc2in", 4, Pins("H4"), IOStandard("2.5 V")),
    ("adc2in", 5, Pins("G3"), IOStandard("2.5 V")),
    ("adc2in", 6, Pins("K4"), IOStandard("2.5 V")),
    ("adc2in", 7, Pins("E3"), IOStandard("2.5 V")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Beagle bone black headers (numbering 1-based, Pin 0 is dummy)
    # PIN   0 1 2   3   4   5    6    7    8    9   10   11  12  13   14  15  16   17   18   19  20   21  22  23   24   25   26   27   28   29   30   31   32   33  34  35  36  37  38  39  40  41  42  43  44  45  46
    # ("P8", "- - - W18 Y18 Y19 AA17 AA20 AA19 AB21 AB20 AB19 Y16 V16 AB18 V15 W17 AB17 AA16 AB16 W16 AB15 W15 Y14 AA15 AB14 AA14 AB13 AA13 AB12 AA12 AB11 AA11 AB10 Y13 Y11 W13 W12 W11 V12 V11 V13 V14 Y17 W14 U15 R13"),
    # ("P9", "- - -   -   -   -    -    -    -   U6  AA2   Y5  Y6  W6   W7  W8  V8  AB8   V7  R11 AB7  AB6 AA7 AA6   Y7  V10   U7   W9   W5   R9   W4   P9    -   K4   -  J4  H3  J8  J9  F5  F4 V17  W3   -   -   -   -")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf         = False

    def __init__(self):
        AlteraPlatform.__init__(self, "10M50DAF484C6GES", _io, _connectors)

    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        # self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
