import hashlib
import hmac
import logging

from Cyanite.cyanite_client import CyaniteMethods
from Fastapi.song import SongManager, serialization


async def verify_signature(secret_key, payload, signature):
    # Create a new HMAC object using the secret key and the payload
    hmac_obj = hmac.new(secret_key.encode(), payload, hashlib.sha512)
    # Generate the HMAC signature
    generated_signature = hmac_obj.hexdigest()
    # Compare the generated signature with the received signature
    return hmac.compare_digest(generated_signature, signature)


async def process_analysis_result(resource: dict, song_manager: SongManager):
    logging.info("Getting library track query...")

    id = resource.get("id")
    logging.info(f"id: {id}")
    response = await CyaniteMethods.library_track_query(id)
    logging.info(f"{response.get('data').get('libraryTrack').get('title')} analysis:")
    result = response.get("data").get("libraryTrack").get("audioAnalysisV6").get("result")

    song_by_id = song_manager.song_by_id(id)

    song_by_id.voice_gender = result.get("predominantVoiceGender")
    logging.info(f"voice_gender: {song_by_id.voice_gender} - {type(song_by_id.voice_gender)}")

    song_by_id.mood = result.get("moodTags")
    song_by_id.mood.extend(result.get("moodAdvancedTags"))
    logging.info(f"mood: {song_by_id.mood} - {type(song_by_id.mood)}")

    song_by_id.genre = result.get("genreTags")
    song_by_id.genre.extend(result.get("advancedGenreTags"))
    logging.info(f"genre: {song_by_id.genre} - {type(song_by_id.genre)}")

    song_by_id.bpm = result.get("bpmRangeAdjusted")
    logging.info(f"bpm: {song_by_id.bpm} - {type(song_by_id.bpm)}")

    song_by_id.key = result.get("keyPrediction").get("value")
    logging.info(f"key: {song_by_id.key} - {type(song_by_id.key)}")

    serialization(song_by_id)
