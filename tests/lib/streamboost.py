# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import time

from devices import prompt
from common import clear_buffer

def stop(console):
    console.sendline('\nstreamboost stop')
    console.expect(['StreamBoost: Executing stop all','streamboost: not found'])
    console.expect(prompt)

def start(console):
    console.sendline('\nstreamboost start')
    console.expect('StreamBoost: Executing start all')
    console.expect(prompt)

def verify_enabled(console):
    '''Check if streamboost is enabled, throw exception if it is not.'''
    console.sendline('\nuci show appflow.tccontroller.enable_streamboost')
    console.expect('enable_streamboost=1', timeout=6)
    console.expect(prompt)

def verify_disabled(console):
    '''Check if StreamBoost is disabled, throw exception if it is not.'''
    console.sendline('\nuci show appflow.tccontroller.enable_streamboost')
    console.expect('enable_streamboost=0', timeout=6)
    console.expect(prompt)

def is_enabled(console):
    '''Return True if StreamBoost is enabled.'''
    console.sendline('\nuci show appflow.tccontroller.enable_streamboost')
    sb_enabled = console.expect(['enable_streamboost=0\r', 'enable_streamboost=1\r'], timeout=6)
    console.expect(prompt)
    if sb_enabled == 0:
        return False
    if sb_enabled == 1:
        return True

def disable(console):
    '''Disable StreamBoost.'''
    console.sendline('\nuci set appflow.tccontroller.enable_streamboost=0')
    console.expect('streamboost=0', timeout=6)
    console.expect(prompt)
    console.sendline('uci commit appflow; luci-reload appflow')
    console.expect('Reloading appflow...')
    console.expect(prompt)
    verify_disabled(console)

def enable(console):
    '''Enable StreamBoost.'''
    console.sendline('\nuci set appflow.tccontroller.enable_streamboost=1')
    console.expect('streamboost=1', timeout=6)
    console.expect(prompt)
    console.sendline('uci commit appflow; luci-reload appflow')
    console.expect('Reloading appflow...')
    console.expect(prompt)
    # SB takes a few seconds to fully start
    time.sleep(4)
    verify_enabled(console)

def enable_if_not(console):
    '''Enable StreamBoost if it is not already enabled'''
    if is_enabled(console):
        return "StreamBoost is already enabled."
    else:
        enable(console)
        return "StreamBoost now set to enabled."

def disable_if_not(console):
    '''Disable StreamBoost if it is not already enabled'''
    if not is_enabled(console):
        return "StreamBoost is already disabled."
    else:
        disable(console)
        return "StreamBoost now set to disabled."

def disable_http_auth(console):
    '''Turn off HTTP Basic Auth on Ozker.'''
    try:
        # Display current setting, if found
        console.sendline('\ngrep OZKER /etc/appflow/streamboost.sys.conf')
        console.expect('OZKER_BASIC_AUTH', timeout=4)
        console.expect(prompt)
    except:
        pass
    # Remove current setting, if present
    console.sendline("sed -i '/OZKER_BASIC_AUTH/d' /etc/appflow/streamboost.sys.conf")
    console.expect(prompt)
    console.sendline("sed -i '/OZKER_BASIC_AUTH/d' /var/run/appflow/streamboost.user.conf")
    console.expect(prompt)
    # Excplicitly disable
    console.sendline('echo "OZKER_BASIC_AUTH=no">>/etc/appflow/streamboost.sys.conf')
    console.expect(prompt)
    console.sendline('echo "OZKER_BASIC_AUTH=no">>/var/run/appflow/streamboost.user.conf')
    console.expect(prompt)

def disable_monit(console):
    '''Monit will restart Daemons that go down.
    Disable monit to prevent it from starting daemons.'''
    console.sendline('echo "SB_DISABLE_MONIT=yes">>/etc/appflow/streamboost.sys.conf')
    console.expect(prompt)

def enable_monit(console):
    '''Monit is enabled by default, but if it sees a
    certain variable, it will not restart daemons.'''
    console.sendline("sed -i '/SB_DISABLE_MONIT/d' /etc/appflow/streamboost.sys.conf")
    console.expect(prompt)

