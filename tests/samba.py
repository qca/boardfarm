# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import random
import re

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class SambaShare(rootfs_boot.RootFSBootTest):
    '''Setup and run Samba and test connection.'''
    def runTest(self):
        board.sendline('rm -f /etc/config/samba; opkg update; opkg install --force-reinstall samba36-server samba36-client kmod-fs-cifs')
        board.expect('Configuring samba36-server')
        board.expect(prompt)
        board.sendline('mkdir -p /tmp/samba; chmod a+rwx /tmp/samba; rm -rf /tmp/samba/*')
        board.expect(prompt)
        board.sendline('uci set samba.@samba[0].homes=0; uci delete samba.@sambashare[0]; uci add samba sambashare; uci set samba.@sambashare[0]=sambashare; uci set samba.@sambashare[0].name="boardfarm-test"; uci set samba.@sambashare[0].path="/tmp/samba"; uci set samba.@sambashare[0].read_only="no"; uci set samba.@sambashare[0].guest_ok="yes"; uci commit samba')
        board.expect(prompt)
        board.sendline('/etc/init.d/samba restart')
        board.sendline('smbclient -N -L 127.0.0.1')
        board.expect('boardfarm-test')
        board.expect(prompt)
        lan.sendline('smbclient -N -L 192.168.1.1')
        lan.expect('boardfarm-test')
        lan.expect(prompt)
        lan.sendline('mkdir -p /mnt/samba; mount -o guest //192.168.1.1/boardfarm-test /mnt/samba')
        lan.expect(prompt)
        lan.sendline('echo boardafarm-testing-string > /mnt/samba/test')
        lan.expect(prompt)
        lan.sendline('umount /mnt/samba')
        lan.expect(prompt)
        board.sendline('cat /tmp/samba/test')
        board.expect('boardafarm-testing-string')
        board.expect(prompt)
