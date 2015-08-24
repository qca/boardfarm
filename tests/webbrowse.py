# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import random
import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class RandomWebBrowse(rootfs_boot.RootFSBootTest):
    '''Created light web traffic.'''
    def runTest(self):
        urls = ['www.amazon.com',
                'www.apple.com',
                'www.baidu.com',
                'www.bing.com',
                'www.cnn.com',
                'www.ebay.com',
                'www.facebook.com',
                'www.google.com',
                'www.imdb.com',
                'www.imgur.com',
                'www.instagram.com',
                'www.linkedin.com',
                'www.microsoft.com',
                'www.nbcnews.com',
                'www.netflix.com',
                'www.pinterest.com',
                'www.reddit.com',
                'www.twitter.com',
                'www.wikipedia.org',
                'www.yahoo.com',
                ]
        #urls = 2 * urls  # browse more
        random.shuffle(urls)
        user = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'
        cmd = "wget -Hp http://%(url)s " + \
              "-e robots=off " + \
              "-P /tmp/ " + \
              "-T 10 " + \
              "--header='Accept: text/html' " + \
              "-U '%(user)s' " + \
              "2>&1 | tail -1"
        for url in urls:
            print("\n%s" % url)
            tmp = cmd % {'url': url, 'user': user}
            lan.sendline(tmp)
            try:
                lan.expect('Downloaded:', timeout=20)
            except Exception:
                lan.sendcontrol('c')
            lan.expect(prompt)
            lan.sendline("rm -rf /tmp/*")
            lan.expect(prompt)
