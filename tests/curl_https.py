import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class CurlSSLGood(rootfs_boot.RootFSBootTest):
    '''Curl can access https and verify signature.'''
    def runTest(self):
        board.sendline('\n')
        board.expect(prompt)
        board.sendline('opkg install ca-certificates')
        board.expect(prompt)
        checks = [ 
                   'https://sha256.badssl.com/',
                   'https://1000-sans.badssl.com/',
                   'https://mozilla-modern.badssl.com/',
                   'https://dh2048.badssl.com/',
                   'https://hsts.badssl.com/',
                   'https://upgrade.badssl.com/',
                   'https://preloaded-hsts.badssl.com/',
                 ]
        for check in checks:
            board.sendline('curl ' + check)
            board.expect('<!DOCTYPE html>')
            board.expect(prompt)
            print '\n\nCurl downloaded ' + check + ' as expected\n'

class CurlSSLBad(rootfs_boot.RootFSBootTest):
    '''Curl can't access https with bad signature.'''
    def runTest(self):
        board.sendline('\n')
        board.expect(prompt)
        board.sendline('opkg install ca-certificates')
        board.expect(prompt)
        checks = [
                   ('https://expired.badssl.com/', 'certificate has expired'),
                   ('https://wrong.host.badssl.com/', 'no alternative certificate subject name matches target host name'),
                   ('https://subdomain.preloaded-hsts.badssl.com/', 'no alternative certificate subject name matches target host name'),
                   ('https://self-signed.badssl.com/', 'unable to get local issuer certificate'),
                   ('https://superfish.badssl.com/', 'unable to get local issuer certificate'),
                   ('https://edellroot.badssl.com/', 'unable to get local issuer certificate'),
                   ('https://dsdtestprovider.badssl.com/', 'unable to get local issuer certificate'),
                   ('https://incomplete-chain.badssl.com/', 'unable to get local issuer certificate'),
                 ]
        for check in checks:
            board.sendline('curl ' + check[0])
            board.expect(check[1])
            board.expect(prompt)
            print '\n\nCurl refused to download ' + check[0] + ' as expected\n'
 
