# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router


class QcomArmBase(openwrt_router.OpenWrtRouter):

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['\(IPQ\) #', '\(IPQ40xx\)', '\(QCA961x\) #']

    def check_memory_addresses(self):
        '''Before flashing, dynamically find addresses and memory size.'''
        self.sendline("smem")
        self.expect("flash_block_size:\s+(0x[0-9A-Fa-f]+)\r")
        self.flash_block_size = int(self.match.group(1), 0)
        try:
            self.expect("APPSBL\s+0x[0-9A-Fa-f]+\s+(0x[0-9A-Fa-f]+)\s+(0x[0-9A-Fa-f]+)\r", timeout=2)
            self.uboot_addr = self.match.group(1)
            self.uboot_size = self.match.group(2)
        except:
            self.uboot_addr = None
            self.uboot_size = None
        try:
            self.expect("HLOS\s+0x[0-9A-Fa-f]+\s+(0x[0-9A-Fa-f]+)\s+(0x[0-9A-Fa-f]+)\r", timeout=2)
            self.kernel_addr = self.match.group(1)
            self.kernel_size = self.match.group(2)
        except:
            self.kernel_addr = None
            self.kernel_size = None
        try:
            self.expect("(rootfs|ubi)\s+0x[0-9A-Fa-f]+\s+(0x[0-9A-Fa-f]+)\s+(0x[0-9A-Fa-f]+)\r", timeout=5)
            self.rootfs_addr = self.match.group(2)
            self.rootfs_size = self.match.group(3)
        except:
            self.rootfs_addr = None
            self.rootfs_size = None

        self.sendline('env default -f')
        self.expect('Resetting to default environment')
        self.expect(self.uprompt)
        self.sendline('setenv ethaddr %s' % self.randomMAC())
        self.expect(self.uprompt)

    def flash_meta(self, META_BUILD):
        '''
        A meta image contains several components wrapped up into one file.
        Here we flash a meta image onto the board.
        '''
        common.print_bold("\n===== Flashing meta =====\n")

        filename = self.prepare_file(META_BUILD)
        self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)
        # probe SPI flash incase this is a NOR boot meta
        if self.model not in ("dk01", "dk04"):
            self.sendline('sf probe')
            self.expect('sf probe')
            self.expect(self.uprompt)
        self.sendline('machid=%s && imgaddr=%s && source $imgaddr:script && echo DONE' % (self.machid, self.uboot_ddr_addr))
        self.expect('DONE')
        try:
            self.expect("Can't find 'script' FIT subimage", timeout=5)
        except:
            pass
        else:
            self.sendline('machid=%s && imgaddr=%s && source $imgaddr:SCRIPT && echo DONE' % (self.machid, self.uboot_ddr_addr))
            self.expect('DONE')
        self.expect('DONE', timeout=400)
        self.expect(self.uprompt)
        # reboot incase partitions changed
        self.reset()
        self.wait_for_boot()
        self.setup_uboot_network()

    def nand_flash_bin(self, addr, size, src):
        # make sure we round writes up to the next sector size
        hsize = hex((((int(size, 0) - 1) / self.flash_block_size) + 1) * self.flash_block_size)

        self.sendline("nand erase %s %s" % (addr, size))
        self.expect("OK", timeout=90)
        self.expect(self.uprompt)
        self.sendline("nand write $fileaddr %s %s" % (addr, hsize))
        self.expect("OK", timeout=90)
        self.expect(self.uprompt)
        self.sendline("nand read %s %s %s" % (src, addr, hsize))
        self.expect(self.uprompt)
        self.sendline("echo $filesize")
        self.readline()
        size = int(self.readline(), 16)
        self.sendline("cmp.b $fileaddr %s %s" % (src, hex(size - 1)))
        self.expect("Total of %s byte\(s\) were the same" % (size - 1))
        self.expect(self.uprompt)

    def spi_flash_bin(self, addr, size, src, esize=None):
        if esize == None:
            esize = size

        self.sendline('sf probe')
        self.expect('SF: Detected')
        self.expect(self.uprompt)
        # erase full partition
        self.sendline('sf erase %s %s' % (addr, esize))
        self.expect(self.uprompt, timeout=180)
        hsize = hex(size)
        self.sendline('sf write %s %s %s' % (src, addr, hsize))
        self.expect(self.uprompt, timeout=180)

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
                ret.append("r3")
            elif e == "icache_misses":
                ret.append("r1")
            elif e == "load_exclusive":
                ret.append("r12013")
            elif e == "store_exclusive":
                ret.append("r12011")
            elif e == "data_sync_barrier":
                ret.append("r12041")
            elif e == "data_mem_barrier":
                ret.append("r12040")
            elif e == "unaligned_load":
                ret.append("r12073")
            elif e == "unaligned_store":
                ret.append("r12071")
            else:
                raise Exception("Unknown perf event %s" % e)

        return (':%s,' % kernel_user).join(ret) + ":%s" % kernel_user

    def parse_perf_board(self):
        if "3.14" in self.kernel_version:
            events = [{'expect': '\s+cycles:ku', 'name': 'cycles', 'sname': 'CPP'},
                    {'expect': '\s+instructions:ku', 'name': 'instructions', 'sname': 'IPP'},
                    {'expect': '\s+r3:ku', 'name': 'dcache_misses', 'sname': 'DMISS'},
                    {'expect': '\s+r1:ku', 'name': 'icache_misses', 'sname': 'IMISS'}]
        else:
            events = [{'expect': 'cycles', 'name': 'cycles', 'sname': 'CPP'},
                    {'expect': 'instructions', 'name': 'instructions', 'sname': 'IPP'},
                    {'expect': 'raw 0x3', 'name': 'dcache_misses', 'sname': 'DMISS'},
                    {'expect': 'raw 0x1', 'name': 'icache_misses', 'sname': 'IMISS'}]

        events += [ {'expect': 'raw 0x12013', 'name': 'load_exclusive', 'sname': 'LDREX'},
                    {'expect': 'raw 0x12011', 'name': 'store_exclusive', 'sname': 'STREX'},
                    {'expect': 'raw 0x12041', 'name': 'data_sync_barrier', 'sname': 'DSB'},
                    {'expect': 'raw 0x12040', 'name': 'data_mem_barrier', 'sname': 'DBM'},
                    {'expect': 'raw 0x12073', 'name': 'unaligned_load', 'sname': 'UNALIGNED_LD'},
                    {'expect': 'raw 0x12071', 'name': 'unaligned_store', 'sname': 'UNALIGNED_ST'}]

        return events
