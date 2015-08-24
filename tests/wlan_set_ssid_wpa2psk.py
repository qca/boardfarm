# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
import lib
import sys
import time
import traceback
from devices import board, wan, lan, wlan, prompt
from lib.wifi import *

class WlanSetSSID_WPA2PSK(rootfs_boot.RootFSBootTest):
    '''Wifi device came up and was able to set SSID.'''
    def wlan_setup(self):
        wlan.sendline('\napt-get install -qy firmware-realtek usbutils wireless-tools wpasupplicant')
        wlan.expect('Reading package')
        wlan.expect(prompt)

    @lib.common.run_once
    def runTest(self):
        wlan_iface = wifi_interface(board)
        wlan_security = "wpa2-psk"
        vap_iface = "0"
        if wlan_iface is None:
            self.skipTest("No wifi interfaces detected, skipping..")

        self.config.ssid = randomSSIDName()

        disable_wifi(board)
        uciSetWifiSecurity(board, vap_iface, wlan_security)
        uciSetChannel(board, "0", "153")
        uciSetWifiSSID(board, self.config.ssid)
        enable_wifi(board)

        # verfiy we have an interface here
        if wlan_iface == "ath0":
            board.sendline('iwconfig %s' % wlan_iface)
            board.expect('%s.*IEEE 802.11.*ESSID.*%s' % (wlan_iface, self.config.ssid))
        else:
            board.sendline('iwinfo %s info' % wlan_iface)
            board.expect('%s.*ESSID.*%s' % (wlan_iface, self.config.ssid))
        board.expect(prompt)

        # wait for AP to set rate, which means it's done coming up
        for i in range(20):
            try:
                essid, channel, rate, freq = wifi_get_info(board, wlan_iface)
                info = "Rate = %s Mb/s, Freq = %s Ghz" % (rate, freq)
                time.sleep(5)
                if wlan_iface == "ath0":
                    assert float(rate) > 0
                elif wlan_iface == "wlan0":
                    assert channel > 0
                lib.common.test_msg("%s\n" % info)
                self.result_message = self.__doc__ + " (%s)" % info
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                if i < 10:
                    pass
            else:
                break
