#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from litex_boards.platforms import gidel_hawkeye

from litex.gen.fhdl.utils import get_signals
from litex.soc.cores.clock import Arria10FPLL, Arria10IOPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litescope import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst.
        clk125 = platform.request("clk125")

        # PLL
        self.submodules.pll = pll = Arria10FPLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk125, 125e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(200), with_led_chaser=True, **kwargs):
        self.platform = platform = gidel_hawkeye.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Gidel HawkEye Arria 10",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq)

        # UARTbone ---------------------------------------------------------------------------------
        self.add_uartbone(name="gpio_serial", baudrate=kwargs["uart_baudrate"])

        # JTAGbone ---------------------------------------------------------------------------------
        if os.path.exists("jtag.sdc"):
            self.platform.toolchain.additional_sdc_commands += \
                [l.rstrip() for l in open("jtag.sdc").readlines()]
        else:
            raise ValueError("no jtag.sdc")
            self.platform.toolchain.additional_sdc_commands.insert(0,
                'create_clock -name jtag -period 30.0 [get_ports {altera_reserved_tck}]',
            )

        self.add_jtagbone()

        # scope ------------------------------------------------------------------------------------
        analyzer_signals = list(set([
            Signal()
        ]))

        self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                                                     depth = 1024*16,
                                                     clock_domain = "sys",
                                                     register = True,
                                                     csr_csv = "analyzer.csv")

        # Leds -------------------------------------------------------------------------------------
        led_pads = platform.request_remaining("user_led")
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = led_pads,
                sys_clk_freq = sys_clk_freq)


# Build --------------------------------------------------------------------------------------------

def argparse_set_def(parser: argparse.ArgumentParser, dst: str, default):
    changed = False
    for a in parser._actions:
        if dst == a.dest:
            a.default = default
            return
    raise ValueError(f'dest var {dst} arg not found')

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Arria V thingy")
    parser.add_argument("--build",               action="store_true", help="Build bitstream.")
    parser.add_argument("--load",                action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",        default=200e6,       help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)

    # argparse_set_def(parser, "cpu_type", "None")
    argparse_set_def(parser, "uart_name", "crossover")
    # argparse_set_def(parser, "uart_name", "gpio_serial")
    argparse_set_def(parser, "uart_baudrate", 2_000_000)
    argparse_set_def(parser, "csr_csv", "csr.csv")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
