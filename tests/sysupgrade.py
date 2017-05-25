# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time
import unittest2
import rootfs_boot
import lib
from devices import board, wan, lan, wlan, prompt

class Sysupgrade(rootfs_boot.RootFSBootTest):
    '''Upgrading via sysupgrade works.'''
    def runTest(self):
        super(Sysupgrade, self).runTest()

        if not hasattr(self.config, "SYSUPGRADE_NEW"):
            self.skipTest("no sysupgrade specified")

        # output some stuff before we kill all the logs in the system, just
        # to be able to review these logs later
        board.sendline('logread')
        board.expect(prompt, timeout=120)
        board.sendline('dmesg')
        board.expect(prompt)

        # This test can damage flash, so to properly recover we need
        # to reflash upon recovery
        self.reflash = True

        board.sendline('touch /etc/config/TEST')
        board.expect('/etc/config/TEST')
        board.expect(prompt)

        board.sendline("cd /tmp")
        filename = board.prepare_file(self.config.SYSUPGRADE_NEW)
        new_filename = board.tftp_get_file(board.tftp_server,
                                                filename, 240)
        board.sendline("sysupgrade -v /tmp/%s" %
                new_filename)
        board.expect("Restarting system", timeout=180)

        lib.common.wait_for_boot(board)
        board.boot_linux()
        board.wait_for_linux()

        board.sendline('ls -alh /etc/config/TEST')
        board.expect('/etc/config/TEST\r\n')
        board.expect(prompt)
