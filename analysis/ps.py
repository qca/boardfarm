# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import analysis
import re
import collections
import os

class PSAnalysis(analysis.Analysis):
    '''Parse top for ps commands, and create graph of process memory usage over time'''
    def analyze(self, console_log, output_dir):
        regex = "root\\@OpenWrt:[^#]+# ps.*?(?=root@OpenWrt)"
        results = re.findall(regex, repr(console_log))

        # now process each time ps was run
        data = collections.defaultdict(list)
        timestamps = collections.defaultdict(list)
        for ps_dump in results:
            for line in ps_dump.split('\\r\\n')[2:]:
                line = re.sub('](?=[^\s])', '] ', line)
                e = line.split()
                if len(e) < 4:
                    continue
                ts = float(e.pop(0).strip('[]'))
                pid = e.pop(0)
                user = e.pop(0)
                mem = e.pop(0)
                while e[0] in ['S', 'R', 'SW', 'SW<', 'DW', 'N', '<', 'D', 'Z']: e.pop(0)
                cmdline = " ".join(e)
                if cmdline[0] == '[' and cmdline[-1] == ']':
                    cmd = cmdline
                else:
                    cmd = os.path.basename(cmdline.split()[0])
                key = pid + '-' + cmd
                data[key].append(mem)
                timestamps[key].append(ts)

        for k in data:
            if len(data[k]) > 1:
                fname = k
                for c in r'[]/\;,><&*:%=+@!#^()|?^':
                        fname = fname.replace(c, '')
                self.make_graph(data[k], k, fname, ts=timestamps[k], output_dir=output_dir)
