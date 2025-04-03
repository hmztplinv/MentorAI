import requests
import json
import re
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Any
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

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
    
    # Detect language (simple approach, for production use a proper language detector)
    language = "en"
    turkish_chars = re.findall(r'[çğıöşüÇĞİÖŞÜ]', text)
    if turkish_chars:
        language = "tr"
    
    # Check for crisis keywords
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
    # Get session
    session = get_session(db, session_id=session_id)
    if not session:
        return {"error": "Session not found"}
    
    # Get user
    user = get_user(db, user_id=session.user_id)
    if not user:
        return {"error": "User not found"}
    
    # Get recent messages
    messages = get_session_messages(
        db, 
        session_id=session_id, 
        limit=settings.SHORT_TERM_MEMORY_LENGTH
    )
    
    # Format messages for context
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Get therapy approach prompt
    therapy_approach = session.therapy_approach
    therapy_prompt = get_therapy_approach_prompt(therapy_approach, user.language)
    
    # Create context
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
    
    # Add long-term memory if available
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
    # Get the last message to use as query
    messages = get_session_messages(db, session_id=session_id, limit=1)
    if not messages:
        return []
    
    last_message = messages[0].content
    
    try:
        # Initialize Chroma client
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        collection = client.get_collection("user_memories")
        
        # Query for relevant memories
        results = collection.query(
            query_texts=[last_message],
            n_results=3,
            where={"user_id": str(user_id)}
        )
        
        # Return documents if found
        if results and "documents" in results:
            return results["documents"][0]  # First query results
        
        return []
    
    except Exception as e:
        print(f"Error querying vector db: {str(e)}")
        return []


def store_in_long_term_memory(db: Session, session_id: int, user_id: int, text: str) -> bool:
    """
    Store important information in long-term memory (vector DB)
    """
    try:
        # Skip if text is too short
        if len(text) < 50:
            return False
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # Initialize Chroma client
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        collection = client.get_collection("user_memories")
        
        # Add chunks to memory
        collection.add(
            documents=chunks,
            metadatas=[{"user_id": str(user_id), "session_id": str(session_id)} for _ in chunks],
            ids=[f"mem_{user_id}_{session_id}_{i}" for i in range(len(chunks))]
        )
        
        return True
    
    except Exception as e:
        print(f"Error storing in vector db: {str(e)}")
        return False


def generate_ai_response(
    db: Session, 
    session_id: int, 
    crisis_mode: bool = False
) -> str:
    """
    Generate AI response using the Phi-4 model
    """
    # Get conversation context
    context = get_conversation_context(db, session_id=session_id)
    
    # Create system message based on therapy approach
    system_message = context.get("therapy_prompt", "")
    
    # Add crisis handling if needed
    if crisis_mode:
        language = context.get("user", {}).get("language", "en")
        if language == "tr":
            system_message += "\n\nKullanıcı kriz durumunda olabilir. Sakin ol, empati kur, ve profesyonel yardım aramalarını teşvik et. Acil durum numaralarını paylaşacağım, ama önce kullanıcıyı sakinleştirmeye çalış."
        else:
            system_message += "\n\nThe user may be in crisis. Stay calm, be empathetic, and encourage them to seek professional help. I will provide emergency numbers, but first try to help them calm down."
    
    # Format messages for API call
    messages = [{"role": "system", "content": system_message}]
    
    # Add conversation history
    for msg in context.get("messages", []):
        messages.append(msg)
    
    # Add memory context if available
    if "long_term_memory" in context and context["long_term_memory"]:
        memory_content = "Previous information about the user:\n" + "\n".join(context["long_term_memory"])
        messages.append({"role": "system", "content": memory_content})
    
    # Set up API request to Ollama
    try:
        response = requests.post(
            f"{settings.OLLAMA_API_BASE}/chat",
            json={
                "model": settings.MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("message", {}).get("content", "")
            
            # Store important responses in long-term memory
            if len(ai_response) > 100:  # Only store substantial responses
                user_id = context.get("session", {}).get("user_id")
                store_in_long_term_memory(db, session_id, user_id, ai_response)
            
            return ai_response
        else:
            print(f"API Error: {response.status_code} - {response.text}")
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