Board Farm
----------

Boardfarm is an open-source framework that was developed at Qualcomm to automate testing of OpenWrt routers and other devices.  When used with continuous integration servers, such as [Jenkins](https://jenkins-ci.org/), boardfarm tests new code commits and nightly builds by flashing software or ipk files onto devices and running tests.

Tests are located in individual files in the "tests" directory. Tests include networking tests (e.g. ping, iperf, netperf), functionality tests (e.g. restart firewall or daemons), wifi tests, ipv4 and ipv6 tests, stability tests, and more.

The simplest tests consist of commands to type expected output. These tests use [Pexpect](https://pexpect.readthedocs.org/en/latest/) to connect to devices and type commands. Examples and explanations of tests are shown later in this document.

Test suites are located in `testsuites.cfg` and are simply lists of test names.  Results of running a test suite are stored in a nicely formated html file that can be emailed to interested parties or sent to a database.

Software Setup
--------------

If you are a Linux user, and wish to run and/or develop tests, please clone this repository and then install needed libaries:
```shell
apt-get install python-pip curl
cd openwrt/
pip install -r requirements.txt
```

The file `config.py` is the main configuration. For example, it sets the location of the file that describes the available hardware.

Hardware Setup
--------------

To setup your own remotely-accessible boards, see BOARD_FARM.md in the docs directory. A "Board Farm" makes devices available over the network and this software connects to available devices to run tests. When a user is using a device, no one else can access or modify it.

Sample Commands
---------------

List available boards:
```shell
./bft -i
```

List available tests:
```shell
./bft -l
```

Connect to any available board of a certain type:
```shell
./bft -b ap135
```

Run a test case on a specific board:
```shell
./bft -n board01 -e MyTest
```

Run a test on any available board:
```shell
./bft -b ap148 -e MyTest
```

Flash some kernel and rootfs images to an available board, and run a specific test:
```shell
./bft -b ap135 -k http://10.0.0.8/~john/openwrt-ar71xx-generic-ap135-kernel.bin -r http://10.0.0.8/~john/openwrt-ar71xx-generic-ap135-rootfs-squashfs.bin -e MyTest
```

Flash some meta image to an available board:
```shell
./bft -b ap148 http://10.0.0.8/~john/nand-ipq806x-single.img -x flash_only
```

See all available command-line options:
```shell
./bft -h
```

Example Test Case 1
-------------------

The following test types a command on a device to check whether a component is installed or not. This test will pass if no exception is thrown.

```python
class AllJoynInstalled(rootfs_boot.RootFSBootTest):
    '''AllJoyn package is installed.'''
    def runTest(self):
        board.sendline('opkg info alljoyn')
        board.expect('Package: alljoyn', timeout=4)
        board.expect('ok installed')
        board.expect(prompt)
```

* `AllJoynInstalled` : A unique name for your test case.
* `'''AllJoyn package is installed.'''` : A one sentence description of your test.
* `sendline()` : types a command on a device.
* `expect()` : string or regular expression to search for in the output from the device.  If no match is seen within 30 seconds, throw an exeption (the test case then fails).  Change search time with the `timeout` argument.
* `prompt` : A regular expression that matches the prompt of openwrt and linux prompts.

Example Test Case 2
-------------------

"Regular Expressions" are a very powerful way of parsing and making sense of text output.  This example checks memory use on the device by using regular expressions and "capture groups".

```python
class MemoryUse(rootfs_boot.RootFSBootTest):
    '''Checked memory use.'''
    def runTest(self):
        board.sendline('cat /proc/meminfo')
        board.expect('MemTotal:\s+(\d+) kB', timeout=5)
        mem_total = int(board.match.group(1))
        board.expect('MemFree:\s+(\d+) kB')
        mem_free = int(board.match.group(1))
        board.expect(prompt)
        mem_used = mem_total - mem_free
        self.result_message = 'Used memory: %s MB. Free memory: %s MB.' % (mem_used/1024, mem_free/1024)
```

* `/proc/meminfo` : This is a file that contains information about memory use in linux. Each line contains a name, a value and a unit:

```bash
root@OpenWrt:/# cat /proc/meminfo
MemTotal:         126372 kB
MemFree:           35720 kB
Buffers:               0 kB
Cached:            23056 kB
SwapCached:            0 kB
Active:            45164 kB
Inactive:          10336 kB
```
* `'MemTotal:\s+(\d+) kB'` : This regular expression looks for the string `"MemTotal:"`, followed by one or more spaces, followed by one or more digits, followed by the string `" kB"`. The paretheses are special, because putting them around something, such as `(\d+)`, creates a capture group.  Every pair of paretheses in a regular expression is a new capture group.
* `board.match.group(1)` : This returns the string within the first capture group. In this case, it is one or more digits, e.g. `"126372"`.

Example Test Case 3
-------------------

Other devices are availble for use. In the case of routers there is at least a device connected to both a LAN port and a WAN port. Commands can be sent do these devices by using `lan.sendline()` and `wan.sendline()`.

```python
class iPerfTest(rootfs_boot.RootFSBootTest):
    '''iPerf from LAN to WAN'''
    def runTest(self):
        wan.sendline('iperf -s > /dev/null &')
        wan.expect(prompt)
        lan.sendline('iperf -t 50 -P 2 -c 192.168.0.1')
        lan.expect('Client connecting to')
        lan.expect(prompt, timeout=60)
        wan.sendline('killall -9 iperf')
        wan.expect(prompt)
    def recover(self):
        lan.sendcontrol('c')
```

* `wan.sendline('iperf -s > /dev/null &')` : This runs the iperf server command on the device connected to the WAN port.
* `lan.sendline('iperf -t 50 -P 2 -c 192.168.0.1')` : This runs the iperf client command on the device connected to the LAN port.
* `recover` : This function only runs if an uncaught exception is thrown within `runTest`.
* `lan.sendcontrol('c')` : Type CTRL-C on the device connected to the LAN port. Since the iperf client command can fail or hang the command prompt, putting this in the `recover` fuction is a good safety measure to prevent hanging the prompt and interfering with tests that follow.

Test Suites
-----------

A test suite is a list of test cases. Several are already defined in in the file `testsuites.cfg`. For example:

```
[basic]
RootFSBootTest
OpenwrtVersion
OpkgList
KernelModules
MemoryUse
InterfacesShow
LanDevPingRouter
RouterPingWanDev
LanDevPingWanDev
```

Optionally, test suite may reference (using `@`) any other previously defined test suites to include all the test cases it contains. For example:
```
[basic-offline]
RootFSBootTest
OpenwrtVersion
OpkgList
KernelModules
MemoryUse
InterfacesShow

[basic]
@basic-offline
LanDevPingRouter
RouterPingWanDev
LanDevPingWanDev
```

To run a test suite on an any available board of type "ap148" simply type:

```shell
./bft --testsuite basic -b ap148
```

Test Results
------------

A test can finish in one of three states: PASS, FAIL, or SKIP.

If an uncaught exception is thrown (such as by `board.expect('something')`), then the test is marked as a FAIL - otherwise it is marked as a PASS.

A result of SKIP is a special case. Tests can check for certain conditions - like check that a component is installed - and leave the test if those conditions are not met. An example:

```python
class SambaPerf(vfat_perf.VFatPerf):
    def runTest(self):
        try:
            board.sendline('opkg list | grep samba')
            board.expect('samba.*- .*\r\n')
        except:
            self.skipTest("Samba not installed.")
```

General Guidelines for Automated Tests
--------------------------------------

The best automated tests share a few qualities:

* They are short - Typically 5 to 50 lines of code.
* They contain little logic - Tests should be less complicated than the things they are testing.
* They are robust - Tests should be more stable than the things they are testing.
* They are easy to read - Tests should follow the [PEP8 Style Guide](http://legacy.python.org/dev/peps/pep-0008/).

The goal is to catch bugs in the software being tested. It is an annoying distraction when tests themselves crash. Keep your tests simple so that others can easily figure them out.

Good luck and thanks for reading!
