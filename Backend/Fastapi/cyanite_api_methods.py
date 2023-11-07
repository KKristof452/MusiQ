from fastapi import UploadFile
import requests


class CyaniteMethods():
    url = "https://api.cyanite.ai/graphql"
    access_token = """Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiSW50ZWdyYXRpb25BY2Nlc3NUb2tlbiIsInZlcnNpb24iOiIxLjAiLCJpbnRlZ3JhdGlvbklkIjo3OTAsInVzZXJJZCI6NjU0MjAsImFjY2Vzc1Rva2VuU2VjcmV0IjoiNWM1MjcwNzI0MmQ0NzMyZmNlMTg3MDYwNzdkM2Q5ZTkxN2NhYTVjMDljYzcwZWVmYmI3MTU2NGQ3Y2U0MjgwOSIsImlhdCI6MTY5OTI2NjQyNX0.-BIjbrqyjMHzv-bxLiadJT10nGCYWdGWq1lbxan4KIM"""

    async def file_upload(upload_file: UploadFile, data: bytes):
        response = await CyaniteMethods.__file_upload_request()
        file_upload_request = response.get("data").get("fileUploadRequest")
        id = file_upload_request.get("id")
        print(f"id: {id}\n")
        upload_url = file_upload_request.get("uploadUrl")
        print(f"upload_url: {upload_url}\n")

        file = {"file": (upload_file.filename, data)}
        # print(f"file: {file}\n")
        header = {"Content-Type": "audio/mpeg"}
        response = requests.put(url=upload_url, files=file, headers=header)
        print(f"put response: {response.json}\n")

        r = await CyaniteMethods.__library_track_creation(id, upload_file.filename)
        print(f"lib_track_creation response: {r}\n")

    
    async def __file_upload_request():
        query = """
            mutation FileUploadRequestMutation {
                fileUploadRequest {
                    # the id will be used for creating the library track from the file upload
                    id
                    # the uploadUrl specifies where we need to upload the file to
                    uploadUrl
                }
            }
        """

        variables = {}

        response = await CyaniteMethods.__request(query, variables)
        return response.json()
    
    async def __library_track_creation(upload_id: str, title: str):
        query = """
            mutation LibraryTrackCreateMutation($input: LibraryTrackCreateInput!) {
                libraryTrackCreate(input: $input) {
                    __typename
                    ... on LibraryTrackCreateSuccess {
                        createdLibraryTrack {
                            id
                        }
                    }
                    ... on LibraryTrackCreateError {
                        code
                        message
                    }
                }
            }
        """

        variables = {"input": {"uploadId": upload_id, "title": title}}

        response = await CyaniteMethods.__request(query, variables)
        return response.json()


    async def __request(query, variables):
        return requests.post(url=CyaniteMethods.url, headers={"Authorization": CyaniteMethods.access_token}, json={"query": query, "variables": variables})
