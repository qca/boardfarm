# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

def apt_install(device, name, timeout=120):
    device.sendline('apt-get install -q -y %s' % name)
    device.expect('Reading package')
    device.expect(device.prompt, timeout=timeout)

def apt_update(device, timeout=120):
    device.sendline('apt-get update')
    device.expect('Reading package')
    device.expect(device.prompt, timeout=timeout)

def install_iperf(device):
    '''Install iPerf benchmark tool if not present.'''
    device.sendline('\niperf -v')
    try:
        device.expect('iperf version', timeout=10)
        device.expect(device.prompt)
    except:
        device.expect(device.prompt)
        device.sendline('apt-get -o DPkg::Options::="--force-confnew" -y --force-yes install iperf')
        device.expect(device.prompt, timeout=60)

def install_lighttpd(device):
    '''Install lighttpd web server if not present.'''
    device.sendline('\nlighttpd -v')
    try:
        device.expect('lighttpd/1', timeout=8)
        device.expect(device.prompt)
    except:
        device.expect(device.prompt)
        apt_install(device, 'lighttpd')

def install_netperf(device):
    '''Install netperf benchmark tool if not present.'''
    device.sendline('\nnetperf -V')
    try:
        device.expect('Netperf version 2.4', timeout=10)
        device.expect(device.prompt)
    except:
        device.expect(device.prompt)
        device.sendline('apt-get -o DPkg::Options::="--force-confnew" -y --force-yes install netperf')
        device.expect(device.prompt, timeout=60)
    device.sendline('/etc/init.d/netperf restart')
    device.expect('Restarting')
    device.expect(device.prompt)

def install_endpoint(device):
    '''Install endpoint if not present.'''
    device.sendline('\npgrep endpoint')
    try:
        device.expect('pgrep endpoint')
        device.expect('[0-9]+\r\n', timeout=5)
        device.expect(device.prompt)
    except:
        device.expect(device.prompt)
        device.sendline('wget http://downloads.ixiacom.com/products/ixchariot/endpoint_library/8.00/pelinux_amd64_80.tar.gz')
        device.expect(device.prompt, timeout=120)
        device.sendline('tar xvzf pelinux_amd64_80.tar.gz')
        device.expect('endpoint.install', timeout=90)
        device.expect(device.prompt, timeout=60)
        device.sendline('./endpoint.install accept_license')
        device.expect('Installation of endpoint was successful.', timeout=90)
        device.expect(device.prompt, timeout=60)

def install_hping3(device):
    '''Install hping3 if not present.'''
    device.sendline('\nhping3 --version')
    try:
        device.expect('hping3 version', timeout=5)
        device.expect(device.prompt)
    except:
        device.expect(device.prompt)
        apt_install(device, 'hping3')
