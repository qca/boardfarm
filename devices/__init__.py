'''

    This directory contains classes for connecting to and controlling
    devices over a network.

'''
board = None
lan = None
wan = None
wlan = None
wlan2g = None
wlan5g = None
prompt = None
def initialize_devices(configuration):
    # Init random global variables. To Do: clean these.
    global power_ip, power_outlet
    conn_cmd = configuration.board.get('conn_cmd')
    power_ip = configuration.board.get('powerip', None)
    power_outlet = configuration.board.get('powerport', None)
    # Init devices
    global board, lan, wan, wlan, wlan2g, wlan5g, prompt
    board = configuration.console
    lan = configuration.lan
    wan = configuration.wan
    wlan = configuration.wlan
    wlan2g = configuration.wlan2g
    wlan5g = configuration.wlan5g

    for device in configuration.devices:
        globals()[device] = getattr(configuration, device)

    board.root_type = None
    # Next few lines combines all the prompts into one list of unique prompts.
    # It lets test writers use "some_device.expect(prompt)"
    prompt = []
    for d in (board, lan, wan, wlan):
        prompt += getattr(d, "prompt", [])
    prompt = list(set(prompt))
