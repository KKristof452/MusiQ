import json
import os
from pathlib import Path

from Utility.file_handler import AUDIO_DIR


OBJ_DIR = Path("./Data/Objects")


class Song():
    def __init__(
        self, 
        id: str, 
        filename: str, 
        title: str = "",
        artists: list = [],
        genre: list = [], 
        bpm: int = 0, 
        mood: list = [], 
        voice_gender: str = "",
        key: str = "",
        cyanite_id: str = "",
        audiopath: str = "", 
        jsonpath: str = ""
    ) -> None:
        self.id = id
        self.filename = filename
        self.title = title
        self.artists = artists
        self.genre = genre
        self.bpm = bpm
        self.mood = mood
        self.voice_gender = voice_gender
        self.key = key
        self.cyanite_id = cyanite_id
        self.audiopath = os.path.join(AUDIO_DIR, f"{filename}.mp3")
        self.jsonpath = os.path.join(OBJ_DIR, f"{filename}.json")


class SongManager():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self.__queue: list[Song] = []
        deserialization(self.__queue)

    def add(self, song: Song):
        self.__queue.append(song)
        serialization(song)
        return self.__queue

    def remove(self, id: str):
        song_to_remove = self.song_by_id(id)
        if not song_to_remove:
            return False, self.__queue
        self.__queue.remove(song_to_remove)
        os.unlink(song_to_remove.audiopath)
        os.unlink(song_to_remove.jsonpath)
        return True, self.__queue
    
    def song_by_id(self, id: str):
        for song in self.__queue:
            if song.id == id:
                return song
        return None
    
    def reorder_queue(self, criteria):
        # Using a custom sort function
        self.queue.sort(key=lambda song: self._calculate_match_score(song, criteria))
    
    def _calculate_match_score(self, song, criteria):
        def check_value(attribute, value):
            if isinstance(attribute, list):
                print(f"attr: {attribute}, type: {type(attribute)}")
                print(value in attribute)
                return value in attribute
            elif isinstance(attribute, str | int):
                print(f"attr: {attribute}, type: {type(attribute)}")
                print(attribute == value)
                return attribute == value
            
        score = 0
        for key, value in criteria.items():
            attribute = getattr(song, key)
            if check_value(attribute, value):
                score += 1
        return -score  # Negative score for descending sort

    @property
    def queue(self):
        return self.__queue
    

def serialization(song):
    with open(song.jsonpath, "w") as json_file:
        json.dump(song.__dict__, json_file)


def deserialization(queue):
    for dirpath, _, filenames in os.walk(OBJ_DIR):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue
            with open(os.path.join(dirpath, filename), "r") as json_file:
                loaded_song = Song(**json.load(json_file))
                queue.append(loaded_song)