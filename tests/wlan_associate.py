# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import unittest2
import rootfs_boot
import lib
import sys
import pexpect
import time
import wlan_set_ssid
import re
from devices import board, wan, lan, wlan, prompt
from lib.wifi import *

class WlanAssociate(wlan_set_ssid.WlanSetSSID):
    '''Wifi device connected and had internet access.'''
    def wlan_setup(self):
        wlan.sendline('\napt-get install -qy usbutils wireless-tools')
        wlan.expect('Reading package')
        wlan.expect(prompt)
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)

    def recover(self):
        wlan.sendcontrol('c')
        wlan.sendcontrol('c')

    @lib.common.run_once
    def runTest(self):
        super(WlanAssociate, self).runTest()
        wlan_iface = wifi_interface(board)
        if wlan_iface is None:
            self.skipTest("No wifi interfaces detected, skipping..")
        if wlan is None:
            self.skipTest("No wlan VM, skipping test..")

        #Determine if we are using a beeliner x86 host. If not, default to usb drivers.
        #Would like to push this out to a library.
        wlan.sendline('lspci |grep -q Atheros; echo $?')
        wlan.expect('(\d+)\r\n')
        check_atheros = int(wlan.match.group(1))

        if check_atheros is not 0:
            print("Creating realtek interface.")
            wlan.sendline('\napt-get install -qy firmware-realtek')
            wlan.expect('Reading package')
            wlan.expect(prompt)
            wlan.sendline('rmmod rtl8192cu 8812au')
            wlan.expect(prompt)
            wlan.sendline('modprobe rtl8192cu')
            wlan.expect(prompt)
            wlan.sendline('modprobe 8812au')
            wlan.expect(prompt)
        else:
            #Check if modules are alerady loaded. If not, load them.
            print("Found Atheros hardware, creating interface.")
            wlan.sendline('lsmod |grep -q ath_hal; echo $?')
            wlan.expect('(\d+)\r\n')
            check_loaded = int(wlan.match.group(1))

            if check_loaded is not 0:
                #rc.wlan takes care of insmod, wlanconfig creates wlan0. Both should be in the path.
                wlan.sendline('rc.wlan up')
                wlan.expect(prompt)
                wlan.sendline('wlanconfig wlan0 create wlandev wifi0 wlanmode sta')
                wlan.expect(prompt)

        wlan.sendline('rfkill unblock all')
        wlan.expect(prompt)

        wlan.sendline('ifconfig wlan0')
        wlan.expect('HWaddr')
        wlan.expect(prompt)

        wlan.sendline('ifconfig wlan0 down')
        wlan.expect(prompt)

        wlan.sendline('ifconfig wlan0 up')
        wlan.expect(prompt)

        # wait until the wifi can see the SSID before even trying to join
        # not sure how long we should really give this, or who's fault it is
        for i in range(0, 20):
            try:
                wlan.sendline('iwlist wlan0 scan | grep ESSID:')
                wlan.expect(self.config.ssid)
                wlan.expect(prompt)
            except:
                lib.common.test_msg("can't see ssid %s, scanning again (%s tries)" % (self.config.ssid, i))
            else:
                break

        time.sleep(10)

        for i in range(0, 2):
            try:
                wlan.sendline('iwconfig wlan0 essid %s' % self.config.ssid)
                wlan.expect(prompt)

                # give it some time to associate
                time.sleep(20)

                # make sure we assocaited
                wlan.sendline('iwconfig wlan0')
                wlan.expect('Access Point: ([0-9A-F]{2}[:-]){5}([0-9A-F]{2})')
                wlan.expect(prompt)
            except:
                lib.common.test_msg("Can't associate with ssid %s, trying again (%s tries) " % (self.config.ssid, i))
            else:
                break

        # get ip on wlan
        wlan.sendline('killall dhclient')
        wlan.expect(prompt)
        time.sleep(10)
        wlan.sendline('dhclient wlan0')
        wlan.expect(prompt)

        # for reference
        wlan.sendline('ifconfig wlan0')
        wlan.expect(prompt)

        # make sure dhcp worked, and for reference of IP
        wlan_ip = wlan.get_interface_ipaddr("wlan0")

        # add route to wan
        wlan.sendline('ip route add 192.168.0.0/24 via 192.168.1.1')
        wlan.expect(prompt)
        wlan.sendline('ip route show')
        wlan.expect(prompt)

        wlan.sendline('ping 192.168.1.1 -c3')
        wlan.expect('3 packets transmitted')
        wlan.expect(prompt)
        wlan.sendline('curl 192.168.1.1 --connect-timeout 5 > /dev/null 2>&1; echo $?')
        wlan.expect('(\d+)\r\n')
        curl_success = int(wlan.match.group(1))

        msg = "Attempt to curl router returns %s\n" % (curl_success)
        lib.common.test_msg(msg)
        assert (curl_success == 0)
