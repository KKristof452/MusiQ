import json
import math
import os
from pathlib import Path

from Utility.file_handler import AUDIO_DIR


OBJ_DIR = Path("./Data/Objects")


class Preferences():
    
    def __init__(self, artists=[], genre=[], min_bpm=0, max_bpm=0, mood=[], voice_gender=[], key=[]) -> None:
        self.artists = artists
        self.genre = genre
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.mood = mood
        self.voice_gender = voice_gender
        self.key = key


class Song():
    def __init__(
        self, 
        id: str, 
        filename: str, 
        user: str,
        title: str = "",
        artists: list = [],
        genre: list = [], 
        bpm: int = 0, 
        mood: list = [], 
        voice_gender: str = "",
        key: str = "",
        cyanite_id: str = "",
        audiopath: str = "", 
        jsonpath: str = "",
        fixed_position: bool = False
    ) -> None:
        self.id = id
        self.filename = filename
        self.user = user
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
        self.fixed_position = False


class SongManager():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self.__queue: list[Song] = []
        deserialization(self.__queue)
        self.preferences = Preferences()

    def add(self, song: Song):
        self.__queue.append(song)
        # TODO reorder queue by priorities
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
    
    def song_by_cyanite_id(self, cyanite_id: str):
        for song in self.__queue:
            if song.cyanite_id == cyanite_id:
                return song
            
    def check_song_existence(self, title, artists):
        for song in self.__queue:
            if (song.title, song.artists) == (title, artists):
                return song.__dict__
        return
    
    def reorder_queue(self):
        if self.preferences is None:
            return
        
        custom_positions = []
        for idx, song in enumerate(self.__queue):
            if song.fixed_position:
                custom_positions.append({idx: song})
        
        custom_positions.reverse()
        for song_position in custom_positions:
            for key, _ in song_position.items():
                self.__queue.pop(key)

        self.__queue.sort(key=lambda song: self._calculate_match_score(song))

        custom_positions.reverse()
        for song_position in custom_positions:
            for key, value in song_position.items():
                self.__queue.insert(key, value)
    
    def _calculate_match_score(self, song):
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
        for key, values in self.preferences.__dict__.items():
            if key == "min_bpm":
                if self.preferences.min_bpm <= song.bpm:
                    print("checking if bpm is in the given range")
                    print("score +1")
                    score += 1
                continue
            
            if key == "max_bpm":
                if self.preferences.max_bpm >= song.bpm:
                    print("checking if bpm is in the given range")
                    print("score +1")
                    score += 1
                continue

            attribute = getattr(song, key)
            print("check_value")
            for value in values:
                if check_value(attribute, value):
                    score += 1
                    print("score +1")
        return -score  # Negative score for descending sort

    def move_song(self, old_index: int, new_index: int):
        if old_index != new_index:
            song = self.__queue.pop(old_index)
            song.fixed_position = True
            self.__queue.insert(new_index, song)

    @property
    def queue(self):
        return self.__queue.copy()
    

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