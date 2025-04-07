import requests
import json
import re
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Any
import chromadb 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings
from app.services.message_service import get_session_messages
from app.services.session_service import get_session
from app.services.user_service import get_user
from app.therapists.prompts import get_therapy_approach_prompt


def check_for_crisis(text: str) -> Tuple[bool, str]:
    """
    Check if a message contains crisis keywords
    Returns (crisis_detected, language)
    """
    text_lower = text.lower()
    

    language = "en"
    turkish_chars = re.findall(r'[çğıöşüÇĞİÖŞÜ]', text)
    if turkish_chars:
        language = "tr"
    

    for keyword in settings.CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True, language
    
    return False, language


def get_conversation_context(db: Session, session_id: int) -> Dict[str, Any]:
    """
    Get the context for the conversation including:
    - User info
    - Session info
    - Recent messages
    - Long-term memory (from vector DB)
    """

    session = get_session(db, session_id=session_id)
    if not session:
        return {"error": "Session not found"}
    

    user = get_user(db, user_id=session.user_id)
    if not user:
        return {"error": "User not found"}
    

    messages = get_session_messages(
        db, 
        session_id=session_id, 
        limit=settings.SHORT_TERM_MEMORY_LENGTH
    )
    

    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    

    therapy_approach = session.therapy_approach
    therapy_prompt = get_therapy_approach_prompt(therapy_approach, user.language)
    

    context = {
        "user": {
            "username": user.username,
            "language": user.language,
            "preferred_therapy_approach": user.preferred_therapy_approach
        },
        "session": {
            "id": session.id,
            "therapy_approach": therapy_approach,
            "title": session.title,
            "created_at": session.created_at.isoformat() if session.created_at else None
        },
        "messages": formatted_messages,
        "therapy_prompt": therapy_prompt
    }
    

    try:
        memory_context = get_long_term_memory(db, session_id, user.id)
        if memory_context:
            context["long_term_memory"] = memory_context
    except Exception as e:
        print(f"Error fetching long-term memory: {str(e)}")
    
    return context


def get_long_term_memory(db: Session, session_id: int, user_id: int) -> List[str]:
    """
    Retrieve relevant long-term memories from vector DB
    """

    messages = get_session_messages(db, session_id=session_id, limit=1)
    if not messages:
        return []
    
    last_message = messages[0].content
    
    try:

        import chromadb
        

        client = chromadb.PersistentClient(path=settings.chromadb_DIR)
        

        try:
            collection = client.get_collection("user_memories")
        except:
            print("Collection 'user_memories' not found, creating it")
            collection = client.create_collection("user_memories")
            return []
        

        results = collection.query(
            query_texts=[last_message],
            n_results=3,
            where={"user_id": str(user_id)}
        )
        

        if results and "documents" in results and len(results["documents"]) > 0:
            return results["documents"][0]  # First query results
        
        return []
    
    except Exception as e:
        print(f"Error querying vector db: {str(e)}")
        return []

def store_in_long_term_memory(db: Session, session_id: int, user_id: int, text: str) -> bool:
    """
    Store important information in long-term memory (vector DB) with unique IDs
    """
    try:

        if len(text) < 50:
            return False
        

        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        import uuid
        from datetime import datetime
        

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        

        chunks = text_splitter.split_text(text)
        

        if len(chunks) > 6:
            chunks = chunks[:6]
        

        client = chromadb.PersistentClient(path=settings.chromadb_DIR)
        

        try:
            collection = client.get_collection("user_memories")
        except:
            collection = client.create_collection("user_memories")
        

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_ids = [
            f"mem_{user_id}_{session_id}_{timestamp}_{uuid.uuid4().hex[:8]}_{i}" 
            for i in range(len(chunks))
        ]
        

        metadatas = [
            {
                "user_id": str(user_id), 
                "session_id": str(session_id),
                "timestamp": timestamp,
                "chunk_index": str(i),
                "total_chunks": str(len(chunks))
            } 
            for i in range(len(chunks))
        ]
        

        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=unique_ids
        )
        
        print(f"Successfully stored {len(chunks)} chunks in long-term memory")
        return True
    
    except Exception as e:

        import traceback
        error_trace = traceback.format_exc()
        print(f"Error storing in vector db: {str(e)}")
        print(f"Traceback: {error_trace}")
        return False


