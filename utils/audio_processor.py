import datetime

from fastapi import UploadFile
from runwisper import transcribe_audio_local
from core.config import settings
import os

def save_audio_file(file: UploadFile) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    
    return filepath

def transcribe_audio(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio file not found")
    return transcribe_audio_local(audio_path)