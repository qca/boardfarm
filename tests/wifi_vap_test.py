# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import wlan_set_ssid
from lib.wifi import *
from devices import board, wan, lan, wlan, prompt
import time

class WlanVAP(wlan_set_ssid.WlanSetSSID):
    '''Test multiple VAPs up and down'''
    def runTest(self):
        enable_wifi(board, index=0)
        # TODO: make sure we have a radio
        enable_wifi(board, index=1)

        for i in range(1, 16):
            wifi_add_vap(board, "wifi0", randomSSIDName())

        for i in range(1, 16):
            wifi_add_vap(board, "wifi1", randomSSIDName())

        for i in range(0, 20):
            board.sendline('wifi down')
            board.expect('wifi down')
            board.expect(prompt, timeout=480)
            board.sendline('wifi up')
            board.expect('wifi up')
            board.expect(prompt, timeout=480)

            # expect 32 vaps to be present
            for i in range(0, 5):
                try:
                    time.sleep(10)
                    board.sendline('ifconfig -a | grep ath | wc -l')
                    board.expect('32')
                    board.expect(prompt)
                except:
                    if i == 4:
                        assert False
                else:
                    break

        for i in range(1, 16):
            wifi_del_vap(board, -1)

        for i in range(1, 16):
            wifi_del_vap(board, -1)
