import os
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import aiofiles

from Fastapi.cyanite_api_methods import CyaniteMethods


class Music():
    
    def __init__(self, title: str, genre: str = "", music: UploadFile = None) -> None:
        self.title = title
        self.genre = genre
        self.music = music


class Queue():

    def __init__(self, que: list[Music] = []) -> None:
        self.que: list[Music] = que


que = Queue([Music("Ready To Fly", "Pop"), Music("Stayin Alive", "Old But Gold")])

app = FastAPI()

class MusicModel(BaseModel):
    title: str
    genre: str = ""
    music: UploadFile | None = None


@app.get("/que", response_model=list[MusicModel])
async def show_queue():
    return [Music("Ready To Fly", "Pop"), Music("Stayin Alive", "Old But Gold")]

@app.post("/add")
async def add_to_queue(uploaded_file: UploadFile):
    for _, _, filenames in os.walk(Path("./Data")):
        existing_files = filenames
    if uploaded_file.filename in existing_files:
        return {"Result": "File already exists"}
    
    async with aiofiles.open(f"./Data/{uploaded_file.filename}", "wb") as out_file:
        song = await uploaded_file.read()
        await out_file.write(song)

    await CyaniteMethods.file_upload(uploaded_file, song)
    
    return {"Result": "Ok"}
