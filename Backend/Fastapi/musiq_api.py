import json
import os
from pathlib import Path
from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, Query, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from Utility.cyanite_api_methods import CyaniteMethods
from Utility.file_handler import file_management, DATA_DIR


class Song():
    def __init__(self, id: str, title: str, filepath: Path, genre: str = "", bpm: int = 0, mood: str = "") -> None:
        self.id = id
        self.title = title
        self.filepath = filepath
        self.genre = genre
        self.bpm = bpm
        self.mood = mood

    def _to_dict(self):
        return {
            "id": self.id, 
            "title": self.title, 
            "filepath": str(self.filepath), 
            "genre": self.genre, 
            "bpm": self.bpm, 
            "mood": self.mood
        }


class SongManager():
    queue: list[Song] = []

    def __init__(self, semi_queue: list[Song] = []) -> None:
        SongManager.queue.extend(semi_queue)

    def add(music: Song):
        SongManager.queue.append(music)

    def remove(id: str):
        for music in SongManager.queue:
            if music.id == id:
                SongManager.queue.remove(music)
                return True
        return False


song_manager = SongManager()


app = FastAPI()


class SongModel(BaseModel):
    id: str
    title: str
    genre: str = ""
    bpm: int = 0
    mood: str = ""


class CyanitEvent(BaseModel):
    version: str | None = None
    resource: dict | None = None
    event: dict | None = None


@app.get("/que", response_model=list[SongModel])
async def show_queue():
    return SongManager.queue


@app.post("/add")
async def add_to_queue(uploaded_file: UploadFile):
    if not uploaded_file.filename.endswith(".mp3"):
        return {"Result": "Invalid file format"}
    
    filename, data = await file_management(uploaded_file)
    if not filename:
        return {"Result": "Fail"}
    title = filename.removesuffix(".mp3")
    id = await CyaniteMethods.file_upload(uploaded_file, title, data)

    new_song = Song(id, title, Path(DATA_DIR, filename))
    SongManager.add(new_song)
    
    return {"Result": "Success", "Queue": SongManager.queue}


@app.get("/queue_json")
async def get_queue_json():
    songs = []
    for song in SongManager.queue:
        songs.append(json.dumps(song._to_dict()))
    return songs


@app.post("/cyanite_event")
async def cyanite_event(event: Annotated[CyanitEvent | None, Body()] = None):
    if event:
        print(event)
        return{"Result": "Success", "event": event}
    return {}
