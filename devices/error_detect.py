# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import pexpect
import common
import re
import inspect
import os

# Add this to your env if you need to disable this for some reason
BFT_DISABLE_ERROR_DETECT = "BFT_DISABLE_ERROR_DETECT" in os.environ

def detect_kernel_panic(console, s):
    if re.findall("Kernel panic - not syncing", s):
        console.close()

        raise Exception('Kernel panic detected')

def detect_crashdump_error(console, s):
    if re.findall("Crashdump magic found", s):
        common.print_bold("Crashdump magic found, trying to save data...");

        console.sendcontrol('c')
        console.sendcontrol('c')
        console.sendcontrol('c')
        console.expect('<INTERRUPT>')
        console.expect(console.uprompt)
        console.setup_uboot_network()
        console.sendline("dumpipq_data")

        tftp_progress = "#" * 30
        tftp_start = "TFTP to server"
        tftp_done = "Bytes transferred"
        tftp_expect = [tftp_progress, tftp_start, tftp_done]

        i = -1
        try:
            # this waits until we get the reseting message which means
            # we are done
            while i < 3:
                i = console.expect(tftp_expect +
                        ["Resetting with watch dog!"] + console.uprompt)
        except:
            common.print_bold("Crashdump upload failed")
        else:
            common.print_bold("Crashdump upload succeeded")

        # TODO: actually parse data too?
        raise Exception('Crashdump detected')

def detect_fatal_error(console):
    if BFT_DISABLE_ERROR_DETECT:
        return

    s = ""

    if isinstance(console.before, str):
        s += console.before
    if isinstance(console.after, str):
        s += console.after

    detect_crashdump_error(console, s)
    #detect_kernel_panic(console, s)

def caller_file_line(i):
    caller = inspect.stack()[i] # caller of spawn or pexpect
    frame = caller[0]
    info = inspect.getframeinfo(frame)

    # readline calls expect
    if info.function == "readline":
        # note: we are calling ourselves, so we have to add more than 1 here
        return caller_file_line(i+2)
    return "%s: %s(): line %s" % (info.filename, info.function, info.lineno)


