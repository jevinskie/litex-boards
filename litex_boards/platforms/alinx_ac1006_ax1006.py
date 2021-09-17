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
    ("rst_n", 0, Pins("M15"), IOStandard("3.3-V LVTTL")),
    ("clk50", 0, Pins("E1"), IOStandard("3.3-V LVTTL")),

    # LEDs
    ("user_led", 0, Pins("R16"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("P16"), IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("N15"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("N16"), IOStandard("3.3-V LVTTL")),

    # Buttons
    ("user_btn", 0, Pins("M16"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 1, Pins("E16"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 2, Pins("E15"), IOStandard("3.3-V LVTTL")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("R6")),
        Subsignal("rx", Pins("M1")),
        IOStandard("3.3-V LVTTL")
     ),

    # SDR SDRAM
    ("sdram_clock", 0, Pins("D3"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("cke", Pins("C9")),
        Subsignal("a",   Pins("B5 A4 B4 A2 D6 C6 E7 D8 C8 E8 A5 F8 F9")),
        Subsignal("dq",  Pins(
            "A15 B14 A14 B13 A13 B12 A12 B11",
            "E9  C11 E10 D11 D12 C14 E11 D14"),
            Misc("FAST_OUTPUT_ENABLE_REGISTER ON"),
            Misc("FAST_INPUT_REGISTER ON")),
        Subsignal("ba",    Pins("A6 B6")),
        Subsignal("cas_n", Pins("B10")),
        Subsignal("cs_n",  Pins("A7")),
        Subsignal("ras_n", Pins("B7")),
        Subsignal("we_n",  Pins("A10")),
        Misc("CURRENT_STRENGTH_NEW \"MAXIMUM CURRENT\""),
        Misc("FAST_OUTPUT_REGISTER ON"),
        Misc("ALLOW_SYNCH_CTRL_USAGE OFF"),
        IOStandard("3.3-V LVTTL"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf         = False

    def __init__(self):
        # AlteraPlatform.__init__(self, "10CL006YU256C8G", _io, _connectors)
        AlteraPlatform.__init__(self, "10CL016YU256C8G", _io, _connectors)
        for cmd in [
            'set_global_assignment -name RESERVE_ALL_UNUSED_PINS_WEAK_PULLUP "AS INPUT TRI-STATED"',
            'set_global_assignment -name STRATIX_DEVICE_IO_STANDARD "3.3-V LVTTL"',
            'set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION "USE AS REGULAR IO"',
            'set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION "USE AS REGULAR IO"',
            'set_global_assignment -name RESERVE_DATA1_AFTER_CONFIGURATION "USE AS REGULAR IO"',
            'set_global_assignment -name RESERVE_FLASH_NCE_AFTER_CONFIGURATION "USE AS REGULAR IO"',
            'set_global_assignment -name RESERVE_DCLK_AFTER_CONFIGURATION "USE AS REGULAR IO"',
        ]:
            self.add_platform_command(cmd)

    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        # self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clock in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        # Calculates clock uncertainties
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
