# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import analysis
import re

class OOMAnalysis(analysis.Analysis):
    '''Parse logs for OOM kernel events'''
    def analyze(self, console_log, output_dir):
        if len(re.findall('Out of memory', console_log)):
            print 'ERROR: log had out of memory condition'
