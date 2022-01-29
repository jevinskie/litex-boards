#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Jevin Sweval <jevinsweval@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from migen import *
from litex_boards.platforms import hpc_store_arriav_v31 as arriav_board

from litex.soc.cores.clock import ArriaVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoDVIPHY
from litex.soc.cores.led import LedChaser

from litex.config import DEFAULT_IP_PREFIX

from liteeth.phy.mii import LiteEthPHYMII

from litescope.core import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = ArriaVPLL(speedgrade="-3")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,  sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(150e6), with_led_chaser=True, with_uartbone=False, with_jtagbone=False,
                 with_ethernet=False, with_etherbone=False, eth_ip=DEFAULT_IP_PREFIX + "50",
                 eth_dynamic_ip=False,
                 **kwargs):
        self.platform = platform = arriav_board.Platform()

        if with_uartbone:
            kwargs["uart_name"] = "crossover"

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on Arria V thingy",
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = self.crg = _CRG(platform, sys_clk_freq)

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.platform.toolchain.additional_sdc_commands += [
                # 'create_clock -name eth_rx_clk -period 40.0 [get_ports {eth_clocks_rx}]',
                # 'create_clock -name eth_tx_clk -period 40.0 [get_ports {eth_clocks_tx}]',
                # 'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_rx_clk}]',
                # 'set_false_path -from [get_clocks {sys_clk}] -to [get_clocks {eth_tx_clk}]',
                # 'set_false_path -from [get_clocks {eth_rx_clk}] -to [get_clocks {eth_tx_clk}]',
            ]
            eth_clock_pads = self.platform.request("eth_clocks")
            eth_pads = self.platform.request("eth")
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = eth_clock_pads,
                pads       = eth_pads)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip)

        # UARTbone ---------------------------------------------------------------------------------
        if with_uartbone:
            self.add_uartbone(name=real_uart_name, baudrate=kwargs["uart_baudrate"])

        # JTAGbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        if True:
            dbg_tx_clk = Signal(8)
            dbg_rx_clk = Signal(8)
            dbg_gtx_clk = Signal(8)
            self.sync.eth_tx += dbg_tx_clk.eq(dbg_tx_clk + 1)
            self.sync.eth_rx += dbg_rx_clk.eq(dbg_rx_clk + 1)
            self.clock_domains.cd_eth_gtx = ClockDomain()
            self.comb += ClockSignal("eth_gtx").eq(eth_clock_pads.gtx)
            self.sync.eth_gtx += dbg_gtx_clk.eq(dbg_gtx_clk + 1)

            analyzer_signals = {
                # *self.ethphy1._signals,
                # self.ethphy.rx.source,
                # self.ethphy.tx.sink,
                # self.ethphy1.crg.rx_cnt, self.ethphy1.crg.tx_cnt,
                # *self.ethphy._signals_recursive,
                # *self.ethcore.icmp.echo._signals, *self.ethcore.icmp.rx._signals, *self.ethcore.icmp.tx._signals,
                # *self.gigabone1_ethcore.arp.rx._signals, *self.gigabone1_ethcore.arp.tx._signals,
                # *self.ethcore.mac.core._signals,
                # eth_clock_pads,
                # eth_pads,
                eth_pads.mdio, eth_pads.mdc,
                # dbg_tx_clk, dbg_rx_clk,
                # dbg_gtx_clk,
                # *self.adc._signals,
            }
            analyzer_signals_denylist = {
                None,
                # self.ethphy1.clock_pads, eth_pads1.tx_data, eth_pads1.tx_ctl,
                # self.gigabone1_ethcore.arp.rx.depacketizer.header,
                # self.gigabone1_ethcore.arp.tx.packetizer.header,
            }
            analyzer_signals -= analyzer_signals_denylist
            analyzer_signals = list(analyzer_signals)
            self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
                depth        = 1024*16,
                clock_domain = "sys",
                register     = True,
                samplerate   = sys_clk_freq,
                csr_csv      = "analyzer.csv")

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
    parser.add_argument("--sys-clk-freq",        default=150e6,       help="System clock frequency.")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",      action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",     action="store_true", help="Enable Etherbone support.")
    parser.add_argument("--eth-ip",              default=DEFAULT_IP_PREFIX + "50", type=str, help="Ethernet/Etherbone IP address.")
    parser.add_argument("--eth-dynamic-ip",      action="store_true", help="Enable dynamic Ethernet IP addresses setting.")
    parser.add_argument("--with-uartbone",       action="store_true", help="Enable UARTbone support.")
    parser.add_argument("--with-jtagbone",       action="store_true", help="Enable JTAGbone support.")
    builder_args(parser)
    soc_core_args(parser)

    argparse_set_def(parser, 'uart_baudrate', 2_000_000)
    argparse_set_def(parser, 'integrated_rom_size', 32*1024)
    argparse_set_def(parser, 'integrated_sram_size', 4*1024)


    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_ethernet            = args.with_ethernet,
        with_etherbone           = args.with_etherbone,
        eth_ip                   = args.eth_ip,
        eth_dynamic_ip           = args.eth_dynamic_ip,
        with_uartbone            = args.with_uartbone,
        with_jtagbone            = args.with_jtagbone,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
