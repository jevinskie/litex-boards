#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from litex_boards.platforms import deca

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.led import LedChaser

from litescope import LiteScopeAnalyzer
from migen.genlib.cdc import AsyncResetSynchronizer
from litex.soc.cores.jtag import JTAGPHY, MAX10JTAG, JTAGTAPFSM

import litex.gen.fhdl.migen_addons

class JTAGHello(Module):
    def __init__(self, tms: Signal, tck: Signal, tdi: Signal, tdo: Signal, rst: Signal, phy: Module):
        self.hello_dr = hello_dr = Signal(32, reset=0xAA00FF55)

        # self.comb += tdo.eq(hello_dr[0])
        self.hello_inner_tdo = hello_inner_tdo = Signal()
        self.comb += tdo.eq(hello_inner_tdo)

        self.sync.jtag += [
            If(phy.reset | phy.capture,
                hello_dr.eq(hello_dr.reset),
            ).Elif(phy.shift,
                hello_dr.eq(Cat(hello_dr[1:], tdi)),
            ),
        ]

        self.comb += hello_inner_tdo.eq(hello_dr[0])
        # self.sync.jtag_inv += hello_inner_tdo.eq(hello_dr[0])

        # # #


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_usb    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)
        pll.create_clkout(self.cd_hdmi, 40e6)

        # USB PLL.
        if with_usb_pll:
            ulpi  = platform.request("ulpi")
            self.comb += ulpi.cs.eq(1) # Enable ULPI chip to enable the ULPI clock.
            self.submodules.usb_pll = pll = Max10PLL(speedgrade="-6")
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(ulpi.clk, 60e6)
            pll.create_clkout(self.cd_usb, 60e6, phase=-120) # -120° from DECA's example (also validated with LUNA).

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_led_chaser=True, with_uartbone=False, with_jtagbone=False,
                 with_video_terminal=False,
                 **kwargs):
        self.platform = platform = deca.Platform()

        # Defaults to JTAG-UART since no hardware UART.
        real_uart_name = kwargs["uart_name"]
        if real_uart_name == "serial":
            if with_jtagbone:
                kwargs["uart_name"] = "crossover"
            else:
                kwargs["uart_name"] = "jtag_atlantic"
        if with_uartbone:
            kwargs["uart_name"] = "crossover"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Terasic DECA",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=False)

        # UARTbone ---------------------------------------------------------------------------------
        if with_uartbone:
            self.add_uartbone(name=real_uart_name, baudrate=kwargs["uart_baudrate"])

        # JTAGbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()
        else:
            # JTAG Hello ---------------------------------------------------------------------------
            platform.add_reserved_jtag_decls()
            reserved_pads = platform.get_reserved_jtag_pads()
            self.submodules.jtag_phy = MAX10JTAG(chain=1, reserved_pads=reserved_pads)

            self.clock_domains.cd_jtag = ClockDomain()
            self.comb += ClockSignal("jtag").eq(self.jtag_phy.tck)
            self.specials += AsyncResetSynchronizer(self.cd_jtag, ResetSignal("sys"))

            self.hello_tdo = hello_tdo = Signal()
            self.submodules.jtag_hello = JTAGHello(self.jtag_phy.tms, self.jtag_phy.tck, self.jtag_phy.tdi,
                                                   hello_tdo, ResetSignal("sys"), self.jtag_phy)
            self.comb += self.jtag_phy.tdo.eq(hello_tdo)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoDVIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        if True:
            analyzer_signals = set([
                *self.jtagbone_phy.jtag._signals(recurse=True),
                # *self.jtag_phy._signals(recurse=True),
                # *self.jtag_hello._signals(recurse=True),
            ])
            analyzer_signals -= set([self.jtagbone_phy.jtag.altera_reserved_tdo])
            # analyzer_signals -= set([self.jtag_phy.altera_reserved_tdo])
            print(f"analyzer_signals: {analyzer_signals}")
            self.submodules.analyzer = LiteScopeAnalyzer(list(analyzer_signals),
                                                         depth          = 256,
                                                         register       = True,
                                                         clock_domain   = "sys",
                                                         csr_csv        = "analyzer.csv")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on DECA")
    parser.add_argument("--build",               action="store_true", help="Build bitstream.")
    parser.add_argument("--load",                action="store_true", help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",        default=100e6,        help="System clock frequency.")
    parser.add_argument("--with-uartbone",       action="store_true", help="Enable UARTbone support.")
    parser.add_argument("--with-jtagbone",       action="store_true", help="Enable JTAGbone support.")
    parser.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA).")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_uartbone            = args.with_uartbone,
        with_jtagbone            = args.with_jtagbone,
        with_video_terminal      = args.with_video_terminal,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
