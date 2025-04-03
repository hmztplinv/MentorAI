import sys
import os
import time
import uuid
# Projenin ana dizinini path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import SessionLocal
from app.services.ai_service import generate_ai_response, check_for_crisis
from app.services.session_service import create_session
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.schemas.session import SessionCreate

def test_ai_service():
    """
    AI servisinin Ollama ile entegrasyonunu test eder
    """
    print("AI Servisi Testi Başlatılıyor...")
    
    # Veritabanı bağlantısı oluştur
    db = SessionLocal()
    
    try:
        # Test kullanıcısı oluştur
        test_user = UserCreate(
            username=f"test_user_{uuid.uuid4().hex[:6]}", # Benzersiz kullanıcı adı
            language="tr",
            preferred_therapy_approach="cbt"
        )
        db_user = create_user(db, test_user)
        print(f"Test kullanıcısı oluşturuldu: {db_user.username}")
        
        # Test oturumu oluştur
        test_session = SessionCreate(
            user_id=db_user.id,
            therapy_approach="cbt",
            title="Test Oturumu"
        )
        db_session = create_session(db, test_session)
        print(f"Test oturumu oluşturuldu: {db_session.title}")
        
        # Kriz algılama testi
        print("\nKriz Algılama Testi:")
        test_text = "Bugün kendimi çok kötü hissediyorum."
        crisis, lang = check_for_crisis(test_text)
        print(f"Metin: '{test_text}'")
        print(f"Kriz algılandı mı: {crisis}, Dil: {lang}")
        
        test_text = "İntihar etmeyi düşünüyorum."
        crisis, lang = check_for_crisis(test_text)
        print(f"Metin: '{test_text}'")
        print(f"Kriz algılandı mı: {crisis}, Dil: {lang}")
        
        # AI yanıt üretme testi
        print("\nAI Yanıt Üretme Testi:")
        test_prompt = "Merhaba, bugün biraz endişeliyim."
        
        print("Ollama API'sine istek gönderiliyor...")
        start_time = time.time()
        
        response = generate_ai_response(db, db_session.id)
        
        end_time = time.time()
        print(f"Yanıt süresi: {end_time - start_time:.2f} saniye")
        print(f"AI Yanıtı:\n{response}")
        
        print("\nTest tamamlandı!")
        
    except Exception as e:
        print(f"Test sırasında hata oluştu: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    test_ai_service()