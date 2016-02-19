# Copyright (c) 2016
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import rootfs_boot
import lib
from devices import board, wan, lan, wlan, prompt
from selenium.webdriver import ActionChains

class WebTest(rootfs_boot.RootFSBootTest):
    '''Login to LuCI'''
    def setUp(self):
        super(WebTest, self).setUp()
        if not lan:
            msg = 'No LAN Device defined, skipping web test.'
            lib.common.test_msg(msg)
            self.skipTest(msg)

        # Set password, just to be sure
        board.sendline("passwd")
        board.expect("New password:", timeout=8)
        board.sendline("password")
        board.expect("Retype password:")
        board.sendline("password")
        board.expect(prompt)

        # Create a driver
        self.driver = lib.common.phantom_webproxy_driver('http://' + lan.name + ':8080')
        self.driver.get("http://192.168.1.1/cgi-bin/luci")
        self.assertIn('192.168.1.1', self.driver.current_url)
        self.assertIn('LuCI', self.driver.title)
        self.driver.find_element_by_name('luci_password').send_keys('password')
        self.driver.find_element_by_class_name('cbi-button-apply').submit()
        self.driver.find_element_by_xpath("//ul/li/a[contains(text(),'Status')]")

class WebOverview(WebTest):
    '''Check overview page'''
    def runTest(self):
        print('Checking overview page')
        action_chains = ActionChains(self.driver)
        status_menu = self.driver.find_element_by_xpath("//ul/li/a[contains(text(),'Status')]")
        overview_menu = self.driver.find_element_by_xpath("//ul/li/a[contains(text(),'Overview')]")
        action_chains.move_to_element(status_menu).click(overview_menu).perform()
        self.assertIn('Overview', self.driver.title)
        print('Managed to switch to overview page')
        for i in [ 'System', 'Memory', 'Network', 'DHCP Leases' ]:
            self.driver.find_element_by_xpath("//fieldset/legend[contains(text(),'" + i + "')]")
            print(' * overview page contains section ' + i)
