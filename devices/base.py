# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import pexpect
from termcolor import colored
from datetime import datetime
import re


class BaseDevice(pexpect.spawn):

    prompt = ['root\\@.*:.*#', ]

    def get_interface_ipaddr(self, interface):
        self.sendline("\nifconfig %s" % interface)
        self.expect('addr:(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*(Bcast|P-t-P):', timeout=5)
        ipaddr = self.match.group(1)
        self.expect(self.prompt)
        return ipaddr

    def get_logfile_read(self):
        if hasattr(self, "_logfile_read"):
            return self._logfile_read
        else:
            return None

    def expect_prompt(self, timeout=30):
        self.expect(self.prompt, timeout=timeout)

    def check_output(self, cmd, timeout=30):
        '''Send a string to device, then  return the output
        between that string and the next prompt.'''
        self.sendline("\n" + cmd)
        self.expect_exact(cmd, timeout=5)
        try:
            self.expect(self.prompt, timeout=timeout)
        except Exception as e:
            self.sendcontrol('c')
            raise Exception("Command did not complete within %s seconds. Prompt was not seen." % timeout)
        return self.before

    def write(self, string):
        self._logfile_read.write(string)
        self.log += string

    def set_logfile_read(self, value):
        class o_helper():
            def __init__(self, out, color):
                self.color = color
                self.out = out
                self.log = ""
                self.start = datetime.now()
            def write(self, string):
                if self.color is not None:
                    self.out.write(colored(string, self.color))
                else:
                    self.out.write(string)
                td = datetime.now()-self.start
                ts = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
                # check for the split case
                if len(self.log) > 1 and self.log[-1] == '\r' and string[0] == '\n':
                    tmp = '\n [%s]' % ts
                    tmp += string[1:]
                    string = tmp
                self.log += re.sub('\r\n', '\r\n[%s] ' % ts, string)
            def flush(self):
                self.out.flush()

        if value is not None:
            self._logfile_read = o_helper(value, getattr(self, "color", None))

    def get_log(self):
        return self._logfile_read.log

    logfile_read = property(get_logfile_read, set_logfile_read)
    log = property(get_log)

    # perf related
    def parse_sar_iface_pkts(self, wan, lan):
        self.expect('Average.*idle\r\nAverage:\s+all(\s+[0-9]+.[0-9]+){6}\r\n')
        idle = float(self.match.group(1))
        self.expect("Average.*rxmcst/s.*\r\n")

        wan_pps = None
        client_pps = None
        if lan is None:
            exp = [wan]
        else:
            exp = [wan,lan]

        for x in range(0, len(exp)):
            i = self.expect(exp)
            if i == 0: # parse wan stats
                self.expect("(\d+.\d+)\s+(\d+.\d+)")
                wan_pps = float(self.match.group(1)) + float(self.match.group(2))
            if i == 1:
                self.expect("(\d+.\d+)\s+(\d+.\d+)")
                client_pps = float(self.match.group(1)) + float(self.match.group(2))

        return idle, wan_pps, client_pps

    def check_perf(self):
        self.sendline('uname -r')
        self.expect('uname -r')
        self.expect(self.prompt)

        self.kernel_version = self.before

        self.sendline('\nperf --version')
        i = self.expect(['not found', 'perf version'])
        self.expect(self.prompt)

        if i == 0:
            return False

        return True

    def check_output_perf(self, cmd, events):
        perf_args = self.perf_args(events)

        self.sendline("perf stat -a -e %s time %s" % (perf_args, cmd))

    def parse_perf(self, events):
        mapping = self.parse_perf_board()
        ret = []

        for e in mapping:
            if e['name'] not in events:
                continue
            self.expect("(\d+) %s" % e['expect'])
            e['value'] = int(self.match.group(1))
            ret.append(e)

        return ret

    # end perf related
