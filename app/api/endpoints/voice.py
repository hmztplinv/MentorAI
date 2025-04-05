from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os

from app.db.base import get_db
from app.schemas.message import ChatRequest, ChatResponse
from app.services.voice_service import transcribe_audio
from app.api.endpoints.chat import send_message

router = APIRouter()


@router.post("/transcribe", response_model=dict)
async def transcribe_voice(
    file: UploadFile = File(...),
    language: str = "tr",
    db: Session = Depends(get_db)
):
    """
    Transcribe uploaded audio file using Whisper
    """
    if not file.filename.endswith((".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported audio format. Please upload .wav, .mp3, .ogg, .flac, .m4a, or .webm files"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Transcribe the audio
        text = transcribe_audio(temp_file_path, language)
        
        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/send", response_model=ChatResponse)
async def send_voice_message(
    session_id: int,
    file: UploadFile = File(...),
    language: str = "tr",
    db: Session = Depends(get_db)
):
    """
    Transcribe audio and send as message in one step
    """
    # Transcribe the audio
    transcription_response = await transcribe_voice(file=file, language=language, db=db)
    
    # Forward to chat endpoint
    chat_request = ChatRequest(
        session_id=session_id,
        message=transcription_response["text"],
        is_voice=True
    )
    
    response = await send_message(chat_request=chat_request, db=db)
    return response