def get_status(console, logread_if_manydown=False, monit=False, now=False):
    '''
    Parse 'streamboost status' to
    return a dictionary like:
      {"redis-server" : "UP",
       "policy-reader": "UP,
       ...}
    '''
    sbdaemon_status = {}
    monit_status = {}
    num_down = 0
    num_tries = 8 
    for i in range(num_tries):
        clear_buffer(console)
        cmd='streamboost status'
        if monit:
            cmd='streamboost status_monit'
        console.sendline("\n" + cmd)
        try:
            console.expect(cmd)
            console.expect(prompt, timeout=60)
            output = console.before
            if monit:
                m = re.search('status=(\d+)',output)
                monit_status = {'code': int(m.group(1))}
            result = re.findall('\[\s+(\w+)\s+\]\s([-\w]+)\s', output)
            sbdaemon_status = dict([(x[1].lower(), x[0]) for x in result])
            num_down = len([x for x in sbdaemon_status if sbdaemon_status[x] == 'DOWN'])
            if not now and ("does not exist" in output or "try again later" in output or num_down > 1):
                print("\nStreamBoost not ready?  Trying again, sleeping 15s...")
                time.sleep(15)
            else:
                break
        except:
            console.sendcontrol('c')
    if num_down > 1 and logread_if_manydown:
        print("\nToo many daemons down. Dumping syslog...")
        print("===== Begin Logread =====")
        console.sendline('\nlogread')
        console.expect('logread')
        console.expect('OpenWrt')
        console.expect(prompt)
        print("\n===== End Logread =====")
    if monit:
        sbdaemon_status.update(monit_status)
    return sbdaemon_status

def verify_running(console, monit=False):
    '''
    Fail if any streamboost daemon is DOWN - besides the bandwidth daemons.
    '''
    ignore_list = ('aperture', 'bandwidth', 'bwestd')
    status = get_status(console, monit=monit)
    num_up = len([x for x in status if status[x] == 'UP'])
    num_down = len([x for x in status if status[x] == 'DOWN' and x not in ignore_list])
    assert num_down == 0 and num_up > 7

def set_bw_limits(console, up_limit, down_limit):
    '''
    Set bandwidth limits in uci, restart Streamboost, then verify new settings.
    up_limit and down_limit must have units of Bytes.
    '''
    # Check limits
    console.sendline('\nuci show appflow.tccontroller | grep limit=')
    console.expect('uplimit')
    console.expect(prompt)
    # Set new limits
    console.sendline('uci set appflow.tccontroller.uplimit=%s' % up_limit)
    console.expect(prompt)
    console.sendline('uci set appflow.tccontroller.downlimit=%s' % down_limit)
    console.expect(prompt)
    console.sendline('uci commit appflow')
    console.expect(prompt)
    for i in range(2):
        try:
            console.sendline('\nluci-reload appflow')
            console.expect('Reloading appflow')
            console.expect(prompt)
            break
        except:
            continue
    time.sleep(2) # give streamboost chance to fully boot
    # Check limits
    console.sendline('redis-cli get settings:bw:up')
    console.expect('"\d+"')
    console.expect(prompt)
    console.sendline('redis-cli get settings:bw:down')
    console.expect('"\d+"')
    console.expect(prompt)
    console.sendline('uci show appflow | grep limit=')
    console.expect('tccontroller')
    console.expect(prompt)
    uplimit = int(re.search('uplimit=(\d+)\r', console.before).group(1))
    downlimit = int(re.search('downlimit=(\d+)\r', console.before).group(1))
    print("\nStreamboost bandwidth limits now at %.1f Mbps upload, %.1f Mbps download." % (uplimit/131072., downlimit/131072.))
    if (uplimit != up_limit) or (downlimit != down_limit):
        print("Warning: Settings now in uci do not agree with intended settings.")

