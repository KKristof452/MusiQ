import json
import os
from pathlib import Path


OBJ_DIR = Path("./Data/Objects")


class Song():
    def __init__(self, id: str, title: str, filepath: str, genre: str = "", bpm: int = 0, mood: str = "") -> None:
        self.id = id
        self.title = title
        self.filepath = filepath
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
                with open(Path(dirpath, filename), "r") as json_file:
                    loaded_song = Song(**json.load(json_file))
                    self.__queue.append(loaded_song)

    def add(self, song: Song):
        self.__queue.append(song)

        with open(Path(OBJ_DIR, f"{len(self.__queue)}_{song.title}.json"), "w") as json_file:
            json.dump(song.__dict__, json_file)

        return self.__queue

    def remove(self, id: str):
        for music in self.__queue:
            if music.id == id:
                self.__queue.remove(music)
                return True, self.__queue
            
        return False, self.__queue

    @property
    def queue(self):
        return self.__queue
    