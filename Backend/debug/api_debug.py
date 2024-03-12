filename1 = "debug/music/3 Nights.mp3"
filename2 = "debug/music/Sub Focus Dimension  Ready To Fly Visualiser.mp3"
filename3 = "debug/music/Ready To Fly (Hardcore Mix).mp3"
filename4 = 'debug/music/asfdffss.mp3'
filename5 = 'debug/music/3_Nights_short.wav'
filename6 = 'debug/music/USA For Africa - We Are The World (HQ official Video).mp3'
filename7 = 'debug/music/Dusty Springfield - Son of a Preacher Man (Official Audio).mp3'
filename8 = 'debug/music/highway_to_hell.mp3'

# =========================ACRCLOUD==========================

#!/usr/bin/env python
#-*- coding:utf-8 -*-


"""
This is a demo program which implements ACRCloud Identify Protocol V1 with the third party library "requests".
We recomment you implement your own app with "requests" too.
You can install this python library by:
1) sudo easy_install requests 
2) sudo pip install requests
"""

import base64
import hashlib
import hmac
from io import BufferedReader, BytesIO
import os
import sys
import time
import soundfile as sf

import requests
import librosa
import json
from acrcloud.acrcloud_extr_tool import create_fingerprint_by_file

'''
Replace "###...###" below with your project's host, access_key and access_secret.
'''
access_key = "aab0b39114320ce409d5162cbd1a596f"
access_secret = "PimrrUxnq8HJ7xmhFsAnV6uqSAxvh9VMU6x84WLl"
requrl = "https://identify-eu-west-1.acrcloud.com/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"
# default is "fingerprint", it's for recognizing fingerprint,
# if you want to identify audio, please change data_type="audio"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
    timestamp)

sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),
                                 digestmod=hashlib.sha1).digest()).decode('ascii')

# suported file formats: mp3,wav,wma,amr,ogg, ape,acc,spx,m4a,mp4,FLAC, etc
# File size: < 1M , You'de better cut large file to small file, within 15 seconds data size is better

y, sr = librosa.load(filename6)
print(librosa.get_duration(y=y, sr=sr))
start_time, end_time = 10, 40
y_cut = y[int(start_time * sr):int(end_time * sr)]
output_file = "cut_audio.wav"
sf.write(output_file, y_cut, sr, format='wav')
with open("y_cut.wav", "wb") as audio:
    audio.write(y_cut)


# sample_bytes = sample.tobytes()
# byte_stream = BytesIO(sample_bytes)
# buffered_reader = BufferedReader(byte_stream)

# fingerprint = create_fingerprint_by_file(filename6, 10, 30, False, 0)
# print(f"fingerprint: {fingerprint}")

# f = open(filename5, "rb")
sample_bytes = os.path.getsize(output_file)

files = [
    ('sample', ('test.mp3', open(output_file, 'rb'), 'audio/mpeg'))
]

# files = [
#     ('sample', ('test.mp3', sample, 'audio/mpeg'))
# ]
data = {'access_key': access_key,
        'sample_bytes': sample_bytes,
        'timestamp': str(timestamp),
        'signature': sign,
        'data_type': data_type,
        "signature_version": signature_version}

r = requests.post(requrl, files=files, data=data)
r.encoding = "utf-8"
result = json.loads(r.text)
# print(result)


# =========================LIBROSA==========================

# import librosa
# import numpy as np
# from hashlib import sha256
# from fastdtw import fastdtw


# def fingerprint_audio(file_path):

#     y, sr = librosa.load(file_path)
#     print(f"y:\n{(y[500000:501000])}")
#     mfccs = librosa.feature.mfcc(y=y, sr=sr)

#     spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
#     spectral_flatness = librosa.feature.spectral_flatness(y=y)

#     mfccs_scaled = librosa.util.normalize(mfccs)

#     fingerprint = np.hstack((mfccs_scaled.flatten(), spectral_centroid.flatten(), spectral_flatness.flatten()))
#     print(f"\nfingerprint:\n{fingerprint}")

#     hash = sha256(fingerprint).hexdigest()
#     print(f"\nhash:\n{hash}")

#     return hash, fingerprint


# def compare_fingerprints(fingerpint1, fingerprint2):
#     distance, path = fastdtw(fingerpint1, fingerprint2)
#     return distance, path

# h1, f1 = fingerprint_audio(filename2)
# h2, f2 = fingerprint_audio(filename3)

# print(f"distance: {compare_fingerprints(f1, f1)[0]}")


