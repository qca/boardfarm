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

class SlabAnalysis(analysis.Analysis):
    '''Make graphs for output of /proc/slabinfo over time'''
    def analyze(self, console_log, output_dir):
        regex = "root\\@OpenWrt:[^#]+# cat /proc/slabinfo.*?(?=root@OpenWrt)"
        results = re.findall(regex, repr(console_log))

        # now process each time ps was run
        data = collections.defaultdict(list)
        timestamps = collections.defaultdict(list)
        for dump in results:
            for line in dump.split('\\r\\n')[3:]:
                line = re.sub('](?=[^\s])', '] ', line)
                e = line.split()
                if len(e) < 4:
                    continue
                ts = float(e.pop(0).strip('[]'))
                slab_name = e.pop(0)
                active_objs = e.pop(0)
                num_objs = e.pop(0)
                objsize = e.pop(0)
                objperslab = e.pop(0)
                pagespeslab = e.pop(0)
                key = 'slab-' + slab_name
                data[key].append(active_objs)
                timestamps[key].append(ts)

        for k in data:
            if len(data[k]) > 1:
                fname = k
                for c in r'[]/\;,><&*:%=+@!#^()|?^':
                        fname = fname.replace(c, '')
                self.make_graph(data[k], k, fname, ts=timestamps[k], output_dir=output_dir)
