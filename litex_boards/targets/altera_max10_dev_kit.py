#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from migen.genlib.cdc import ClockBuffer

from litex_boards.platforms import altera_max10_dev_kit

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.mii import LiteEthPHYMII

from litescope import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_usb_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BareSoC(SoCCore):
    def __init__(self, platform, clk_freq, sys_clk_freq=int(50e6), **kwargs):
        super().__init__(platform, clk_freq, **kwargs)
        self.platform = platform = altera_max10_dev_kit.Platform()

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Altera's Max 10 dev kit",
            ident_version = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=False)

        # JTAGBone
        self.add_jtagbone()

        # self.add_uartbone(baudrate=3_000_000)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)

class BaseSoC(SoCCore):
    def __init__(self,
                 sys_clk_freq=int(50e6),
                 with_led_chaser     = True,
                 with_jtagbone       = False,
                 with_uartbone       = False,
                 with_ethernet       = False,
                 with_etherbone      = False,
                 eth_ip              = "192.168.43.50",
                 eth_dynamic_ip      = False,
                 with_analyzer       = False,
                 **kwargs):
        self.platform = platform = altera_max10_dev_kit.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Altera's Max 10 dev kit",
            ident_version = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq, with_usb_pll=False)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # UARTbone
        if with_uartbone:
            self.add_uartbone(baudrate=3_000_000)

        # Ethernet
        if with_ethernet or with_etherbone:
            eth_clock_pads = self.platform.request("eth_clocks")
            eth_pads = self.platform.request("eth")
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = eth_clock_pads,
                pads       = eth_pads)
            # self.specials.eth_rx_clk_buf = ClockBuffer(self.ethphy.crg.cd_eth_rx)
            self.platform.toolchain.additional_sdc_commands += [
                'create_clock -name eth_rx_clk -period 40.0 [get_ports {eth_clocks_rx}]',
                'create_clock -name eth_tx_clk -period 40.0 [get_ports {eth_clocks_tx}]',
                'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_rx_clk}]',
                'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_tx_clk}]',
                'set_false_path -from [get_clocks {eth_rx_clk}] -to [get_clocks {eth_tx_clk}]',
            ]
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # Analyzer ---------------------------------------------------------------------------------
        if with_analyzer:
            analyzer_signals = list({
                *self.ethphy._signals,
                # *self.ethphy._signals_recursive,
                # *self.ethcore.icmp.echo._signals, *self.ethcore.icmp.rx._signals, *self.ethcore.icmp.tx._signals,
                *self.ethcore.arp.rx._signals, *self.ethcore.arp.tx._signals,
                # eth_clock_pads,
                eth_pads,
            })
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 256,
                clock_domain = "sys",
                register     = True,
                csr_csv      = "analyzer.csv")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
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
    parser = argparse.ArgumentParser(description="LiteX SoC on DECA")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--with-jtagbone",       action="store_true", help="Enable Jtagbone support")
    parser.add_argument("--with-uartbone",       action="store_true", help="Enable Jtagbone support")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",      action="store_true", help="Enable Ethernet support")
    ethopts.add_argument("--with-etherbone",     action="store_true", help="Enable Etherbone support")
    parser.add_argument("--eth-ip",              default="192.168.43.50", type=str, help="Ethernet/Etherbone IP address")
    parser.add_argument("--eth-dynamic-ip",      action="store_true", help="Enable dynamic Ethernet IP addresses setting")
    parser.add_argument("--with-analyzer",       action="store_true", help="Enable Analyzer support")
    builder_args(parser)
    soc_core_args(parser)
    argparse_set_def(parser, 'csr_csv', 'csr.csv')
    argparse_set_def(parser, 'uart_baudrate', 3_000_000)
    # argparse_set_def(parser, 'uart_fifo_depth', 1024)
    # argparse_set_def(parser, 'cpu_type', 'picorv32')
    # argparse_set_def(parser, 'cpu_variant', 'minimal')

    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_jtagbone            = args.with_jtagbone,
        with_uartbone            = args.with_uartbone,
        with_ethernet            = args.with_ethernet,
        with_etherbone           = args.with_etherbone,
        eth_ip                   = args.eth_ip,
        eth_dynamic_ip           = args.eth_dynamic_ip,
        with_analyzer            = args.with_analyzer,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
