class CyaniteQueries():
    file_upload_request = """
        mutation FileUploadRequestMutation {
            fileUploadRequest {
                # the id will be used for creating the library track from the file upload
                id
                # the uploadUrl specifies where we need to upload the file to
                uploadUrl
            }
        }
    """

    library_track_creation = """
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

    


