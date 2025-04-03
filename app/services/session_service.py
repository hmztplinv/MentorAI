from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate


def get_session(db: Session, session_id: int) -> Optional[SessionModel]:
    """
    Get session by ID
    """
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_session_with_messages(db: Session, session_id: int) -> Optional[SessionModel]:
    """
    Get session with all messages
    """
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[SessionModel]:
    """
    Get all sessions for a user with pagination
    """
    return (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_session(db: Session, session: SessionCreate) -> SessionModel:
    """
    Create a new session
    """
    db_session = SessionModel(
        user_id=session.user_id,
        therapy_approach=session.therapy_approach,
        title=session.title or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: int, session_data: SessionUpdate) -> SessionModel:
    """
    Update existing session
    """
    db_session = get_session(db, session_id=session_id)
    
    # Update only provided fields
    update_data = session_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def end_session(db: Session, session_id: int) -> SessionModel:
    """
    End a session by setting ended_at timestamp
    """
    db_session = get_session(db, session_id=session_id)
    db_session.ended_at = datetime.now()
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int) -> SessionModel:
    """
    Delete session and return deleted session data
    """
    db_session = get_session(db, session_id=session_id)
    db.delete(db_session)
    db.commit()
    return db_session


def generate_session_summary(db: Session, session_id: int) -> str:
    """
    Generate a summary of the session
    """
    db_session = get_session(db, session_id=session_id)
    
    # This would be implemented with LLM in ai_service.py
    # For now, just return a placeholder
    summary = f"Session summary for session {session_id}"
    
    # Update the session with the summary
    db_session.summary = summary
    db.commit()
    
    return summary