# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router


class WRT3200ACM(openwrt_router.OpenWrtRouter):
    '''
    Marvell board
    '''

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['Marvell>>']
    uboot_eth = "egiga1"
    wan_iface = "wan"

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)
        self.sendline('setenv firmwareName %s' % filename)
        self.expect(self.uprompt)
        self.sendline('run update_both_images')
        self.expect(self.uprompt, timeout=90)

    def boot_linux(self, rootfs=None):
        self.sendline('boot')
