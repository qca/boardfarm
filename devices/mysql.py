#!/usr/bin/env python
# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import sys

class MySqlReporter():
    '''
    If results are archived somewhere (e.g. a Jenkins server, or other
    build server), the MySqlReporter class can be used to insert the
    location of the results to a MySQL database.

    Example credential file:
    host="myserver.something.com"
    port=3349
    user="username"
    passwd="password"
    db="database_name"
    '''

    def __init__(self,
                 credential_dir='/local/mnt/workspace/',
                 credential_file='findit_db'):
        try:
            import MySQLdb
        except Exception as e:
            print(e)
            print("WARNING: Unable to import MySQLdb.")
            print("Perhaps install it: sudo apt-get install python-mysqldb")
            raise Exception
        try:
            sys.path.insert(0, credential_dir)
            self.credentials = __import__(credential_file)
        except Exception as e:
            print(e)
            print("WARNING: Unable to import mysql credentials:\n"
                  "%s" % (credential_dir + credential_file))
            raise Exception
        self.db = MySQLdb.connect(host=self.credentials.host,
                                  port=self.credentials.port,
                                  user=self.credentials.user,
                                  passwd=self.credentials.passwd,
                                  db=self.credentials.db)
        self.cur = self.db.cursor()

    def insert_data(self, build_id, url, jobname):
        '''
        Given a build ID (e.g. APSS.LN.0.0.1-00047-S-1) and a
        url, insert these into the database.
        '''
        cmd = ("INSERT INTO TestResults "
               "(TestResultsBuildID, TestResultsJobName, TestResultsLink) "
               "VALUES (%(BuildID)s, %(JobName)s, %(ResultsLink)s)")
        data = {
            'BuildID': build_id,
            'JobName': jobname,
            'ResultsLink': url
            }
        try:
            print('Insert into myqsl %s:%s: %s' % (self.credentials.host,
                                                   self.credentials.port,
                                                   data))
            self.cur.execute(cmd, data)
            self.db.commit()
        except Exception as e:
            print(e)
            print("WARNING: Unable to insert data into database.")

if __name__ == '__main__':
    reporter = MySqlReporter()
    reporter.insert_data('test', 'something.com/openwrt/results/results.html')
