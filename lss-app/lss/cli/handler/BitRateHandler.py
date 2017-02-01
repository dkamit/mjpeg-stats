import urllib2
import time
from cement.core.handler import CementBaseHandler


class BitRateHandler(CementBaseHandler):
    class Meta:
        label = 'BitRate'
        description = 'This is to calculate Bitrate of stream'

    def __init__(self):
        self.read_bytes = 0

    def calculeteBitRate(self, args):
        start_time = time.time()
        req = urllib2.urlopen(args.url)
        print req.headers
        for chunk in req:
            end_time = time.time()
            self.read_bytes = self.read_bytes + len(chunk)
            if (end_time - start_time) >= int(args.interval):
                print("BitRate is {0}".format((self.read_bytes * 8) / ( int(args.interval) * 1024.0 * 1024.0 )) + " Mbps")
                start_time = end_time
                self.read_bytes = 0
