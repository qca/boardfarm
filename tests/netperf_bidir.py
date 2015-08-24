# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import unittest2
import lib
import netperf_reverse_test
import pexpect
import sys
import time

from devices import board, wan, lan, wlan, prompt

class NetperfBidirTest(netperf_reverse_test.NetperfReverseTest):
    def runTest(self):
        board.sendline('mpstat -P ALL 30 1')
        opts = ""
        num_conns = 1

        up = down = 0.0
        for i in range(0, num_conns):
            self.run_netperf_cmd(lan, "192.168.0.1 -c -C -l 30 -- %s" % opts)
            self.run_netperf_cmd(lan, "192.168.0.1 -c -C -l 30 -t TCP_MAERTS -- %s" % opts)

        for i in range(0, num_conns):
            up += float(self.run_netperf_parse(lan))
            down += float(self.run_netperf_parse(lan))

        board.expect('Average.*idle\r\nAverage:\s+all(\s+[0-9]+.[0-9]+){10}\r\n')
        idle_cpu = float(board.match.group(1))
        avg_cpu = 100 - float(idle_cpu)

        msg = "Bidir speed was %s 10^6Mbits/sec with %s average cpu" % ((up + down), avg_cpu)
        lib.common.test_msg(msg)
        self.result_message = msg
