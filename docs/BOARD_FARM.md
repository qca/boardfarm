Board Farm
----------

A "Board Farm" is simply one or more boards (such as routers) connected to a network so that they are remotely accessable to testers or developers.

There are many benefits to building a board farm, including:

* Users can simply ssh/telnet over the network to use boards and devices connected to those boards.
* It frees users from having to physically connect wires or setup their own non-standard setup at their desk or elsewhere.
* Automated build systems can run tests on boards when a new build is compiled.

This document describes how to physically setup a Board Farm.


Minimal Example
---------------

![Image of Router, Network-controlled power switch, and computers](https://raw.githubusercontent.com/qca/boardfarm/master/docs/Simple_Board_Farm.jpg "Minimal Test Station")

This is one router test station. The black cylinder in the center is 1 router. The web-controlled power switch in the upper-left allows devices to be remotely power-cycled. White Ethernet cables connect devices to the local network. Three, small computers run Debian Linux. One computer is connected to the router's LAN, one computer is connected to the router's WAN, and the last computer is connected to the Serial Console of the router.

Ingredients
-----------

The smallest board farm requires:

* 1 board (e.g. a router).
* 1 console server. (or local serial connection (see below)
* 1 network-controlled power switch.
* 2 computers each with 2 network interfaces - Preferably Debian Linux. Can be small Raspberry PI computers, or more powerful computers (to acheive gigabit throughput).
* Several ethernet cables, and serial connector for the board.

A console server allows users to ssh/telnet to it and gain console access to boards.  They can be made for free using any Linux computer by using libraries such as [ser2net]([http://sourceforge.net/projects/ser2net/).  Console servers can also be purchased: there are open-source, linux-based console servers available from [OpenGear](http://opengear.com/products/cm4100-console-server).

Network-controlled power switches allow users to turn on and off power outlets over the network.  They can be purchased from various places with different amounts of features typically for a few hundred USD/EUR.

Physical Connections
--------------------

Here we assume the "board" you wish to test is a router.

Ethernet connections:

    Local Network <---> eth0-Computer-eth1 <---> LAN-Router-WAN <---> eth1-Computer-eth0 <---> Local Network

Serial Connections:

    Console server <---> Router

Power Connections: Only the router needs to be plugged into the Network-controlled power switch.  All others can be connected to standard power outlets.

Setup of the Computers
----------------------

The computers connected to the boards need a few libraries:

    apt-get install -y openssh-server openssh-client sudo tftp-hpa tftpd-hpa curl socat tinyproxy iperf

Both computers need 2 network interfaces:

* `eth0` connected to the local area network
* `eth1` connected to the board

The routing table on the computers needs to be setup such that traffic to the local area network goes to eth0, while all other traffic goes through eth1, through the router.

The routing table on the LAN-side computer:

    # route -n
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    0.0.0.0         192.168.1.1     0.0.0.0         UG    0      0        0 eth1
    10.0.0.0        0.0.0.0         255.0.0.0       U     0      0        0 eth0
    192.168.1.0     0.0.0.0         255.255.255.0   U     0      0        0 eth1

The routing table on the WAN-side computer:

    # route -n
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    0.0.0.0         10.0.0.1        0.0.0.0         UG    0      0        0 eth0
    10.0.0.0        0.0.0.0         255.0.0.0       U     0      0        0 eth0
    192.168.0.0     0.0.0.0         255.255.255.0   U     0      0        0 eth1

After setting up the computers one should be able to ssh to the computers and run, for example, `iperf` throughput test through the router.

Board Farm Config File
----------------------
All routers in a board farm need an entry in the boardfarm_config.json file like so:

```json
  {
    "<name>": {
      "board_type": "<model>",
      "conn_cmd": "telnet <server> <port>",
      "lan_device": "10.0.0.107",
      "wan_device": "bf-vm-YY.something.com",
      "powerip": "<powerserver>",
      "powerport": "<outlet>"
    }
  }
```

Where:
* `name` is any unique name at all
* `model` is a descriptive model name
* `conn_cmd` is the command to run to connect to the board
* `lan_device` and `wan_device` are the devices connected to the board (must have ssh server)
* `powerip` and `powerport` are the network-control power unit and outlet to reset the board

Using a local serial port (i.e. no console server)
----------------------
Boardfarm also supports using a local serial port. This is useful when you have
your PC connected directly to the device under test. To do so, you'd modify your
board farm JSON config file as follows:

* add `"connection_type": "local_serial"` to your board entry
* replace the current `conn_cmd` element with with `"conn_cmd": "cu -l <port> -s <speed>"` in your board entry

Where:
* `port` is the path to your serial port. One example would be `/dev/ttyUSB0`.
* `speed` is the baud rate for the serial port connection. One example would be `115200`.

Additionally, you must install the `cu` program on your connecting computer. If running,
a Debian based system, you would run:
```
apt-get install cu
```
If running openSUSE, you would run:
```
zypper in uucp
```
