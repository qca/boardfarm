# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import random
import re

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class Nmap_LAN(rootfs_boot.RootFSBootTest):
    '''Ran nmap port scanning tool on LAN interface.'''
    def recover(self):
        lan.sendcontrol('c')
    def runTest(self):
        lan.sendline('nmap -sS -A -v -p 1-10000 192.168.1.1')
        lan.expect('Starting Nmap')
        lan.expect('Nmap scan report', timeout=660)
        lan.expect(prompt, timeout=60)
        open_ports = re.findall("(\d+)/tcp\s+open", lan.before)
        msg = "Found %s open TCP ports on LAN interface: %s." % \
            (len(open_ports), ", ".join(open_ports))
        self.result_message = msg

class Nmap_WAN(rootfs_boot.RootFSBootTest):
    '''Ran nmap port scanning tool on WAN interface.'''
    def recover(self):
        wan.sendcontrol('c')
    def runTest(self):
        wan_ip_addr = board.get_interface_ipaddr('eth0')
        wan.sendline('\nnmap -sS -A -v %s' % wan_ip_addr)
        wan.expect('Starting Nmap', timeout=5)
        wan.expect('Nmap scan report', timeout=120)
        wan.expect(prompt, timeout=60)
        open_ports = re.findall("(\d+)/tcp\s+open", wan.before)
        msg = "Found %s open TCP ports on WAN interface." % len(open_ports)
        self.result_message = msg
        assert len(open_ports) == 0

class UDP_Stress(rootfs_boot.RootFSBootTest):
    '''Ran nmap through router, creating hundreds of UDP connections.'''
    def runTest(self):
        start_port = random.randint(1, 11000)
        lan.sendline('\nnmap --min-rate 100 -sU -p %s-%s 192.168.0.1' % (start_port, start_port+200))
        lan.expect('Starting Nmap', timeout=5)
        lan.expect('Nmap scan report', timeout=30)
        lan.expect(prompt)
    def recover(self):
        lan.sendcontrol('c')
