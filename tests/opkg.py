# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class OpkgList(rootfs_boot.RootFSBootTest):
    '''Opkg list shows installed packages.'''
    def runTest(self):
        board.sendline('\nopkg list-installed | wc -l')
        board.expect('opkg list')
        board.expect('(\d+)\r\n')
        num_pkgs = int(board.match.group(1))
        board.expect(prompt)
        board.sendline('opkg list-installed')
        board.expect(prompt)
        self.result_message = '%s OpenWrt packages are installed.' % num_pkgs
        self.logged['num_installed'] = num_pkgs

class CheckQosScripts(rootfs_boot.RootFSBootTest):
    '''Package "qos-scripts" is not installed.'''
    def runTest(self):
        board.sendline('\nopkg list | grep qos-scripts')
        try:
            board.expect('qos-scripts - ', timeout=4)
        except:
            return   # pass if not installed
        assert False # fail if installed

