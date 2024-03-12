import logging
import os
from pathlib import Path
import aiofiles

from fastapi import UploadFile
from ACRCloud.acrcloud_client import ACRCloudMethods


AUDIO_DIR = Path("./Data/Audio")


async def file_management(file: UploadFile):
    filename = filename_determination(file.filename)
    logging.info(f"generated filename: {filename}")
    try:
        async with aiofiles.open(Path(AUDIO_DIR, filename), "wb") as out_file:
            data = await file.read()
            await out_file.write(data)
        return filename, data
    except Exception as ex:
        logging.error(f"file_management() - {ex}\n")
        return "", b"\x00"


def filename_determination(original_filename: str):
    filename = original_filename
    filename_exists = True
    iteration = 1
    while(filename_exists):
        filename_exists = check_filename_existence(filename)
        if filename_exists:
            logging.info(f"Filename collision: {filename}")
            filename = original_filename.removesuffix(".mp3") + f"_{iteration}.mp3"
        iteration += 1
    logging.info(f"Original filename: {original_filename} - Result filename: {filename}\n")
    return filename


def check_filename_existence(filename: str):
    for _, _, filenames in os.walk(AUDIO_DIR):
        if filename in filenames:
            return True
    return False
