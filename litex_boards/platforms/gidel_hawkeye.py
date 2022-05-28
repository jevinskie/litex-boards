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

    # Leds.

    # DDR4 SDRAM.
    ("ddram", 0,
    ),

    # SGMII Ethernet

    # GPIO 1
    ("gpio", 0, Pins(
        ""),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO 2
    ("gpio", 1, Pins(
        ""),
        IOStandard("3.3-V LVTTL")
    ),

    # GPIO 3
    ("gpio", 2, Pins(
        ""),
        IOStandard("3.3-V LVTTL")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("J4", ""),
    ("J13", ""),
    ("J14", "")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf         = False

    def __init__(self):
        AlteraPlatform.__init__(self, "10AX048E4F29E3SG", _io, _connectors)
        self.add_platform_command('set_global_assignment -name RESERVE_PIN "AS INPUT TRI-STATED"')

    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
        # Generate PLL clocsk in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
