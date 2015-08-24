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

from devices import board, wan, lan, wlan, prompt

class NetperfReverseTest(netperf_test.NetperfTest):
    '''Setup Netperf and Ran Reverse Throughput.'''
    def runTest(self):
        # setup port forwarding to lan netperf server
        lan_priv_ip = lan.get_interface_ipaddr("eth1")
        board.uci_forward_traffic_redirect("tcp", "12865", lan_priv_ip)
        # setup port for data socket separate from control port
        board.uci_forward_traffic_redirect("tcp", "12866", lan_priv_ip)

        wan_ip = board.get_interface_ipaddr(board.wan_iface)

        # send at router ip, which will forward to lan client
        wan.sendline('')
        wan.expect(prompt)
        board.sendline('mpstat -P ALL 30 1')
        speed = self.run_netperf(wan, wan_ip, "-c -C -l 30 -t TCP_STREAM -- -P ,12866")
        board.expect('Average.*idle\r\nAverage:\s+all(\s+[0-9]+.[0-9]+){10}\r\n')
        idle_cpu = float(board.match.group(1))
        avg_cpu = 100 - float(idle_cpu)
        lib.common.test_msg("Average cpu usage was %s" % avg_cpu)

        self.result_message = "Setup NetperfReverse and Ran Throughput (Speed = %s 10^6bits/sec, CPU = %s)" % (speed, avg_cpu)
