import whisper
import os
import tempfile
from typing import Optional

from app.core.config import settings

# Global model instance
_model = None


def get_whisper_model():
    """
    Get or initialize the Whisper model
    """
    global _model
    if _model is None:
        print(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model


def transcribe_audio(audio_path: str, language: str = "tr") -> str:
    """
    Transcribe audio file using Whisper
    """
    model = get_whisper_model()
    
    # Set language code
    if language == "tr":
        language_code = "tr"
    else:
        language_code = "en"
    
    # Transcribe
    result = model.transcribe(
        audio_path, 
        language=language_code,
        fp16=False  # Set to True if GPU is available
    )
    
    return result["text"]