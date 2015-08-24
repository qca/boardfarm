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

class NetperfUdpTest(netperf_test.NetperfTest):
    @lib.common.run_once
    def runTest(self):
        super(NetperfUdpTest, self).runTest()

        self.run_netperf(lan, "192.168.0.1 -c -C -l 30 -t UDP_STREAM -- -m 1460 -M 1460")

        # setup port forwarding to lan netperf server
        lan_priv_ip = lan.get_interface_ipaddr("eth1")
        board.uci_forward_traffic_redirect("tcp", "12865", lan_priv_ip)
        # setup port for data socket separate from control port
        board.uci_forward_traffic_redirect("udp", "12866", lan_priv_ip)

        wan_ip = board.get_interface_ipaddr(board.wan_iface)

        # send at router ip, which will forward to lan client
        wan.sendline('')
        wan.expect(prompt)
        self.run_netperf(wan, wan_ip, "-c -C -l 30 -t UDP_STREAM -- -P ,12866 -m 1460 -M 1460")
