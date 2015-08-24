# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
#!/usr/bin/env python

import pexpect
import sys
import base

# Netgear Switch Prompt
prompt = "\(M4100-50G\) "

class NetgearM4100(base.BaseDevice):
    '''
    A netgear switch allows for changing connections by modifying
    VLANs on ports.
    '''

    def __init__(self,
                 conn_cmd,
                 username='admin',
                 password='bigfoot1'):
        pexpect.spawn.__init__(self, '/bin/bash', args=['-c', conn_cmd])
        self.logfile_read = sys.stdout
        self.username = username
        self.password = password
        self.prompt = prompt
        self.connect()

    def connect(self):
        self.sendline("\n")
        i = self.expect(["User:", prompt], timeout=20)
        if i == 0:
            self.sendline(self.username)
            self.expect("Password:")
            self.sendline(self.password)
            self.expect(prompt)

    def disconnect(self):
        # Leave config mode
        self.sendline("exit")
        self.expect(prompt)
        # Leave privileged mode
        self.sendline("exit")
        self.expect(prompt)
        # Quit
        self.sendline("quit")
        self.expect('User:')
        self.close()

    def change_port_vlan(self, port, vlan):
        # Enter privileged mode
        self.sendline("enable")
        i = self.expect([prompt, "Password:"])
        if i == 1:
            self.sendline(self.password)
            self.expect(prompt)
        # Enter config mode
        self.sendline("configure")
        self.expect(prompt)
        # Enter interface config mode
        port_name = "0/%01d" % port
        self.sendline("interface %s" % port_name)
        self.expect(prompt)
        # Remove previous VLAN
        self.sendline("no vlan pvid")
        self.expect(prompt)
        self.sendline("vlan participation exclude 3-1024")
        self.expect(prompt)
        # Include new VLAN
        self.sendline("vlan pvid %s" % vlan)
        self.expect(prompt)
        self.sendline("vlan participation include %s" % vlan)
        self.expect(prompt)
        # Leave interface config mode
        self.sendline("exit")
        self.expect(prompt)

    def setup_standard_vlans(self, min_port=1, max_port=49):
        '''
        Create enough VLANs, then put ports on VLANS such that:
        port 1 & 2 are on VLAN 3
        port 3 & 4 are on VLAN 4
        etc...
        Also remove all ports from VLAN 1 (default setting).
        '''
        # Enter privileged mode
        self.sendline("enable")
        i = self.expect([prompt, "Password:"])
        if i == 1:
            self.sendline("password")
            self.expect(prompt)
        # Create all VLANS
        self.sendline("vlan database")
        self.expect(prompt)
        self.sendline("vlan 3-50")
        self.expect(prompt)
        self.sendline("exit")
        self.expect(prompt)
        # Enter config mode
        self.sendline("configure")
        self.expect(prompt)
        # Remove all interfaces from VLAN 1 (default setting)
        self.sendline("interface 0/1-0/48")
        self.expect(prompt)
        self.sendline("vlan participation exclude 1")
        self.expect(prompt)
        self.sendline("exit")
        self.expect(prompt)
        # Loop over all interfaces
        pvid = 3 # initial offset of 3 due to netgear BS
        for i in range(min_port, max_port, 2):
            low = i
            high = i + 1
            # configure interfaces
            self.sendline("interface 0/%01d-0/%01d" % (low, high))
            self.expect(prompt)
            self.sendline("vlan pvid %s" % pvid)
            self.expect(prompt)
            self.sendline("vlan participation include %s" % pvid)
            self.expect(prompt)
            # Leave interface configuration
            self.sendline("exit")
            self.expect(prompt)
            pvid += 1

    def print_vlans(self):
        '''
        Query each port on switch to see connected mac addresses.
        Print connection table in the end.
        '''
        vlan_macs = {}
        # Enter privileged mode
        self.sendline("enable")
        i = self.expect([prompt, "Password:"])
        if i == 1:
            self.sendline("password")
            self.expect(prompt)
        # Check each port
        for p in range(1, 48):
            port_name = "0/%01d" % p
            self.sendline('show mac-addr-table interface %s' % port_name)
            tmp = self.expect(['--More--', prompt])
            if tmp == 0:
                self.sendline()
            result = self.before.split('\n')
            for line in result:
                if ':' in line:
                    mac, vlan, _ = line.split()
                    vlan = int(vlan)
                    if vlan not in vlan_macs:
                        vlan_macs[vlan] = []
                    vlan_macs[vlan].append(mac)
        #print vlan_macs
        print("\n\n")
        print("VLAN Devices")
        print("---- -----------------")
        for vlan in sorted(vlan_macs):
            #devices = [mac_to_name(x) for x in vlan_macs[vlan]]
            devices = [x for x in vlan_macs[vlan]]
            print("%4s %s" % (vlan, " <-> ".join(devices)))

if __name__ == '__main__':
    switch = NetgearM4100(conn_cmd='telnet 10.0.0.64 6031',
                          username='admin',
                          password='password'
                          )
    switch.print_vlans()
    switch.disconnect()
