# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import sys
import time
import pexpect
import base

from termcolor import colored, cprint


class DebianBox(base.BaseDevice):
    '''
    A linux machine running an ssh server.
    '''

    prompt = ['root\\@.*:.*#', '/ # ', ".*:~ #" ]

    def __init__(self,
                 name,
                 color,
                 username,
                 password,
                 port,
                 output=sys.stdout,
                 reboot=False,
                 location=None):
        if name is None:
            return
        pexpect.spawn.__init__(self,
                               command="ssh",
                               args=['%s@%s' % (username, name),
                                     '-p', port,
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null'])
        self.name = name
        self.color = color
        self.output = output
        self.username = username
        self.password = password
        self.port = port
        self.location = location
        cprint("%s device console = %s" % (name, colored(color, color)), None, attrs=['bold'])
        try:
            i = self.expect(["yes/no", "assword:", "Last login"], timeout=30)
        except pexpect.TIMEOUT as e:
            raise Exception("Unable to connect to %s." % name)
        except pexpect.EOF as e:
            if hasattr(self, "before"):
                print(self.before)
            raise Exception("Unable to connect to %s." % name)
        if i == 0:
            self.sendline("yes")
            i = self.expect(["Last login", "assword:"])
        if i == 1:
            self.sendline(password)
        else:
            pass
        self.expect(self.prompt)

        if reboot:
            self.reset()

        self.logfile_read = output

    def reset(self):
        self.sendline('reboot')
        self.expect(['going down','disconnected'])
        try:
            self.expect(self.prompt, timeout=10)
        except:
            pass
        time.sleep(15)  # Wait for the network to go down.
        for i in range(0, 20):
            try:
                pexpect.spawn('ping -w 1 -c 1 ' + self.name).expect('64 bytes', timeout=1)
            except:
                print(self.name + " not up yet, after %s seconds." % (i + 15))
            else:
                print("%s is back after %s seconds, waiting for network daemons to spawn." % (self.name, i + 14))
                time.sleep(15)
                break
        self.__init__(self.name, self.color,
                      self.output, self.username,
                      self.password, self.port,
                      reboot=False)

    def get_ip_addr(self, interface):
        self.sendline("\nifconfig %s" % interface)
        self.expect('addr:(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*(Bcast|P-t-P):', timeout=5)
        ipaddr = self.match.group(1)
        self.expect(self.prompt)
        return ipaddr

    def ip_neigh_flush(self):
        self.sendline('\nip -s neigh flush all')
        self.expect('flush all')
        self.expect(self.prompt)

    def turn_on_pppoe(self):
        self.sendline('apt-get -o Dpkg::Options::="--force-confnew" -y install pppoe')
        self.expect(self.prompt)
        self.sendline('cat > /etc/ppp/pppoe-server-options << EOF')
        self.sendline('noauth')
        self.sendline('ms-dns 8.8.8.8')
        self.sendline('ms-dns 8.8.4.4')
        self.sendline('EOF')
        self.expect(self.prompt)
        self.sendline('pppoe-server -k -I eth1 -L 192.168.2.1 -R 192.168.2.10 -N 4')
        self.expect(self.prompt)

    def turn_off_pppoe(self):
        self.sendline("\nkillall pppoe-server pppoe pppd")
        self.expect("pppd")
        self.expect(self.prompt)

    def start_tftp_server(self):
        # set WAN ip address, for now this will always be this address for the device side
        self.sendline('ifconfig eth1 down')
        self.expect(self.prompt)

        # install packages required
        self.sendline('apt-get -o DPkg::Options::="--force-confnew" -qy install tftpd-hpa')

        # set WAN ip address, for now this will always be this address for the device side
        self.sendline('ifconfig eth1 192.168.0.1')
        self.expect(self.prompt)

        #configure tftp server
        self.sendline('/etc/init.d/tftpd-hpa stop')
        self.expect('Stopping')
        self.expect(self.prompt)
        self.sendline('rm -rf /tftpboot')
        self.expect(self.prompt)
        self.sendline('rm -rf /srv/tftp')
        self.expect(self.prompt)
        self.sendline('mkdir -p /srv/tftp')
        self.expect(self.prompt)
        self.sendline('ln -sf /srv/tftp/ /tftpboot')
        self.expect(self.prompt)
        self.sendline('mkdir -p /tftpboot/tmp')
        self.expect(self.prompt)
        self.sendline('chmod a+w /tftpboot/tmp')
        self.expect(self.prompt)
        self.sendline('mkdir -p /tftpboot/crashdump')
        self.expect(self.prompt)
        self.sendline('chmod a+w /tftpboot/crashdump')
        self.expect(self.prompt)
        self.sendline('sed /TFTP_OPTIONS/d -i /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('echo TFTP_OPTIONS=\\"-4 --secure --create\\" >> /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('sed /TFTP_DIRECTORY/d -i /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('echo TFTP_DIRECTORY=\\"/srv/tftp\\" >> /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('/etc/init.d/tftpd-hpa restart')
        self.expect(self.prompt)

    def restart_tftp_server(self):
        self.sendline('\n/etc/init.d/tftpd-hpa restart')
        self.expect('Restarting')
        self.expect(self.prompt)

    def configure(self, kind):
        if kind == "wan_device":
            self.setup_as_wan_gateway()
        elif kind == "lan_device":
            self.setup_as_lan_device()

    def setup_as_wan_gateway(self):
        self.sendline('killall iperf ab hping3')
        self.expect(self.prompt)
        self.sendline('\nsysctl net.ipv6.conf.all.disable_ipv6=0')
        self.expect('sysctl ')
        self.expect(self.prompt)

        # potential cleanup so this wan device works
        self.sendline('iptables -t nat -X')
        self.expect(self.prompt)
        self.sendline('iptables -t nat -F')
        self.expect(self.prompt)

        # install packages required
        self.sendline('apt-get -o DPkg::Options::="--force-confnew" -qy install isc-dhcp-server procps iptables lighttpd')
        self.expect(self.prompt)

        # set WAN ip address
        self.sendline('ifconfig eth1 192.168.0.1')
        self.expect(self.prompt)
        self.sendline('ifconfig eth1 up')
        self.expect(self.prompt)

        # configure DHCP server
        self.sendline('/etc/init.d/isc-dhcp-server stop')
        self.expect(self.prompt)
        self.sendline('sed s/INTERFACES=.*/INTERFACES=\\"eth1\\"/g -i /etc/default/isc-dhcp-server')
        self.expect(self.prompt)
        self.sendline('cat > /etc/dhcp/dhcpd.conf << EOF')
        self.sendline('ddns-update-style none;')
        self.sendline('option domain-name "bigfoot-test";')
        self.sendline('option domain-name-servers 8.8.8.8, 8.8.4.4;')
        self.sendline('default-lease-time 600;')
        self.sendline('max-lease-time 7200;')
        self.sendline('subnet 192.168.0.0 netmask 255.255.255.0 {')
        self.sendline('          range 192.168.0.10 192.168.0.100;')
        self.sendline('          option routers 192.168.0.1;')
        self.sendline('}')
        self.sendline('EOF')
        self.expect(self.prompt)
        self.sendline('/etc/init.d/isc-dhcp-server start')
        self.expect(['Starting ISC DHCP server.*dhcpd.', 'Starting isc-dhcp-server.*'])
        self.expect(self.prompt)

        # configure routing
        self.sendline('sysctl net.ipv4.ip_forward=1')
        self.expect(self.prompt)
        wan_ip_uplink = self.get_ip_addr("eth0")
        self.sendline('iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source %s' % wan_ip_uplink)
        self.expect(self.prompt)

        self.sendline('echo 0 > /proc/sys/net/ipv4/tcp_timestamps')
        self.expect(self.prompt)
        self.sendline('echo 0 > /proc/sys/net/ipv4/tcp_sack')
        self.expect(self.prompt)

        self.sendline('ifconfig eth1')
        self.expect(self.prompt)

        self.turn_off_pppoe()

    def setup_as_lan_device(self, gw="192.168.1.1"):
        # potential cleanup so this wan device works
        self.sendline('killall iperf ab hping3')
        self.expect(self.prompt)
        self.sendline('\niptables -t nat -X')
        self.expect('iptables -t')
        self.expect(self.prompt)
        self.sendline('sysctl net.ipv6.conf.all.disable_ipv6=0')
        self.expect(self.prompt)
        self.sendline('sysctl net.ipv4.ip_forward=1')
        self.expect(self.prompt)
        self.sendline('iptables -t nat -F; iptables -t nat -X')
        self.expect(self.prompt)
        self.sendline('iptables -F; iptables -X')
        self.expect(self.prompt)
        self.sendline('iptables -t nat -A PREROUTING -p tcp --dport 222 -j DNAT --to-destination %s:22' % gw)
        self.expect(self.prompt)
        self.sendline('iptables -t nat -A POSTROUTING -o eth1 -p tcp --dport 22 -j MASQUERADE')
        self.expect(self.prompt)
        self.sendline('echo 0 > /proc/sys/net/ipv4/tcp_timestamps')
        self.expect(self.prompt)
        self.sendline('echo 0 > /proc/sys/net/ipv4/tcp_sack')
        self.expect(self.prompt)
        self.sendline('pkill --signal 9 -f dhclient.*eth1')
        self.expect(self.prompt)

    def start_lan_client(self, gw="192.168.1.1"):
        self.sendline('\nifconfig eth1 up')
        self.expect('ifconfig eth1 up')
        self.expect(self.prompt)
	self.sendline("dhclient -r eth1")
        self.expect(self.prompt)
        self.sendline('\nifconfig eth1 0.0.0.0')
        self.expect(self.prompt)
        self.sendline('rm /var/lib/dhcp/dhclient.leases')
        self.expect(self.prompt)
        for attempt in range(3):
            try:
                self.sendline('dhclient -v eth1')
                self.expect('DHCPOFFER', timeout=30)
                self.expect(self.prompt)
                break
            except:
                self.sendcontrol('c')
        else:
            raise Exception("Error: Device on LAN couldn't obtain address via DHCP.")
        self.sendline('ifconfig eth1')
        self.expect(self.prompt)
        self.sendline('route del default')
        self.expect(self.prompt)
        self.sendline('route del default')
        self.expect(self.prompt)
        self.sendline('route del default')
        self.expect(self.prompt)
        self.sendline('route add default gw %s' % gw)
        self.expect(self.prompt)
        # Setup HTTP proxy, so board webserver is accessible via this device
        self.sendline('apt-get -qy install tinyproxy curl apache2-utils nmap')
        self.expect('Reading package')
        self.expect(self.prompt, timeout=150)
        self.sendline('curl --version')
        self.expect(self.prompt)
        self.sendline('ab -V')
        self.expect(self.prompt)
        self.sendline('nmap --version')
        self.expect(self.prompt)
        self.sendline("sed -i 's/^Port 8888/Port 8080/' /etc/tinyproxy.conf")
        self.expect(self.prompt)
        self.sendline("sed -i 's/^#Allow 10.0.0.0/Allow 10.0.0.0/' /etc/tinyproxy.conf")
        self.expect(self.prompt)
        self.sendline('/etc/init.d/tinyproxy restart')
        self.expect('Restarting')
        self.expect(self.prompt)
        # Write a useful ssh config for routers
        self.sendline('mkdir -p ~/.ssh')
        self.sendline('cat > ~/.ssh/config << EOF')
        self.sendline('Host %s' % gw)
        self.sendline('StrictHostKeyChecking no')
        self.sendline('UserKnownHostsFile=/dev/null')
        self.sendline('')
        self.sendline('Host krouter')
        self.sendline('Hostname %s' % gw)
        self.sendline('StrictHostKeyChecking no')
        self.sendline('UserKnownHostsFile=/dev/null')
        self.sendline('EOF')
        self.expect(self.prompt)
        # Copy an id to the router so people don't have to type a password to ssh or scp
        self.sendline('nc %s 22 -w 1' % gw)
        self.expect_exact('nc %s 22 -w 1' % gw)
        if 0 == self.expect(['SSH'] + self.prompt, timeout=5):
            self.sendline('[ -e /root/.ssh/id_rsa ] || ssh-keygen -N "" -f /root/.ssh/id_rsa')
            self.expect(self.prompt)
            self.sendline('scp ~/.ssh/id_rsa.pub %s:/etc/dropbear/authorized_keys' % gw)
            self.expect_exact('scp ~/.ssh/id_rsa.pub %s:/etc/dropbear/authorized_keys' % gw)
            try:
                # When resetting, no need for password
                self.expect("root@%s's password:" % gw, timeout=5)
                self.sendline('password')
            except:
                pass
            self.expect(self.prompt)

if __name__ == '__main__':
    # Example use
    dev = DebianBox('10.0.0.173',
                    'blue',
                    username="root",
                    password="bigfoot1",
                    port="22")
    dev.sendline('echo Hello')
    dev.expect('Hello', timeout=4)
    dev.expect(dev.prompt)
    dev.reset()
    dev.sendline('echo Hello')
    dev.expect('Hello', timeout=4)
    dev.expect(dev.prompt)
