# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class OpkgConfUpdateMD5(rootfs_boot.RootFSBootTest):
    '''Check that opkg will overwrite old configuration files with known MD5.'''
    def runTest(self):
        board.sendline('\ncp /etc/config/ulogd /etc/config/ulogd.bak')
        board.expect(prompt)
        board.sendline('echo boardfarmteststring > /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('touch -r /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('sed -i "s|/etc/config/ulogd .*|/etc/config/ulogd 48b1215c8d419a33818fc1f42c118aed|" /usr/lib/opkg/status')
        board.expect(prompt)
        board.sendline('opkg install --force-reinstall ulogd')
        board.expect(prompt)
        board.sendline('grep boardfarmteststring /etc/config/ulogd || uname')
        board.expect('Linux')
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
    def recover(self):
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)

class OpkgConfNotUpdateMD5(rootfs_boot.RootFSBootTest):
    '''Check that opkg will not overwrite old modified configuration files with known MD5.'''
    def runTest(self):
        board.sendline('\ncp /etc/config/ulogd /etc/config/ulogd.bak')
        board.expect(prompt)
        board.sendline('echo boardfarmteststring > /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('touch -r /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('sed -i "s|/etc/config/ulogd .*|/etc/config/ulogd aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|" /usr/lib/opkg/status')
        board.expect(prompt)
        board.sendline('opkg install --force-reinstall ulogd')
        board.expect('Existing conffile /etc/config/ulogd is different from the conffile in the new package')
        board.expect(prompt)
        board.sendline('grep boardfarmteststring /etc/config/ulogd && uname')
        board.expect('Linux')
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
    def recover(self):
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)

class OpkgConfUpdateSHA256(rootfs_boot.RootFSBootTest):
    '''Check that opkg will overwrite old configuration files with known MD5.'''
    def runTest(self):
        board.sendline('\ncp /etc/config/ulogd /etc/config/ulogd.bak')
        board.expect(prompt)
        board.sendline('echo boardfarmteststring > /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('touch -r /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('sed -i "s|/etc/config/ulogd .*|/etc/config/ulogd 4212ae0a86f553b7aac741a734a0b973193a9fbe179b28a5d8c2a50cc51e25f0|" /usr/lib/opkg/status')
        board.expect(prompt)
        board.sendline('opkg install --force-reinstall ulogd')
        board.expect(prompt)
        board.sendline('grep boardfarmteststring /etc/config/ulogd || uname')
        board.expect('Linux')
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
    def recover(self):
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)

class OpkgConfNotUpdateSHA256(rootfs_boot.RootFSBootTest):
    '''Check that opkg will not overwrite old modified configuration files with known MD5.'''
    def runTest(self):
        board.sendline('\ncp /etc/config/ulogd /etc/config/ulogd.bak')
        board.expect(prompt)
        board.sendline('echo boardfarmteststring > /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('touch -r /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
        board.sendline('sed -i "s|/etc/config/ulogd .*|/etc/config/ulogd aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|" /usr/lib/opkg/status')
        board.expect(prompt)
        board.sendline('opkg install --force-reinstall ulogd')
        board.expect('Existing conffile /etc/config/ulogd is different from the conffile in the new package')
        board.expect(prompt)
        board.sendline('grep boardfarmteststring /etc/config/ulogd && uname')
        board.expect('Linux')
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)
    def recover(self):
        board.sendline('\nmv /etc/config/ulogd.bak /etc/config/ulogd')
        board.expect(prompt)

