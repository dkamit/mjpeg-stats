import urllib2
import time
import re
import os
import uuid
import sys
import json
import requests
from cement.core.handler import CementBaseHandler
import ConfigParser

class AllStatsHandler(CementBaseHandler):
    class Meta:
        label = 'all_stats'
        description = 'Calculate the stats of the stream'

    def __init__(self):
        self.read_bytes = 0
        self.fps = 0

    def printTo(self, file_name, app, message):
        with open(file_name,'a') as sf:
            sf.write(message + "\n")

    def derive_url(self, user, password, environment, cam_id):
        auth_url = "https://{0}.synthesize.com/api/v1/users/authenticate/{1}".format(environment, user)
        response = requests.post(auth_url, data='\'' + password + '\'', headers={'Content-Type': 'application/json'}).content
        parsed_json = json.loads(response)
        token = parsed_json['Payload']['Token']
        if token is None:
            print "Enter valid username and password"
            sys.exit(1)
        request_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ token}
        tuner_convert_url = "https://{0}.synthesize.com/streaming/api/v1/livestream/convert/channel/{1}".format(environment, cam_id)
        r = requests.get(tuner_convert_url, headers=request_headers)
        convertedId = json.loads(r.text)['convertedId']
        channel_url = "https://{0}.synthesize.com/streaming/api/v1/livestream/tuner/channel/{1}".format(environment, convertedId)
        r = json.loads(requests.get(channel_url, headers=request_headers).text)
        if r['streamURL'] is None:
            print "Enter a valid cam id"
            sys.exit(1)
        return "{0}&auth=Bearer%20{1}".format(r['streamURL'], r['token'])

    def get_quality_by_bitrate(self, configured_bitrate, bitrate):
        if configured_bitrate * 3 < bitrate:
            return 'High Quality Stream'
        elif configured_bitrate * 2 < bitrate:
            return 'Quality Stream'
        elif configured_bitrate * 1 < bitrate:
            return 'Acceptable Quality'
        else:
            return 'Low Quality'

    def get_quality_by_framerate(self, configured_fps, framerate, deviance):
        if (configured_fps - configured_fps * deviance/100 < framerate) and (configured_fps + configured_fps * deviance/100 > framerate):
            return 'Good frame rate'
        else:
            return 'Low frame rate'

    def calculate_stats(self, app):
        try:
            configured_fps=app.config.getint('lss','framerate')
        except ConfigParser.NoOptionError:
            print("Please update .lss.conf in your home directory for framerate configuration using default 10 for now")
            configured_fps = 10
        try:
            configured_bitrate=app.config.getint('lss','bitrate')
        except ConfigParser.NoOptionError:
            print("Please update .lss.conf in your home directory for bitrate configuration using default 3 for now")
            configured_bitrate=3

        try:
            deviance=app.config.getint('lss','deviance')
        except ConfigParser.NoOptionError:
            print("Please update .lss.conf in your home directory for deviance configuration using default 20 percent for now")
            deviance=20

        args = app.pargs
        headers = ['DATE', 'Bit Rate (Mbps)', 'Frame Rate(Fps)', 'Approx Latency(Milli Seconds)', 'Dropped Frame Count', 'Dropped Frames', 'Test Status']
        uid = str(uuid.uuid1())
        if not os.path.exists('tmp'):
            os.makedirs('tmp/')
        os.makedirs('tmp/' + str(uid))
        if not args.url:
            args.url = self.derive_url(args.user, args.password, args.environment, args.cam_id)
            print args.url
        start_time = time.time()
        time_to_exit = start_time + int(args.terminate)
        req = urllib2.urlopen(args.url)
        stats_file = 'tmp/' + uid + '/stats.tsv'
        print("Stats are collected in file {0}".format(stats_file))
        # print req.headers
        self.printTo(stats_file,app,"|".join(headers))
        data_read = ''
        i=0
        lat = 0
        frame_numbers = []
        for chunk in req:
            end_time = time.time()
            data_read += chunk
            self.read_bytes += len(chunk)
            f = chunk.count('--myboundary')
            self.fps = self.fps + f
            if f>0:
                m = re.search(r'\W*Prysm-SequenceNumber: (\d+)', data_read)
                if m:
                    i=m.group(1)
                    frame_numbers.append(int(i))
                m = re.search(r'\W*Prysm-Timestamp: (\d+)', data_read)
                if m:
                    lat += (time.time()*1000-int(m.group(1)))
                with open('tmp/'+uid+"/" + str(i) + '.txt','a') as f:
                    f.write(data_read)
                    data_read = ''
            if (end_time - start_time) >= int(args.interval):
                bitrate = (self.read_bytes * 8) / ( int(args.interval) * 1024.0 * 1024.0 )
                framerate = self.fps * 1.0/int(args.interval)
                frame_numbers.sort()
                start_frame = int(frame_numbers[0])
                end_frame = int(frame_numbers[-1])
                expected_frames = range(start_frame, end_frame + 1)
                dropped = list(set(expected_frames) - set(frame_numbers))
                avg_lat = lat/self.fps
                start_time = end_time
                self.read_bytes = 0
                self.fps = 0
                lat = 0
                frame_numbers = []

                bitrate_quality = self.get_quality_by_bitrate(configured_bitrate, bitrate)
                framerate_quality = self.get_quality_by_framerate(configured_fps, framerate, deviance)

                final_result = bitrate_quality + ' with ' + framerate_quality

                self.printTo(stats_file, app, "{0}|{1}|{2}|{3}|{4}|{5}".format(time.ctime(),bitrate, framerate,
                 avg_lat, len(dropped), dropped))

                app.render([[time.ctime(),bitrate,framerate,avg_lat,len(dropped), dropped, final_result]], headers = headers)
                if end_time >=time_to_exit:
                    print("Exiting ...")
                    sys.exit(0)
