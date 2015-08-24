# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import analysis
import re

class SbConnectionsAnalysis(analysis.Analysis):
    '''Look for streamboost 2.0 number of connections and make graphs'''
    def analyze(self, console_log, output_dir):
        regex = r"redis-cli -s \$s keys \\'conndb...flow\\' \| wc -l" + \
                analysis.newline_re_match + "(\d+)" + analysis.newline_re
        timestamps, results = analysis.split_results(re.findall(regex, repr(console_log)))

        if len(timestamps) == len(results) and len(results) > 1:
            self.make_graph(results, "streamboost connections", "sb_connections", ts=timestamps, output_dir=output_dir)
        elif len(results) > 1:
            self.make_graph(results, "streamboost connections", "sb_connections", output_dir=output_dir)

        regex = "redis-cli -s \$s scard flowdb.flows" + analysis.newline_re_match + \
                "\(integer\) (\d+)" + analysis.newline_re
        timestamps, results = analysis.split_results(re.findall(regex, repr(console_log)))

        if len(timestamps) == len(results) and len(results) > 1:
            self.make_graph(results, "streamboost flows", "sb_flows", ts=timestamps, output_dir=output_dir)
        if len(results) > 1:
            self.make_graph(results, "streamboost flows", "sb_flows", output_dir=output_dir)
