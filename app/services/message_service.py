from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.message import Message as MessageModel
from app.schemas.message import MessageCreate, MessageUpdate


def get_message(db: Session, message_id: int) -> Optional[MessageModel]:
    """
    Get message by ID
    """
    return db.query(MessageModel).filter(MessageModel.id == message_id).first()


def get_session_messages(
    db: Session, 
    session_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[MessageModel]:
    """
    Get all messages for a session with pagination
    """
    return (
        db.query(MessageModel)
        .filter(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_message(db: Session, message: MessageCreate) -> MessageModel:
    """
    Create a new message
    """
    db_message = MessageModel(
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        is_voice=message.is_voice
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_message(db: Session, message_id: int, message_data: MessageUpdate) -> MessageModel:
    """
    Update existing message (only metadata like sentiment, not content)
    """
    db_message = get_message(db, message_id=message_id)
    
    # Update only provided fields
    update_data = message_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_message, key, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int) -> MessageModel:
    """
    Delete message and return deleted message data
    """
    db_message = get_message(db, message_id=message_id)
    db.delete(db_message)
    db.commit()
    return db_message