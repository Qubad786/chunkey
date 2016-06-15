#! usr/bin/env python

import os
import sys
import subprocess

"""
Encode streams of input -> output for HLS five stream video

NOTE: Just a test, so will need greater looking into

Generate master manifest, upload (easy, via boto) to output bucket

"""

'''
MANIFEST : 
https://s3.amazonaws.com/veda-testoutput/HLS_TEST/XXXXXXXX2015-V000700_.m3u8

#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=192000,RESOLUTION=320x180
OUTPUT_TEST/XXXXXXXX2015-V000700_.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=480x270
OUTPUT_TEST/XXXXXXXX2015-V000700_.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
OUTPUT_TEST/XXXXXXXX2015-V000700_.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720
OUTPUT_TEST/XXXXXXXX2015-V000700_.m3u8
'''

'''
ffmpeg command :

"-b:a 64k -ar 44100 -c:v libx264 -vf scale=1920:1080 -crf 18 -r 24 -g 72 
-f hls -hls_time 9 -hls_list_size 0 -s 1920x1080 
/Users/tiagorodriguez/Desktop/HLS_testbed/0/XXXXXXXX2015-V000700_0.m3u8",

'''

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import Settings

import util_functions



class HLS_Command():

    def __init__(self, mezz_file, **kwargs):
        self.settings = Settings()
        self.mezz_file = mezz_file

        self.encode_list = []
        self.video_id = kwargs.get(
            'video_id', mezz_file.split('/')[-1].split('.')[0]
            )
        self.video_root = os.path.join(self.settings.WORKDIR, self.video_id)


    def run(self):
        """
        Groom environ, make dirs
        """
        if not os.path.exists(self.settings.WORKDIR):
            os.mkdir(self.settings.WORKDIR)

        if not os.path.exists(self.video_root):
            os.mkdir(self.video_root)

        self._GENERATE()
        processed = self._EXECUTE()


    def _GENERATE(self):
        """
        Generate ffmpeg commands into array by use in transcode function

        """
        for name, profile in self.settings.TRANSCODE_PROFILES.iteritems():
            ffcommand = ['ffmpeg -y -i']
            ffcommand.append(self.mezz_file)

            """
            Add Audio
            """
            ffcommand.append("-b:a")
            ffcommand.append(profile['audio_depth'])
            ffcommand.append("-ar")
            ffcommand.append("44100")

            """
            Add codec
            """
            ffcommand.append("-c:v")
            ffcommand.append("libx264")
            
            """
            Add scaling / rate factor / framerate
            """
            ffcommand.append("-vf")
            ffcommand.append("scale=" + profile['scale'])
            ffcommand.append("-crf")
            ffcommand.append(profile['rate_factor'])
            ffcommand.append("-r")
            ffcommand.append(profile['fps'])
            ffcommand.append("-g")
            ffcommand.append("72")
            ffcommand.append("-f")
            """
            Add HLS Commands
            """
            ffcommand.append("hls")
            ffcommand.append("-hls_time")
            ffcommand.append(str(self.settings.HLS_TIME))
            ffcommand.append("-hls_list_size")
            ffcommand.append("0")
            ffcommand.append("-s")
            ffcommand.append(profile['scale'].replace(':', 'x'))

            """
            Add output files
            """
            if not os.path.exists(os.path.join(self.video_root, name)):
                os.mkdir(os.path.join(self.video_root, name))
            destination = os.path.join(self.video_root, name, self.video_id)
            destination += ".m3u8"

            ffcommand.append(destination)
            if len(ffcommand) > 0:

                self.encode_list.append(' '.join((ffcommand)))

        return None


    def _EXECUTE(self):
        for command in self.encode_list:

            files_array = [f for f in command.split(' ') if '/' in f]
            source_file = files_array[0]
            output_file = files_array[1]

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                shell=True, 
                universal_newlines=True
                )
            """ 
            get vid info, gen status
            """
            util_functions.status_bar(process=process)

            if not os.path.exists(output_file):
                return False

        return True










def main():

    HE = HLS_Command(mezz_file = '/Users/tiagorodriguez/Desktop/HLS_testbed/TEST_VIDEO/XXXXXXXXT114-V015600.mp4')
    HE.run()



if __name__ == '__main__':
    sys.exit(main())










