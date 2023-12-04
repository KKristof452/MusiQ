import json
import logging
from pathlib import Path
from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from Utility.cyanite_utility import process_analysis_result, verify_signature
from Fastapi.song import Song, SongManager

from Utility.cyanite_api_methods import CyaniteMethods
from Utility.file_handler import file_management


logging.basicConfig(filename=Path("logs/MusiQ.log"), 
                    filemode="w", 
                    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
                    level=logging.INFO
                    )


song_manager = SongManager()

app = FastAPI()


class SongModel(BaseModel):
    id: str
    title: str
    genre: list = []
    bpm: int = 0
    mood: list = []
    voice_gender: str = ""
    key: str = ""


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


@app.delete("/remove/{id}")
async def remove_from_queue(id: str):
    song_manager.remove(id)
    return song_manager.queue


@app.post("/set_priorities")
def prioritize_queue(priority: Annotated[str, Query()] = "{}"):
    try:
        priority = json.loads(priority)
        if type(priority) is not dict:
            raise HTTPException(status_code=400, detail="Query must be a valid dictionary.")
    except json.JSONDecodeError as ex:
        return {"Result": "Fail", "Message": f"'{ex.doc}' is not a valid JSON document."}
    except TypeError as ex:
        return {"Result": "Fail", "Message": f"{ex}"}
    
    if not priority:
        return {"Result": "No priority was set."}

    song_manager.reorder_queue(priority)
    
    return {"Result": "Priority was set.", "Priority": priority}


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
