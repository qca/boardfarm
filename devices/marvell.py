# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router
import pexpect

class WRT3200ACM(openwrt_router.OpenWrtRouter):
    '''
    Marvell board
    '''

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['Venom>>']
    uboot_eth = "egiga1"
    wan_iface = "wan"

    def reset(self, break_into_uboot=False):
        if not break_into_uboot:
            self.power.reset()
        else:
            self.wait_for_boot()

    def wait_for_boot(self):
        '''Power-cycle this device.'''
        self.power.reset()

        self.expect_exact('General initialization - Version: 1.0.0')
        for not_used in range(10):
            self.expect(pexpect.TIMEOUT, timeout=0.1)
            self.sendline(' ')
            if 0 != self.expect([pexpect.TIMEOUT] + self.uprompt, timeout=0.1):
                break

    def wait_for_linux(self):
        self.wait_for_boot()
        self.sendline("boot")
        super(WRT3200ACM, self).wait_for_linux()

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)
        self.sendline('setenv firmwareName %s' % filename)
        self.expect(self.uprompt)
        self.sendline('run update_both_images')
        self.expect(self.uprompt, timeout=90)

    def boot_linux(self, rootfs=None):
        self.sendline('boot')
