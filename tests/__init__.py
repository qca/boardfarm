# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
import lib

# Import from every file
import os
import glob
test_files = glob.glob(os.path.dirname(__file__)+"/*.py")
for x in sorted([os.path.basename(f)[:-3] for f in test_files if not "__" in f]):
    try:
        exec("from %s import *" % x)
    except Exception as e:
        print(e)
        print("Warning: could not import from file %s." % x)
