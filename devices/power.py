# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import pexpect
import dlipower


def get_power_device(ip_address, username=None, password=None, outlet=None):
    '''
    Try to determine the type of network-controlled power switch
    at a given IP address. Return a class that can correctly
    interact with that type of switch.
    '''
    if ip_address is None:
        return HumanButtonPusher()
    p = pexpect.spawn('curl -L %s' % ip_address)
    try:
        t = p.expect_exact(['<title>Power Controller </title>',
                            'Sentry Switched CDU',
                            '<title>APC | Log On</title>'], timeout=90)
    except pexpect.EOF as e:
        if hasattr(p, "before"):
            print(p.before)
        raise Exception("Unable to connect to %s." % ip_address)
    except Exception as e:
        print(e)
        raise Exception("\nError connecting to %s" % ip_address)
    if t == 0:
        return DLIPowerSwitch(ip_address, outlet=outlet, username=username, password=password)
    elif t == 1:
        return SentrySwitchedCDU(ip_address, outlet=outlet)
    elif t == 2:
        return APCPower(ip_address, outlet=outlet)
    else:
        raise Exception("No code written to handle power device found at %s" % ip_address)


class PowerDevice():
    '''
    At minimum, power devices let users reset an outlet over a network.
    '''

    def __init__(self, ip_address, username=None, password=None):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        # Maybe verify connection is working here

    def reset(self, outlet):
        '''Turn an outlet OFF, maybe wait, then back ON.'''
        raise Exception('Code not written to reset with this type of power device at %s' % self.ip_address)


class SentrySwitchedCDU(PowerDevice):
    '''
    Power Unit from Server Technology.
    '''
    def __init__(self,
                 ip_address,
                 outlet,
                 username='admn',
                 password='bigfoot1'):
        PowerDevice.__init__(self, ip_address, username, password)
        self.outlet = outlet
        # Verify connection
        try:
            pcon = self.__connect()
            pcon.sendline('status .a%s' % self.outlet)
            i = pcon.expect(['Command successful', 'User/outlet -- name not found'])
            if i == 1:
                raise Exception('\nOutlet %s not found' % self.outlet)
            pcon.close()
        except Exception as e:
            print(e)
            print("\nError with power device %s" % ip_address)
            raise Exception("Error with power device %s" % ip_address)

    def __connect(self):
        pcon = pexpect.spawn('telnet %s' % self.ip_address)
        pcon.expect('Sentry Switched CDU Version 7', timeout=15)
        pcon.expect('Username:')
        pcon.sendline(self.username)
        pcon.expect('Password:')
        pcon.sendline(self.password)
        i = pcon.expect(['Switched CDU:', 'Critical Alert'])
        if i == 0:
            return pcon
        else:
            print("\nCritical failure in %s, skipping PDU\n" % self.power_ip)
            raise Exception("critical failure in %s" % self.power_ip)

    def reset(self, retry_attempts=2):
        print("\n\nResetting board %s %s" % (self.ip_address, self.outlet))
        for attempt in range(retry_attempts):
            try:
                pcon = self.__connect()
                pcon.sendline('reboot .a%s' % self.outlet)
                pcon.expect('Command successful')
                pcon.close()
                return
            except Exception as e:
                print(e)
                continue
        raise Exception("\nProblem resetting outlet %s." % self.outlet)

class HumanButtonPusher(PowerDevice):
    '''
    Tell a person to physically reboot the router.
    '''
    def __init__(self):
        PowerDevice.__init__(self, None)
    def reset(self):
        print("\n\nUser power-cycle the device now!\n")

class APCPower(PowerDevice):
    '''Resets an APC style power control port'''
    def __init__(self,
                 ip_address,
                 outlet,
                 username='apc',
                 password='apc'):
        PowerDevice.__init__(self, ip_address, username, password)
        self.outlet = outlet
    def reset(self):
        pcon = pexpect.spawn('telnet %s' % self.ip_address)
        pcon.expect("User Name :")
        pcon.send(self.username + "\r\n")
        pcon.expect("Password  :")
        pcon.send(self.password + "\r\n")
        pcon.expect("> ")
        pcon.send("1" + "\r\n")
        pcon.expect("> ")
        pcon.send("2" + "\r\n")
        pcon.expect("> ")
        pcon.send("1" + "\r\n")
        pcon.expect("> ")
        pcon.send(self.outlet + "\r\n")
        pcon.expect("> ")
        pcon.send("1" + "\r\n")
        pcon.expect("> ")
        pcon.send("6" + "\r\n")
        pcon.send("YES")
        pcon.send("" + "\r\n")
        pcon.expect("> ")

class DLIPowerSwitch(PowerDevice):
    '''Resets a DLI based power switch'''
    def __init__(self,
                 ip_address,
                 outlet,
                 username,
                 password):
        PowerDevice.__init__(self, ip_address, username, password)
        self.switch = dlipower.PowerSwitch(hostname=ip_address, userid=username, password=password)
        self.outlet = outlet

    def reset(self, outlet=None):
        if outlet is None:
            outlet = self.outlet
        self.switch.cycle(outlet)
