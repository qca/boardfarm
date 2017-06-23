import pexpect


class SshConnection:
    '''
        To use, set conn_cmd in your json to "ssh root@192.168.1.1 -i ~/.ssh/id_rsa""
        and set connection_type to "ssh"

        '''
    def __init__(self, device=None, conn_cmd=None, ssh_password='None', **kwargs):
        self.device = device
        self.conn_cmd = conn_cmd
        self.ssh_password = ssh_password

    def connect(self):
        pexpect.spawn.__init__(self.device,
                               command='/bin/bash',
                               args=['-c', self.conn_cmd])

        try:
            result = self.device.expect(["assword:", "passphrase"] + self.device.prompt)
        except pexpect.EOF as e:
            raise Exception("Board is in use (connection refused).")
        if result == 0 or result == 1:
            assert self.ssh_password is not None, "Please add ssh_password in your json configuration file."
            self.device.sendline(self.ssh_password)
            self.device.expect(self.device.prompt)

    def close(self):
        self.device.sendline('exit')
