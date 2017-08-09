# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import qcom_akronite_nand


class QcomDakotaRouterNAND(qcom_akronite_nand.QcomAkroniteRouterNAND):
    '''
    Board with a Dakota processor.
    '''

    uboot_ddr_addr = "0x88000000"
    machid_table = {"dk03": "8010100", "dk04-nand": "8010001", "dk06-nand": "8010005", "dk07-nand": "8010006", "ea8300": "8010006"}
    uboot_network_delay = 5

    def boot_linux_ramboot(self):
        '''Boot Linux from initramfs'''
        common.print_bold("\n===== Booting linux (ramboot) for %s =====" % self.model)

        bootargs = 'console=ttyMSM0,115200 clk_ignore_unused norootfssplit mem=256M %s' % self.get_safe_mtdparts()
        if self.boot_dbg:
            bootargs += " dyndbg=\"module %s +p\"" % self.boot_dbg

        self.sendline("setenv bootargs '%s'" % bootargs)
        self.expect(self.uprompt)
        self.sendline('set fdt_high 0x85000000')
        self.expect(self.uprompt)
        self.sendline("bootm %s" % self.uboot_ddr_addr)
        self.expect("Loading Device Tree to")
        self.rambooted = True
