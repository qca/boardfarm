# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import lib
import rootfs_boot
import time
import re

import lib.wifi
from devices import board, wan, lan, wlan, prompt

class WiFiMemUse(rootfs_boot.RootFSBootTest):
    '''Measured WiFi memory use when enabled.'''
    def recover(self):
        board.sendcontrol('c')
    def runTest(self):
        # Disable WiFi
        board.sendline('\nwifi detect > /etc/config/wireless')
        board.expect('wifi detect')
        board.expect(prompt)
        board.sendline('uci commit wireless; wifi')
        board.expect(prompt)
        # One of these commands should be available
        board.sendline('iwconfig || iwinfo')
        board.expect(prompt)
        memfree_wifi_off = board.get_memfree()
        # Enable WiFi
        lib.wifi.enable_all_wifi_interfaces(board)
        time.sleep(90) # give time to start and settle
        board.sendline('iwconfig || iwinfo')
        board.expect(['ESSID', 'IEEE'])
        board.expect(prompt)
        memfree_wifi_on = board.get_memfree()
        mem_used = (int(memfree_wifi_off)-int(memfree_wifi_on)) / 1000
        self.result_message = 'Enabling all WiFi interfaces uses %s MB.' % (mem_used)
        self.logged['mem_used'] = mem_used

class TurnOnWifi(rootfs_boot.RootFSBootTest):
    '''Turn on all WiFi interfaces.'''
    def runTest(self):
        wlan_iface = lib.wifi.wifi_interface(board)
        lib.wifi.enable_wifi(board)
        lib.wifi.wait_wifi_up(board, wlan_iface=wlan_iface)
        board.sendline('\nifconfig')
        board.expect('HWaddr')
        board.expect(prompt)
