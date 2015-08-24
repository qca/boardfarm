# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class KernelModules(rootfs_boot.RootFSBootTest):
    '''lsmod shows loaded kernel modules.'''
    def runTest(self):
        board.sendline('\nlsmod | wc -l')
        board.expect('lsmod ')
        board.expect('(\d+)\r\n')
        num = int(board.match.group(1)) - 1 # subtract header line
        board.expect(prompt)
        board.sendline('lsmod | sort')
        board.expect(prompt)
        self.result_message = '%s kernel modules are loaded.' % num
        self.logged['num_loaded'] = num
