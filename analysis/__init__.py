# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import os
import glob
# import all analysis classes
analysis_files = glob.glob(os.path.dirname(__file__)+"/*.py")
for x in sorted([os.path.basename(f)[:-3] for f in analysis_files if not "__" in f]):
    exec("from %s import *" % x)
