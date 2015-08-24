# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import unittest2
import lib
import netperf_test
import pexpect
import sys
import time

from netperf_test import install_netperf
from devices import board, wan, lan, wlan, prompt

class NetperfStressTest(netperf_test.NetperfTest):
    @lib.common.run_once
    def wan_setup(self):
        install_netperf(wan)
    @lib.common.run_once
    def lan_setup(self):
        install_netperf(lan)

    def runTest(self):
        # Record number of bytes and packets sent through interfaces
        board.sendline("\nifconfig | grep 'encap\|packets\|bytes'")
        board.expect('br-lan')
        board.expect(prompt)

        # Start netperf tests
        num_conn = 200
        run_time = 30
        pkt_size = 256

        board.sendline('mpstat -P ALL %s 1' % run_time)
        print("\nStarting %s netperf tests in parallel." % num_conn)
        opts = '192.168.0.1 -c -C -l %s -- -m %s -M %s -D' % (run_time, pkt_size, pkt_size)
        for i in range(0, num_conn):
            self.run_netperf_cmd_nowait(lan, opts)
        # Let netperf tests run
        time.sleep(run_time*1.5)

        board.expect('Average:\s+all.*\s+([0-9]+.[0-9]+)\r\n')
        idle_cpu = board.match.group(1)
        avg_cpu = 100 - float(idle_cpu)
        print("Average cpu usage was %s" % avg_cpu)

        # try to flush out backlog of buffer from above, we try b/c not all might start
        # correctly
        try:
            for i in range(0, num_conn):
                lan.exepct('TEST')
        except:
            pass

        # add up as many netperf connections results that were established
        try:
            bandwidth = 0.0
            conns_parsed = 0
            for i in range(0, num_conn):
                bandwidth += self.run_netperf_parse(lan, timeout=1) * run_time
                conns_parsed += 1
        except Exception as e:
            # print the exception for logging reasons
            print(e)
            pass

        # make sure at least one netperf was run
        assert (conns_parsed > 0)

        board.sendline('pgrep logger | wc -l')
        board.expect('([0-9]+)\r\n')
        n = board.match.group(1)

        print("Stopped with %s connections, %s netperf's still running" % (conns_parsed, n))
        print("Mbits passed was %s" % bandwidth)

        # Record number of bytes and packets sent through interfaces
        board.sendline("ifconfig | grep 'encap\|packets\|bytes'")
        board.expect('br-lan')
        board.expect(prompt)

        lan.sendline('killall netperf')
        lan.expect(prompt)
        lan.sendline("")
        lan.expect(prompt)
        lib.common.clear_buffer(lan)

        self.result_message = "Ran %s/%s for %s seconds (Pkt Size = %s, Mbits = %s, CPU = %s)" \
                                    % (conns_parsed, num_conn, run_time, pkt_size, bandwidth, avg_cpu)
