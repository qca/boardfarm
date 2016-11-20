# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import string
import time

import rootfs_boot
from devices import board, wan, lan, wlan, prompt
from lib.wifi import *

def wifi_cycle(board, num_times=5, wlan_iface="ath0"):
    '''Enable and disable wifi some number of times.'''
    if wifi_on(board):
        disable_wifi(board, wlan_iface)
    wifi_name = randomSSIDName()
    board.sendline('uci set wireless.@wifi-iface[0].ssid=%s' % wifi_name)
    board.expect(prompt)
    board.sendline('uci set wireless.@wifi-iface[0].encryption=psk2')
    board.expect(prompt)
    board.sendline('uci set wireless.@wifi-iface[0].key=%s' % randomSSIDName())
    board.expect(prompt)
    board.sendline('echo "7 7 7 7" > /proc/sys/kernel/printk')
    board.expect(prompt)
    for i in range(1, num_times+1):
        enable_wifi(board)
        wait_wifi_up(board, wlan_iface=wlan_iface)
        disable_wifi(board, wlan_iface=wlan_iface)
        print("\n\nEnabled and disabled WiFi %s times." % i)
    board.sendline('echo "1 1 1 7" > /proc/sys/kernel/printk')
    board.expect(prompt)

class WiFiOnOffCycle(rootfs_boot.RootFSBootTest):
    '''Enabled and disabled wifi once.'''
    def runTest(self):
        wlan_iface = wifi_interface(board)
        if wlan_iface is None:
            self.skipTest("No wifi interfaces detected, skipping..")

        wifi_cycle(board, num_times=1, wlan_iface=wlan_iface)

class WiFiOnOffCycle5(rootfs_boot.RootFSBootTest):
    '''Enabled and disabled wifi 5 times.'''
    def runTest(self):
        wlan_iface = wifi_interface(board)
        if wlan_iface is None:
            self.skipTest("No wifi interfaces detected, skipping..")

        wifi_cycle(board, num_times=5, wlan_iface=wlan_iface)

class WiFiOnOffCycle20(rootfs_boot.RootFSBootTest):
    '''Enabled and disabled wifi 20 times.'''
    def runTest(self):
        wlan_iface = wifi_interface(board)
        if wlan_iface is None:
            self.skipTest("No wifi interfaces detected, skipping..")

        wifi_cycle(board, num_times=20, wlan_iface=wlan_iface)
        # Leave with wifi enabled
        enable_wifi(board)
        wait_wifi_up(board, wlan_iface=wlan_iface)
