# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router


class QcomMipsRouter(openwrt_router.OpenWrtRouter):
    '''
    Board with a MIPS processor.
    '''

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['ath>', 'ar7240>']

    def __init__(self, *args, **kwargs):
        super(QcomMipsRouter, self).__init__(*args, **kwargs)
        if self.model in ("ap152", "ap152-8M"):
            self.lan_iface = "eth0.1"
            self.wan_iface = "eth0.2"

    def check_memory_addresses(self):
        '''Before flashing an image, set memory addresses.'''
        if self.model in ("ap135", "ap147", "ap152", "ap151-16M"):
            # would be nice to dynamically detect these
            self.kernel_addr = "0x9fe80000"
            self.rootfs_addr = "0x9f050000"
        elif self.model in ("db120", "ap143", "ap151", "ap152-8M"):
            self.kernel_addr = "0x9f680000"
            self.rootfs_addr = "0x9f050000"

    def flash_rootfs(self, ROOTFS):
        '''Flash Root File System image'''
        common.print_bold("\n===== Flashing rootfs =====\n")
        filename = self.prepare_file(ROOTFS)
        if self.model == "ap135-nand":
            self.tftp_get_file_uboot("0x82060000", filename)
            self.sendline('nand erase 0x700000 0x1E00000')
            self.expect('OK')
            self.expect(self.uprompt)
            self.sendline('nand write.jffs2 0x82060000 0x700000 $filesize')
            self.expect('OK')
            self.expect(self.uprompt)
            # erase the overlay otherwise, things will be in a weird state
            self.sendline('nand erase 0x1F00000')
            self.expect('OK')
            self.expect(self.uprompt)
            return
        self.tftp_get_file_uboot("0x82060000", filename)
        self.sendline('erase %s +$filesize' % self.rootfs_addr)
        self.expect('Erased .* sectors', timeout=180)
        self.expect(self.uprompt)
        self.sendline('cp.b $fileaddr %s $filesize' % self.rootfs_addr)
        self.expect('done', timeout=80)
        self.expect(self.uprompt)
        self.sendline('cmp.b $fileaddr %s $filesize' % self.rootfs_addr)
        self.expect('Total of .* bytes were the same')

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")
        filename = self.prepare_file(KERNEL)
        self.tftp_get_file_uboot("0x82060000", filename)
        if self.model == "ap135-nand":
            self.sendline('nand erase 0x100000 $filesize')
            self.expect('OK')
            self.expect(self.uprompt)
            self.sendline('nand write.jffs2 0x82060000 0x100000 $filesize')
            self.expect('OK')
            self.expect(self.uprompt)
            return
        self.sendline('erase %s +$filesize' % self.kernel_addr)
        self.expect('Erased .* sectors', timeout=60)
        self.expect(self.uprompt)
        self.sendline('cp.b $fileaddr %s $filesize' % self.kernel_addr)
        self.expect('done', timeout=60)
        self.sendline('cmp.b $fileaddr %s $filesize' % self.kernel_addr)
        self.expect('Total of .* bytes were the same')
        self.expect(self.uprompt)

    def boot_linux(self, rootfs=None):
        common.print_bold("\n===== Booting linux for %s on %s =====" % (self.model, self.root_type))
        if self.model == "ap135-nand":
            self.sendline('setenv bootcmd nboot 0x81000000 0 0x100000')
            self.expect(self.uprompt)
        else:
            self.sendline("setenv bootcmd 'bootm %s'" % self.kernel_addr)
            self.expect(self.uprompt)
        self.sendline("saveenv")
        self.expect(self.uprompt)
        self.sendline("print")
        self.expect(self.uprompt)
        self.sendline("boot")

    def perf_args(self, events, kernel_user="ku"):
        if len(events) > 4:
            raise Exception("only 4 events at a time are supported")

        ret = []
        for e in events:
            if e == "cycles":
                ret.append("cycles")
            elif e == "instructions":
                ret.append("instructions")
            elif e == "dcache_misses":
                ret.append("r98")
            elif e == "icache_misses":
                ret.append("r86")
            else:
                raise Exception("Unknown perf event %s" % e)

        return (':%s,' % kernel_user).join(ret) + ":%s" % kernel_user

    def parse_perf_board(self):
        events = [{'expect': 'cycles', 'name': 'cycles', 'sname': 'CPP'},
                {'expect': 'instructions', 'name': 'instructions', 'sname': 'IPP'},
                {'expect': 'r98:ku', 'name': 'dcache_misses', 'sname': 'DMISS'},
                {'expect': 'r86:ku', 'name': 'icache_misses', 'sname': 'IMISS'}]

        return events
