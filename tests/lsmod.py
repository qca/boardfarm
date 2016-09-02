# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class KernelModules(rootfs_boot.RootFSBootTest):
    '''lsmod shows loaded kernel modules.'''
    def runTest(self):
        board.check_output('lsmod | wc -l')
        tmp = re.search('\d+', board.before)
        num = int(tmp.group(0)) - 1 # subtract header line
        board.check_output('lsmod | sort')
        self.result_message = '%s kernel modules are loaded.' % num
        self.logged['num_loaded'] = num
