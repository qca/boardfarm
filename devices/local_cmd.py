import pexpect

class LocalCmd():
    '''
    Set connection_type to local_cmd, ignores all output for now
    '''
    def __init__(self, device=None, conn_cmd=None, **kwargs):
        self.device = device
        self.conn_cmd = conn_cmd

    def connect(self):
        pexpect.spawn.__init__(self.device,
                           command='/bin/bash',
                           args=['-c', self.conn_cmd])

    def close():
        self.device.sendcontrol('c')
