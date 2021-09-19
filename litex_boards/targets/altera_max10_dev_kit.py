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
from migen.fhdl.tools import list_clock_domains, list_clock_domains_expr

from litex_boards.platforms import altera_max10_dev_kit

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.altera_adc import Max10ADC

from liteeth.phy import LiteEthPHY
from liteeth.phy.mii import LiteEthPHYMII
from liteeth.phy.altera_rgmii import LiteEthPHYRGMII

from litescope import LiteScopeAnalyzer

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, with_rgmii_pll=False, rgmii_tx_delay=2e-9, with_adc_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst.
        clk50 = platform.request("clk50")

        # PLL
        self.submodules.pll = pll = Max10PLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)

        if with_rgmii_pll:
            self.clock_domains.cd_ethphy1_rx = ClockDomain()
            self.clock_domains.cd_ethphy1_tx = ClockDomain()
            self.clock_domains.cd_ethphy1_tx_delayed = ClockDomain(reset_less=True)
            tx_phase = 125e6*rgmii_tx_delay*360
            assert tx_phase < 360
            # first so it uses clkout[0] to directly drive PIN
            pll.create_clkout(self.cd_ethphy1_tx_delayed, 125e6, phase=tx_phase)
            pll.create_clkout(self.cd_ethphy1_tx, 125e6, with_reset=False)

        pll.create_clkout(self.cd_sys, sys_clk_freq)

        if with_adc_pll:
            self.clock_domains.cd_adc = ClockDomain()
            clk10_adc = platform.request("clk10_adc")
            self.submodules.pll_adc = pll_adc = Max10PLL(speedgrade="-6")
            self.comb += pll_adc.reset.eq(self.rst)
            pll_adc.register_clkin(clk10_adc, 10e6)
            pll_adc.create_clkout(self.cd_adc, 10e6)  # first so it uses clkout[0]

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
                 sys_clk_freq=int(125e6),
                 with_led_chaser     = True,
                 with_jtagbone       = False,
                 with_uartbone       = False,
                 with_ethernet       = False,
                 with_etherbone      = False,
                 with_gigabone       = False,
                 eth_ip              = "192.168.43.50",
                 eth_dynamic_ip      = False,
                 with_analyzer       = False,
                 with_adc            = False,
                 **kwargs):
        self.platform = platform = altera_max10_dev_kit.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Altera's Max 10 dev kit",
            ident_version = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_adc_pll=with_adc, with_rgmii_pll=True)

        # Jtagbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        # UARTbone
        if with_uartbone:
            self.add_uartbone(baudrate=3_000_000)

        # Ethernet
        eth_clock_pads0 = self.platform.request("eth_clocks")
        eth_pads0 = self.platform.request("eth")
        if with_ethernet or with_etherbone:
            self.add_constant("USE_ALT_MODE_FOR_88E1111")
            self.add_constant("ALT_MODE_FOR_88E1111_PHYADDR0", 0)
            self.add_constant("ALT_MODE_FOR_88E1111", 0b1111)  # HW_CONFIG GMII

            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = eth_clock_pads0,
                pads       = eth_pads0)
            self.ethphy = ClockDomainsRenamer({"eth_rx": "ethphy_rx", "eth_tx": "ethphy_tx"})(self.ethphy)

            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, phy_cd="ethphy", dynamic_ip=eth_dynamic_ip)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, phy_cd="ethphy", ip_address=eth_ip)

        eth_clock_pads1 = self.platform.request("eth_clocks")
        eth_pads1 = self.platform.request("eth")
        if with_gigabone:
            # self.add_constant("ALT_MODE_FOR_88E1111_PHYADDR1", 1)

            self.submodules.ethphy1 = LiteEthPHYRGMII(
                clock_pads = eth_clock_pads1,
                pads       = eth_pads1,
                cd_eth_rx  = self.crg.cd_ethphy1_rx)
            self.ethphy1 = ClockDomainsRenamer({"eth_rx": "ethphy1_rx",
                                                "eth_tx": "ethphy1_tx",
                                                "eth_tx_delayed": "ethphy1_tx_delayed"})(self.ethphy1)

            import socket
            a0, a1, a2, a3 = socket.inet_aton(eth_ip)
            eth_ip1 = socket.inet_ntoa(bytes([a0, a1, a2, a3+1]))
            if False:
                self.add_etherbone(name="gigabone1",
                                   phy=self.ethphy1,
                                   phy_cd="ethphy1_eth",
                                   mac_address=0x10e2d5000000+1,
                                   ip_address=eth_ip1)
            else:
                # Timing constraints
                eth_rx_clk = self.crg.cd_ethphy1_rx.clk
                eth_tx_clk = self.crg.cd_ethphy1_tx.clk
                self.platform.add_period_constraint(eth_rx_clk, 1e9 / self.ethphy1.rx_clk_freq)
                self.platform.add_period_constraint(eth_tx_clk, 1e9 / self.ethphy1.tx_clk_freq)
                self.platform.add_false_path_constraints(self.crg.cd_sys.clk, eth_rx_clk, eth_tx_clk)
                self.platform.associate_clock_and_pad(eth_rx_clk, self.ethphy1.clock_pads.rx)
                self.platform.associate_clock_and_pad(eth_tx_clk, self.ethphy1.clock_pads.tx)

        # ADC --------------------------------------------------------------------------------------
        if with_adc:
            self.submodules.adc = Max10ADC(adc_num=0)
            self.adc.do_finalize()
            self.platform.add_false_path_constraints(self.crg.cd_sys.clk, self.crg.cd_adc.clk)

        # Analyzer ---------------------------------------------------------------------------------
        if with_analyzer:
            analyzer_signals = list({
                *self.ethphy1._signals,
                self.ethphy1.crg.rx_cnt, self.ethphy1.crg.tx_cnt,
                # *self.ethphy._signals_recursive,
                # *self.ethcore.icmp.echo._signals, *self.ethcore.icmp.rx._signals, *self.ethcore.icmp.tx._signals,
                # *self.ethcore.arp.rx._signals, *self.ethcore.arp.tx._signals,
                # *self.ethcore.mac.core._signals,
                # eth_clock_pads,
                eth_pads1,
                # *self.adc._signals,
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
    parser.add_argument("--sys-clk-freq",        default=125e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--with-jtagbone",       action="store_true", help="Enable JTAGbone support")
    parser.add_argument("--with-uartbone",       action="store_true", help="Enable UARTbone support")
    ethopts = parser.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",      action="store_true", help="Enable 100 Mbps Ethernet support on port A")
    ethopts.add_argument("--with-etherbone",     action="store_true", help="Enable 100 Mbps Etherbone support on port A")
    parser.add_argument("--with-gigabone",       action="store_true", help="Enable Gigabit Etherbone support on port B")
    parser.add_argument("--eth-ip",              default="192.168.43.50", type=str, help="Ethernet/Etherbone IP address")
    parser.add_argument("--eth-dynamic-ip",      action="store_true", help="Enable dynamic Ethernet IP addresses setting")
    parser.add_argument("--with-adc",            action="store_true", help="Enable ADC and internal temperature support")
    parser.add_argument("--with-analyzer",       action="store_true", help="Enable Analyzer support")
    builder_args(parser)
    soc_core_args(parser)
    argparse_set_def(parser, 'csr_csv', 'csr.csv')
    argparse_set_def(parser, 'uart_baudrate', 3_000_000)
    # argparse_set_def(parser, 'uart_fifo_depth', 1024)
    # argparse_set_def(parser, 'cpu_type', 'picorv32')
    # argparse_set_def(parser, 'cpu_variant', 'minimal')
    argparse_set_def(parser, 'integrated_rom_size', 32*1024)
    argparse_set_def(parser, 'integrated_sram_size', 4*1024)

    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq             = int(float(args.sys_clk_freq)),
        with_jtagbone            = args.with_jtagbone,
        with_uartbone            = args.with_uartbone,
        with_ethernet            = args.with_ethernet,
        with_etherbone           = args.with_etherbone,
        with_gigabone            = args.with_gigabone,
        eth_ip                   = args.eth_ip,
        eth_dynamic_ip           = args.eth_dynamic_ip,
        with_analyzer            = args.with_analyzer,
        with_adc                 = args.with_adc,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
