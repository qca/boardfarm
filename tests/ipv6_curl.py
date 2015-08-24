# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class IPv6_File_Download(rootfs_boot.RootFSBootTest):
    '''Downloaded file through router using IPv6.'''
    def runTest(self):
        # WAN Device: create large file in web directory
        fname = "/var/www/20mb.txt"
        wan.sendline('\n[ -e "%s" ] || head -c 20971520 /dev/urandom > %s' % (fname, fname))
        wan.expect('/var')
        wan.expect(prompt)
        # LAN Device: download the file
        lan.sendline('\ncurl -m 57 -g -6 http://[5aaa::6]/20mb.txt > /dev/null')
        lan.expect('Total', timeout=5)
        i = lan.expect(["couldn't connect", '20.0M  100 20.0M'], timeout=60)
        if i == 0:
            assert False
        lan.expect(prompt)
