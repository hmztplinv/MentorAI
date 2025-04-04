# tests/test_therapy_approaches.py dosyasını oluşturalım
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import SessionLocal
from app.services.ai_service import generate_ai_response
from app.services.session_service import create_session, update_session
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.schemas.session import SessionCreate, SessionUpdate
from app.core.config import settings
import uuid

def test_therapy_approaches():
    """
    Farklı terapi yaklaşımlarını test eder
    """
    print("Terapi Yaklaşımları Testi Başlatılıyor...")
    
    # Veritabanı bağlantısı oluştur
    db = SessionLocal()
    
    try:
        # Test kullanıcısı oluştur
        test_user = UserCreate(
            username=f"test_user_{uuid.uuid4().hex[:6]}", 
            language="tr",
        )
        db_user = create_user(db, test_user)
        print(f"Test kullanıcısı oluşturuldu: {db_user.username}")
        
        # Varsayılan oturumu oluştur
        test_session = SessionCreate(
            user_id=db_user.id,
            therapy_approach="cbt",
            title="Terapi Yaklaşımları Test Oturumu"
        )
        db_session = create_session(db, test_session)
        print(f"Test oturumu oluşturuldu: {db_session.title}")
        
        # Her terapi yaklaşımını test et
        for approach in settings.THERAPY_APPROACHES:
            print(f"\n{approach.upper()} yaklaşımı test ediliyor...")
            
            # Oturumu güncelle - terapi yaklaşımını değiştir
            session_update = SessionUpdate(therapy_approach=approach)
            updated_session = update_session(db, db_session.id, session_update)
            
            # Test cümlesi gönder ve yanıt al
            test_prompt = "Bugün kendimi biraz kaygılı hissediyorum, ne önerirsin?"
            response = generate_ai_response(db, db_session.id)
            
            print(f"Cevap: {response[:150]}...")
            
        print("\nTüm terapi yaklaşımları test edildi!")
        
    except Exception as e:
        print(f"Test sırasında hata oluştu: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    test_therapy_approaches()