# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import random
import re
import string
import time
from devices import prompt

wlan_iface = None

def wifi_interface(console):
    global wlan_iface

    if wlan_iface is None:
        console.sendline('uci show wireless | grep wireless.*0.*type=')
        i = console.expect(["type='?mac80211'?", "type='?qcawifi'?"])
        if i == 0:
            wlan_iface = "wlan0"
        elif i == 1:
            wlan_iface = "ath0"
        else:
            wlan_iface = None

    return wlan_iface

def randomSSIDName():
    return 'wifi-' + ''.join(random.sample(string.lowercase+string.digits,10))

def uciSetWifiSSID(console, ssid):
    console.sendline('uci set wireless.@wifi-iface[0].ssid=%s; uci commit wireless; wifi' % ssid)
    console.expect(prompt)

def uciSetWifiMode(console, radio, hwmode):
    console.sendline('uci set wireless.wifi%s.hwmode=%s; uci commit wireless' % (radio, hwmode))
    console.expect(prompt)

def uciSetChannel(console, radio, channel):
    console.sendline('uci set wireless.wifi%s.channel=%s; uci commit wireless' % (radio, channel))
    console.expect(prompt)

def enable_wifi(board, index=0):
    board.sendline('\nuci set wireless.@wifi-device[%s].disabled=0; uci commit wireless' % index)
    board.expect('uci set')
    board.expect(prompt)
    board.sendline('wifi')
    board.expect('wifi')
    board.expect(prompt, timeout=50)
    time.sleep(20)

def enable_all_wifi_interfaces(board):
    '''Find all wireless interfaces, and enable them.'''
    board.sendline('\nuci show wireless | grep disabled')
    board.expect('grep disabled')
    board.expect(prompt)
    # The following re.findall should return list of settings:
    # ['wireless.radio0.disabled', 'wireless.radio1.disabled']
    settings = re.findall('([\w\.]+)=\d', board.before)
    for s in settings:
        board.sendline('uci set %s=0' % s)
        board.expect(prompt)
    board.sendline('uci commit wireless')
    board.expect(prompt)
    board.sendline('wifi')
    board.expect(prompt, timeout=50)

def disable_wifi(board, wlan_iface="ath0"):
    board.sendline('uci set wireless.@wifi-device[0].disabled=1; uci commit wireless')
    board.expect('uci set')
    board.expect(prompt)
    board.sendline('wifi')
    board.expect(prompt)
    board.sendline('iwconfig %s' % wlan_iface)
    board.expect(prompt)

def wifi_on(board):
    '''Return True if WiFi is enabled.'''
    board.sendline('\nuci show wireless.@wifi-device[0].disabled')
    try:
        board.expect('disabled=0', timeout=5)
        board.expect(prompt)
        return True
    except:
        return False

def wifi_get_info(board, wlan_iface):
    try:
        if "ath" in wlan_iface:
            board.sendline('iwconfig %s' % wlan_iface)
            board.expect('ESSID:"(.*)"')
            essid = board.match.group(1)
            board.expect("Frequency:([^ ]+)")
            freq = board.match.group(1)
            essid = board.match.group(1)
            board.expect('Bit Rate[:=]([^ ]+) ')
            rate = float(board.match.group(1))
            board.expect(prompt)
            # TODO: determine channel
            channel = -1.0
        elif "wlan" in wlan_iface:
            board.sendline("iwinfo wlan0 info")
            board.expect('ESSID: "(.*)"')
            essid = board.match.group(1)
            board.expect('Channel:\s*(\d+)\s*\(([\d\.]+)\s*GHz')
            channel = int(board.match.group(1))
            freq = float(board.match.group(2))
            board.expect('Bit Rate: ([^ ]+)')
            try:
                rate = float(board.match.group(1))
            except:
                rate = -1.0
            board.expect(prompt)
        else:
            print("Unknown wireless type")
    except:
        board.sendline('dmesg')
        board.expect(prompt)
        raise

    return essid, channel, rate, freq

def wait_wifi_up(board, num_tries=10, sleep=15, wlan_iface="ath0"):
    '''Wait for WiFi Bit Rate to be != 0.'''
    for i in range(num_tries):
        time.sleep(sleep)
        essid, channel, rate, freq = wifi_get_info(board, wlan_iface)
        if "ath" in wlan_iface and rate > 0:
            return
        if "wlan" in wlan_iface == "wlan0" and essid != "" and channel != 0 and freq != 0.0:
            return

    if rate == 0:
        print("\nWiFi did not come up. Bit Rate still 0.")
        assert False

def wifi_add_vap(console, phy, ssid):
    console.sendline('uci add wireless wifi-iface')
    console.expect(prompt)
    console.sendline('uci set wireless.@wifi-iface[-1].device="%s"' % phy)
    console.expect(prompt)
    console.sendline('uci set wireless.@wifi-iface[-1].network="lan"')
    console.expect(prompt)
    console.sendline('uci set wireless.@wifi-iface[-1].mode="ap"')
    console.expect(prompt)
    console.sendline('uci set wireless.@wifi-iface[-1].ssid="%s"' % ssid)
    console.expect(prompt)
    console.sendline('uci set wireless.@wifi-iface[-1].encryption="none"')
    console.expect(prompt)
    console.sendline('uci commit')
    console.expect(prompt)

def wifi_del_vap(console, index):
    console.sendline('uci delete wireless.@wifi-iface[%s]' % index)
    console.expect(prompt)
    console.sendline('uci commit')
    console.expect(prompt)

def uciSetWifiSecurity(board, vap_iface, security):
    if security.lower() in ['none']:
        print("Setting security to none.")
        board.sendline('uci set wireless.@wifi-iface[%s].encryption=none' % vap_iface)
        board.expect(prompt)
    elif security.lower() in ['wpa-psk']:
        print("Setting security to WPA-PSK.")
        board.sendline('uci set wireless.@wifi-iface[%s].encryption=psk+tkip' % vap_iface)
        board.expect(prompt)
        board.sendline('uci set wireless.@wifi-iface[%s].key=1234567890abcdexyz' % vap_iface)
        board.expect(prompt)
    elif security.lower() in ['wpa2-psk']:
        print("Setting security to WPA2-PSK.")
        board.sendline('uci set wireless.@wifi-iface[%s].encryption=psk2+ccmp' % vap_iface)
        board.expect(prompt)
        board.sendline('uci set wireless.@wifi-iface[%s].key=1234567890abcdexyz' % vap_iface)
        board.expect(prompt)
