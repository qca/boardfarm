# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
#!/usr/bin/env python

import re

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

class TestsuiteConfigReader(object):
    '''
    Read config file like:

      [testsuiteA]
      test1
      test2
      test1
      test2
      [testsuiteB]
      test7
      test2
      [testsuiteC]
      @testsuiteB
      test3

    And from that, create dictionary like:

      {'testsuiteA' : [test1, test2, test1, test2, ...]
       'testsuiteB' : [test7, test2, ...]
       'testsuiteC' : [test7, test2, test3, ...]
      }
    '''

    def __init__(self):
        self.section = {}

    def read(self, filenames):
        for f in filenames:
            try:
                self.read_config(f)
            except Exception as e:
                print(e)
                continue

    def read_config(self, fname):
        '''
        Read local or remote (http) config file and parse into a dictionary.
        '''
        try:
            if fname.startswith("http"):
                s_config = urlopen(fname).read()
            else:
                s_config = open(fname, 'r').read()
        except Exception as e:
            print(e)
            raise Exception("Warning: Unable to read/access %s" % fname)
        current_section = None
        for i, line in enumerate(s_config.split('\n')):
            try:
                if line == '' or re.match('^\s+', line) or line.startswith('#'):
                    continue
                if '[' in line:
                    current_section = re.search('\[(.*)\]', line).group(1)
                    if current_section not in self.section:
                        self.section[current_section] = []
                if '@' in line:
                    ref_section = re.search('@(.*)', line).group(1)
                    if ref_section in self.section:
                        self.section[current_section] = self.section[current_section] + self.section[ref_section]
                elif re.match('\w+', line):
                    if current_section:
                        self.section[current_section].append(line)
            except Exception as e:
                print(e)
                print("Error line %s of %s" % (i+1, fname))
                continue

    def __str__(self):
        result = []
        for name in sorted(self.section):
            result.append('* %s' % name)
            for i, x in enumerate(self.section[name]):
                result.append(' %2s %s' % (i+1, x))
        return "\n".join(result)

if __name__ == '__main__':
    import os
    filenames = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '../testsuites.cfg'),
                ]
    t = TestsuiteConfigReader()
    t.read(filenames)
    print(t)
