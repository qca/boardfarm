# Copyright (c) 2017
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router


class RPI(openwrt_router.OpenWrtRouter):
    '''
    Raspberry pi board
    '''

    wan_iface = "erouter0"
    lan_iface = "brlan0"

    uprompt = ["U-Boot>"]
    uboot_eth = "sms0"
    uboot_ddr_addr = "0x1000000"
    uboot_net_delay = 0

    fdt = "uImage-bcm2710-rpi-3-b.dtb"
    fdt_overlay = "uImage-pi3-disable-bt-overlay.dtb"

    # can't get u-boot to work without a delay
    delaybetweenchar = 0.05

    def flash_uboot(self, uboot):
        '''In this case it's flashing the vfat partition of the bootload.
           Need to have that image u-boot and serial turned on via dtoverlay
           for things to work after flashing'''
        common.print_bold("\n===== Flashing bootloader (and u-boot) =====\n")
        filename = self.prepare_file(uboot)
        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)

        self.sendline('mmc part')
        # get offset of ext (83) partition after a fat (0c) partition
        self.expect('\r\n\s+\d+\s+(\d+)\s+(\d+).*0c( Boot)?\r\n')
        start = hex(int(self.match.groups()[0]))
        if (int(size) != int(self.match.groups()[1]) * 512):
                raise Exception("Partition size does not match, refusing to flash")
        self.expect(self.uprompt)
        count = hex(int(size/512))
        self.sendline('mmc erase %s %s' % (start, count))
        self.expect(self.uprompt)
        self.sendline('mmc write %s %s %s' % (self.uboot_ddr_addr, start, count))
        self.expect(self.uprompt, timeout=120)

        self.reset()
        self.wait_for_boot()
        self.setup_uboot_network()

    def flash_rootfs(self, ROOTFS):
        common.print_bold("\n===== Flashing rootfs =====\n")
        filename = self.prepare_file(ROOTFS)

        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename, timeout=160)
        self.sendline('mmc part')
        # get offset of ext (83) partition after a fat (0c) partition
        self.expect('0c( Boot)?\r\n\s+\d+\s+(\d+)\s+(\d+).*83\r\n')
        start = hex(int(self.match.groups()[-2]))
        sectors = int(self.match.groups()[-1])
        self.expect(self.uprompt)

        # increase partition size if required
        if (int(size) > (sectors * 512)):
            self.sendline("mmc read %s 0 1" % self.uboot_ddr_addr)
            self.expect(self.uprompt)
            gp2_sz = int(self.uboot_ddr_addr, 16) + int("0x1da", 16)
            self.sendline("mm 0x%08x" % gp2_sz)
            self.expect("%08x: %08x ?" % (gp2_sz, sectors))
            # pad 100M
            self.sendline('0x%08x' % int((int(size) + 104857600) / 512))
            self.sendcontrol('c')
            self.sendcontrol('c')
            self.expect(self.uprompt)
            self.sendline('echo FOO')
            self.expect_exact('echo FOO')
            self.expect_exact('FOO')
            self.expect(self.uprompt)
            self.sendline("mmc write %s 0 1" % self.uboot_ddr_addr)
            self.expect(self.uprompt)
            self.sendline('mmc rescan')
            self.expect(self.uprompt)
            self.sendline('mmc part')
            self.expect(self.uprompt)

        count = hex(int(size/512))
        self.sendline('mmc erase %s %s' % (start, count))
        self.expect(self.uprompt)
        self.sendline('mmc write %s %s %s' % (self.uboot_ddr_addr, start, count))
        self.expect_exact('mmc write %s %s %s' % (self.uboot_ddr_addr, start, count))
        self.expect(self.uprompt, timeout=120)

    def flash_linux(self, KERNEL):
        common.print_bold("\n===== Flashing linux =====\n")

        filename = self.prepare_file(KERNEL)
        size = self.tftp_get_file_uboot(self.uboot_ddr_addr, filename)

        self.sendline('fatwrite mmc 0 %s uImage $filesize' % self.uboot_ddr_addr)
        self.expect(self.uprompt)

    def boot_linux(self, rootfs=None):
        common.print_bold("\n===== Booting linux for %s on %s =====" % (self.model, self.root_type))

        #self.sendline('setenv bootargs "8250.nr_uarts=1 bcm2708_fb.fbwidth=1824 bcm2708_fb.fbheight=984 bcm2708_fb.fbswap=1 dma.dmachans=0x7f35 bcm2709.boardrev=0xa02082 bcm2709.serial=0xc07187c2 bcm2709.uart_clock=48000000 smsc95xx.macaddr=B8:27:EB:71:87:C2 vc_mem.mem_base=0x3dc00000 vc_mem.mem_size=0x3f000000  dwc_otg.lpm_enable=0 console=ttyAMA0,115200 root=mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait"')
        #self.expect(self.uprompt)

        self.sendline("setenv bootcmd 'fatload mmc 0 ${kernel_addr_r} uImage; bootm ${kernel_addr_r} - ${fdt_addr}'")
        self.expect(self.uprompt)
        self.sendline('saveenv')
        self.expect(self.uprompt)
        self.sendline('boot')

        # Linux handles serial better ?
        self.delaybetweenchar = None
