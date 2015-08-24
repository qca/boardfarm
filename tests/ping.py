# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class RouterPingWanDev(rootfs_boot.RootFSBootTest):
    '''Router can ping device through WAN interface.'''
    def runTest(self):
        board.sendline('\nping -c5 192.168.0.1')
        board.expect('5 packets received', timeout=10)
        board.expect(prompt)
    def recover(self):
        board.sendcontrol('c')

class RouterPingInternet(rootfs_boot.RootFSBootTest):
    '''Router can ping internet address by IP.'''
    def runTest(self):
        board.sendline('\nping -c2 8.8.8.8')
        board.expect('2 packets received', timeout=10)
        board.expect(prompt)

class RouterPingInternetName(rootfs_boot.RootFSBootTest):
    '''Router can ping internet address by name.'''
    def runTest(self):
        board.sendline('\nping -c2 www.google.com')
        board.expect('2 packets received', timeout=10)
        board.expect(prompt)

class LanDevPingRouter(rootfs_boot.RootFSBootTest):
    '''Device on LAN can ping router.'''
    def runTest(self):
        lan.sendline('\nping -i 0.2 -c 5 192.168.1.1')
        lan.expect('PING ')
        lan.expect('5 received', timeout=15)
        lan.expect(prompt)

class LanDevPingWanDev(rootfs_boot.RootFSBootTest):
    '''Device on LAN can ping through router.'''
    def runTest(self):
        lan.sendline('\nping -i 0.2 -c 5 192.168.0.1')
        lan.expect('PING ')
        lan.expect('5 received', timeout=15)
        lan.expect(prompt)
    def recover(self):
        lan.sendcontrol('c')

class LanDevPingInternet(rootfs_boot.RootFSBootTest):
    '''Device on LAN can ping through router to internet.'''
    def runTest(self):
        lan.sendline('\nping -c2 8.8.8.8')
        lan.expect('2 received', timeout=10)
        lan.expect(prompt)
    def recover(self):
        lan.sendcontrol('c')
