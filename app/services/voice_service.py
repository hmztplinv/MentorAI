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
        try:
            import torch
            print(f"CUDA kullanılabilir: {torch.cuda.is_available()}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Kullanılan cihaz: {device}")
            _model = whisper.load_model(settings.WHISPER_MODEL, device=device)
            print("Whisper modeli başarıyla yüklendi!")
        except Exception as e:
            print(f"Whisper modeli yüklenirken hata: {e}")
            raise
    return _model


def transcribe_audio(audio_path: str, language: str = "tr") -> str:
    """
    Transcribe audio file using Whisper
    """
    model = get_whisper_model()
    
    
    import os
    absolute_path = os.path.abspath(audio_path)
    print(f"Kullanılacak mutlak dosya yolu: {absolute_path}")
    
    
    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {absolute_path}")
    
    
    file_size = os.path.getsize(absolute_path)
    print(f"Dosya boyutu: {file_size} bytes")
    if file_size == 0:
        raise ValueError(f"Ses dosyası boş: {absolute_path}")
    
    # Set language code
    if language == "tr":
        language_code = "tr"
    else:
        language_code = "en"
    
    try:
        # Transcribe
        result = model.transcribe(
            absolute_path,  
            language=language_code,
            fp16=False  
        )
        return result["text"]
    except Exception as e:
        print(f"Whisper transkripsiyon hatası: {str(e)}")
        import traceback
        print(f"Hata ayrıntıları: {traceback.format_exc()}")
        raise