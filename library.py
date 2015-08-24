# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import os

from termcolor import cprint

def print_bold(msg):
    cprint(msg, None, attrs=['bold'])

def print_board_info(x):
    for key in sorted(x):
        print_bold("  %s: %s" % (key, x[key]))

def process_test_results(raw_test_results):
    full_results = {'test_results': [],
                    'tests_pass': 0,
                    'tests_fail': 0,
                    'tests_skip': 0,
                    'tests_total': 0,
                    }
    for i, x in enumerate(raw_test_results):
        message = None
        name = x.__class__.__name__
        grade = None
        try:
            grade = x.result_grade
        except:
            pass
        if grade == "OK" or grade == "Unexp OK":
            full_results['tests_pass'] += 1
        elif grade == "FAIL" or grade == "Exp FAIL":
            full_results['tests_fail'] += 1
        elif grade == "SKIP" or grade is None:
            full_results['tests_skip'] += 1
        try:
            # Use only first line of docstring result message
            message = x.__doc__.split('\n')[0]
        except:
            print_bold("WARN: Please add docstring to %s." % x)
        try:
            message = x.result_message
        except:
            pass
        if hasattr(x, 'long_result_message'):
            long_message = x.long_result_message
        else:
            long_message = ""
        full_results['test_results'].append({"name": name, "message": message, "long_message": long_message, "grade": grade})
    full_results['tests_total'] = len(raw_test_results)
    return full_results

def send_results_to_myqsl(testsuite, output_dir):
    '''
    Send url of results to a MySQL database.  Only do this if we are on
    a build server (use the build environment variables).
    '''
    dir = output_dir.replace(os.getcwd(), '').strip(os.sep)
    build_id = os.environ.get('image_build_id', '')
    build_url = os.environ.get('BUILD_URL', '')
    if '' not in (build_id, testsuite, build_url):
        from devices import mysql
        build_url = build_url.replace("https://", "") + "artifact/openwrt/%s/results.html" % dir
        title = 'Board Farm Results (suite: %s)' % testsuite
        reporter = mysql.MySqlReporter()
        reporter.insert_data(build_id, build_url, title)
