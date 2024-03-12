#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from acrcloud.recognizer import ACRCloudRecognizer

filepath1 = 'debug/music/USA For Africa - We Are The World (HQ official Video).mp3'

if __name__ == '__main__':
    config = {
        #Replace "xxxxxxxx" below with your project's host, access_key and access_secret.
        'host': 'https://identify-eu-west-1.acrcloud.com/v1/identify',
        'access_key': 'aab0b39114320ce409d5162cbd1a596f', 
        'access_secret':'PimrrUxnq8HJ7xmhFsAnV6uqSAxvh9VMU6x84WLl',
        'timeout':10 # seconds
    }

    '''This module can recognize ACRCloud by most of audio/video file. 
        Audio: mp3, wav, m4a, flac, aac, amr, ape, ogg ...
        Video: mp4, mkv, wmv, flv, ts, avi ...'''
    re = ACRCloudRecognizer(config)

    #recognize by file path, and skip 0 seconds from from the beginning of sys.argv[1].
    print(re.recognize_by_file(filepath1, 0))

    buf = open(filepath1, 'rb').read()
    #recognize by file_audio_buffer that read from file path, and skip 0 seconds from from the beginning of sys.argv[1].
    print(re.recognize_by_filebuffer(buf, 0))