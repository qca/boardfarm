import pexpect

class Ser2NetConnection():
    def __init__(self, device=None, conn_cmd=None, **kwargs):
        self.device = device
        self.conn_cmd = conn_cmd

    def connect(self):
        pexpect.spawn.__init__(self.device,
                               command='/bin/bash',
                               args=['-c', self.conn_cmd])

        try:
            result = self.device.expect(["assword:", "ser2net.*\r\n", "OpenGear Serial Server"])
        except pexpect.EOF as e:
            raise Exception("Board is in use (connection refused).")
        if result == 0:
            raise Exception("Password required and not supported")

    def close():
        self.device.sendline("~.")
