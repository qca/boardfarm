# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import os

# Boardfarm configuration describes test stations - see boardfarm doc.
# Can be local or remote file.
boardfarm_config_location = os.environ.get('BFT_CONFIG', 'boardfarm_config_example.json')

# Test Suite config files. Standard python config file format.
testsuite_config_files = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testsuites.cfg'), ]

# Logstash server - a place to send JSON-format results to
# when finished. Set to None or name:port, e.g. 'logstash.mysite.com:1300'
logging_server = None

# Elasticsearch server. Data in JSON-format can be directly sent here.
# Set to None or to a valid host, see documentation:
#     https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch
elasticsearch_server = None

# Code change server like gerrit, github, etc... Used only in display
# of the results html file to list links to code changes tested.
code_change_server = None
