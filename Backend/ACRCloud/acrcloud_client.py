
import base64
import hashlib
import hmac
import time
import logging

import json
import requests
from acrcloud.acrcloud_extr_tool import create_fingerprint_by_filebuffer


class ACRCloudMethods:
    access_key = "aab0b39114320ce409d5162cbd1a596f"
    access_secret = "PimrrUxnq8HJ7xmhFsAnV6uqSAxvh9VMU6x84WLl"
    requrl = "https://identify-eu-west-1.acrcloud.com/v1/identify"

    http_method = "POST"
    http_uri = "/v1/identify"
    # default is "fingerprint", it's for recognizing fingerprint,
    # if you want to identify audio, please change data_type="audio"
    data_type = "fingerprint"
    signature_version = "1"
    timestamp = time.time()

    string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
    timestamp)

    sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'), 
                                     digestmod=hashlib.sha1).digest()).decode('ascii')

    def __song_identification(file):
        fingerprint = create_fingerprint_by_filebuffer(file, 10, 30, False, 0)

        files = [('sample', ('test.mp3', fingerprint, 'audio/mpeg'))]
        data = {'access_key': ACRCloudMethods.access_key,
                'sample_bytes': len(fingerprint),
                'timestamp': str(ACRCloudMethods.timestamp),
                'signature': ACRCloudMethods.sign,
                'data_type': ACRCloudMethods.data_type,
                'signature_version': ACRCloudMethods.signature_version}
        
        r = requests.post(ACRCloudMethods.requrl, files=files, data=data)
        r.encoding = "utf-8"
        result = json.loads(r.text)
        return result
    
    def get_song_metadata(file):
        filtered_metadata = []
        orig_metadata = ACRCloudMethods.__song_identification(file)
        logging.info(f"orig_metadata:\n{orig_metadata}\n")
        for metadata in orig_metadata.get("metadata").get("music"):
            filtered_metadata.append({
                "title": metadata.get("title", ""),
                "album": metadata.get("album", {}).get("name", ""),
                "artists": [x.get("name") for x in metadata.get("artists", [])],
                "release_date": metadata.get("release_date", "")
                })
            
        return filtered_metadata
        
