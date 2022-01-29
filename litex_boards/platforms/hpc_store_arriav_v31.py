#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("clk50",     0, Pins("AL5")),
    ("clk125",    0, Pins("AN3")),
    ("clk100",    0, Pins("AF17"), IOStandard("SSTL-15")),
    ("clk100",    1, Pins("A16"),  IOStandard("SSTL-15")),
    ("rst_n",     0, Pins("C6")),

    # Leds.
    ("user_led", 0, Pins("AG8")),
    ("user_led", 1, Pins("AF8")),
    ("user_led", 2, Pins("AF7")),
    ("user_led", 3, Pins("AE7")),
    ("user_led", 4, Pins("AE6")),
    ("user_led", 5, Pins("AD6")),
    ("user_led", 6, Pins("AC7")),
    ("user_led", 7, Pins("AC6")),

    # Port 0 / A (closest to PCIe root port)
    ("eth_clocks", 0,
        Subsignal("tx",  Pins("AM13")),
        Subsignal("rx",  Pins("AP2")),
        Subsignal("gtx", Pins("AH8")),
        IOStandard("2.5 V")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AC13")),
        Subsignal("mdio",    Pins("AC12")),
        Subsignal("mdc",     Pins("AD12")),
        Subsignal("rx_dv",   Pins("AH11")),
        Subsignal("rx_er",   Pins("AG11")),
        Subsignal("rx_data", Pins("AP6  AP7  AN8  AP8  AN9  AP10 AN11 AP11")),
        Subsignal("tx_en",   Pins("AL12")),
        Subsignal("tx_er",   Pins("AL13")),
        Subsignal("tx_data", Pins("AL11 AK11 AJ11 AJ13 AK12 AH13 AH12 AG12")),
        IOStandard("2.5 V")
    ),

    # Port 1 / B (closest to SFP ports)
    ("eth_clocks", 1,
        Subsignal("tx",  Pins("AH14")),
        Subsignal("rx",  Pins("AH7")),
        Subsignal("gtx", Pins("AM14")),
        IOStandard("2.5 V")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("AN14")),
        Subsignal("mdio",    Pins("AP14")),
        Subsignal("mdc",     Pins("AN12")),
        Subsignal("rx_dv",   Pins("AK15")),
        Subsignal("rx_er",   Pins("AH15")),
        Subsignal("rx_data", Pins("AK14 AC14 AD14 AE14 AJ16 AH16 AF16 AE16")),
        Subsignal("tx_en",   Pins("AN15")),
        Subsignal("tx_er",   Pins("AL14")),
        Subsignal("tx_data", Pins("AG15 AG14 AL16 AF14 AM16 AP16 AE15 AD15")),
        IOStandard("2.5 V")
    ),

    # USB-Serial
    ("serial", 0,
        Subsignal("tx", Pins("AJ6")),
        Subsignal("rx", Pins("AK6")))
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf         = False

    def __init__(self):
        AlteraPlatform.__init__(self, "5AGTFC7H3F35I3", _io)

    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clocsk in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
