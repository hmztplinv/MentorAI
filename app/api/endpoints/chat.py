from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.message import ChatRequest, ChatResponse, MessageCreate
from app.services.session_service import get_session
from app.services.message_service import create_message, get_session_messages
from app.services.ai_service import generate_ai_response, check_for_crisis
from app.core.config import settings

router = APIRouter()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    # Check if session exists
    session = get_session(db, session_id=chat_request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if session has ended
    if session.ended_at is not None:
        raise HTTPException(status_code=400, detail="Session has ended")
    
    # Create user message
    user_message = MessageCreate(
        session_id=chat_request.session_id,
        role="user",
        content=chat_request.message,
        is_voice=chat_request.is_voice
    )
    created_user_message = create_message(db=db, message=user_message)
    
    # Check for crisis keywords
    crisis_detected, language = check_for_crisis(chat_request.message)
    if crisis_detected:
        # Update message with crisis flag
        created_user_message.crisis_detected = True
        db.commit()
        
        # Get emergency contacts for the user's language
        emergency_info = settings.EMERGENCY_CONTACTS.get(
            language, 
            settings.EMERGENCY_CONTACTS["en"]  # Default to English
        )
        
        # Generate AI response with crisis handling
        ai_response = generate_ai_response(
            db=db,
            session_id=chat_request.session_id,
            crisis_mode=True
        )
        
        # Create AI message
        ai_message = MessageCreate(
            session_id=chat_request.session_id,
            role="assistant",
            content=ai_response,
            is_voice=False
        )
        created_ai_message = create_message(db=db, message=ai_message)
        created_ai_message.crisis_detected = True
        db.commit()
        
        return ChatResponse(
            response=ai_response,
            crisis_detected=True,
            emergency_info=emergency_info
        )
    
    # Normal message flow
    # Get previous messages for context
    previous_messages = get_session_messages(
        db, 
        session_id=chat_request.session_id, 
        limit=settings.SHORT_TERM_MEMORY_LENGTH
    )
    
    # Generate AI response
    ai_response = generate_ai_response(
        db=db,
        session_id=chat_request.session_id
    )
    
    # Create AI message
    ai_message = MessageCreate(
        session_id=chat_request.session_id,
        role="assistant",
        content=ai_response,
        is_voice=False
    )
    created_ai_message = create_message(db=db, message=ai_message)
    
    return ChatResponse(
        response=ai_response,
        crisis_detected=False
    )