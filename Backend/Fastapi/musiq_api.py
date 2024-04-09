from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path
from typing import Annotated
from uuid import uuid4
from secrets import token_bytes

from fastapi import Body, Depends, FastAPI, Form, HTTPException, Query, Request, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from ACRCloud.acrcloud_client import ACRCloudMethods
from jose import JWTError, jwt

from Cyanite.cyanite_utility import process_analysis_result, verify_signature
from Fastapi.song import Song, SongManager
from Cyanite.cyanite_client import CyaniteMethods
from Utility.file_handler import file_management
from Fastapi.musiq_auth import User, get_current_admin_user, get_current_user, authenticate_admin_user, \
    admin_users, standard_users, create_access_token, Token, ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES, STANDARD_ACCESS_TOKEN_EXPIRE_MINUTES


logging.basicConfig(filename=Path("logs/MusiQ.log"), 
                    filemode="w", 
                    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
                    level=logging.INFO
                    )


class SongModel(BaseModel):
    id: str
    title: str
    genre: list = []
    bpm: int = 0
    mood: list = []
    voice_gender: str = ""
    key: str = ""


song_manager = SongManager()

app = FastAPI()


@app.post("/admin_token")
async def login_for_admin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_admin_user(admin_users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@app.post("/standard_token")
async def one_time_login(nickname: Annotated[str, Form()]):
    if nickname in admin_users or nickname in standard_users:
        raise HTTPException(
            status_code=400,
            detail="Nickname already in use"
        )
    access_token_expires = timedelta(minutes=STANDARD_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": nickname}, expires_delta=access_token_expires)
    standard_users[nickname] = {"username": nickname}
    return Token(access_token=access_token, token_type="bearer")


@app.get("/queue/list", response_model=list[SongModel])
async def show_queue():
    return song_manager.queue


@app.post("/queue/add")
async def add_to_queue(uploaded_file: UploadFile):
    if not uploaded_file.filename.endswith(".mp3"):
        return {"Result": "Invalid file format"}
    
    file_data = await uploaded_file.read()
    filtered_metadata = ACRCloudMethods.get_song_metadata(file_data)
    logging.info(f"filtered_metadata:\n{filtered_metadata}\n")
    filename, data = await file_management(uploaded_file, file_data)
    if not filename:
        return {"Result": "Fail"}
    filename = filename.removesuffix(".mp3")

    unique_id = str(uuid4())
    metadata = filtered_metadata[0]
    title, artists = metadata.get("title"), metadata.get("artists")

    existing = song_manager.check_song_existence(title, artists)
    if not existing:
        cyanite_id = await CyaniteMethods.file_upload(uploaded_file, title, data)
        logging.info("Cyanite analysation started!")
        new_song = Song(unique_id, filename, title=title, artists=artists, cyanite_id=cyanite_id)
    else:
        logging.info("Song already in queue, skipping analysation!")
        new_song = Song(
            unique_id, filename, title=title, artists=artists, 
            voice_gender=existing.get("voice_gender"), genre=existing.get("genre"),
            mood=existing.get("mood"), bpm=existing.get("bpm"), key=existing.get("key")
        )

    song_manager.add(new_song)

    logging.info(f"New song added: {filename}, length of queue: {len(song_manager.queue)}")
    
    return {"Result": "Success", "Data": new_song, "Filtered metadata": filtered_metadata}


@app.delete("/queue/remove/{id}")
async def remove_from_queue(id: str, current_user: Annotated[User, Depends(get_current_admin_user)]):
    all_ids = [song.id for song in song_manager.queue]
    if id not in all_ids:
        return {"Result": "Fail", "Message": f"Song with id '{id}' not found!"}
    song_manager.remove(id)
    return {"Result": "Success", "Queue": song_manager.queue}


@app.post("/settings/{id}/metadata")
async def set_metadata(id: str, metadata: Annotated[str, Query()] = '{"title": "", "artists": []}'):
    try:
        metadata = json.loads(metadata)
        if type(metadata) is not dict:
            raise HTTPException(status_code=400, detail="Query must be a valid dictionary.")
    except json.JSONDecodeError as ex:
        return {"Result": "Fail", "Message": f"'{ex.doc}' is not a valid JSON document."}
    except TypeError as ex:
        return {"Result": "Fail", "Message": f"{ex}"}
    title = metadata.get("title")
    artists = metadata.get("artists")
    if title and artists:
        song = song_manager.song_by_id(id)
        song.title = title
        song.artists = artists
        return {"Result": "Success", "Title": title, "Artists": artists}
    return {"Result": "Fail", "Title": title, "Artists": artists}


@app.post("/settings/priorities")
def prioritize_queue(priority: Annotated[str, Query()] = "{}"):
    try:
        priority = json.loads(priority)
        if type(priority) is not dict:
            raise HTTPException(status_code=400, detail="Query must be a valid dictionary.")
    except json.JSONDecodeError as ex:
        return {"Result": "Fail", "Priority": {}, "Message": f"'{ex.doc}' is not a valid JSON document."}
    except TypeError as ex:
        return {"Result": "Fail", "Priority": {}, "Message": f"{ex}"}
    
    if not priority:
        return {"Result": "Fail", "Priority": {}, "Message": "No priority was set."}

    song_manager.reorder_queue(priority)
    
    return {"Result": "Success", "Priority": priority, "Message": "Priority was set."}


@app.post("/cyanite_event")
async def cyanite_event(request: Request):
    logging.info(f"webhook event received!")
    signature = request.headers.get("signature")
    if not signature:
        logging.info(f"--> Signature missing")
        raise HTTPException(status_code=400, detail="Signature missing")
    
    body = await request.body()
    if not await verify_signature(CyaniteMethods.webhook_secret, body, signature):
        logging.info("--> Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    data = await request.json()
    logging.info(f"--> data: {data}")
    resource = data.get("resource")
    event = data.get("event")

    if not (resource and event):
        logging.info("--> Invalid body")
        raise HTTPException(status_code=400, detail="Invalid body")
    if event.get("status") == "failed":
        logging.info("--> Analysis failed")
        return {"Result": "Fail"}
    if not event.get("type") == "AudioAnalysisV6":
        logging.info("--> Unexpected event type")
        return {"Result": "Fail", "Message": f"Unexpected event type: {event.get("type")}"}
    
    logging.info("Processing analysis result")
    await process_analysis_result(resource, song_manager)
    logging.info("Processing done")

    return {"Result": "Success"}


@app.get("/whoami")
async def who_am_i(current_user: Annotated[User, Depends(get_current_user)]):
    return {"current_user": current_user}

app.get("is_admin")
async def is_admin(current_user: Annotated[User, Depends(get_current_admin_user)]):
    if current_user:
        return {"is_admin": True}
    return {"is_admin": False}
