# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
import lib
import os
import sys
import glob
from devices import board, wan, lan, wlan, prompt

def print_subclasses(cls):
    for x in cls.__subclasses__():
        print(x.__name__)
        print_subclasses(x)


class Interact(rootfs_boot.RootFSBootTest):
    '''Interact with console, wan, lan, wlan connections and re-run tests'''

    def print_legacy_devices(self):
        print("  LAN device:    ssh %s@%s" % (self.config.board.get('lan_username', "root"), self.config.board.get('lan_device')))
        print("  WAN device:    ssh %s@%s" % (self.config.board.get('wan_username', "root") ,self.config.board.get('wan_device')))

    def print_dynamic_devices(self):
        for device in self.config.devices:
            d = getattr(self.config, device)
            print("  %s device:    ssh %s@%s" % (device, d.username, d.name))

    def runTest(self):
        legacy = hasattr(self.config, "wan_device")
        lib.common.test_msg("Press Ctrl-] to stop interaction and return to menu")
        board.sendline()
        try:
            board.interact()
        except:
            return

        while True:
            print("\n\nCurrent station")
            print("  Board console: %s" % self.config.board.get('conn_cmd'))
            if legacy:
                self.print_legacy_devices()
            self.print_dynamic_devices()
            print('Pro-tip: Increase kernel message verbosity with\n'
                  '    echo "7 7 7 7" > /proc/sys/kernel/printk')
            print("Menu")
            print("  1: Enter console")
            i = 2
            if legacy: 
                print("  2: Enter wan console")
                print("  3: Enter lan console")
                print("  4: Enter wlan console")
                i = 5

            print("  %s: List all tests" % i)
            i += 1
            print("  %s: Run test" % i)
            i += 1
            print("  %s: Reset board" % i)
            i += 1
            print("  %s: Enter interactive python shell" % i)
            i += 1
            if len(self.config.devices) > 0:
                print("  Type a device name to connect: %s" % self.config.devices)
            print("  x: Exit")
            key = raw_input("Please select: ")

            if key in self.config.devices:
                d = getattr(self.config, key)
                d.interact()

            if key == "1":
                board.interact()
            elif legacy and key == "2":
                wan.interact()
            elif legacy and key == "3":
                lan.interact()
            elif legacy and key == "4":
                wlan.interact()
            elif (legacy and key == "5") or key == "2":
                try:
                    # re import the tests
                    test_files = glob.glob(os.path.dirname(__file__)+"/*.py")
                    for x in sorted([os.path.basename(f)[:-3] for f in test_files if not "__" in f]):
                        exec("from %s import *" % x)
                except:
                    print("Unable to re-import tests!")
                else:
                    # list what we can re-run
                    rfs_boot = rootfs_boot.RootFSBootTest
                    print("Available tests:")
                    print_subclasses(rfs_boot)
            elif (legacy and key == "6") or key == "3":
                try:
                    # re import the tests
                    test_files = glob.glob(os.path.dirname(__file__)+"/*.py")
                    for x in sorted([os.path.basename(f)[:-3] for f in test_files if not "__" in f]):
                        exec("from %s import *" % x)
                except:
                    print("Unable to re-import tests!")
                else:
                    # TODO: use an index instead of test name
                    print("Type test to run: ")
                    test = sys.stdin.readline()

                    try:
                        board.sendline()
                        board.sendline('echo \"1 1 1 7\" > /proc/sys/kernel/printk')
                        board.expect(prompt)
                        t = eval(test)
                        cls = t(self.config)
                        lib.common.test_msg("\n==================== Begin %s ====================" % cls.__class__.__name__)
                        cls.testWrapper()
                        lib.common.test_msg("\n==================== End %s ======================" % cls.__class__.__name__)
                        board.sendline()
                    except:
                        print("Unable to (re-)run specified test")

            elif (legacy and key == "7") or key == "4":
                board.reset()
                print("Press Ctrl-] to stop interaction and return to menu")
                board.interact()
            elif (legacy and key == "8") or key == "5":
                print "Enter python shell, press Ctrl-D to exit"
                try:
                    from IPython import embed
                    embed()
                except:
                    try:
                        import readline # optional, will allow Up/Down/History in the console
                        import code
                        vars = globals().copy()
                        vars.update(locals())
                        shell = code.InteractiveConsole(vars)
                        shell.interact()
                    except:
                        print "Unable to spawn interactive shell!"
            elif key == "x":
                break
