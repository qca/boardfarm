# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import analysis
import re

class ConnectionsAnalysis(analysis.Analysis):
    '''Look at logs for number of connections and create graph from results'''
    def analyze(self, console_log, output_dir):
        regex = "cat /proc/sys/net/netfilter/nf_conntrack_count" \
                + analysis.newline_re_match + "(\d+)" + analysis.newline_re
        timestamps, results = analysis.split_results(re.findall(regex, repr(console_log)))

        if len(timestamps) == len(results) and len(results) > 1:
            self.make_graph(results, "num connections", "connections", ts=timestamps, output_dir=output_dir)
        elif len(results) > 1:
            self.make_graph(results, "num connections", "connections", output_dir=output_dir)
