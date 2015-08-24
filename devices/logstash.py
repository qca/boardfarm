# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
#!/usr/bin/env python

import json
import os
import socket

class RemoteLogger(object):
    '''
    Write data to remote logging server, in thise case, Logstash.
    '''

    def __init__(self, server, subtype='demo'):
        '''Logging server requires some default data for easy searching.'''
        username = os.environ.get('BUILD_USER_ID', None)
        if username is None:
            username = os.environ.get('USER', '')
        self.default_data = {
            'type': 'qcatest',
            'subtype': subtype,
            'hostname': socket.gethostname(),
            'user': username,
            'build_url': os.environ.get('BUILD_URL', 'None'),
            'change_list': os.environ.get('change_list', 'None'),
            'apss': os.environ.get('apss', 'None').split('-')[0],
            'manifest': os.environ.get('manifest', 'None'),
        }
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        name, port = server.split(':')
        self.logserver_ip = socket.gethostbyname(name)
        self.logserver_port = int(port)

    def log(self, data, debug=False):
        '''data must be a simple dictionary.'''
        # Put in default data
        data.update(self.default_data)
        s = json.dumps(data)
        self.sock.sendto(s, (self.logserver_ip, self.logserver_port))
        print("Logstash: %s bytes of data sent to %s:%s." % (len(s), self.logserver_ip, self.logserver_port))
        if len(s) > 8192:
            print("Logstash: WARNING, Data size too large. May not have logged result.")
        if debug:
            print(data)
