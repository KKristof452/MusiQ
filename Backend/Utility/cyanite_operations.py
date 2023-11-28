import hashlib
import hmac


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


def verify_signature(secret_key, payload, signature):
    # Create a new HMAC object using the secret key and the payload
    hmac_obj = hmac.new(secret_key.encode(), payload, hashlib.sha512)
    # Generate the HMAC signature
    generated_signature = hmac_obj.hexdigest()
    # Compare the generated signature with the received signature
    return hmac.compare_digest(generated_signature, signature)
