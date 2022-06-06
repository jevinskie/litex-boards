#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

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

    # GPIO serial
    ("gpio_serial", 0,
        Subsignal("tx", Pins("J14:1")),
        Subsignal("rx", Pins("J14:3")),
        IOStandard("3.0-V LVTTL")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # TODO: J4
    # TODO: J13

    # PIN        1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16
    # Inter-board I/Os
    ("J14", "-   E16 -   C16 -   E17 -   D17 -   C17 D23 D18 D22 C18 E22 D19 E21")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk125"
    default_clk_period = 1e9/125e6
    create_rbf         = False
    dump_atoms         = True

    def __init__(self, create_pof=False):
        AlteraPlatform.__init__(self, "10AX048E4F29E3SG", _io, _connectors)
        self.add_platform_command('set_global_assignment -name RESERVE_PIN "AS INPUT TRI-STATED"')
        self.add_platform_command('set_global_assignment -name STRATIX_DEVICE_IO_STANDARD "1.8 V"')
        self.add_platform_command('set_global_assignment -name PRESERVE_UNUSED_XCVR_CHANNEL ON')
        self.add_platform_command('set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION "USE AS REGULAR IO"')
        if create_pof:
            self.add_platform_command('set_global_assignment -name USE_CONFIGURATION_DEVICE ON')
            self.add_platform_command('set_global_assignment -name STRATIXV_CONFIGURATION_SCHEME "ACTIVE SERIAL X4"')
            self.add_platform_command('set_global_assignment -name ACTIVE_SERIAL_CLOCK FREQ_100MHZ')
            self.add_platform_command('set_global_assignment -name STRATIXII_CONFIGURATION_DEVICE EPCQL256')
        # Generate PLL clocsk in STA
        self.toolchain.additional_sdc_commands.append("derive_pll_clocks -create_base_clocks -use_net_name")
        self.toolchain.additional_sdc_commands.append("derive_clock_uncertainty")
        # custom ini
        if os.path.exists("quartus.ini"):
            self.toolchain.additional_ini_settings += [l.rstrip() for l in open("quartus.ini").readlines()]

    def create_programmer(self):
        return USBBlaster(cable_name="USB-BlasterII")

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk125", loose=True), 1e9/125e6)
