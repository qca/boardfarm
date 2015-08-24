# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import os
import re

# no repr
newline = r"\r\n\[[^\]]+\] "
newline_match = r"\r\n\[([^\]]+)\] "
# with repr
newline_re = r"\\r\\n\[[^\]]+\] "
newline_re_match = r"\\r\\n\[([^\]]+)\] "

def prepare_log(log):
    '''Strips some stuff from outside logs so we can parse'''
    # TODO: convert other timestamps into seconds since boot
    return log

def split_results(results):
    t = [x[0] for x in results]
    r = [x[1] for x in results]

    if len(r) == len(t):
        return t, r

    # fallback to no timestamps
    return None, results

class Analysis():
    '''Base analysis class, each child class should implement the analyze function'''
    def analyze(self, console_log, output_dir):
        pass

    def make_graph(self, data, ylabel, fname, ts=None, xlabel="seconds since boot (probably)", output_dir=None):
        '''Helper function to make a PNG graph'''
        if not output_dir:
            return

        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt

        plt.gca().yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%d'))
        plt.gca().xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%d'))
        if ts is None:
            plt.plot(data)
        else:
            plt.plot(ts, data)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.savefig(os.path.join(output_dir, "%s.png" % fname))
        plt.clf()

        # TODO: save simple CSV file?
