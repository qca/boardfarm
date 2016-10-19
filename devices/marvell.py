# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router


class MarvellBoard(openwrt_router.OpenWrtRouter):
    '''
    Marvell board
    '''

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['Marvell>>']
    uboot_eth = "egiga1"

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)
        self.sendline('tftpboot $defaultLoadAddr %s && nand erase $priKernAddr $priFwSize && nand write $defaultLoadAddr $priKernAddr $filesize' % filename)
        self.expect(self.uprompt)

    def boot_linux(self, rootfs=None):
        self.sendline('boot')
