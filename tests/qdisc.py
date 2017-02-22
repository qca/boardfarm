# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class DelQdisc(rootfs_boot.RootFSBootTest):
    '''Tries to remove qdisc root node'''
    def runTest(self):
        board.sendline('tc qdisc del dev eth0 root')
        i = board.expect(['RTNETLINK answers: No such file or directory'] + board.prompt)
        if i == 0:
            raise Exception("Failed to delete all qdiscs")
