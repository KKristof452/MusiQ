import logging
from fastapi import UploadFile
import requests

from Utility.cyanite_api_queries import CyaniteQueries


class CyaniteMethods():
    url = "https://api.cyanite.ai/graphql"
    access_token = """Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiSW50ZWdyYXRpb25BY2Nlc3NUb2tlbiIsInZlcnNpb24iOiIxLjAiLCJpbnRlZ3JhdGlvbklkIjo3OTAsInVzZXJJZCI6NjU0MjAsImFjY2Vzc1Rva2VuU2VjcmV0IjoiNWM1MjcwNzI0MmQ0NzMyZmNlMTg3MDYwNzdkM2Q5ZTkxN2NhYTVjMDljYzcwZWVmYmI3MTU2NGQ3Y2U0MjgwOSIsImlhdCI6MTY5OTI2NjQyNX0.-BIjbrqyjMHzv-bxLiadJT10nGCYWdGWq1lbxan4KIM"""

    async def file_upload(upload_file: UploadFile, title: str, data: bytes):
        response = await CyaniteMethods.__file_upload_request()
        file_upload_request = response.get("data").get("fileUploadRequest")
        id = file_upload_request.get("id")
        logging.debug(f"id: {id}\n")
        upload_url = file_upload_request.get("uploadUrl")
        logging.debug(f"upload_url: {upload_url}\n")

        file = {"file": (title, data)}
        header = {"Content-Type": "audio/mpeg"}
        # response = requests.put(url=upload_url, files=file, headers=header)
        # print(f"put response: {response.json}\n")

        # response = await CyaniteMethods.__library_track_creation(id, upload_file.filename)
        # print(f"lib_track_creation response: {response}\n")

        return id
    
    async def __file_upload_request():
        query = CyaniteQueries.file_upload_request
        variables = {}

        response = await CyaniteMethods.__request(query, variables)
        return response.json()
    
    async def __library_track_creation(upload_id: str, title: str):
        query = CyaniteQueries.library_track_creation
        variables = {"input": {"uploadId": upload_id, "title": title}}
        
        response = await CyaniteMethods.__request(query, variables)
        return response.json()

    async def __request(query, variables):
        return requests.post(url=CyaniteMethods.url, headers={"Authorization": CyaniteMethods.access_token}, json={"query": query, "variables": variables})
