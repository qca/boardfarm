# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import qcom_arm_base

class QcomAkroniteRouterNOR(qcom_arm_base.QcomArmBase):
    '''
    Board with an Akronite processor.
    '''

    def __init__(self, *args, **kwargs):
        super(QcomAkroniteRouterNOR, self).__init__(*args, **kwargs)
        self.uboot_ddr_addr = "0x42000000"
        machid_table = {"ap148-nor": "1260"}
        if self.model in machid_table:
            self.machid = machid_table[self.model]
        else:
            raise Exception("Unknown machid for %s, please add to table")

    def flash_rootfs(self, ROOTFS):
        common.print_bold("\n===== Flashing rootfs =====\n")
        filename = self.prepare_file(ROOTFS)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.spi_flash_bin("0x006b0000", size, self.uboot_ddr_addr, "0x1920000")

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.spi_flash_bin("0x0062b0000", size, self.uboot_ddr_addr, "0x400000")

    def boot_linux(self, rootfs=None):
        common.print_bold("\n===== Booting linux for %s on %s =====" % (self.model, self.root_type))
        self.reset()
        self.wait_for_boot()

        self.sendline("set bootargs 'console=ttyMSM0,115200'")
        self.expect(self.uprompt)
        self.sendline("set fsbootargs 'rootfstype=squashfs,jffs2'")
        self.expect(self.uprompt)
        self.sendline('set bootcmd bootipq')
        self.expect(self.uprompt)
        self.sendline("saveenv")
        self.expect(self.uprompt)
        self.sendline("print")
        self.expect(self.uprompt)
        self.sendline('run bootcmd')
