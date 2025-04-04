# tests/test_whisper.py dosyasını güncelle
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.voice_service import transcribe_audio
import wave  # wav dosyası bilgilerini okumak için

def create_test_wav_if_not_exists(filepath, duration=1.0, framerate=16000):
    """Eğer test ses dosyası yoksa oluştur"""
    if os.path.exists(filepath):
        return
    
    # Klasörü oluştur
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Boş bir wav dosyası oluştur
    nframes = int(duration * framerate)
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(framerate)
        wf.setnframes(nframes)
        wf.writeframes(b'\x00' * nframes * 2)  # Sessiz ses
    
    print(f"Test ses dosyası oluşturuldu: {filepath}")

def test_whisper():
    """
    Whisper ses tanıma özelliğini test eder
    """
    print("Mevcut çalışma dizini:", os.getcwd())
    
    print("Whisper Ses Tanıma Testi Başlatılıyor...")
    
    # Test ses dosyaları
    test_files = [
        {"path": "tests/audio/turkish_sample.wav", "language": "tr"},
        {"path": "tests/audio/english_sample.wav", "language": "en"}
    ]
    
    # Test dosyalarını oluştur
    for test in test_files:
        create_test_wav_if_not_exists(test["path"])
        print(f"Ses dosyası mutlak yolu: {os.path.abspath(test['path'])}")
        print(f"Dosya var mı?: {os.path.exists(test['path'])}")
    
    for test in test_files:
        print(f"\nSes dosyası test ediliyor: {test['path']}, Dil: {test['language']}")
        try:
            transcript = transcribe_audio(test["path"], test["language"])
            print(f"Çevrilen metin: {transcript}")
        except Exception as e:
            print(f"Hata: {str(e)}")
    
    print("\nTest tamamlandı!")

if __name__ == "__main__":
    test_whisper()