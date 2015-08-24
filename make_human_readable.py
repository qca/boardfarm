#!/usr/bin/env python

# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import json
import os
import re
import sys

from string import Template
try:
    from collections import Counter
except:
    from future.moves.collections import Counter

import config

owrt_tests_dir = os.path.dirname(os.path.realpath(__file__))

def pick_template_filename():
    '''
    Decide which HTML file to use as template for results.
    This allows for different format for different audiences.
    '''
    templates = {'basic': owrt_tests_dir+"/html/template_results_basic.html",
                 'full': owrt_tests_dir+"/html/template_results.html"}
    if os.environ.get('test_suite') == 'daily_au':
        return templates['basic']
    else:
        return templates['full']

def changes_to_html(changes):
    '''
    Input: "15408,8 17196,2 17204,1"
    Output: String of html links, e.g.
         <a href="https://gerrit.mysite.com/#/c/15408/">15408,8</a>,
         <a href...
    '''
    if not changes:
        return None
    if not config.code_change_server:
        return changes
    base_url = config.code_change_server
    list_changes = re.findall('\d+,\d+', changes)
    if not list_changes:
        return None
    result = []
    for c in list_changes:
        try:
            change_id, _ = c.split(',')
            url = base_url + change_id
            s = '<a href="%s">%s</a>' % (url, c)
            result.append(s)
        except:
            continue
    return ", ".join(result)

def xmlresults_to_html(test_results,
                       output_name=owrt_tests_dir+"/results/results.html",
                       title=None,
                       board_info={}):
    parameters = {'build_url' : os.environ.get('BUILD_URL'),
                  'total_test_time' : 'unknown',
                  'summary_title' : title,
                  'changes': changes_to_html(os.environ.get('change_list')),
                  "board_type": "unknown",
                  "lan_device": "unknown",
                  "wan_device": "unknown",
                  "conn_cmd"  : "unknown"}
    try:
        parameters.update(board_info)
    except Exception as e:
        print(e)

    # categorize the results data
    results_table_lines = []
    results_fail_table_lines = []
    grade_counter = Counter()
    styles = {'OK': 'ok',
              'Unexp OK': 'uok',
              'SKIP': 'skip',
              None: 'skip',
              'FAIL': 'fail',
              'Exp FAIL': 'efail'}
    for i, t in enumerate(test_results):
        t['num'] = i+1
        t['style'] = styles[t['grade']]
        if i % 2 == 0:
            t['row_style'] = "even"
        else:
            t['row_style'] = "odd"
        grade_counter[t['grade']] += 1
        if 'FAIL' == t['grade']:
            results_fail_table_lines.append('<tr class="%(row_style)s"><td>%(num)s</td><td class="%(style)s">%(grade)s</td><td>%(name)s</td></tr>' % t)
        results_table_lines.append('<tr class="%(row_style)s"><td>%(num)s</td><td class="%(style)s">%(grade)s</td><td>%(name)s</td><td>%(message)s</td></tr>' % t)
        if t['long_message'] != "":
            results_table_lines.append('<tr class="%(row_style)s"><td colspan=4><pre align="left">' % t)
            results_table_lines.append("%(long_message)s" % t)
            results_table_lines.append('</pre></td></tr>')

    # process the summary counter
    results_summary_table_lines = []
    for e, v in grade_counter.items():
        t['style'] = styles[t['grade']]
        results_summary_table_lines.append('<tr><td class="%s">%s: %d</td></tr>' % (styles[e], e, v))

    # Create the results tables
    parameters['table_results'] = "\n".join(results_table_lines)
    if len(results_fail_table_lines) == 0:
        parameters['table_fail_results'] = "<tr><td>None</td></tr>"
    else:
        parameters['table_fail_results'] = "\n".join(results_fail_table_lines)
    parameters['table_summary_results'] = "\n".join(results_summary_table_lines)

    # Other parameters
    try:
        test_seconds = int(os.environ.get('TEST_END_TIME'))-int(os.environ.get('TEST_START_TIME'))
        parameters['total_test_time'] = "%s minutes" % (test_seconds/60)
    except:
        pass
    # Substitute parameters into template html to create new html file
    template_filename = pick_template_filename()
    f = open(template_filename, "r").read()
    s = Template(f)
    f = open(output_name, "w")
    f.write(s.substitute(parameters))
    f.close()
    print("Created %s" % output_name)

def get_title():
    try:
        title = os.environ.get('summary_title')
        if title:
            return title
    except:
        pass
    try:
        return os.environ.get('JOB_NAME')
    except:
        return None

if __name__ == '__main__':
    try:
        list_results = json.load(open(sys.argv[1], 'r'))['test_results']
        xmlresults_to_html(list_results, title="Test Results")
    except Exception as e:
        print(e)
        print("To use make_human_readable.py:")
        print("./make_human_readable.py results/test_results.json")
