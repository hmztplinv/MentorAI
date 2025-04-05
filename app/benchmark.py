#!/usr/bin/env python3
"""
AI Psikolog Uygulaması Performans Benchmark Aracı
Bu script, uygulamanın farklı bileşenlerinin performansını ölçer ve darboğazları tespit eder.
"""

import time
import asyncio
import requests
import json
import statistics
from contextlib import contextmanager
from typing import List, Dict, Any, Generator
import sys
import os

# Ana dizini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Uygulama modüllerini import et
from app.core.config import settings
from app.db.base import SessionLocal
from app.services.ai_service import generate_ai_response, get_conversation_context
from app.services.session_service import get_session
from app.services.user_service import get_user
from app.models.user import User
from app.models.session import Session
from app.models.message import Message

@contextmanager
def timer(description: str) -> Generator[None, None, float]:
    """İşlem süresini ölçen context manager"""
    start = time.time()
    yield
    elapsed_time = time.time() - start
    print(f"{description}: {elapsed_time:.4f} saniye")
    return elapsed_time

def test_direct_ollama_api():
    """Doğrudan Ollama API'sine istek göndererek temel performansı ölç"""
    print("\n=== Doğrudan Ollama API Testi ===")
    
    messages = [
        {"role": "system", "content": "Sen bir psikolojik danışmansın."},
        {"role": "user", "content": "Bugün kendimi çok stresli hissediyorum."}
    ]
    
    # İstek gövdesi
    request_body = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": 100,
            "temperature": 0.7
        }
    }
    
    times = []
    for i in range(3):
        with timer(f"Ollama API Çağrısı #{i+1}"):
            response = requests.post(
                f"{settings.OLLAMA_API_BASE}/chat",
                json=request_body,
                timeout=60
            )
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Sadece ilk 50 karakteri göster
                    print(f"Yanıt: {result.get('message', {}).get('content', '')[:50]}...")
                except Exception as e:
                    print(f"Yanıt işleme hatası: {str(e)}")
            else:
                print(f"API Hatası: {response.status_code} - {response.text}")
        
        times.append(time.time() - times[-1] if times else time.time())
        time.sleep(1)  # API'yi boğmamak için kısa bir bekleme
    
    if times:
        print(f"Ortalama Ollama API yanıt süresi: {statistics.mean(times):.4f} saniye")
        print(f"Medyan Ollama API yanıt süresi: {statistics.median(times):.4f} saniye")

def test_ai_service():
    """AI servisi fonksiyonlarının performansını ölç"""
    print("\n=== AI Servisi Testi ===")
    
    # Veritabanı oturumu oluştur
    db = SessionLocal()
    
    try:
        # Test için bir kullanıcı ve oturum bul veya oluştur
        user = db.query(User).first()
        if not user:
            print("Veritabanında kullanıcı bulunamadı. Lütfen önce bir kullanıcı oluşturun.")
            return
        
        session = db.query(Session).filter(Session.user_id == user.id).first()
        if not session:
            print("Veritabanında oturum bulunamadı. Lütfen önce bir oturum oluşturun.")
            return
        
        print(f"Test kullanıcısı: {user.username} (ID: {user.id})")
        print(f"Test oturumu: ID: {session.id}, Terapi yaklaşımı: {session.therapy_approach}")
        
        # Bağlam alma süresini ölç
        with timer("Konuşma bağlamı alma"):
            context = get_conversation_context(db, session_id=session.id)
        
        # AI yanıtı oluşturma süresini ölç
        times = []
        for i in range(3):
            with timer(f"AI yanıtı oluşturma #{i+1}"):
                response = generate_ai_response(db, session_id=session.id)
                print(f"Yanıt: {response[:50]}...")  # Sadece ilk 50 karakteri göster
            
            times.append(time.time() - times[-1] if times else time.time())
            time.sleep(1)  # API'yi boğmamak için kısa bir bekleme
        
        if times:
            print(f"Ortalama AI yanıt oluşturma süresi: {statistics.mean(times):.4f} saniye")
            print(f"Medyan AI yanıt oluşturma süresi: {statistics.median(times):.4f} saniye")
        
    finally:
        db.close()

