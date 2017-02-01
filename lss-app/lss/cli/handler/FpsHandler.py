import urllib2
import os
import time
import re
from cement.core.handler import CementBaseHandler


class FpsHandler(CementBaseHandler):
    class Meta:
        label = 'Fps'
        description = 'This is to calculate FPS of stream'

    def __init__(self):
        self.fps = 0

    def calculeteFrameRate(self, args):
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        i=0
        start_time = time.time()
        req = urllib2.urlopen(args.url)
        print req.headers
        data_read = ''
        for chunk in req:
            data_read += chunk
            end_time = time.time()
            f = chunk.count('--myboundary')
            self.fps = self.fps + f
            if f>0:
                m = re.search(r'\W*Prysm-SequenceNumber: (\d+)', data_read)
                if m:
                    i=m.group(1)
                with open('tmp/' + str(i) + '.txt','a') as f:
                    f.write(data_read)
                    data_read = ''
                if end_time - start_time > int(args.interval):
                    print("Frame rate is {0}".format(self.fps * 1.0/int(args.interval)))
                    self.fps=0
                    start_time = end_time
