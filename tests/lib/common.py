# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import json
import junitxml
import pexpect
import sys
import subprocess
import time
import unittest2
import urllib2
import os
import signal
from termcolor import cprint

from selenium import webdriver
from selenium.webdriver.common.proxy import *

ubootprompt = ['ath>', '\(IPQ\) #', 'ar7240>']
linuxprompt = ['root\\@.*:.*#', '@R7500:/# ']
prompts = ubootprompt + linuxprompt + ['/.* # ', ]

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def spawn_ssh_pexpect(ip, user='root', pw='bigfoot1', prompt=None, port="22", via=None, color=None, o=sys.stdout):
    if via:
        p = via.sendline("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
                                            % (user, ip, port))
        p = via
    else:
        p = pexpect.spawn("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
                                            % (user, ip, port))

    i = p.expect(["yes/no", "assword:", "Last login"], timeout=30)
    if i == 0:
        p.sendline("yes")
        i = self.expect(["Last login", "assword:"])
    if i == 1:
        p.sendline(pw)
    else:
        pass

    if prompt is None:
        p.prompt = "%s@.*$" % user
    else:
        p.prompt = prompt

    p.expect(p.prompt)

    from termcolor import colored
    class o_helper():
            def __init__(self, color):
                    self.color = color
            def write(self, string):
                    o.write(colored(string, color))
            def flush(self):
                    o.flush()

    if color is not None:
        p.logfile_read = o_helper(color)
    else:
        p.logfile_read = o

    return p

def clear_buffer(console):
    try:
        console.read_nonblocking(size=2000, timeout=1)
    except:
        pass

def phantom_webproxy_driver(ipport):
    '''
    Use this if you started web proxy on a machine connected to router's LAN.
    '''
    service_args = [
        '--proxy=' + ipport,
        '--proxy-type=http',
    ]
    print("Attempting to setup Phantom.js via proxy %s" % ipport)
    driver = webdriver.PhantomJS(service_args=service_args)
    driver.set_window_size(1024, 768)
    driver.set_page_load_timeout(30)
    return driver

def firefox_webproxy_driver(ipport):
    '''
    Use this if you started web proxy on a machine connected to router's LAN.
    '''
    proxy = Proxy({
            'proxyType': 'MANUAL',
            'httpProxy': ipport,
            'ftpProxy': ipport,
            'sslProxy': ipport,
            'noProxy': ''
            })
    print("Attempting to open firefox via proxy %s" % ipport)
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.phishy-userpass-length', 255)
    driver = webdriver.Firefox(proxy=proxy, firefox_profile=profile)
    caps = webdriver.DesiredCapabilities.FIREFOX
    proxy.add_to_capabilities(caps)
    #driver = webdriver.Remote(desired_capabilities=caps)
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)
    return driver

def test_msg(msg):
    cprint(msg, None, attrs=['bold'])
