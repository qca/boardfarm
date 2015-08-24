# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time

import rootfs_boot

from devices import board, wan, lan, wlan, prompt
from lib.common import run_once

class Set_IPv6_Addresses(rootfs_boot.RootFSBootTest):
    '''Set IPv6 addresses and default routes for router and devices.'''
    @run_once
    def runTest(self):
        # Router
        board.sendline('uci set network.lan6=interface')
        board.expect(prompt)
        board.sendline('uci set network.lan6.proto=static')
        board.expect(prompt)
        board.sendline('uci set network.lan6.ip6addr=4aaa::1/64')
        board.expect(prompt)
        board.sendline('uci set network.lan6.ifname=@lan')
        board.expect(prompt)
        board.sendline('uci set network.wan6=interface')
        board.expect(prompt)
        board.sendline('uci set network.wan6.proto=static')
        board.expect(prompt)
        board.sendline('uci set network.wan6.ip6addr=5aaa::1/64')
        board.expect(prompt)
        board.sendline('uci set network.wan6.ifname=@wan')
        board.expect(prompt)
        board.sendline('uci commit network')
        board.expect(prompt)
        board.network_restart()
        # Lan-side Device
        lan.sendline('\nip -6 addr add 4aaa::6/64 dev eth1')
        lan.expect('ip -6')
        lan.expect(prompt)
        lan.sendline('ip -6 route add 4aaa::1 dev eth1')
        lan.expect(prompt)
        lan.sendline('ip -6 route add default via 4aaa::1 dev eth1')
        lan.expect(prompt)
        if 'No route to host' in lan.before:
            raise Exception('Error setting ivp6 routes')
        # Wan-side Device
        wan.sendline('\nip -6 addr add 5aaa::6/64 dev eth1')
        wan.expect('ip -6')
        wan.expect(prompt)
        wan.sendline('ip -6 route add 5aaa::1 dev eth1')
        wan.expect(prompt)
        wan.sendline('ip -6 route add default via 5aaa::1 dev eth1')
        wan.expect(prompt)
        if 'No route to host' in wan.before:
            raise Exception('Error setting ivp6 routes')
        # Wlan-side Device
        if wlan:
            wlan.sendline('\nip -6 addr add 4aaa::7/64 dev wlan0')
            wlan.expect('ip -6')
            wlan.expect(prompt)
            wlan.sendline('ip -6 route add 4aaa::1 dev eth1')
            wlan.expect(prompt)
            wlan.sendline('ip -6 route add default via 4aaa::1 dev wlan0')
            wlan.expect(prompt)
        # Give things time to get ready
        time.sleep(20)
        # Check addresses
        board.sendline('\nifconfig | grep -B2 addr:')
        board.expect('ifconfig ')
        board.expect(prompt)
        lan.sendline('\nifconfig | grep -B2 addr:')
        lan.expect('ifconfig ')
        lan.expect(prompt)
        wan.sendline('\nifconfig | grep -B2 addr:')
        wan.expect('ifconfig ')
        wan.expect(prompt)


class Remove_IPv6_Addresses(rootfs_boot.RootFSBootTest):
    '''Removed IPv6 addresses and default routes for router and devices.'''
    def runTest(self):
        board.sendline('\nuci delete network.lan.ip6addr')
        board.expect('uci ')
        board.expect(prompt)
        board.sendline('uci delete network.wan.ip6addr')
        board.expect(prompt)
        board.sendline('ip -6 addr delete 5aaa::1/64 dev eth0')
        board.expect(prompt)
        board.sendline('uci commit network')
        board.expect(prompt)
        board.network_restart()
        # Lan-side Device
        lan.sendline('\nip -6 addr del 4aaa::6/64 dev eth1')
        lan.expect('ip -6')
        lan.expect(prompt)
        lan.sendline('ip -6 route del default')
        lan.expect(prompt)
        # Wan-side Device
        wan.sendline('\nip -6 addr del 5aaa::6/64 dev eth1')
        wan.expect('ip -6')
        wan.expect(prompt)
        wan.sendline('ip -6 route del default')
        wan.expect(prompt)
        time.sleep(10)
