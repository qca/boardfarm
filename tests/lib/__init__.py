# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
import unittest2
import common

def expectedFailureIf(test):
    def wrap(func):
        def wrapped(self, *args, **kwargs):
            if test():
                @unittest2.expectedFailure
                def f(): func(self)

                return f()
            return func(self)
        return wrapped
    return wrap
