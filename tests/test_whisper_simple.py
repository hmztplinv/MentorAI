import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import whisper

def test_whisper_direct():
    """Whisper'ı doğrudan test et"""
    print("Whisper doğrudan test ediliyor...")
    
    model = whisper.load_model("base")
    print("Model yüklendi")
    
    test_file = "test_audio.wav"
    import wave
    with wave.open(test_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b'\x00' * 16000 * 2)
    
    print(f"Test dosyası oluşturuldu: {os.path.abspath(test_file)}")
    
    try:
        result = model.transcribe(test_file)
        print(f"Transkripsiyon sonucu: {result['text']}")
    except Exception as e:
        print(f"Hata: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_whisper_direct()