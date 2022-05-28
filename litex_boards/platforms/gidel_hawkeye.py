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
    # Clk / Rst
    ("clk100",   0, Pins("AA16"), IOStandard("HCSL")),
    ("clk125",   0, Pins("AA16"), IOStandard("1.8 V")),

    # LEDs
    ("user_led", 0, Pins("F17"),  IOStandard("3.0-V LVTTL")),
    ("user_led", 1, Pins("H22"),  IOStandard("3.0-V LVTTL")),
    ("user_led", 2, Pins("H23"),  IOStandard("3.0-V LVTTL")),
    ("user_led", 3, Pins("E20"),  IOStandard("3.0-V LVTTL")),
    ("user_led", 4, Pins("D20"),  IOStandard("3.0-V LVTTL")),

    # SGMII Ethernet

    # DDR4 SDRAM

    # PCIe

    # GPIO 1 (J4)

    # GPIO 2 (J13)

    # GPIO 3 (J14)
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # ("J4", "- K17 H16 "),
    # ("J13", ""),
    # ("J14", "")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6
    create_rbf         = False

    def __init__(self):
        AlteraPlatform.__init__(self, "10AX048E4F29E3SG", _io, _connectors)
        self.add_platform_command('set_global_assignment -name RESERVE_PIN "AS INPUT TRI-STATED"')
        self.add_platform_command('set_global_assignment -name STRATIX_DEVICE_IO_STANDARD "1.8 V"')
        self.add_platform_command('set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION "USE AS REGULAR IO"')


    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
        # Generate PLL clocsk in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
