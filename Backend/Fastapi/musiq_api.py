import logging
from pathlib import Path
from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, Query, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from Fastapi.song import Song, SongManager

from Utility.cyanite_api_methods import CyaniteMethods
from Utility.file_handler import file_management, AUDIO_DIR


logging.basicConfig(filename=Path("logs/MusiQ.log"), 
                    filemode="w", 
                    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
                    level=logging.DEBUG
                    )


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
    return song_manager.queue


@app.post("/add")
async def add_to_queue(uploaded_file: UploadFile):
    if not uploaded_file.filename.endswith(".mp3"):
        return {"Result": "Invalid file format"}
    
    filename, data = await file_management(uploaded_file)
    if not filename:
        return {"Result": "Fail"}
    title = filename.removesuffix(".mp3")
    id = await CyaniteMethods.file_upload(uploaded_file, title, data)

    new_song = Song(id, title)
    song_manager.add(new_song)

    logging.info(f"New song added: {filename}")
    
    return {"Result": "Success", "Queue": song_manager.queue}


@app.delete("/remove_from_queue/{id}")
async def remove_from_queue(id: str):
    song_manager.remove(id)
    return song_manager.queue


@app.post("/cyanite_event")
async def cyanite_event(event: Annotated[CyanitEvent | None, Body()] = None):
    if event:
        print(event)
        return{"Result": "Success", "event": event}
    
    return {}
