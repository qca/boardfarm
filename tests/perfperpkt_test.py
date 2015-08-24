# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import unittest2
import lib
import iperf_test
import pexpect
import sys
import time

from devices import board, wan, lan, wlan, prompt

class PerfPerPktTest(iperf_test.iPerfTest):
    '''Count various perf events on a per packet basis'''

    def extra(self, perf_parse):
        # calculate abstract IPC
        for p in perf_parse:
            if p['name'] == "instructions":
                insn = p['value']
            if p['name'] == "cycles":
                cyc = p['value']

        ipc = float(insn) / cyc
        self.logged['ipc'] = ipc
        return ", IPC=%.2f" % ipc

    def perf_events(self):
        return ["cycles",
                "instructions",
                "dcache_misses",
                "icache_misses"]

    def runTest(self, client=lan, client_name="br-lan"):
        if not board.check_perf():
            self.result_message = 'perf not in image. skipping test.'
            self.skipTest('perf not installed, skipping test')

        wan_iface = board.get_wan_iface()

        # TODO: remove these and run separate tests
        board.sendline('streamboost disable')
        board.expect(prompt)
        board.sendline('rmmod ecm')
        board.expect(prompt)

        self.pkt_size = 200
        self.conns = 5
        self.test_time = 60

        # work around so we can call from connect testsuite (without reboot)
        board.get_wan_iface()

        self.run_iperf_server(wan)
        self.run_iperf(client, opts="-t %s -P %s -N -m -M %s" % (self.test_time+10, self.conns, self.pkt_size))

        # run perf wrapper command
        board.check_output_perf("sar -u -n DEV 100000 1", self.perf_events())

        speed = self.parse_iperf(client, connections=self.conns, t=self.test_time)
        self.kill_iperf(wan)
        lib.common.test_msg("\n speed was %s Mbit/s" % speed)

        # extract cpu and packet info
        board.sendcontrol('c')
        idle, wan_pps, client_pps = board.parse_sar_iface_pkts(wan_iface, client_name)
        lib.common.test_msg("\n idle cpu: %s" % idle)
        lib.common.test_msg("client pps = %s" % client_pps)
        lib.common.test_msg("wan pps = %s" % wan_pps)

        if client_name is not None:
            total_pps = min(wan_pps, client_pps)
        else:
            total_pps = wan_pps
        lib.common.test_msg("\n using total pps = %s" % total_pps)

        wan_pkts = wan_pps * self.test_time

        if client_name is not None:
            client_pkts = client_pps * self.test_time
        else:
            client_pkts = 'n/a'

        lib.common.test_msg("\n client pkts = %s wan pkts = %s" % (client_pkts, wan_pkts))

        if client_name is not None:
            total_pkts = min(client_pkts, wan_pkts)
        else:
            total_pkts = wan_pkts

        lib.common.test_msg("\n using total packets = %s" % total_pkts)
        self.logged['total_pkts'] = total_pkts

        # extract perf info
        perf_msg = ""

        results = board.parse_perf(self.perf_events())
        for p in results:
            p['value_per_pkt'] = p['value'] / total_pkts
            lib.common.test_msg("\n %s = %s (per pkt = %s)" % \
                    (p['name'], p['value'], p['value_per_pkt']))
            perf_msg += ", %s=%.2f" % (p['sname'], p['value_per_pkt'])

            # restore legacy names
            if p['name'] == "instructions":
                name = "insn_per_pkt"
            elif p['name'] == "cycles":
                name = "cycles_per_pkt"
            elif p['name'] == "dcache_misses":
                name = "dcache_miss_per_pkt"
            elif p['name'] == "icache_misses":
                name = "icache_miss_per_pkt"

            self.logged[name] = float(p['value_per_pkt'])

        extra_msg = self.extra(results)

        self.result_message = "TP=%.2f Mbits/s IDLE=%.2f, PPS=%.2f%s%s" % \
            (speed, idle, total_pps, perf_msg, extra_msg)

        self.logged['test_time'] = self.test_time

class PerfBarrierPerPktTest(PerfPerPktTest):
    '''Count barrier related perf events on a per packet basis'''
    def perf_events(self):
        return ["cycles", "instructions", "data_sync_barrier", "data_mem_barrier"]

    def extra(self, perf_parse):
        return ""

class PerfLockPerPktTest(PerfPerPktTest):
    '''Count lock related perf events on a per packet basis'''
    def perf_events(self):
        return ["cycles", "instructions", "load_exclusive", "store_exclusive"]

    def extra(self, perf_parse):
        return ""

class PerfUnalignedPerPktTest(PerfPerPktTest):
    '''Count unaligned load/store perf events on a per packet basis'''
    def perf_events(self):
        return ["cycles", "instructions", "unaligned_load", "unaligned_store"]

    def extra(self, perf_parse):
        return ""

class PerfPerPktTestWifi(PerfPerPktTest):
    '''Count various perf events on a per packet basis over wifi'''
    def runTest(self):
        # for wlan since it's not reporting packets properly, we just assign
        # it to None and add logic in the parse section to take the other iface
        # packet count if this is none
        super(PerfPerPktTestWifi, self).runTest(client=wlan, client_name=None)
