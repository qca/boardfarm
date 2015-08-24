# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
#!/usr/bin/env python

import datetime
import os
import socket
import sys

try:
    import elasticsearch
except Exception as e:
    print(e)
    print("Please install needed module:\n"
          "  sudo pip install -U elasticsearch")
    sys.exit(1)

class ElasticsearchLogger(object):
    '''
    Write data directly to an elasticsearch cluster.
    '''

    def __init__(self, server, index='boardfarm', doc_type='bft_run'):
        self.server = server
        self.index = index + "-" + datetime.datetime.utcnow().strftime("%Y.%m.%d")
        self.doc_type = doc_type
        # Connect to server
        self.es = elasticsearch.Elasticsearch([server])
        # Set default data
        username = os.environ.get('BUILD_USER_ID', None)
        if username is None:
            username = os.environ.get('USER', '')
        self.default_data = {
            'hostname': socket.gethostname(),
            'user': username,
            'build_url': os.environ.get('BUILD_URL', 'None'),
            'change_list': os.environ.get('change_list', 'None'),
            'apss': os.environ.get('apss', 'None').split('-')[0],
            'manifest': os.environ.get('manifest', 'None'),
        }

    def log(self, data, debug=False):
        # Put in default data
        self.default_data['@timestamp'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        data.update(self.default_data)
        result = self.es.index(index=self.index, doc_type=self.doc_type, body=data)
        if result and 'created' in result and result['created'] == True:
            doc_url = "%s%s/%s/%s" % (self.server, self.index, self.doc_type, result['_id'])
            print("Elasticsearch: Data stored at %s" % (doc_url))
        else:
            print(result)
            raise Exception('Elasticsearch: problem storing data.')
        if debug:
            print(data)
