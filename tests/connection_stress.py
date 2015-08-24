# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
import time
from devices import board, wan, lan, wlan, prompt

class Connection_Stress(rootfs_boot.RootFSBootTest):
    '''Measured CPU use while creating thousands of connections.'''
    def runTest(self):
        num_conn = 5000
        # Wan device: Create small file in web dir
        fname = 'small.txt'
        cmd = '\nhead -c 10000 /dev/urandom > /var/www/%s' % fname
        wan.sendline(cmd)
        wan.expect(prompt)
        # Lan Device: download small file a lot
        concurrency = 25
        url = 'http://192.168.0.1/%s' % fname
        # Start CPU monitor
        board.sendline('\nmpstat -P ALL 10000 1')
        # Lan Device: download small file a lot
        lan.sendline('\nab -dn %s -c %s %s' % (num_conn, concurrency, url))
        lan.expect('Benchmarking', timeout=5)
        lan.expect('Requests per second:\s+(\d+)')
        reqs_per_sec = int(lan.match.group(1))
        lan.expect(prompt)
        # Stop CPU monitor
        board.sendcontrol('c')
        board.expect('Average:\s+all(\s+[0-9]+.[0-9]+){10}\r\n')
        idle_cpu = float(board.match.group(1))
        avg_cpu = 100 - float(idle_cpu)
        board.expect(prompt)
        msg = "ApacheBench measured %s connections/second, CPU use = %s%%." % (reqs_per_sec, avg_cpu)
        self.result_message = msg
        time.sleep(5) # Give router a few seconds to recover
    def recover(self):
        board.sendcontrol('c')
        board.expect(prompt)
        lan.sendcontrol('c')
        time.sleep(2) # Give router a few seconds to recover