def test_chat_endpoint():
    """Chat API endpoint'inin performansını ölç"""
    print("\n=== Chat API Endpoint Testi ===")
    
    # Veritabanı oturumu oluştur
    db = SessionLocal()
    
    try:
        # Test için bir kullanıcı ve oturum bul
        user = db.query(User).first()
        if not user:
            print("Veritabanında kullanıcı bulunamadı. Lütfen önce bir kullanıcı oluşturun.")
            return
        
        session = db.query(Session).filter(Session.user_id == user.id).first()
        if not session:
            print("Veritabanında oturum bulunamadı. Lütfen önce bir oturum oluşturun.")
            return
        
        # API isteği gövdesi
        request_body = {
            "session_id": session.id,
            "message": "Bugün kendimi biraz stresli hissediyorum, ne yapmamı önerirsin?",
            "is_voice": False
        }
        
        # API endpoint URL
        api_url = f"http://localhost:8000{settings.API_V1_STR}/chat/send"
        
        with timer("Chat API Endpoint Çağrısı"):
            response = requests.post(
                api_url,
                json=request_body,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Yanıt: {result.get('response', '')[:50]}...")  # Sadece ilk 50 karakteri göster
            else:
                print(f"API Hatası: {response.status_code} - {response.text}")
    
    finally:
        db.close()

def analyze_ai_service_code():
    """AI servisi kodunu analiz ederek potansiyel performans sorunlarını tespit et"""
    print("\n=== AI Servisi Kod Analizi ===")
    
    # Kontrol edilecek fonksiyonların listesi
    check_points = [
        "generate_ai_response fonksiyonu yüksek timeout değeri (45 saniye) kullanıyor",
        "Ollama API yapılandırmasında stream=False kullanılıyor (stream=True daha hızlı olabilir)",
        "Ollama API çağrısı için num_predict değeri (150) yüksek olabilir",
        "get_long_term_memory fonksiyonu, her seferinde bir koleksiyon oluşturmaya çalışıyor",
        "store_in_long_term_memory fonksiyonu, çok fazla işlem içeriyor"
    ]
    
    for point in check_points:
        print(f"- {point}")

def profile_memory_usage():
    """Bellek kullanımını profilleme"""
    try:
        import tracemalloc
        
        print("\n=== Bellek Kullanımı Profili ===")
        tracemalloc.start()
        
        # Veritabanı oturumu oluştur
        db = SessionLocal()
        
        try:
            # Var olan bir oturum bul
            session = db.query(Session).first()
            if not session:
                print("Veritabanında oturum bulunamadı. Bellek profili oluşturulamadı.")
                return
            
            # AI yanıtı oluştur ve bellek kullanımını ölç
            context = get_conversation_context(db, session_id=session.id)
            response = generate_ai_response(db, session_id=session.id)
            
            # Bellek istatistiklerini al
            current, peak = tracemalloc.get_traced_memory()
            print(f"Mevcut bellek kullanımı: {current / 1024**2:.2f} MB")
            print(f"En yüksek bellek kullanımı: {peak / 1024**2:.2f} MB")
            
            # En çok bellek kullanan 5 bloğu göster
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            print("En çok bellek kullanan 5 kod bloğu:")
            for stat in top_stats[:5]:
                print(f"{stat.count} blok: {stat.size / 1024:.1f} KB - {stat.traceback.format()[0]}")
        
        finally:
            db.close()
            tracemalloc.stop()
    
    except ImportError:
        print("tracemalloc modülü bulunamadı. Bellek profili oluşturulamadı.")

def main():
    """Ana benchmark fonksiyonu"""
    print("=== AI Psikolog Uygulaması Performans Benchmark ===")
    print(f"Model: {settings.MODEL_NAME}")
    print(f"Ollama API: {settings.OLLAMA_API_BASE}")
    
    # Doğrudan Ollama API'sini test et
    test_direct_ollama_api()
    
    # AI servisini test et
    test_ai_service()
    
    # Chat endpoint'ini test et (sunucu çalışıyorsa)
    try:
        test_chat_endpoint()
    except Exception as e:
        print(f"Chat endpoint testi başarısız: {str(e)}")
        print("Sunucunun çalıştığından emin olun (uvicorn app.main:app)")
    
    # AI servisini analiz et
    analyze_ai_service_code()
    
    # Bellek kullanımını profille
    profile_memory_usage()
    
    print("\n=== Performans Önerileri ===")
    print("1. Ollama API timeout değerini düşürün (şu anda 45 saniye)")
    print("2. Ollama API isteğinde stream=True kullanarak daha erken yanıt almayı deneyin")
    print("3. num_predict değerini düşürerek daha kısa yanıtlar oluşturun")
    print("4. Chroma DB işlemlerini optimize edin, her istekte koleksiyon oluşturmayı önleyin")
    print("5. Uzun süreli bellek işlemlerini asenkron olarak arka planda yapın")
    print("6. api_service.py dosyasındaki hata yakalama ve işleme mantığını optimize edin")
    print("7. Çok uzun sistem mesajlarını kısaltın veya basitleştirin")

if __name__ == "__main__":
    main()