# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.


# Read simple test suite config files
import config
import devices.configreader
tmp = devices.configreader.TestsuiteConfigReader()
tmp.read(config.testsuite_config_files)
list_tests = tmp.section

# Create long or complicated test suites at run time.
# key = suite name, value = list of tests names (strings)
new_tests = {}

# Combine simple and dynamic dictionary of test suites
list_tests.update(new_tests)
