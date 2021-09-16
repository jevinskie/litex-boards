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
