# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class OpenwrtVersion(rootfs_boot.RootFSBootTest):
    '''Openwrt release file exists and contains expected data.'''
    def runTest(self):
        board.check_output('cat /etc/openwrt_release', timeout=6)
        info = dict(re.findall('DISTRIB_([a-zA-Z]+)=[\'"]([^"\']+)[\'"]', board.before))
        self.result_message = 'Openwrt release is "%(RELEASE)s", revision "%(REVISION)s", and codename "%(CODENAME)s".' % info
        self.logged['rev'] = info['REVISION']
        self.logged['name'] = info['CODENAME']