def generate_ai_response(
    db: Session, 
    session_id: int, 
    crisis_mode: bool = False
) -> str:
    """
    Generate AI response using the Phi-4 model with optimized performance
    """

    context = get_conversation_context(db, session_id=session_id)
    

    system_message = context.get("therapy_prompt", "")
    

    if crisis_mode:
        language = context.get("user", {}).get("language", "en")
        if language == "tr":
            system_message += "\n\nKullanıcı kriz durumunda olabilir. Sakin ol, empati kur, ve profesyonel yardım aramalarını teşvik et. Acil durum numaralarını paylaşacağım, ama önce kullanıcıyı sakinleştirmeye çalış."
        else:
            system_message += "\n\nThe user may be in crisis. Stay calm, be empathetic, and encourage them to seek professional help. I will provide emergency numbers, but first try to help them calm down."
    

    messages = [{"role": "system", "content": system_message}]
    

    conversation_messages = context.get("messages", [])
    

    if len(conversation_messages) > 25:
        optimized_messages = conversation_messages[-25:]
    else:
        optimized_messages = conversation_messages
    
    messages.extend(optimized_messages)
    

    if "long_term_memory" in context and context["long_term_memory"]:
        memory_points = context["long_term_memory"][:1]  
        memory_content = "Kullanıcı hakkında önceki bilgiler:\n" + "\n".join(memory_points)
        messages.append({"role": "system", "content": memory_content})
    

    print(f"API isteği gönderiliyor: {settings.OLLAMA_API_BASE}/chat")
    print(f"Model: {settings.MODEL_NAME}")
    
    import json  # 
    

    try:
        api_request = {
            "model": settings.MODEL_NAME,
            "messages": messages,
            "stream": False,  
            "options": {
                "num_predict": 600,     # Daha kısa yanıtlar
                "temperature": 0.85,     # Daha az yaratıcı ama hızlı
                "top_p": 0.95,           # Daha odaklı yanıtlar
                "top_k": 80,            # Token seçimini sınırla
                "seed": None              # Tutarlı yanıtlar için
            }
        }
        
        print(f"Ollama API isteği: {json.dumps(api_request, ensure_ascii=False)[:200]}...")
        
        response = requests.post(
            f"{settings.OLLAMA_API_BASE}/chat",
            json=api_request,
            timeout=120  
        )
        
        if response.status_code == 200:
            try:

                result = response.json()
                ai_response = result.get("message", {}).get("content", "")
            except json.JSONDecodeError:

                print("JSON ayrıştırma hatası, alternatif işleme yapılıyor")

                text = response.text.strip()
                if text:

                    last_json_end = text.rfind("}")
                    if last_json_end > 0:
                        last_json_start = text.rfind("{", 0, last_json_end)
                        if last_json_start >= 0:
                            try:
                                last_json_str = text[last_json_start:last_json_end+1]
                                last_json = json.loads(last_json_str)
                                ai_response = last_json.get("message", {}).get("content", "")
                            except:
                                ai_response = "Yanıt işlenemedi."
                        else:
                            ai_response = "Yanıt ayrıştırılamadı."
                    else:
                        ai_response = "Geçerli yanıt bulunamadı."
                else:
                    ai_response = "Boş yanıt alındı."
            


            if len(ai_response) > 100 and not crisis_mode:  
                user_id = context.get("session", {}).get("user_id", 0)
                if user_id > 0:  
                    try:
                        store_in_long_term_memory(db, session_id, user_id, ai_response)
                    except Exception as e:
                        print(f"Hafıza depolamada hata: {str(e)}")
            
            return ai_response
        else:
            print(f"API Hatası: {response.status_code} - {response.text}")
            return get_fallback_response(context.get("user", {}).get("language", "en"))
    
    except requests.exceptions.Timeout:
        print("API isteği zaman aşımına uğradı.")
        return get_fallback_response(context.get("user", {}).get("language", "en"))
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return get_fallback_response(context.get("user", {}).get("language", "en"))

def get_fallback_response(language: str) -> str:
    """
    Return a fallback response if the AI generation fails
    """
    if language == "tr":
        return "Özür dilerim, şu anda yanıt oluşturmakta sorun yaşıyorum. Lütfen biraz sonra tekrar deneyin."
    else:
        return "I apologize, but I'm having trouble generating a response right now. Please try again shortly."