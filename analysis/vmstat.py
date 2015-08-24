# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import analysis
import re
import collections

class VmStatAnalysis(analysis.Analysis):
    '''Make graphs from /proc/vmstat over time'''
    def analyze(self, console_log, output_dir):
        results = re.findall(analysis.newline_match + 'nr_(\w+) (\d+)', console_log)
        data = collections.defaultdict(list)
        timestamps = collections.defaultdict(list)
        for t, k, v in results:
            data[k].append(int(v))
            timestamps[k].append(float(t))

        sz = len(data.itervalues().next())
        for k in data:
            if len(data[k]) > 1:
                sz = min(len(data[k]), sz)
                self.make_graph(data[k], k, k, ts=timestamps[k], output_dir=output_dir)

        # not great, just trimming some data to fit but works OK
        # for the time being
        for k in data:
            data[k] = data[k][:sz]
            timestamps[k] = timestamps[k][:sz]

        from operator import add
        if len(data['slab_unreclaimable']) > 1:
            self.make_graph(map(add, data['slab_unreclaimable'], data['active_anon']),
                        'slab_unreclaimable + active_anon',
                        'slab_unreclaimable+active_anon',
                        ts=timestamps['slab_unreclaimable'], output_dir=output_dir)

        if len(data['free_pages']) > 1:
            self.make_graph(map(add, data['free_pages'], data['inactive_file']),
                        'free_pages + inactive_file',
                        'free_pages+inactive_file',
                        ts=timestamps['free_pages'], output_dir=output_dir)
