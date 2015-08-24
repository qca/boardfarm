# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class Webserver_Running(rootfs_boot.RootFSBootTest):
    '''Router webserver is running.'''
    def runTest(self):
        board.sendline('\nps | grep -v grep | grep http')
        board.expect('uhttpd')
        board.expect(prompt)

class WebGUI_Access(rootfs_boot.RootFSBootTest):
    '''Router webpage available to LAN-device at http://192.168.1.1/.'''
    def runTest(self):
        url = 'http://192.168.1.1/'
        lan.sendline('\ncurl -v %s' % url)
        lan.expect('<html')
        lan.expect('<body')
        lan.expect('</body>')
        lan.expect('</html>')
        lan.expect(prompt)

class WebGUI_NoStackTrace(rootfs_boot.RootFSBootTest):
    '''Router webpage at cgi-bin/luci contains no stack traceback.'''
    def runTest(self):
        board.sendline('\ncurl -s http://127.0.0.1/cgi-bin/luci | head -15')
        board.expect('cgi-bin/luci')
        board.expect(prompt)
        assert 'traceback' not in board.before

class Webserver_Download(rootfs_boot.RootFSBootTest):
    '''Downloaded small file from router webserver in reasonable time.'''
    def runTest(self):
        board.sendline('\nhead -c 1000000 /dev/urandom > /www/deleteme.txt')
        board.expect('head ', timeout=5)
        board.expect(prompt)
        lan.sendline('\ncurl -m 25 http://192.168.1.1/deleteme.txt > /dev/null')
        lan.expect('Total', timeout=5)
        lan.expect('100 ', timeout=10)
        lan.expect(prompt, timeout=10)
        board.sendline('\nrm -f /www/deleteme.txt')
        board.expect('deleteme.txt')
        board.expect(prompt)
    def recover(self):
        board.sendcontrol('c')
        lan.sendcontrol('c')
        board.sendline('rm -f /www/deleteme.txt')
        board.expect(prompt)
