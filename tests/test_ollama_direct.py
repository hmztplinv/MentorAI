import requests
import json
import time

def test_ollama_direct():
    print("Ollama API doğrudan test ediliyor...")
    
    data = {
        "model": "phi4:latest",
        "messages": [{"role": "user", "content": "Merhaba, nasılsın?"}],
        "stream": False  
    }
    
    print(f"Gönderilen veri: {json.dumps(data, ensure_ascii=False)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=data,
            timeout=60
        )
        
        end_time = time.time()
        print(f"Yanıt süresi: {end_time - start_time:.2f} saniye")
        
        if response.status_code == 200:
            print(f"Ham yanıt: {response.text[:200]}...")
            
            try:
                result = response.json()
                print(f"Ollama Yanıtı: {result.get('message', {}).get('content', '')}")
            except json.JSONDecodeError as e:
                print(f"JSON ayrıştırma hatası: {e}")
        else:
            print(f"API Hatası: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    test_ollama_direct()