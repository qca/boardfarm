# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time
import unittest2
import lib
import sys
import traceback

from devices import board, wan, lan, wlan, prompt

class LinuxBootTest(unittest2.TestCase):

    def __init__(self, config):
        super(LinuxBootTest, self).__init__("testWrapper")
        self.config = config
        self.reset_after_fail = True
        self.dont_retry = False
        self.logged = dict()

    def id(self):
        return self.__class__.__name__

    def setUp(self):
        lib.common.test_msg("\n==================== Begin %s ====================" % self.__class__.__name__)
    def tearDown(self):
        lib.common.test_msg("\n==================== End %s ======================" % self.__class__.__name__)

    def wan_setup(self):
        None

    def lan_setup(self):
        None

    def wlan_setup(self):
        None

    def wan_cleanup(self):
        None

    def lan_cleanup(self):
        None

    def wlan_cleanup(self):
        None

    def testWrapper(self):
        if not board.isalive():
            self.result_grade = "SKIP"
            self.skipTest("Board is not alive")
            raise

        try:
            if wan and hasattr(self, 'wan_setup'):
                self.wan_setup()
            if lan and hasattr(self, 'lan_setup'):
                self.lan_setup()
            if wlan and hasattr(self, 'wlan_setup'):
                self.wlan_setup()

            if self.config.retry and not self.dont_retry:
                retry = self.config.retry
            else:
                retry = 0

            while retry >= 0:
                try:
                    self.runTest()
                    retry = -1
                except Exception as e:
                    retry = retry - 1
                    if(retry > 0):
                        print(e.get_trace())
                        print("\n\n----------- Test failed! Retrying in 5 seconds... -------------")
                        time.sleep(5)
                    else:
                        raise

            if wan and hasattr(self, 'wan_cleanup'):
                self.wan_cleanup()
            if lan and hasattr(self, 'lan_cleanup'):
                self.lan_cleanup()
            if wlan and hasattr(self, 'wlan_cleanup'):
                self.wlan_cleanup()

            if hasattr(self, 'expected_failure') and self.expected_failure:
                self.result_grade = "Unexp OK"
            else:
                self.result_grade = "OK"
        except unittest2.case.SkipTest:
            self.result_grade = "SKIP"
            print("\n\n=========== Test skipped! Moving on... =============")
            raise
        except Exception as e:
            if hasattr(self, 'expected_failure') and self.expected_failure:
                self.result_grade = "Exp FAIL"
            else:
                self.result_grade = "FAIL"
            print("\n\n=========== Test failed! Running recovery ===========")
            if e.__class__.__name__ == "TIMEOUT":
                print(e.get_trace())
            else:
                print(e)
                traceback.print_exc(file=sys.stdout)
            self.recover()
            raise

    def recover(self):
        if self.__class__.__name__ == "LinuxBootTest":
            print("aborting tests, unable to boot..")
            sys.exit(1)
        print("ERROR: No default recovery!")
        raise "No default recovery!"
