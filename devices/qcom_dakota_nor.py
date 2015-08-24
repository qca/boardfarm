# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import qcom_arm_base

class QcomDakotaRouterNOR(qcom_arm_base.QcomArmBase):
    '''
    Board with an Akronite processor.
    '''

    def __init__(self, *args, **kwargs):
        super(QcomDakotaRouterNOR, self).__init__(*args, **kwargs)
        self.uboot_ddr_addr = "0x88000000"
        machid_table = {"dk01-nor": "8010000"}
        if self.model in machid_table:
            self.machid = machid_table[self.model]
        else:
            raise Exception("Unknown machid for %s, please add to table" % self.model)

    def flash_rootfs(self, ROOTFS):
        common.print_bold("\n===== Flashing rootfs =====\n")
        filename = self.prepare_file(ROOTFS)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.spi_flash_bin(self.rootfs_addr, size, self.uboot_ddr_addr, self.rootfs_size)

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.spi_flash_bin(self.kernel_addr, size, self.uboot_ddr_addr, self.kernel_size)

    def boot_linux(self, rootfs=None):
        common.print_bold("\n===== Booting linux for %s on %s =====" % (self.model, self.root_type))
        self.reset()
        self.wait_for_boot()

        self.sendline("setenv bootcmd bootipq")
        self.expect(self.uprompt)
        self.sendline("setenv bootargs")
        self.expect(self.uprompt)
        self.sendline("saveenv")
        self.expect(self.uprompt)
        self.sendline("print")
        self.expect(self.uprompt)
        self.sendline('run bootcmd')
        # if run isn't support, we just reset u-boot and
        # let the bootcmd run that way
        try:
            self.expect('Unknown command', timeout=5)
        except:
            pass
        else:
            self.sendline('reset')
