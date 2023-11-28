import json
import os
from pathlib import Path

from Utility.file_handler import AUDIO_DIR


OBJ_DIR = Path("./Data/Objects")


class Song():
    def __init__(self, id: str, title: str, genre: str = "", bpm: int = 0, mood: str = "", audiopath: str = "", jsonpath: str = "") -> None:
        self.id = id
        self.title = title
        self.audiopath = os.path.join(AUDIO_DIR, f"{title}.mp3")
        self.jsonpath = os.path.join(OBJ_DIR, f"{title}.json")
        self.genre = genre
        self.bpm = bpm
        self.mood = mood


class SongManager():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self.__queue: list[Song] = []

        for dirpath, _, filenames in os.walk(OBJ_DIR):
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(dirpath, filename), "r") as json_file:
                    loaded_song = Song(**json.load(json_file))
                    self.__queue.append(loaded_song)

    def add(self, song: Song):
        self.__queue.append(song)

        with open(song.jsonpath, "w") as json_file:
            json.dump(song.__dict__, json_file)

        return self.__queue

    def remove(self, id: str):
        for song in self.__queue:
            if song.id == id:
                self.__queue.remove(song)
                os.unlink(song.audiopath)
                os.unlink(song.jsonpath)
                return True, self.__queue
             
        return False, self.__queue

    @property
    def queue(self):
        return self.__queue
    