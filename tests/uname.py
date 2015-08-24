# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class Uname(rootfs_boot.RootFSBootTest):
    '''Checked board system information.'''
    def runTest(self):
        board.sendline('\nuname -a')
        board.expect('uname -a', timeout=6)
        board.expect(prompt)
        info = board.before.replace('\r', '').replace('\n', '')
        self.result_message = info
        board.sendline('uname -m')
        board.expect('uname -m')
        board.expect(prompt)
        self.logged['machine'] = board.before.replace('\r', '').replace('\n', '')
        board.sendline('uname -r')
        board.expect('uname -r')
        board.expect(prompt)
        self.logged['release'] = board.before.replace('\r', '').replace('\n', '')
        board.sendline('uname -s')
        board.expect('uname -s')
        board.expect(prompt)
        self.logged['kernel'] = board.before.replace('\r', '').replace('\n', '')
