# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import unittest2
import lib
import rootfs_boot
import pexpect
import sys
import time
import os
from devices import board, wan, lan, wlan, prompt

def install_netperf(device):
    # Check version
    device.sendline('\nnetperf -V')
    try:
        device.expect('Netperf version 2.4', timeout=10)
        device.expect(device.prompt)
    except:
        # Install Netperf
        device.sendline('apt-get update')
        device.expect(device.prompt, timeout=60)
        device.sendline('apt-get -o DPkg::Options::="--force-confnew" -y --force-yes install netperf')
        device.expect(device.prompt, timeout=60)
    device.sendline('/etc/init.d/netperf restart')
    device.expect('Restarting')
    device.expect(device.prompt)

class NetperfTest(rootfs_boot.RootFSBootTest):
    '''Setup Netperf and Ran Throughput.'''
    @lib.common.run_once
    def lan_setup(self):
        super(NetperfTest, self).lan_setup()
        install_netperf(lan)
    @lib.common.run_once
    def wan_setup(self):
        super(NetperfTest, self).wan_setup()
        install_netperf(wan)
    def recover(self):
        lan.sendcontrol('c')

    # if you are spawning a lot of connections, sometimes it
    # takes too long to wait for the connection to be established
    # so we use this version
    def run_netperf_cmd_nowait(self, device, ip, opts="", quiet=False):
        device.sendline('netperf -H %s %s &' % (ip, opts))

    def run_netperf_cmd(self, device, ip, opts="", quiet=False):
        if quiet:
            device.sendline('netperf -H %s %s > /dev/null &' % (ip, opts))
        else:
            device.sendline('netperf -H %s %s &' % (ip, opts))
            device.expect('TEST.*\r\n')

    def run_netperf_parse(self, device, timeout=60):
        device.expect('[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+.[0-9]+\s+([0-9]+.[0-9]+)', timeout=timeout)
        ret = device.match.group(1)
        lib.common.test_msg("Speed was %s 10^6bits/sec" % ret)
        return float(ret)

    def run_netperf(self, device, ip, opts="", timeout=60):
        self.run_netperf_cmd(device, ip, opts=opts)
        return self.run_netperf_parse(device)

    def runTest(self):
        super(NetperfTest, self).runTest()

        board.sendline('mpstat -P ALL 30 1')
        speed = self.run_netperf(lan, "192.168.0.1 -c -C -l 30")
        board.expect('Average.*idle\r\nAverage:\s+all(\s+[0-9]+.[0-9]+){10}\r\n')
        idle_cpu = float(board.match.group(1))
        avg_cpu = 100 - float(idle_cpu)
        lib.common.test_msg("Average cpu usage was %s" % avg_cpu)

        self.result_message = "Setup Netperf and Ran Throughput (Speed = %s 10^6bits/sec, CPU = %s)" % (speed, avg_cpu)

def run_netperf_tcp(device, run_time, pkt_size, direction="up"):
    if direction == "up":
        cmd = "netperf -H 192.168.0.1 -c -C -l %s -- -m %s -M %s -D" % (run_time, pkt_size, pkt_size)
    else:
        cmd = "netperf -H 192.168.0.1 -c -C -l %s -t TCP_MAERTS -- -m %s -M %s -D" % (run_time, pkt_size, pkt_size)
    device.sendline(cmd)
    device.expect('TEST.*\r\n')
    device.expect(device.prompt, timeout=run_time+4)

class Netperf_UpTCP256(rootfs_boot.RootFSBootTest):
    '''Netperf upload throughput (TCP, packets size 256 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=256)

class Netperf_UpTCP512(rootfs_boot.RootFSBootTest):
    '''Netperf upload throughput (TCP, packets size 512 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=512)

class Netperf_UpTCP1024(rootfs_boot.RootFSBootTest):
    '''Netperf upload throughput (TCP, packets size 1024 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=1024)

class Netperf_DownTCP256(rootfs_boot.RootFSBootTest):
    '''Netperf download throughput (TCP, packets size 256 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=256, direction="down")

class Netperf_DownTCP512(rootfs_boot.RootFSBootTest):
    '''Netperf download throughput (TCP, packets size 512 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=512, direction="down")

class Netperf_DownTCP1024(rootfs_boot.RootFSBootTest):
    '''Netperf download throughput (TCP, packets size 1024 Bytes).'''
    def runTest(self):
        run_netperf_tcp(device=lan, run_time=15, pkt_size=1024, direction="down")
