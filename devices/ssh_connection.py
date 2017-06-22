import pexpect


class SshConnection:
    '''
        To use, set conn_cmd in your json to "ssh root@192.168.1.1 -i ~/.ssh/id_router_key""
        and set connection_type to "ssh"

        '''
    def __init__(self, device=None, conn_cmd=None, key_password='None', **kwargs):
        self.device = device
        self.conn_cmd = conn_cmd
        self.key_password = key_password

    def connect(self):
        pexpect.spawn.__init__(self.device,
                               command='/bin/bash',
                               args=['-c', self.conn_cmd])

        try:
            result = self.device.expect(["assword:", "passphrase"])
        except pexpect.EOF as e:
            raise Exception("Board is in use (connection refused).")
        if result == 0 or result == 1:
            self.device.sendline(self.key_password)
            prompt = ['root\\@.*:.*#', '/ # ', '@R7500:/# ']
            self.device.expect(prompt)

    def close(self):
        self.device.sendline('exit')
