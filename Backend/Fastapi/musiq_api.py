from datetime import timedelta
import json
import logging
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Body, Depends, FastAPI, Form, HTTPException, Query, Request, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from ACRCloud.acrcloud_client import ACRCloudMethods

from Cyanite.cyanite_utility import process_analysis_result, verify_signature
from Fastapi.song import Song, SongManager
from Cyanite.cyanite_client import CyaniteMethods
from Utility.file_handler import file_management
from Fastapi.musiq_auth import User, get_current_admin_user, get_current_user, authenticate_admin_user, \
    admin_users, standard_users, create_access_token, Token, ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES, STANDARD_ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(filename=Path("logs/MusiQ.log"), 
                    filemode="w", 
                    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
                    level=logging.INFO
                    )


class SongModel(BaseModel):
    id: str
    user: str
    title: str
    artists: list = []
    genre: list = []
    bpm: int = 0
    mood: list = []
    voice_gender: str = ""
    key: str = ""


song_manager = SongManager()

app = FastAPI()

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    print(standard_users)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/queue/list", response_model=list[SongModel])
async def show_queue():
    return song_manager.queue


@app.post("/queue/add")
async def add_to_queue(uploaded_file: UploadFile, current_user: Annotated[User, Depends(get_current_user)]):
    if not uploaded_file.filename.endswith(".mp3"):
        return {"Result": "Invalid file format"}
    
    file_data = await uploaded_file.read()
    filtered_metadata = ACRCloudMethods.get_song_metadata(file_data)
    logging.info(f"filtered_metadata:\n{filtered_metadata}\n")
    filename, data = await file_management(uploaded_file, file_data)
    if not filename:
        raise HTTPException(status_code=415, detail="The uploaded file is not mp3.")
    filename = filename.removesuffix(".mp3")

    unique_id = str(uuid4())
    metadata = filtered_metadata[0]
    title, artists = metadata.get("title"), metadata.get("artists")

    existing = song_manager.check_song_existence(title, artists)
    if not existing:
        cyanite_id = await CyaniteMethods.file_upload(uploaded_file, title, data)
        logging.info("Cyanite analysation started!")
        new_song = Song(id=unique_id, filename=filename, user=current_user.username, title=title, artists=artists, cyanite_id=cyanite_id)
    else:
        logging.info("Song already in queue, skipping analysation!")
        new_song = Song(
            id=unique_id, filename=filename, user=current_user.username, title=title, artists=artists, 
            voice_gender=existing.get("voice_gender"), genre=existing.get("genre"),
            mood=existing.get("mood"), bpm=existing.get("bpm"), key=existing.get("key")
        )

    song_manager.add(new_song)

    logging.info(f"New song added: {filename}, length of queue: {len(song_manager.queue)}")
    
    return {"Data": new_song, "Filtered metadata": filtered_metadata, "Queue": song_manager.queue}


@app.delete("/queue/{id}/remove")
async def remove_from_queue(id: str, current_user: Annotated[User, Depends(get_current_admin_user)]):
    all_ids = [song.id for song in song_manager.queue]
    if id not in all_ids:
        raise HTTPException(status_code=409, detail=f"Song with id '{id}' not found!")
    song_manager.remove(id)
    return song_manager.queue


@app.patch("/queue/{id}/move")
async def move(id: str, old_index: int, new_index: int, current_user: Annotated[User, Depends(get_current_admin_user)]):
    if id != song_manager.queue[old_index].id:
        raise HTTPException(status_code=409, detail="Song ID and index do not match.")
    song_manager.move_song(old_index, new_index)
    return song_manager.queue


@app.post("/queue/settings/{id}/metadata")
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


@app.post("/queue/settings/priorities")
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


@app.post("/queue/logout")
async def standard_logout(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_admin:
        return {"Result": "Success", "User": current_user}
    del standard_users[current_user.username]
    return {"Result": "Success", "User": current_user}


@app.get("/test")
async def who_am_i(current_user: Annotated[User, Depends(get_current_user)]):
    return {"Current_user": current_user}
