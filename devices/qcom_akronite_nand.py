# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import qcom_arm_base


class QcomAkroniteRouterNAND(qcom_arm_base.QcomArmBase):
    '''
    Board with an Akronite processor.
    '''

    def __init__(self, *args, **kwargs):
        super(QcomAkroniteRouterNAND, self).__init__(*args, **kwargs)
        self.uboot_ddr_addr = "0x42000000"
        machid_table = {"db149": "125b", "ap145": "12ca",
                  "ap148": "1260", "ap148-beeliner": "1260",
                  "ap148-osprey": "1260", "ap160-1": "136b",
                  "ap160-2": "136b", "ap161": "136c",
                  "dk04": "8010001"}
        if self.model in machid_table:
            self.machid = machid_table[self.model]
        else:
            raise Exception("Unknown machid for %s, please add to table")

    def flash_uboot(self, uboot):
        '''Flash Universal Bootloader image.'''
        common.print_bold("\n===== Flashing u-boot =====\n")
        filename = self.prepare_file(uboot)
        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.sendline('ipq_nand sbl')
        self.expect(self.uprompt)
        self.nand_flash_bin(self.uboot_addr, self.uboot_size, self.uboot_ddr_addr)
        self.reset()
        self.wait_for_boot()
        self.setup_uboot_network()

    def flash_rootfs(self, ROOTFS):
        common.print_bold("\n===== Flashing rootfs =====\n")
        filename = self.prepare_file(ROOTFS)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        self.nand_flash_bin(self.rootfs_addr, self.rootfs_size, self.uboot_ddr_addr)

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)

        raise Exception("Kernel is in UBI rootfs, not separate")

    def boot_linux(self, rootfs=None):
        common.print_bold("\n===== Booting linux for %s on %s =====" % (self.model, self.root_type))
        self.reset()
        self.wait_for_boot()

        self.sendline("setenv bootcmd bootipq")
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