def print_redis_stats_size(console):
    '''Print size of a few important things in redis database.'''
    console.sendline('\nredis-cli info memory')
    console.expect('Memory')
    console.expect(prompt)
    console.sendline('redis-cli llen eventdb:events')
    console.expect('integer')
    console.expect(prompt)
    console.sendline('redis-cli lrange eventdb:events 0 -1 | wc -c')
    console.expect('\d+')
    console.expect(prompt)
    console.sendline('redis-cli llen eventdb:features')
    console.expect('integer')
    console.expect(prompt)
    console.sendline('redis-cli lrange eventdb:features 0 -1 | wc -c')
    console.expect('\d+')
    console.expect(prompt)

def run_aperture(console):
    '''Run bandwidth measurementt and return results in Mbps.'''
    console.sendline('\nstreamboost measure')
    console.expect('streamboost measure')
    try:
        console.expect(prompt, timeout=180)
    except Exception as e:
        print("\nAperture failed to finish after 3 minutes.")
        print("Sending CTRL-C.")
        console.sendcontrol('c')
        console.expect(prompt)
        return None, None
    try:
        up_result   = re.search(r'uplimit=([0-9]+)\r\n', console.before).group(1)
        down_result = re.search(r'downlimit=([0-9]+)\r\n', console.before).group(1)
        up_result_mbps = int(up_result)*8.0/(1000.*1000.)
        down_result_mbps = int(down_result)*8.0/(1000.*1000.)
        return up_result_mbps, down_result_mbps
    except Exception as e:
        return None, None

def check_detection_files_version(console):
    '''Find the version of the Flow detection file yaml.'''
    console.sendline("")
    if console.model in ('dlink-dgl5500', 'zyxel-nbg6716'):
        console.sendline("drflocs -D -k /etc/ssl/private/client_key.pem -w /tmp/run/appflow/wopr.yaml.enc | grep timestamp")
        console.expect('timestamp:')
    else:
        console.sendline("opkg list | grep '[wopr|p0f]-db\|policy-redis'")
        console.expect('wopr-db -')
        console.expect(prompt)
        console.sendline("grep timestamp /etc/appflow/wopr.yaml")
    console.expect(prompt)

def get_wopr_version(console):
    '''Return version number of Application detection config file.'''
    console.sendline("\ngrep timestamp /etc/appflow/wopr.yaml")
    console.expect("timestamp: '([_\d]+)'")
    version = console.match.group(1)
    console.expect(prompt)
    return version

def get_detected_flows(console, duration=10, sleep=2):
    '''
    Return dictionary with keys are detected flow names, and values are downloaded bytes.
    Poll every 'delay' seconds for a duration of seconds.
    '''
    # Fist create dict where key=name, value=list of down_bytes
    final_result = {}
    for i in range(duration/sleep):
        console.sendline('\ncurl http://127.0.0.1/cgi-bin/ozker/api/flows')
        console.expect('"flows":')
        console.expect(prompt)
        result = re.findall('"down_bytes":(\d+),"up_bytes":\d+,"name":"([_a-z0-9]+)"', console.before)
        detected_flows = {}
        if result:
            detected_flows = dict([(x[1],int(x[0])) for x in result])
        for k in detected_flows:
            if k not in final_result:
                final_result[k] = []
            final_result[k].append(detected_flows[k])
        time.sleep(sleep)
    # Modify to dict so that key=flowname, value=total bytes downloaded
    # This formula is fancy. Example: [0, 2, 4, 0, 1, 6] = 10.
    # It has to be, because flows can stop and "start over" at zero.
    for n in final_result:
        nums = final_result[n]
        final_result[n] = sum([nums[i+1]-nums[i] for i in range(len(nums)-1) if nums[i+1]>nums[i]])
    return final_result


def get_pid(console, name):
    try:
        cmd="top -b -n 1 | grep " + name + " | grep -v grep | awk '{print $1}'"
        console.sendline(cmd)
        console.expect('(\d+)\r\n', timeout=5)
        pid = int(console.match.group(1))
        console.expect(prompt)
        return pid
    except:
        return -1 

def kill_pid(console, pid):
    cmd="kill " + str(pid)
    console.sendline(cmd)
    console.expect(prompt)
