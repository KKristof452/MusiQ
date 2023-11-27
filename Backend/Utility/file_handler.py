import json
import logging
import os
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from pydub import AudioSegment
import numpy as np


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


def __read_audio(file_name):
    audio = AudioSegment.from_mp3(file_name)
    # Normalize to the same frame rate and channels for consistent comparison
    audio = audio.set_frame_rate(44100).set_channels(1)
    return np.array(audio.get_array_of_samples())


def compare_audio_waveform(audio1: str | UploadFile, audio2: str | UploadFile):
    # Read the audio files
    audio1 = __read_audio(audio1)
    audio2 = __read_audio(audio2)

    # Check if the length of th two audio files are equal
    if len(audio1) != len(audio2):
        return False

    # Compare the waveforms
    difference = np.sum((audio1 - audio2) ** 2)

    if difference == 0:
        return True
    else:
        return False
